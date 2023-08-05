import json
import pickle
import argparse
import sys ,time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lal import gpstime
from gwpy.time import from_gps, to_gps
import os
import logging

# Sourcing the submodule of mly in a very unpythonic way 
sys.path.append("/".join(sys.argv[0].split("/")[:-1])+"/mly/")



from mly.tools import dirlist
from mly.datatools import *
from search_functions import *

# # # Initialising logging

# create logger
logger = logging.getLogger("logger_for_manager")
logger.setLevel(logging.INFO)



# create console handler and set level to debug
ch = logging.handlers.TimedRotatingFileHandler('log/manager.log', when='M',interval=1, backupCount=1,)
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)




# # # Managing arguments
# 
# List of arguments to pass:
arguments = [

    "restriction",
    "timeUnit"
]

#Construct argument parser:
parser = argparse.ArgumentParser()

parser.add_argument('--restriction')
parser.add_argument('--timeUnit')

 
# Pass arguments
args = parser.parse_args()

# Store arguments in dictionary:
kwdict = {}
for argument in arguments:
    kwdict[argument] = getattr(args, argument)

    
with open('config.json') as json_file:
    config = json.load(json_file)
    
config={ **kwdict , **config}
    
# # # Argument checks

config = checkOutputDirectoryArguments(config)

# The size in which we group the outputs
if config['maxDataFrameSize']==None: 
    config['maxDataFrameSize']=3600

maxDataFrameSize = int(config['maxDataFrameSize'])

if config['restriction']==None: 
    config['restriction']=0.0
restriction=float(config['restriction'])
    
# This is the time scale to use for the plots
timeUnitDict={1:'s', 60:'m', 3600:'h', 24*3600:'days',30*24*3600:'months', 365*24*3600:'years'}

if config['timeUnit']==None: 
    config['timeUnit']=3600
else:
    config['timeUnit']=int(config['timeUnit'])
    

sys.stdout.flush()

