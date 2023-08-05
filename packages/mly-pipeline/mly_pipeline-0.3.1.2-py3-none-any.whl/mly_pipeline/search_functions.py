import json, pickle, sys, time, os, argparse

import numpy             as np
import matplotlib.pyplot as plt

from os                import path
from math              import ceil
from gwpy.timeseries   import TimeSeries
from gwpy.segments     import SegmentList, Segment
from gwpy.time         import to_gps, from_gps
from scipy.interpolate import interp1d
from scipy             import signal
from lal               import gpstime
from dqsegdb2.query    import query_segments

from ast               import literal_eval as make_tuple

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from tensorflow.keras.models import load_model
from tensorflow.keras import Model

# Sourcing the submodule of mly in a very unpythonic way 
sys.path.append("/".join(sys.argv[0].split("/")[:-1])+"/mly/")



    
from mly.datatools import DataPod
from mly.validators import Validator


def checkDetectorArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked detector parameters.
        
       Parameters
       ----------
       
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------
    
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    """
    
    #Detector options: 
    allowed_detectors = "HLV"
    default_detectors = "HLV"
           
    # Check detector arguments:    
    if config["detectors"] == None: 
        # Output warning and set detectors to default if no detectors inputted.
        print(f"Warning! No detectors inputted. Using default detector values: \
 {default_detectors}")
        config["detectors"] = list(default_detectors)     
    elif not all((det in allowed_detectors) for det in config["detectors"] ):
        # Output warning and set detectors to default if no detectors inputted
        # not allowed.
        print(f"Warning! No invalid detectors inputted: {config['detectors']} \
        only {allowed_detectors} allowed. Using default detector values: \
        {default_detectors}")
        config["detectors"] = list(default_detectors)
    else:
        # Set config to list of inputted detectors if inputted and valid.
        config["detectors"] = list(config["detectors"])
    
    return config

def checkChannelArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked channel parameters.
       
       Parameters
       ----------

       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------

       config: dict
           Dictionary containing program runtime variables
    """
    # Check if channels is a dictionary
    if not isinstance(config['channels'],dict):
        raise TypeError("Channel must be a dictionary, with keys the initials of the detectors.")
    # Check if channels has all the detectors
    # if not config["detectors"]==list(config['channels'].keys()):
    #     raise ValueError("Missmach of the length of detectors and the number of channels")

    return config

def checkThresholdArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked threshold parameters.
       
       Parameters
       ----------

       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------

       config: dict
           Dictionary containing program runtime variables
    """
    
    # Check threshold arguments:    
    if config["far_config"]["threshold"] != None:
        threshold = float(config["far_config"]["threshold"])
        if threshold <= 0:
            # Raise error if threshold is not above 0.
            raise ValueError(f"Error! Inputted threshold {threshold} must be \
 greater than zero.");
        elif not isinstance(threshold,(int,float)):
            # Raise error if threshold is not float or integer.
            raise ValueError(f"Error! Inputted threshold {threshold} must be \
 float or integer.");
        else: 
            # Set config threshold to threshold if present, a valid type and
            # above 0.
            config["far_config"]["threshold"] = threshold
    else:
        # Raise error if no threshold inputted.
        raise ValueError(f"Error! No threshold inputted. Please input a threshold \
 value using the following syntax when running the command --threshold <value>.");
    
    return config

def checkOutputDirectoryArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked output directory parameters.
       
       Parameters
       ----------

       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------

       config: dict
           Dictionary containing program runtime variables
    """
    
    # Check output directory:
    if config["output_directory"] != None:
        if not os.path.isdir(config["output_directory"]):
            # Raise error if directory does not exist:
            raise FileNotFoundError(f"{config['output_directory']} is not a valid path.")
    
        if config["output_directory"][-1] != "/":
            config["output_directory"] += "/"
    else:
        # If output directory does not exist set config output_directory to None:
        config["output_directory"] = None
    
    return config

def checkTriggerDirectoryArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked trigger directory parameters.
       
       Parameters
       ----------

       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------

       config: dict
           Dictionary containing program runtime variables
    """
    
   #Check trigger directory:
    if config["trigger_directory"] != None:
        if os.path.isdir(config["trigger_directory"]):
            # Set config trigger directory if trigger directory argument present and directory
            # exists.
            config["trigger_directory"] = config["trigger_directory"]
        else:
            # Raise error if trigger directory does not exist:
            raise FileNotFoundError(f"{config['trigger_directory']} is not a valid path")
    else:
        # Raiser error if no trigger directory inputted:
        raise FileNotFoundError("You need to specify a directory where the triggers \
 will be saved using the following syntax when running the command --trigger_directory <value>.")
    
    return config

def checkTriggerPlotDirectoryArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked trigger plot directory parameters.
       
       Parameters
       ----------
       
       config: dict
           Dictionary containing program runtime variables
    
       Returns
       ------- 
       
       config: dict
           Dictionary containing program runtime variables
    """
    
    #Check trigger plot directory:
    if config['triggerplot_directory'] != None:
        if os.path.isdir(config['triggerplot_directory']):
            # Set config trigger directory if trigger directory argument
            # present and directory exists.
            config["triggerplot_directory"] = config["triggerplot_directory"]
        else:
             # Raise error if triggerplot directory does not exist.
            raise FileNotFoundError(f"{config['triggerplot_directory']} is not a valid path")
    else:
        # If output directory does not exist set trigger plot directory to None.
        config["triggerplot_directory"] = None
    
    return config

def checktriggerDestinationArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked trigger_destination parameters.
       
       Parameters
       ----------

       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------

       config: dict
           Dictionary containing program runtime variables
    """

    if config['trigger_destination']!=None:

        if config['trigger_destination'] in ['test','playground','dev1']:
            url = "https://gracedb-"+config['trigger_destination']+".ligo.org/api"
            print("Current trigger_destination url is :"+url)
                
            config['trigger_destination'] = url

        elif config['trigger_destination'] == 'online':
            url = "https://gracedb-test.ligo.org/api"
            print("Current trigger_destination url is :"+url)
        else:
            raise ValueError("https://gracedb-"+config['trigger_destination']+".ligo.org/api not a valid trigger_destination")
    else:
        
        config['trigger_destination'] = None
    
    return config

def checkSplitArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked splitter parameters.
       
       Parameters
       ----------

       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------
           
       config: dict
           Dictionary containing program runtime variables
    """
    
    #Check split value:
    if config["splitter"]!=None:
        try:
            config["splitter"] = make_tuple(config["splitter"])
        except:
            #Raise exception if splitter cannot be made into tuple set splitter to None.
            raise ValueError(f"Error! splitter value {config['splitter']} cannot be \ made into tuple.")
        if not isinstance(config['splitter'],(list,tuple)):
            config["splitter"] = None
        elif config["splitter"][1]>=0:
            config["num_scripts"]  = config['splitter'][0]
            config["script_index"] = config['splitter'][1]
        else:
            raise ValueError("splitter must be a list or a tuple of two values. "
                             "The first is the number of scripts to split the search"
                             " and the second is the label (each for each script) of the individual scripts")                      
    else:
        config["num_scripts"]  = 1 
        config["script_index"] = 1    
    
    return config

def checkTimeReferenceArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked output directory parameters.
       
       Parameters
       ----------
       
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------
    
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    """
    
    # Check output directory:
    if config['time_reference'] == None and "OFFLINE" not in config["search_mode"]:
        
        raise ValueError("You need a common reference of unix time for the splitter"
                        " otherwize you might have overlapin analysis")
    elif isinstance(config['time_reference'],(str,int)):
        
        config["time_reference"] = int(config['time_reference'])-315964782

    elif "OFFLINE" not in config["search_mode"]:

        raise ValueError("time_reference must be the current unix time in numerical or string format")

    return config

def checkSkymapArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked output directory parameters.
       
       Parameters
       ----------
       
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------
    
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    """
    
    # Check output directory:
    if config['skymap']==None:
        config['skymap']=False
    if isinstance(config['skymap'],str):
        config['skymap']=bool(config['skymap'])
    
    if not isinstance(config['skymap'],bool):
        raise TypeError("skymap option must be True or False")
    else:

        return config

    
def checkMasterDirectoryArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked output directory parameters.
       
       Parameters
       ----------
       
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------
    
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    """
    # Check output directory:
    if config['masterDirectory']==None:
        pass
    elif isinstance(config['masterDirectory'],str) and os.path.isdir(config['masterDirectory']):
        if config['masterDirectory'][-1]!='/': config['masterDirectory']+='/'
    elif "OFFLINE" not in config["search_mode"]:
        raise ValueError("The masterDirectory is not properly defined: "+config['masterDirectory'])

    return config


def checkBufferDirectoryArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary with error checked output directory parameters.
       
       Parameters
       ----------
       
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------
    
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    """
    # Check buffer directory:
    if config["bufferDirectory"] != None:
        if os.path.isdir(config["bufferDirectory"]):
            # Set config buffer directory if buffer directory argument present and directory
            # exists.
            if config["bufferDirectory"][-1]!='/':
                config["bufferDirectory"]+= "/"
            config["bufferDirectory"] = config["bufferDirectory"]
        elif "OFFLINE" not in config["search_mode"]:
            # Raise error if directory does not exist:
            raise FileNotFoundError(f"{config['bufferDirectory']} is not a valid path.")
    else:
        # If output directory does not exist set config output_directory to None:
        config["bufferDirectory"] = None
    
    return config
    


def check_segment_list(config):

    if  "OFFLINE" not in config["search_mode"]:
        return config

    segment_list = config['segment_list']

    if isinstance(segment_list,str):
        segment_list = list(Segment(el[0],el[1]) for el in np.loadtxt( segment_list , delimiter = ','))
        segment_list = SegmentList( segment_list).coalesce()

    elif isinstance(segment_list,list) and all(isinstance(el,(int,float)) for el in segment_list ) and len(segment_list)==2:

        config = find_default_segments(config)

        segment_list = config['segment_list']

    if isinstance(segment_list,list) and len(segment_list)!=0:
        segment_list = SegmentList( segment_list).coalesce()

        segment_list_cleared = []
        for i, seg in enumerate(segment_list):
            if (seg[1]-seg[0]) > config["required_buffer"]: 
                segment_list_cleared.append(seg)
        segment_list_cleared = SegmentList(segment_list_cleared).coalesce()

        config['segment_list'] = segment_list_cleared

    else:
        raise ValueError("No segment list provided", config['segment_list'])


    # Breaking up segments that are bigger than the max_continuous_segment
    segment_list_capped = []
    for segment in segment_list_cleared:
        segment_size = segment[1] - segment[0]

        if segment_size >  config['max_continuous_segment'] + config["required_buffer"] - config["duration"]:
            # Number of segments-1 to brake the original segment
            breaks = int(segment_size /  ( config['max_continuous_segment'] + config["required_buffer"] - config["duration"]) )
            for k in range(breaks):
                segment_list_capped.append(Segment(
                                     segment[0]+k* config['max_continuous_segment']
                                    ,segment[0]+(k+1)* config['max_continuous_segment'] + config["required_buffer"] - config["duration"]))
            # The remaining segment without window correction must also be

            remnant_size = segment[1]-(segment[0]+(k+1)* config['max_continuous_segment'] + config["required_buffer"] - config["duration"])
            
            if remnant_size >= config["required_buffer"]:
                segment_list_capped.append(Segment(segment[0]+(k+1)* config['max_continuous_segment']
                                                  ,segment[0]+(k+1)* config['max_continuous_segment']+remnant_size))
        elif config["required_buffer"] - config["duration"] <= segment_size < config['max_continuous_segment']:

            segment_list_capped.append(Segment(segment[0] ,segment[1]))

    config['segment_list'] = segment_list_capped 

    return config

        
        

    
