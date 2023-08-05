#! /usr/bin/env python3

from ast import literal_eval as make_tuple
from lal import gpstime
from scipy import signal
from scipy.interpolate import interp1d
from gwpy.time import to_gps, from_gps
from gwpy.timeseries import TimeSeries
from math import ceil
from os import path
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import argparse
import os
import time
import sys
import pickle
import json
import logging

from tensorflow.keras.models import load_model

# Sourcing the submodule of mly in a very unpythonic way 
sys.path.append("/".join(sys.argv[0].split("/")[:-1])+"/mly/")

print("/".join(sys.argv[0].split("/")[:-1])+"/mly/")


from mly.datatools import DataPod
from mly.validators import Validator
from mly.null_energy_map import *
from search_functions import *


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# # # Initialising logging

# create logger
logger = logging.getLogger("logger_for_search")
logger.setLevel(logging.INFO)



# create console handler and set level to debug
ch = logging.handlers.TimedRotatingFileHandler('log/search.log', when='H',interval=1, backupCount=1,)
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)





def main(**kwargs):
    """ Main functionality of the search script. Given the arguments
    provided it conducts a real time search on gravitational wave data. It
    uses a predefined given model for iference.

    Parameters
    ----------

    detectors: {'HL','HLV'}
        It specifies which detectors to use to conduct the search. If 'HL' is
        chosen, it generates gaussian noise that follows Virgo background(x32),
        to provide nominal data for Virgo.

    channels: {'NOISE','MDC'}
        It specifies which channel to use for the search.
        'NOISE' represents a predefined set of channels without injections.
        'MDC' represents a predifned set of channels with injections for the MDC

    threshold : float
        The minimum score for witch the search will issue a trigger event.

    output_directory: str (path, optional)
        The path of the directory where the search will save the output of the model
        for each instance processed. If not specified it doesn't save the outputs.

    trigger_directory: str (path, optional)
        The path of the directory where the search will save the output of the model
        for each instance that was above the threshold value. If not specified
        it doesn't save anything. It is important to have this directory specified if
        you want to send triggers to GraceDB (using mly_to_grace.py).

    triggerplot_directory: str (path, optional)
        The path of the file where the search will save a plot of the timeseries data
        for each instance that was above the threshold value and issued a trigger.

    trigger_destination: {'test, 'playground', 'dev1', None}
        The GraceDB domain for the triggers to be uploaded. Each option represent
        a corresponding url. If equals to None, it will not issue an GraceDB event.
        
    splitter: list
        A way to split the search into different parallel jobs. The list must have
        two parameters. The first is the amount of scripts this search is split into.
        The second is which part of the split this function will run. For example a 
        splitter value of [4,1] means that we will splitted the search into 4 scripts
        where each script processes every other 4 seconds, and that this function will
        run the every 4 plus 1 seconds part. For a full search we will have to run the
        same function for splitter values of: [4,0], [4,1], [4,2], [4,3]. If not 
        specified it is equal to [1,0]
        
    skymap: bool
        If True it will allow the creation of a skymap whenever it issues events. This
        is passed to another function 'mly_to_grace'.
    
    time_reference: float
        A unix time reference so that should be the same among different functions when
        used splitter. It is suggested to use `unixtime=$(date +%s)` at the beggining of
        the script and pass `$unixtime` as time_reference.    
        
    fileSystem: str/path
        A path to a valid file system directory. A valid file system
        directory needs to have subfolders with the initials of all
        detectors used and a 'temp' file that also includes subfolders
        with initials of all detectors. This is used for the calculation
        of continues false alarm rates. If not specified, it will not save data 
        into the file system.
        
    bufferDirectory: str/path
        A directory path where it will save the buffer data around each second
        to be used for the calculation of efficiencies. If not specified, it 
        will not save the buffer data.
        
    Note
    ----

    This function doesn't return anything. It runs until it is stoped or until it
    raises an Exception.
    """


    start_time = time.time()


    with open('config.json') as json_file:
        config = json.load(json_file)
    
    config = { **config , **kwargs }
    # # # Command line arguments processing
    
    # Check arguments and set values in config dict:
    config = checkArguments(config)
    config['logger'] = 'search.log'




    # # # Setup parameters for the models
    
    # Loading models
    
    model1 = load_model(config["model1_path"]) # Load coincidence model
    model2 = load_model(config["model2_path"]) # Load coherence model
    td_pe_model = load_model(config["td_pe_model_path"]) # Load time-domain PE model
    fd_pe_model = load_model(config["fd_pe_model_path"]) # Load frequency-domain PE model
    logger.info(f"S{config['script_index']} - Loading models complete.")

    # This parameter format is used in inference
    
    models = [
        [model1 , model2],
        [["strain"], ["strain","correlation"]]
        ]      
    
    # Mapping keeps consistent the categorical format
    mapping = 2 * [{
        "noise": [1, 0],
        "signal": [0, 1]
    }]
    
    
    
    # # # Initialization before loop
    
    # For all scripts we need a common reference of gps time,
    # That time depends on the tiem reference provided at the start
    # and the start lag.
    initial_gps_time = config['time_reference'] - config["start_lag"] 
    
    # GPS index counts how many gps times have been searched by this script alone:
    gps_index = 0 
    
    subconfig = config.copy()
    for key in ['detectors','fs','duration','restriction','prefixes','frames','channels','size']:
        subconfig.pop(key,None)
    
    
    # # # Main Loop
    while (1):  
        
        # Get GPS time for this script to search
        gps_time, gps_index = calculateRequiredGPSTime(config, gps_index, initial_gps_time)
        logger.info(f"S{config['script_index']} - Requested / Difference from current GPS time: {gps_time} / {gpstime.gps_time_now() - gps_time}")

        
        loopt0 = time.time()  #Get time at iteration start.
        
        # # Data Aquisition 
        buffers = aquireData(config, gps_time)
        
        getdatatime=time.time()
        
        # If data aquisition fails, reset loop:
        if (buffers is None):
            sys.stdout.flush()
            continue
            
        logger.info(f"S{config['script_index']} - Detector data aquisition time: {getdatatime - loopt0}") 
        
        gpsBeforeInference = gpstime.gps_time_now()
        timeBeforeInference = time.time()
                
        # # Data processing and inference
        
        # Putting data inside datapod format 
        buffer_pod = DataPod(
            np.array(buffers),
            detectors = config["detectors"], 
            fs = config["fs"], 
            gps = len(config["detectors"])*[float(gps_time)] 
        )
        

        result, thepod = Validator.falseAlarmTest(
                                        models = models,
                                        duration = config["duration"],
                                        fs =  config["fs"],
                                        size = 1,
                                        detectors = config["detectors"],
                                        backgroundType = "real",
                                        noiseSourceFile = buffer_pod,
                                        windowSize = config["required_buffer"],          
                                        mapping = mapping,
                                        strides = None,
                                        plugins = ["correlation_30",'snr'],
                                        restriction = None,
                                        podreturn = True,
                                        **subconfig
                                    )
        # Change format of detector name to include 1 (ex. H->H1)
        ifos = [f"{detector}1" for detector in config["detectors"]] 
        
        # Create mly_output dictionary, GraceDB event file basis
        
        interpolated_FAR_t0=time.time()
        interpolated_FAR_trials = 0
        while interpolated_FAR_trials < 3:
            try:
                interpolated_FAR = far(config['farfile']+"/"+"FARfile_interpolation.pkl"
                                    ,result["total"][0], inverse = False)
                break
            except:
                try:
                    interpolated_FAR = far(config['farfile']+"/"+"FARfile_interpolation_reserve.pkl"
                                        ,result["total"][0], inverse = False)
                    break
                except Exception as e:
                    interpolated_FAR_trials+=1
                    if interpolated_FAR_trials >= 3:
                        raise e
        logger.info(f"S{config['script_index']} - Loading interpolated_FAR time: ",time.time()-interpolated_FAR_t0,interpolated_FAR_trials)


        mly_output = {
            "gpstime": result["GPSH"][0],
            "far": interpolated_FAR,
            "ifos": ifos,
            "scores": {
                "coincidence": result["scores1"][0],
                "coherency": result["scores2"][0],
                "combined": result["total"][0]
            }

        }
        
        
        # Internal latency, from GPS selection to scores.
        logger.debug(f"S{config['script_index']} - internal_latency", gpsBeforeInference - gps_time)

        # # # Follow up
        
        # Print scores
        print(mly_output["scores"])

        # Create string of joined detector names
        detectors = "".join(config["detectors"])

        threshold_t0=time.time()
        threshold_trials = 0
        while threshold_trials < 3:
            try:
                threshold = far(config['farfile']+"/"+"FARfile_interpolation_inverse.pkl"
                                    ,config['far_config']['threshold'], inverse = True)
                break
            except:
                try:
                    threshold = far(config['farfile']+"/"+"FARfile_interpolation_inverse_reserve.pkl"
                                        ,config['far_config']['threshold'], inverse = True)
                    break
                except Exception as e:
                    threshold_trials+=1
                    if threshold_trials >= 3:
                        raise e
        logger.debug(f"S{config['script_index']} - Loading threshold interpolation time: ",time.time()-threshold_t0,threshold_trials)


            
        # If result us above threshold, do all even relate actions 
        if mly_output["scores"]["combined"] >= threshold:
            # Perform time- and frequency-domain parameter estimation.
            # It adds parameter estimation to events.
            mly_output = runTimeFrequencyParameterEstimation(
                thepod, td_pe_model, fd_pe_model, mly_output
            )
            
            # Saving trigger into the trigger_directory
            with open(f"{config['trigger_directory']}/T_{mly_output['gpstime']}_{detectors}.json", "w") as mly_json:
                json.dump(mly_output, mly_json,indent=4)
                mly_json.close()

            # Saving trigger DataPod into the trigger_directory
            with open(f"{config['trigger_directory']}/T_{mly_output['gpstime']}_{detectors}.pkl", 'wb') as mly_pkl:
                pickle.dump(thepod, mly_pkl, 4)
                
            # Saving trigger background DataPod into the trigger_directory
            with open(f"{config['trigger_directory']}/T_{mly_output['gpstime']}_{detectors}_buffer.pkl", 'wb') as mly_pkl:
                pickle.dump(buffer_pod, mly_pkl, 4)
                                
            # Sending trigger to GraceDB 

            with open( f"{config['trigger_directory']}/T_{mly_output['gpstime']}_{detectors}.out"
            ,"wb") as out:

                # Using subprocess to create mly_to grace function and run it independently.
                p = subprocess.Popen(["python", config["mlyPipelineSource"]+"/mly_to_grace.py", "--triggerfile"
                                      ,f"{config['trigger_directory']}/T_{mly_output['gpstime']}_{detectors}.json"
                                      ,"--trigger_destination", str(config['trigger_destination'])
                                      ,"--triggerplot_directory",config['triggerplot_directory']
                                      ,"--config",str(config)
                                      ,"--skymap", str(config['skymap'])]
                                      #+" > "+f"{config['trigger_directory']}/T_{mly_output['gpstime']}_{detectors}.out &"
                                      ,stdout=out, stderr=out,shell=False)
            
            logger.info(f"S{config['script_index']} - TRIGGER follow-up script initialised for: "+str(mly_output['gpstime']))
                

            # Saving output to output directory. Notice that the name starts with T_ for triggers
            if config["output_directory"] != None:
                with open(f"{config['output_directory']}T_{mly_output['gpstime']}_{detectors}.json", "w") as mly_json:
                    json.dump(mly_output, mly_json,indent=4)
                    mly_json.close()
                    
        # If result is below threshold, we just save the output. Note that the name starts with N_
        elif config["output_directory"] != None:
            
            with open(f"{config['output_directory']}N_{mly_output['gpstime']}_{detectors}.json", "w") as mly_json:
                json.dump(mly_output, mly_json, indent=4)
                mly_json.close()
                
        # If fileSystem parameter is provided, we save the second processed by the model in
        # the file system directory.
        if config["masterDirectory"]!=None:
            podToFileSystem(thepod, masterDirectory = config["masterDirectory"])

        # If bufferDirectory is provided, we save the buffer_pod in the 
        # buffer directory.
        if config["bufferDirectory"] != None:
            buffer_pod.save(config["bufferDirectory"] 
                            + "temp/" + str(buffer_pod.gps[0]) 
                            + "_" + str(int(buffer_pod.duration)))  
        
        # Timing the loop to see if we need more splits in splitter.
        print(f"Processing loop duration: {str(time.time()-timeBeforeInference)}")  
        
        gps_time += config["num_scripts"]
        
        sys.stdout.flush()

        if time.time() - start_time > 24*3600:

            os.system(f"> search_step_{config['script_index']}.out")      


if __name__ == "__main__":

    # List of arguments to pass:
    arguments = [
        "splitter",
        "time_reference",
    ]

    # Construct argument parser:
    parser = argparse.ArgumentParser()
    [parser.add_argument(f"--{argument}") for argument in arguments]

    # Pass arguments:
    args = parser.parse_args()

    # Store arguments in dictionary:
    kwargs = {}
    for argument in arguments:
        kwargs[argument] = getattr(args, argument)

    main(**kwargs)