while (1):
    
    loopT0=time.time()
    
    output_directory = config['output_directory']
    
    frameSizeCheck=0
    fileList = dirlist(output_directory)
    dFramesList  = []
    jsonList = []
    # Listing the files in the directory
    # Separating the json from pkl
    for file in fileList:

        if ".json" in file:
            jsonList.append(file)
        elif ".pkl" in file:
            dFramesList.append(file)

    # if there are no new outputs we skip that step
    if len(jsonList)!=0: 

        # We expect that every time the manager runs, there is a tempFrame
        # file that might have events but it is not of the size we group
        # them (maxDataFrameSize). 
        try:

            with open(output_directory+'tempFrame.pkl','rb') as obj:
                tempFrame = pickle.load(obj)
        # The first time manager is running this file is created instead.
        except Exception as e:
            tempFrame = pd.DataFrame(columns = ['gpstime','far','ifos'
                                                ,'coincidence','coherency'
                                                ,'combined','trigger'])
            logger.info(f"Creating tempfile for the first time.")

        # The size of the frame
        initialTempFrameSize=len(tempFrame)

        # A check value to make sure we add all the json files.
        frameSizeCheck = len(jsonList) + initialTempFrameSize
        print("firstcheck",frameSizeCheck, len(tempFrame))

        # Adding all the events in json format to the tempFrame
        for file in jsonList:
            try:
                with open(output_directory+file,"r") as jf:
                    p=json.load(jf)
                    jf.close()
            except Exception as e:
                logger.warning(f"Exception in loading json file {file}, {e}")
                continue



        # Reformating the score parameters to the desired format.
            for k in list(p['scores'].keys()):
                p[k]=p['scores'][k]
            # Making a list of ifos to avoid line breaking into two
            p['ifos'] = [p['ifos']]

            if file[0]=='N':
                p['trigger']=False
            elif file[0]=='T':
                p['trigger']=True
            else:
                p['trigger']=False


            del(p['scores'])  
            print('jsontopd',pd.DataFrame.from_dict(p))
            tempFrame=pd.concat([tempFrame, pd.DataFrame.from_dict(p)]
                                ,ignore_index=True)

        # Reseting index and sorting by GPS time
        tempFrame=tempFrame.sort_values(by="gpstime").reset_index(drop=True)
        # Rearanging the columns
        tempFrame = tempFrame[['gpstime','far','ifos','coincidence','coherency'
                            ,'combined','trigger']]
        print(tempFrame.head(4))
        # Chopping the tempFrame to chuncs of maxDataFrameSize outputs
        # IMPORTANT: We don't separate them by hour, we just collect 
        # maxDataFrameSize of them together
        while len(tempFrame) > maxDataFrameSize:

            print("secondcheck",frameSizeCheck, len(tempFrame))

            # Creating a newframe to include the maxDataFrameSize instances
            newFrame=tempFrame[:maxDataFrameSize]
            with open(output_directory+str(newFrame['gpstime'][0])+"-"
                    +str(newFrame['gpstime'][maxDataFrameSize-1])
                    +"_"+str(maxDataFrameSize)+'.pkl', 'wb') as output:
                pickle.dump(newFrame, output, 4)

            logger.info("Saving group of outputs: ", output_directory+str(newFrame['gpstime'][0])+"-"
                +str(newFrame['gpstime'][maxDataFrameSize-1])
                +"-"+str(maxDataFrameSize)+'.pkl')

            # Removing the newframe from tempFrame
            tempFrame=tempFrame[maxDataFrameSize:].reset_index(drop=True)

            frameSizeCheck-=maxDataFrameSize

        # What is left in tempFrame, overights the tempFrame.pkl
        with open(output_directory+'tempFrame.pkl', 'wb') as output:
            pickle.dump(tempFrame, output, 4)
            logger.info(f"Saving the incomplete group of outputs: {output_directory}tempFrame.pkl")

        
        # We remove all json files already included in a dataFrame
        for file in jsonList:
            os.system("rm "+output_directory+file )


        # # Plotting all available events in a zero-lagged score rate
        # # (Might remove in the future, used to see consistency)
        # testNumber=0
        # dFramesList  = []
        # scores=[]
        # # Listing the files in the directory
        # # Separating the json from pkl
        # fileList = dirlist(output_directory)
        # for file in fileList:
        #     if ".pkl" in file : dFramesList.append(file)

        # for file in dFramesList:

        #     with open(output_directory+file,'rb') as obj:
        #         frame_ = pickle.load(obj)

        #     testNumber+=len(frame_)

        #     scores+=list(frame_[frame_['combined']>=restriction]['combined'])


        # s=np.sort(scores)[::-1]


        # fig,ax1=plt.subplots(figsize=(6,6))

        # ax1.loglog(s,np.arange(len(s))+1,label='O3a '+config['detectors']+' backround')
        # ax1.set_title(config['detectors']+"-FAR up to : "+str(from_gps(gpstime.gps_time_now()))+", total time: "+"{:.2f}".format(testNumber/config['timeUnit'])+timeUnitDict[config['timeUnit']])


        # #ax1.set_yticks(np.array([1e0,1e1,119,1e3,1e4,1e5,1e6]))
        # #ax1.set_yticklabels(np.array(['10 years','1 year','1 month','3.6 days','8.64 hours', '51.84 min' ,'5.18 min']))

        # ax1.set_ylim(1,)
        # if restriction>0: ax1.set_xlim(restriction,1)
        # ax1.set_xlabel("Scores")
        # ax1.set_ylabel("FAR")
        # plt.savefig('./'+config['detectors']+"_far.png")
        # plt.close('all')

        
    
    # # # FileSystem for FAR management
    #
    # Listing all files saved in the temp file (files to be managed)
    detectors= list( det for det in config['detectors'])
    
    t0=time.time()

    numberOfFiles={}
    fileNumbers={}
    dataSetDict={}
    
    # For each detector we count how many files have been saved in all
    # detectors and we sort them.
    for det in detectors:
        numberOfFiles[det] = len(dirlist(config['masterDirectory']+'/temp/'+det))
        fileNumbers[det] = sorted(list(file.split('_')[0] for file in dirlist(
            config['masterDirectory']+'/temp/'+det)))
        dataSetDict[det] = []

    # If there are no files we skip this step
    if len(fileNumbers[detectors[0]])==0:
        logger.info(f"Empty temp directory")
        #time.sleep(60)
          
    # If the files included in temp are less than maxDataFrameSize, we skip
    # this step.
    elif (int(float(fileNumbers[detectors[0]][-1]))
         -int(float(fileNumbers[detectors[0]][0]))) < maxDataFrameSize:
        logger.info(f"Not enough data \
                    {maxDataFrameSize - (int(float(fileNumbers[detectors[0]][-1])) -  int(float(fileNumbers[detectors[0]][0])))}\
                     to run the FAR test yet")
        
    # If the files included in temp are enough we group them
    elif (int(float(fileNumbers[detectors[0]][-1]))
          -int(float(fileNumbers[detectors[0]][0]))) >= maxDataFrameSize:
        
        c=0
        
        # We keep track of the files used to delete them later
        filesToDelete=[]
        
        # Checking that all detectors have the same number of files
        logger.debug(f"Number of files for each detector: {list(len(fileNumbers[det]) for det in detectors)}")
        
        lastFileNumber=None
        # print("group size check: ",len(fileNumbers[detectors[0]][:int(maxDataFrameSize)]))
        
        for filenumber in fileNumbers[detectors[0]][:int(maxDataFrameSize)]:

            # For each file we in first detector we check that it exists in the
            # other detectors too. 
            if all( list( os.path.isfile(config['masterDirectory']
                                         +'/temp/'+det+'/'+fileNumbers[detectors[0]][c]
                                         +'_1.pkl') for det in detectors)):
                
                for det in detectors:
                    dataSetDict[det].append(
                        DataPod.load(config['masterDirectory']
                                     +'/temp/'+det+'/'+str(filenumber)+'_1.pkl'))
                    
                lastFileNumber=int(float(filenumber))
                filesToDelete.append(str(filenumber)+'_1.pkl')
                
                
            
            # Othewise we delete it and it can't be used
            else:
                filesToDelete.append(str(filenumber)+'_1.pkl')
            
            c+=1

        # We use those two for name creation
        first = str(int(float(fileNumbers[detectors[0]][0])))
        last = str(lastFileNumber)
        # print('first,last: ',first,last)
        
        # Saving the instances in dataSets
        for det in detectors:
            _set = DataSet(dataSetDict[det])
            name = first+'-'+last+'_'+str(len(_set))
            _set.save(config['masterDirectory']+'/' + det + '/' + name)

            # # Deleting files that already passed.
            for file in filesToDelete:
                try:
                    os.system("rm "+config['masterDirectory']+'/temp/'+det+'/'+file)
                except Exception as e:
                    pass

    
    # # # Efficiency test buffer management
    #
    
    if os.path.isdir(config['efficiencies']):
        
        # How many inferences to wait to run the test, roughly how often in seconds

        efficiencyTestBuffer = config["eff_config"]["howOften"]

        # We load all the buffer pods that live in temp
        buffer_set = []
        pod_list = sorted(dirlist(config['bufferDirectory']+"/temp"))
        
        num_pods = len(pod_list)
        
        # If number of the buffer pods are more than maxDataFrameSize, we 
        # putting them in a dataSet to be used.
        logger.info(f"Buffer size accumulated: {num_pods}/{efficiencyTestBuffer} .Start efficiency test: {num_pods >= efficiencyTestBuffer}")
        # I there are enough buffer pods we can save them to be used in an efficiency test.
        if num_pods >= efficiencyTestBuffer:
            
            for each_pod in pod_list[:efficiencyTestBuffer]:
                pod = DataPod.load(config['bufferDirectory']+"/temp/"+each_pod) 
                buffer_set.append(pod)

            buffer_dataset = DataSet(buffer_set)
            buffer_dataset.save(config['bufferDirectory']+"/BUFFER_SET")

            logger.info(f"Saving {config['bufferDirectory']}/BUFFER_SET")
            # Removing all the ones we used after we made sure the set is saved.   
            for each_pod in pod_list[:efficiencyTestBuffer]:

                os.system("rm "+config['bufferDirectory']+"/temp/"+each_pod)
                
            # Running the efficiencies script only if the previous has finished.
            if len(dirlist(config['efficiencies'])) <= 2:
                os.system("nohup python "+config["mlyPipelineSource"]+"/make_eff_estimation.py --mode condor > efficiencyTest.out &")
                logger.info(f"Efficiency test initiated")


    
    # # # FAR test management 
    #

    # The list of all temporary inference files
    if os.path.isdir(config['falseAlarmRates']):
        
        inference_temp_files = dirlist(config['falseAlarmRates'])

        for directory in ['hourly', 'condor', 'FARfile','temp']:
            if directory in inference_temp_files: inference_temp_files.remove(directory)


        # The list of all the files in hourly (grouped by hour/DAG of generation)
        hourly_files = dirlist(config['falseAlarmRates']+"/hourly")

        # The list of all condor dagman directories
        condor_files =  dirlist(config['falseAlarmRates']+"/condor")

        # The group names (start-end gps) in inference_temp_files
        inference_temp_files_groups = list(file.split("_")[0] for file in inference_temp_files)
        inference_temp_files_groups = list(dict.fromkeys(inference_temp_files_groups))

        # The group names inside hourly
        hourly_files_groups = list(file.split("_")[0] for file in hourly_files)

        # The group names of condor directories
        condor_groups= list(file.split("_")[0] for file in condor_files)

        logger.debug(f"HOURLY GROUPS: {len(hourly_files_groups)}")
        logger.debug(f"TEMP GROUPS: {len(inference_temp_files_groups)}")

        # First we will go through the files that already have a group inside hourly
        # We will add them in their corresponding hourly group file and remove them 
        # from inference_temp_files

        for hgroup, hfile_name in zip(hourly_files_groups, hourly_files):

            if hgroup in inference_temp_files_groups:

                with open(config['falseAlarmRates']+"/hourly/"+hfile_name,'rb') as obj:
                    hfile = pickle.load(obj)
                
                hfile_size = int(hfile_name.split("_")[-1][:-4])

                to_remove_from_inference_temp_files = []

                for file_name in inference_temp_files:
                    
                    if hgroup in file_name:

                        with open(config['falseAlarmRates']+"/"+file_name,'rb') as obj:
                            file = pickle.load(obj)

                        file = file[file['score'] >= restriction]

                        hfile = pd.concat([hfile, file], ignore_index=True)
                        
                        # Adding the size of the file to the hourly file
                        hfile_size += int(file_name.split("_")[-1][:-4])

                        #TEMPORARY
                        os.system("rm "+config['falseAlarmRates']+"/"+file_name)
                        to_remove_from_inference_temp_files.append(file_name)

                new_hfile_name = "_".join(hfile_name.split("_")[:-1])+"_"+str(hfile_size)
                with open(config['falseAlarmRates']+"/hourly/"+new_hfile_name+'.pkl', 'wb') as output:
                    pickle.dump(hfile, output, 4)

                os.system("rm "+config['falseAlarmRates']+"/hourly/"+hfile_name)

                for file_name in to_remove_from_inference_temp_files:
                    inference_temp_files.remove(file_name)

        # Now we can create new hourly files for the new groups that appeared
        # First we reset the inference_temp_files. There will be no already existing froup
        # for those files

        # Reseting temp_file_groups 
        inference_temp_files_groups = list(file.split("_")[0] for file in inference_temp_files)
        inference_temp_files_groups = list(dict.fromkeys(inference_temp_files_groups))

        # A check to make sure all files left do not belong in an existing group.
        check = all( [ all([hgroup not in file for file in inference_temp_files]) for hgroup in hourly_files_groups] )
        logger.debug(f"All groups left are new: {check}")


        for tgroup in inference_temp_files_groups:

            to_remove_from_inference_temp_files = []

            for file_name in inference_temp_files:

                if tgroup in file_name:

                    if len(to_remove_from_inference_temp_files)==0:

                        with open(config['falseAlarmRates']+"/"+file_name,'rb') as obj:
                            new_hfile = pickle.load(obj)

                        new_hfile_size = int(file_name.split("_")[-1][:-4])

                        to_remove_from_inference_temp_files.append(file_name)
                    
                    else:

                        with open(config['falseAlarmRates']+"/"+file_name,'rb') as obj:
                            file = pickle.load(obj)

                        new_hfile = pd.concat([new_hfile, file], ignore_index=True)

                        new_hfile_size += int(file_name.split("_")[-1][:-4])

                        to_remove_from_inference_temp_files.append(file_name)

            new_hfile_name = tgroup+"_"+str(new_hfile_size)
            with open(config['falseAlarmRates']+"/hourly/"+new_hfile_name+'.pkl', 'wb') as output:
                pickle.dump(new_hfile, output, 4)

            logger.info(f"Informing / Saving FAR file : {config['falseAlarmRates']}/hourly/{new_hfile_name}.pkl")

            for file_name in to_remove_from_inference_temp_files:
                inference_temp_files.remove(file_name)

                #TEMPORARY
                os.system("rm "+config['falseAlarmRates']+"/"+file_name)

        logger.debug(f"This should be zero, inference_temp_files: {len(inference_temp_files)}")


        hourly_files = dirlist(config['falseAlarmRates']+"/hourly") 

        for i, hfile_name in enumerate(hourly_files):

            if i==0: 
                with open(config['falseAlarmRates']+"/hourly/"+hfile_name,'rb') as obj:
                    farfile = pickle.load(obj)

                farfile_size = int(hfile_name.split("_")[-1][:-4])
            else:
                
                with open(config['falseAlarmRates']+"/hourly/"+hfile_name,'rb') as obj:
                    farfile_part = pickle.load(obj)

                farfile = pd.concat([farfile, farfile_part], ignore_index=True)

                farfile_size += int(hfile_name.split("_")[-1][:-4])

        # Deleting the old FARfile before creating the new one (they have the size of tests on their name).
        farfile_to_delete = None
        old_far_files = dirlist(config['falseAlarmRates']+"/FARfile")
        for file in old_far_files:
            if 'FARfile_interpolation' not in file:
                farfile_to_delete = file
                logger.info(f"FARfile to be replaced: {farfile_to_delete}")
                break 

        if len(hourly_files)!=0:
            with open(config['falseAlarmRates']+"/FARfile/FARfile_"+str(farfile_size)+".pkl", 'wb') as output:
                pickle.dump(farfile, output, 4)

                logger.info(f"New FARfile saved: {config['falseAlarmRates']}/FARfile/FARfile_{farfile_size}.pkl")

            far_interpolation_output = far_interpolation(farfile, farfile_size, inverse = False)
            far_interpolation_output_inverse = far_interpolation(farfile, farfile_size, inverse = True)

            with open(config['falseAlarmRates']+"/FARfile/FARfile_interpolation.pkl", 'wb') as output:
                pickle.dump( far_interpolation_output , output, 4)
            with open(config['falseAlarmRates']+"/FARfile/FARfile_interpolation_reserve.pkl", 'wb') as output:
                pickle.dump( far_interpolation_output , output, 4)
                
            with open(config['falseAlarmRates']+"/FARfile/FARfile_interpolation_inverse.pkl", 'wb') as output:
                pickle.dump(far_interpolation_output_inverse , output, 4)
            with open(config['falseAlarmRates']+"/FARfile/FARfile_interpolation_inverse_reserve.pkl", 'wb') as output:
                pickle.dump(far_interpolation_output_inverse , output, 4)
            
            logger.info(f"New FARfile interpolations saced")

            if (farfile_to_delete is not None 
                    and farfile_to_delete!="FARfile_"+str(farfile_size)+".pkl"):
                os.system("rm "+config['falseAlarmRates']+"/FARfile/"+farfile_to_delete)
            
        # Overwriting config farfile when enough files
        if len(hourly_files)!=0 and (farfile_size) >= 1*365*24*3600 and (config['path']+"/"+config['falseAlarmRates'] not in config['farfile']):

            with open('config.json') as json_file:
                _config = json.load(json_file)
                _config['farfile'] = config['falseAlarmRates']+"/FARfile"
            with open("config.json", "w") as config_json:
                json.dump(_config, config_json,indent=4)
                config_json.close()

            logger.info(f"FARFILE UPDATED FROM THE TEMPORARY TO THE SEARCH LOCAL!")
            raise SystemError("This is just an interuption to load the new FAR sourse.")
        # # Deleting old condor directories 
        # c = 0
        # for cgroup, cdir in zip(condor_groups, condor_files):
        #     if ((c < len(hourly_files_groups) - config['far_config']['parallelGenerations'])
        #                 and (cgroup in hourly_files_groups)
        #                 and (cgroup not in inference_temp_files_groups)):

        #         os.system("rm -r "+config['falseAlarmRates']+"/condor/"+cdir)
        #     c+=1

    # Timing
    logger.info(f"Manager loop time:{time.time()-loopT0}, waiting 5 minutes ... ")
    sys.stdout.flush()

    time.sleep(5*60)
    
