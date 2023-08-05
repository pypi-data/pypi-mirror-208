#!/usr/bin/env python
import sys
# Sourcing the submodule of mly in a very unpythonic way 
sys.path.append("/".join(sys.argv[0].split("/")[:-1])+"/mly/")


import os
import time ,json, argparse
from pycondor import Job, Dagman
from mly.datatools import DataSet
from mly.validators import Validator
from mly.tools import *
from functools import partial
from typing import Callable
from lal import gpstime
import numpy as np
import pickle
import matplotlib.pyplot as plt
from search_functions import far, stackVirgo

with open('config.json') as json_file:
    config = json.load(json_file)

config = stackVirgo(config)

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


# # # Managing arguments
# 
# List of arguments to pass:
arguments = ['mode','injectionPath','injectionSNR','injectionHRSS']

#Construct argument parser:
parser = argparse.ArgumentParser()

parser.add_argument('--mode')
parser.add_argument('--injectionPath')
parser.add_argument('--injectionSNR' , default = None)
parser.add_argument('--injectionHRSS', default = None)

# Pass arguments
args = parser.parse_args()

# Store arguments in dictionary:
kwdict = {}
for argument in arguments:
    kwdict[argument] = getattr(args, argument)


def moving_average(x, w):
    ma=[]
    for i in range(len(x)):
        if i<int(w/2)+1:
            ma.append(np.mean(x[:i+1]))
        elif i>=len(x)-(w/2+1):
            ma.append(np.mean(x[i:]))
        else:
            ma.append(np.mean(x[i-int(w/2):i+int(w/2)]))

    return np.array(ma)