def checkArguments(config):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary. Includes error checking.
       
       Parameters
       ----------
       
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------
    
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    """
    
    check_functions = [
        checkDetectorArguments, 
        checkChannelArguments, 
        checkThresholdArguments,
        checkOutputDirectoryArguments,
        checkTriggerDirectoryArguments,
        checkTriggerPlotDirectoryArguments,
        checktriggerDestinationArguments,
        checkSplitArguments,
        checkTimeReferenceArguments,
        checkSkymapArguments,
        checkMasterDirectoryArguments,
        checkBufferDirectoryArguments,
        
        check_segment_list,
        stackVirgo, 
        check_filename_prefix
    ]
    
    for function in check_functions:
        config = function(config)

    return config 

def stackVirgo(config): 
    
    """If virgo detector is not present adds new pure noise channel in its place.
       
       Parameters
       ----------
       
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    
       Returns
       -------
    
       config: dict 
           Dictionary containing comand line arguments
           
       config: dict
           Dictionary containing program runtime variables
    """
    
    #If in HL mode add white noise as virgo channel:
    if "V" not in config["detectors"]:
        
        del config["frames_directory"]['V']
        del config["channels"]['V']

        config["stackDetectorDict"] = { 
            "duration": config["duration"],
            "fs": config["fs"],
            "detectors" : "V",
            "backgroundType" :"optimal",
            "PSDm":{"V": 32}
        }
        
    return config 

def check_filename_prefix(config):
    # Issue to sort out for .read and .get methods
    prefix_name_list = []
    for k in list(config['frames_directory'].keys()):
        frame_files = os.listdir(config['frames_directory'][k])
        print(frame_files[0])
        prefix_name_list.append(frame_files[0].split("-1")[0][5:]+"-")
    
    if all( name == prefix_name_list[0] for name in prefix_name_list):
        config['prefix'] = prefix_name_list[0]
        return config
    else:
        raise ValueError("Prefix names are not consistent in frames")


    
def readFrameFile(frames, channel, start_gps = None, end_gps = None, wait = 0.5, timeout = 10, count=0):
    
    """A wrapper function for TimeSeries.read from gwpy. It reads the channels
    from the frames provided. If the reading fails for any reason it 
    waits <wait> time and tries again, up to <timeout> times.
    
    Parameters
    ----------
    
    frames : str/list of strings
        A the paths to all the frame files to be read. When reading more
        than one frame file, make sure they are continuous and they have
        not been through any prossessing beforhand.
        
    channel: str 
        The channel to read from the frame filies.
        
    wait : float (seconds)
        The amount of time to wait before retring.
        
    timeout: int 
        The amount of times the script will try to get the data.
        
    count: int
        This is used only for the recursive part of the function.
        It is the number of times it already tried.
        
        
    Returns
    -------
    
    timeseries data: gwpy.timeseries.TimeSeries 
        If data are fetched sucessfully it returns a gwpy TimeSeries
        
    None: 
        If data are not fetched after <timeout> attemts

    """

    try:
        data = TimeSeries.read(frames, channel, start = start_gps, end = end_gps)
        return data
        
    except Exception as e:

        time.sleep(wait)
        count += 1;
        
        if count < timeout:
            return readFrameFile(frames, channel, start_gps, end_gps 
                                    , wait = wait, timeout=timeout, count = count)
            
        else:
            print(e)
            print("Could not find frames.")
            
        return None
    
def far_interpolation(testfile, testNumber, inverse = False):

    """Creates an interpolation function based on the FARfile
    provided. 
       
    Parameters
    ----------
    
    testfile: str (path)
        The pickle file or the path to that file, 
        that has the false alarm test values to be used 
        for the interpolation.
        
    testNumber: int 
        The file provided might only have the loudest 
        results from a bigger test dustribution. By defining
        testNumber the total number of thests is used.
        
    inverse: bool
        If false it will give an interpolation of FAR to scores.
        Or if true it will give an interpolation of scores to given FAR.
    
    Returns
    -------

    interpolation function: scipy.interpolate
    """
    if isinstance(testfile,str):
        with open(testfile,'rb') as obj:
            dataR = pickle.load(obj)
    else:
        dataR = testfile
                
    # dataR= dataR[dataR['score'] > 0.0001]

    try:
        scoreR=np.sort(np.array(dataR['score'])).tolist()[::-1]
    except Exception as e:
        scoreR=np.sort(np.array(dataR['scores1'])*np.array(dataR['scores2'])).tolist()[::-1]
    scoreFrequency=(np.arange(len(scoreR))+1)/testNumber
    
    if inverse==False:
        
        farInterpolation=interp1d(
            scoreR,
            scoreFrequency,
            bounds_error=False,
            fill_value=(scoreFrequency[-1],scoreFrequency[0])
        )
        return farInterpolation
        
    elif inverse==True:
        
        farInterpolation=interp1d(
            scoreFrequency,
            scoreR,
            bounds_error=False,
            fill_value=(scoreR[-1],scoreR[0])
            )
        return farInterpolation
    


def far(far_interp, input , inverse=False):
    
    """Uses the interpolation function provided
    to provide the FAR of the input score provided (inverse=False)
    or the score corresponding to the input FAR provided
    (inverse=True). 
    
    Parameters
    ----------
    
    far_interp: str (path)
        The interpolation function to use
        
    input: float (score or FAR)
        The score value to evaluate on the interpolation
        function (inverse=False) which returns a FAR value,
        or the FAR value to evaluate on the interpolation
        function (inverse=True) which returns a score value.
    
    inverse: bool
        If false it will give FAR for a given score. If
        true it will give score for a given FAR.

    Returns
    -------

    event FAR or score: float
        The FAR coresponding value of <input> using the 
        interpolation. Or the score value of <input>.
    """
    
    if isinstance(far_interp,str):
        with open(far_interp,'rb') as obj:
            far_interp = pickle.load(obj)
    
    return float(far_interp(input))




def find_default_segments(config, inclusion_flags=[] 
                                , exclusion_flags=[]):

    if os.path.exists(config["path"]+"/segments.txt"):
        return config
    
    detectors = config['detectors']
    start = config['segment_list'][0]
    end = config['segment_list'][1]

    if isinstance(start,str):
        start = to_gps(start)
    if isinstance(end,str):
        end = to_gps(end)

    run_dict = dict(o1 = Segment(1126051217,1137254417),
                    o2 = Segment(1164556817,1187733618),
                    o3a = Segment(1238166018, 1253977218),
                    o3b = Segment(1256655618, 1269363618))

    frame_dict = dict(o1 = {'H': 'H1_HOFT_C02'
                        ,'L': 'L1_HOFT_C02'
                        ,'V': 'V1Online'},
                o2 = {'H': 'H1_HOFT_C02'
                        ,'L': 'L1_HOFT_C02'
                        ,'V': 'V1Online'},
                        
                o3a = {'H': 'H1_HOFT_C01'
                        ,'L': 'L1_HOFT_C01'
                        ,'V': 'V1Online'},
                o3b = {'H': 'H1_HOFT_C01'
                        ,'L': 'L1_HOFT_C01'
                        ,'V': 'V1Online'})


    channel_dict = dict(o1 = {'H': 'H1:DCS-CALIB_STRAIN_C02'
                        ,'L': 'L1:DCS-CALIB_STRAIN_C02'
                        ,'V': 'V1:Hrec_hoft_16384Hz'},
                o2 = {'H': 'H1:DCS-CALIB_STRAIN_C02'
                        ,'L': 'L1:DCS-CALIB_STRAIN_C02'
                        ,'V': 'V1:Hrec_hoft_16384Hz'},                  
                o3a = {'H': 'H1:DCS-CALIB_STRAIN_C01'
                        ,'L': 'L1:DCS-CALIB_STRAIN_C01'
                        ,'V': 'V1:Hrec_hoft_16384Hz'},
                o3b = {'H': 'H1:DCS-CALIB_STRAIN_C01'
                        ,'L': 'L1:DCS-CALIB_STRAIN_C01'
                        ,'V': 'V1:Hrec_hoft_16384Hz'})

    detector_active_flag = {'H1': 'H1:DMT-ANALYSIS_READY:1'
                        ,'L1': 'L1:DMT-ANALYSIS_READY:1'
                        ,'V1': 'V1:ITF_SCIENCE:1'}

    selected_run = None
    for run in run_dict.keys():
        if (start in run_dict[run]) and (end in run_dict[run]):
            selected_run = run
            break
    if selected_run is None:
        raise ValueError("start and end date do not belong in the same or any observing run\n", from_gps(start), from_gps(end))
        

    detector_segments = []

    for det in detectors:
        individual_detector_segment = query_segments(detector_active_flag[det+'1'], start, end)['active']
        for flag in inclusion_flags:
            try: 
                print("Flag(+)  ", flag[det+"1"])
                individual_detector_segment = individual_detector_segment & query_segments(flag[det+'1'], start, end)['active']
            except KeyError:
                print("Flag ", flag[det+"1"], " was not found, continuing to the next.")
            except:
                raise

        for flag in exclusion_flags:
            try:
                print("Flag(-)  ", flag[det+"1"])
                individual_detector_segment = individual_detector_segment & ~query_segments(flag[det+'1'], start, end)['active']
            except KeyError:
                print("Flag ", flag[det+"1"], " was not found, continuing to the next.")
            except:
                raise
        print(det,individual_detector_segment)
        detector_segments.append(individual_detector_segment)

    coincident_segments = detector_segments[0]
    for segment in detector_segments[1:]:
        coincident_segments = coincident_segments & segment

    config['frames_directory']= frame_dict[selected_run]
    config['channels'] = channel_dict[selected_run]
    config['segment_list'] = coincident_segments

    segmentlist = list([seg[0],seg[1]] for seg in coincident_segments)
    np.savetxt('test_write_segments.txt', segmentlist, delimiter=',')

    return config

def calculateRequiredGPSTime(config, gps_index, initial_gps_time):
    
    """Injests command line arguments dictionary and outputs runtime config
        dictionary. Includes error checking.
       
       Parameters
       ----------
           
       config: dict
           Dictionary containing program runtime variables
           
       gps_index: int
           How many gps times have been searched by this script alone.
           
       initial_gps_time: int
           First gps time searched by set of scripts.
    
       Returns
       -------
    
       gps_time: int 
           GPS time to search during this iteration.
           
       gps_index: int
           How many gps times have been searched by this script alone.
    """
    
    # Unpack variables for readability:
    num_scripts = config["num_scripts"]
    script_index = config["script_index"]
    gps_reset_time = config["gps_reset_time"]
    required_buffer = config["required_buffer"]
    
    #Find gps time for script
    gps_time = initial_gps_time + num_scripts*gps_index + script_index
    
    # If gps_time falls to far behind current time, reset gps time by  
    # making the index go appropriatly forward.
    if (gpstime.gps_time_now() - gps_time) > gps_reset_time:            
        gps_index += int(gpstime.gps_time_now()-gps_time)//num_scripts  
        gps_time = initial_gps_time + num_scripts*gps_index + script_index
        print("RESETING GPS TIME INDEX")
    else:
        # Iterate gps index
        gps_index += 1

    return gps_time, gps_index

def aquireData(config, gps_time):
    
    """Aquires required data at inputted gps time.
       
       Parameters
       ----------
           
       config: dict
           Dictionary containing program runtime variables
           
       gps_time: int
           GPS time in which to search for data

       Returns
       -------
    
       buffers: list 
           List containing data streams from required detectors at requested time
    """
    
    buffers = []
    for detector, detector_initial in enumerate(config["detectors"]):

        #Combine path to frame file with prefix variable for readability:
        prefix = config['frames_directory'][detector_initial] + detector_initial+"-"+detector_initial+"1_"+config['prefix']

        #Generate names of fram files to be read:
        frames = [f"{prefix}{gps_time + i}-1.gwf" for i in range(config["required_buffer"] + 1)]

        #Search for frame files, return None if not found
        strain = readFrameFile(
            frames, 
            config["channels"][detector_initial],
            wait = config["wait"],
            timeout = int((config["num_scripts"]*1.5)/config["wait"]) # Using up to 1.5 times the time available in one loop of time. 
        )

        if strain != None:
            #Resample all strain data:
            strain = strain.resample(config["fs"]).value[int(config["fs"]*0.5):-int(config["fs"]*0.5)]
        else:
            #If no frame file is found return None
            return None

        #Raise error if erroneoud data detected
        zeros=len(np.where(strain==0.0)[0]) # weidly it returns array in a tuple
        if zeros>=0.10*len(strain):
            print(f"Error! Data in detector ",detector," has many zeros : {str(zeros/len(strain))}")
            return None
        else:
            buffers.append(strain.tolist()) # Why do we convert this to a list?
            
    return buffers


def runTimeFrequencyParameterEstimation(thepod: DataPod, 
                                        td_pe_model: Model,
                                        fd_pe_model: Model,
                                        mly_output: dict) -> dict:
    
    """Peforms time domain parameter estimation on inputted datapod.
       
       Parameters
       ----------
       
       thepod: datapod
           Data pod on which to perform time-
           and frequency-domain parameter estimation
       
       td_pe_model: tf_model
           Model with which to perform time-domain parameter estimation
       
       fd_pe_model: 
	   Model with which to perform frequency-domain parameter estimation 
       
       mly_output: dictionary
           Dictionary containing mly output values.

       Returns
       -------
    
       mly_output: dictionary
           Dictionary containing mly output values.
    """
    
    analysis_strain = thepod.strain
    analysis_strain = analysis_strain.reshape(1, 1024, 3)
    
    td_predictions = td_pe_model.predict(analysis_strain)
    mly_output["SNR"] = (thepod.snr[-1])
    mly_output["central_time"] = mly_output['gpstime']+(td_predictions[0][0]).item()
    mly_output["duration"] = (td_predictions[0][1]).item()
    
    fd_predictions = fd_pe_model.predict(analysis_strain)
    mly_output["central_freq"] = (fd_predictions[0][0]).item()
    mly_output["bandwidth"] = (fd_predictions[0][1]).item()

    return mly_output

   
def podToFileSystem(pod, masterDirectory):
    
    """This function takes a dataPod and splits it into seperate ones
    depending on the detectors included. It saves individual DataPods
    into a temporary file until the manager merges all the pods into a
    DataSet.
    
    Parameters
    ----------
        
    pod : mly.datatools.DataPod
        The DataPod object to be included in the fileSystem
    
    masterDirectory: str (path)
        A path to a valid file system directory. A valid file system
        directory needs to have subfolders with the initials of all
        detectors used and a 'temp' file that also includes subfolders
        with initials of all detectors.
    
    Note
    ----
    
    We don't use checking functions to save time in low latency searces.
    """
    
    detectors = pod.detectors
    for det in detectors:
        _gps = pod.gps[pod.detectors.index(det)]
        _pod = DataPod(pod.strain[pod.detectors.index(det)]
                       ,detectors = [det]
                       ,fs = pod.fs
                       ,gps = [_gps])
        
        _pod.save(masterDirectory+'temp/'+det+'/'+str(_gps)+'_1')
    

def helloworld():
    print("helloworld")