def main():
    
    mode = kwdict['mode']
    
    if mode=='test':

        size = int(float(config["eff_config"]["testSize"]))
        injection_path = kwdict['injectionPath']
        noiseSource = config["bufferDirectory"]+"/BUFFER_SET.pkl"
        injectionSNR = kwdict["injectionSNR"]
        injectionHRSS = kwdict["injectionHRSS"]
        
        efficiencyDirectory = config["efficiencies"]+"/"
        print("INJSNR",injectionSNR, type(injectionSNR))
        print("INJHRSS",injectionHRSS, type(injectionHRSS))
        if injectionSNR != None:

            injectionSNR = np.array(list(float(_) for _ in injectionSNR.split(',')))
            injectionSNR = np.arange(injectionSNR[0], injectionSNR[1], injectionSNR[2]).tolist()

        if injectionHRSS != None:
            injectionHRSS = np.array(list(float(_) for _ in injectionHRSS.split(',')))
            injectionHRSS = np.arange(injectionHRSS[0], injectionHRSS[1], injectionHRSS[2]).tolist()


        print("INJSNR",injectionSNR)
        print("INJHRSS",injectionHRSS)
        noiseSource = DataSet.load(noiseSource)
        gps_time_start = int(noiseSource[0].gps[0])
        gps_time_end = int(noiseSource[-1].gps[0])

        models = [[config['model1_path'],config['model2_path']]
                  ,[["strain"], ["strain", "correlation"]]]

        # print(models)
        # print(injectionSNR)
        # print(injectionHRSS)
        print('injection_path: ',injection_path)
        t0=time.time()
        print("savefile",efficiencyDirectory+f"_{injection_path.split('/')[-1]}_{gps_time_start}-{gps_time_end}")

        if 'V' not in config['detectors']:
            efficiencies = Validator.accuracy(models=models, 
                                        duration=1, 
                                        size=size,
                                        fs=1024,
                                        detectors=config['detectors'], 
                                        labels={"type": "signal"},
                                        backgroundType="real",
                                        injectionFolder=injection_path,
                                        injectionSNR = injectionSNR,
                                        noiseSourceFile = noiseSource,
                                        windowSize = 16, 
                                        plugins=["correlation_30"], 
                                        mapping=2 * [{"noise":[ 1, 0], "signal":[0, 1]}],
                                        name=f"{injection_path.split('/')[-1]}_{gps_time_start}-{gps_time_end}",
                                        savePath = efficiencyDirectory,
                                        injectionHRSS = injectionHRSS, #list(np.arange(0, 100) * 1e-23)
                                        stackDetectorDict = config['stackDetectorDict']
            )   


        else:
            efficiencies = Validator.accuracy(models=models, 
                                duration=1, 
                                size=size,
                                fs=1024,
                                detectors=config['detectors'], 
                                labels={"type": "signal"},
                                backgroundType="real",
                                injectionFolder=injection_path,
                                injectionSNR = injectionSNR,
                                noiseSourceFile = noiseSource,
                                windowSize = 16, 
                                plugins=["correlation_30"], 
                                mapping=2 * [{"noise":[ 1, 0], "signal":[0, 1]}],
                                name=f"{injection_path.split('/')[-1]}_{gps_time_start}-{gps_time_end}",
                                savePath = efficiencyDirectory,
                                injectionHRSS = injectionHRSS
                                )#list(np.arange(0, 100) * 1e-23))]]

        print(time.time()-t0)
        #return efficiencies
    
    elif mode=='plot':
        
        farfile_inverse_interpolation = config["farfile"]+"/FARfile_interpolation_inverse.pkl"
        efficiencyDirectory = config["efficiencies"]+"/"

        thresholds = {#'10year': far(farfile_inverse_interpolation, 1/(10*365*24*3600) , inverse = True)
                      '1year': far(farfile_inverse_interpolation, 1/(365*24*3600) , inverse = True)
                      ,'1month': far(farfile_inverse_interpolation, 1/(365*24*3600/12) , inverse = True)
                      ,'2hours': far(farfile_inverse_interpolation, 1/(2*3600) , inverse = True)

                     }

        print(thresholds)
        
        tkeys=list(thresholds.keys())    
        
        tests= dirlist(efficiencyDirectory)

        tests.remove('condor')
        tests.remove('history')
        
        timeInterval = tests[0].split("_")[-1][:-4]
        
        colours=['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']

        fig,ax=plt.subplots(2,3,figsize=(15,10))

        ACC50={}

        for t in range(len(tkeys)):
            ACC50[tkeys[t]]={}

            for l in range(len(tests)):
                label = tests[l].split('_')[0]

                with open(efficiencyDirectory+tests[l],'rb') as handle: data= pickle.load(handle)

                acc=[]
                
                if 'hrss' in data.keys():
                    looper = data['hrss']
                    xlabel = 'hrss'
                    
                    for hrss in range(len(looper)):
                        count=0
                        for sc in np.array(data['scores1'][hrss])*np.array(data['scores2'][hrss]):
                            if sc>=thresholds[tkeys[t]]: count+=1
                        acc.append(100*count/len(np.array(data['scores1'][hrss])*np.array(data['scores2'][hrss])))
                    
                    #ax[0,t].plot(looper,moving_average(acc,10),label=label,color=colours[l])
                    ax[0,t].plot(looper,acc,label=label,color=colours[l])

                    mvave=moving_average(acc,10)
                    for snr in range(1,len(looper)):

                        if mvave[snr]>50 and mvave[hrss-1]<=50:
                            ACC50[tkeys[t]][label]=looper[snr]

                    ax[0,t].set_title('Efficiency of FAR '+tkeys[t])
                    ax[0,t].set_xlabel(xlabel)
                    ax[0,t].set_ylim(0,100)
                    ax[0,t].grid(True,which='both')

                elif 'snrs' in data.keys():
                    looper = data['snrs']
                    xlabel = 'SNR'
                    
                    
                    for snr in range(len(looper)):
                        count=0
                        for sc in np.array(data['scores1'][snr])*np.array(data['scores2'][snr]):
                            if sc>=thresholds[tkeys[t]]: count+=1
                        acc.append(100*count/len(np.array(data['scores1'][snr])*np.array(data['scores2'][snr])))
                        
                    #ax[1,t].plot(looper,moving_average(acc,10),label=label,color=colours[l])
                    ax[1,t].plot(looper,acc,label=label,color=colours[l])

                    mvave=moving_average(acc,10)
                    for snr in range(1,len(looper)):

                        if mvave[snr]>50 and mvave[snr-1]<=50:
                            ACC50[tkeys[t]][label]=looper[snr]

                    ax[1,t].set_xlabel(xlabel)
                    ax[1,t].set_ylim(0,100)
                    ax[1,t].grid(True,which='both')

                
        ax[0,0].set_ylabel("% of signals detected")
        ax[1,0].set_ylabel("% of signals detected")

        ax[0,2].legend()
        ax[1,2].legend()

        fig.savefig('./Efficiencies.png')

        for test in tests:

            os.system('mv '+ efficiencyDirectory + test 
                      +' '+ efficiencyDirectory + 'history/'+ test)

            os.system('cp ./Efficiencies.png '
                      +efficiencyDirectory+'history/Efficiencies_'
                    +timeInterval+'.png')

            
    elif mode=='condor':
        

        accounting_group_user=config['accounting_group_user']
        accounting_group=config['accounting_group']

        injSourceDir = config["eff_config"]["injectionDirectoryPath"]
        
        efficiencyDirectory = config["efficiencies"]+"/"

        error = efficiencyDirectory+'condor/error'
        output = efficiencyDirectory+'condor/output'
        log = efficiencyDirectory+'condor/log'
        submit = efficiencyDirectory+'condor/submit'

        dagman = Dagman(name='efficiencyTestDagman',submit=submit)


        injection_paths_HRSS =  config["eff_config"]["injectionsWithHRSS"]
        
        injection_paths_SNR = config["eff_config"]["injectionsWithSNR"]

        os.system('chmod 777 '+config["mlyPipelineSource"]+'/make_eff_estimation.py')
        
        job_list=[]

        for injection_path in injection_paths_HRSS:
            print(injSourceDir+injection_path)

            jobname = injection_path.split('/')[-1]
            print(injSourceDir+injection_path)
            thearguments = ("--mode=test" 
                             +" --injectionPath="+injSourceDir+injection_path
                             +" --injectionHRSS="+config['eff_config']['injectionHRSS'])



            job = Job(name = jobname
                       ,executable = config["mlyPipelineSource"]+"/make_eff_estimation.py"
                       ,arguments = thearguments
                       ,submit=submit
                       ,error=error
                       ,output=output
                       ,log=log
                       ,getenv=True
                       ,dag=dagman
                       ,extra_lines=["accounting_group_user="+accounting_group_user
                                    ,"accounting_group="+accounting_group
                                    ,"request_disk            = 64M"])

            job_list.append(job)
            
            
            
            
            
        for injection_path in injection_paths_SNR:

            jobname = injection_path.split('/')[-1]
            print(injSourceDir+injection_path)
            thearguments = ( "--mode=test"
                             +" --injectionPath="+injSourceDir+injection_path
                             +" --injectionSNR="+config['eff_config']['injectionSNR'])





            job = Job(name = jobname
                       ,executable = config["mlyPipelineSource"]+"/make_eff_estimation.py"
                       ,arguments = thearguments
                       ,submit=submit
                       ,error=error
                       ,output=output
                       ,log=log
                       ,getenv=True
                       ,dag=dagman
                       ,extra_lines=["accounting_group_user="+accounting_group_user
                                    ,"accounting_group="+accounting_group
                                    ,"request_disk            = 64M"])

            job_list.append(job)


        plot_job = Job(name = 'plotJob'
                   ,executable = config["mlyPipelineSource"]+"/make_eff_estimation.py"
                   ,arguments = ("--mode=plot")
                   ,submit=submit
                   ,error=error
                   ,output=output
                   ,log=log
                   ,getenv=True
                   ,dag=dagman
                   ,extra_lines=["accounting_group_user="+accounting_group_user
                                ,"accounting_group="+accounting_group
                                ,"request_disk            = 64M"])

        plot_job.add_parents(job_list)


        dagman.build_submit()

if __name__ == "__main__":
    main()
