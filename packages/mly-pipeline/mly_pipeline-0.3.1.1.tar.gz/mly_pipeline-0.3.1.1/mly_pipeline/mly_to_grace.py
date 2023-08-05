#! /usr/bin/env python3
import pickle
import os
import sys
import json
import argparse
import ast
import numpy as np

# Sourcing the submodule of mly in a very unpythonic way 
sys.path.append("/".join(sys.argv[0].split("/")[:-1])+"/mly/")
from mly.datatools import DataPod


from lal import gpstime
from ligo.gracedb.rest import GraceDb

# # # Managing arguments
# 
# List of arguments to pass:
arguments = [
    "trigger_destination",
    "skymap_directory",
    "triggerfile",
    "triggerplot_directory",
    "skymap",
    "config"
]

#Construct argument parser
parser = argparse.ArgumentParser()
[parser.add_argument(f"--{argument}") for argument in arguments]

# Pass arguments
args = parser.parse_args()

# Store arguments in dictionary
kwargs = {}
for argument in arguments:
    kwargs[argument] = getattr(args, argument)

# Config file is inherited by the search script updated

config = ast.literal_eval(kwargs['config'])      
#def main(**kwargs):
    
    
"""This function issues a GraceDB event provided with a json file.

Parameters
----------


trigger_destination: {'test, 'playground', 'dev1', None}
    The GraceDB domain for the triggers to be uploaded. Each option represent
    a corresponding url. If equals to None, it will not issue an GraceDB event.

triggerfile : 'str'
    The path to the json file to use for the event.

"""

# print("Main beggining: ",gpstime.gps_time_now()- float(kwargs['triggerfile'].split('_')[-2]))
# Argument checks

if kwargs['triggerfile']!=None:

    if os.path.isfile(kwargs['triggerfile']):
        triggerfile = kwargs['triggerfile']
    else:
        raise FileNotFoundError(
            kwargs['triggerfile'] +
            " is not a valid file path")
else:
    raise FileNotFoundError("You need to specify the trigger file path.")




# # # Push to GraceDb

# Checking latencies
gpsbefore = gpstime.gps_time_now()

# If the authentication is correct and we can send events, trigger_destination
# can be defined.


if kwargs['trigger_destination'] != 'None':

    url=kwargs['trigger_destination']

    client = GraceDb(service_url=url)

    graceEventOutput = client.createEvent(group="Burst", 
                                           pipeline="MLy",
                                           filename=triggerfile,
                                           search="AllSky")
    
    graceEventDict = graceEventOutput.json()
    
    print(triggerfile+" uploaded to "+url)

# Otherwise for just testing we can create a fake id to use.
else:
    
    graceEventDict = {'graceid':'FAKEID'+str(np.random.randint(999999))}

# Checking latency from the GPS time involved    
print("Latency before opening client: ",gpsbefore- float(kwargs['triggerfile'].split('_')[-2]))


# # # Extra features to be added
#
# To this point an event is created. The following is to be added after the
# event creation in the future. Some arguments are checked here so that 
# they don't contribute to the event latency until their feature is used


# If there is not local copy of mly 
# it is imported by vasileios.skliris 
# IMPORTANT TO CLONE YOUR OWN COPY 



from mly.datatools import DataPod

# Loading the pod that has all the data that produced the trigger
with open(triggerfile[:-4]+'pkl','rb') as obj:
    thepod = pickle.load(obj)

with open(f"{triggerfile[:-5]}_buffer.pkl", 'rb') as obj:
    buffer = pickle.load(obj)
    
if kwargs['skymap']==None:
    kwargs['skymap']=False
if isinstance(kwargs['skymap'],str):
    kwargs['skymap']=bool(kwargs['skymap'])

    
    
# Probably this could go below skymap generation?    
if kwargs['triggerplot_directory'] != 'None':
    
    print('triggerplot_checkpoint')
    # Creating a directory for each event using the graceid from the event creation.
    # Not always works.
    try:
        eventDirectory = graceEventDict['graceid']+'-'+triggerfile.split('_')[-2]+'-'+triggerfile.split('_')[-1].split('.')[0]
    except Exception as e:
        print(e)
        eventDirectory = 'NoGraceID'+'-'+triggerfile.split('_')[-2]+'-'+triggerfile.split('_')[-1].split('.')[0]
    
    # Making an event directory
    os.mkdir(f"{kwargs['triggerplot_directory']}/{eventDirectory}")


    
if kwargs['skymap']:

    from mly.null_energy_map import *
    from ligo.skymap.io import fits

    # Create skymap plugin:
    sky_map_plugin = createSkymapPlugin(
        config["nside"], config["fs"], config["duration"])

    # Generate Skymap
    buffer.addPlugIn(sky_map_plugin)
    
    skymap_path = f"{kwargs['triggerplot_directory']}/{eventDirectory}/T_{triggerfile.split('_')[-2]}_{triggerfile.split('_')[-1][:-5]}_skymap.fits"
    
    skymap_fits = buffer.skymap

    with open(skymap_path, "w") as f:
        fits.write_sky_map(f.name, skymap_fits, nest=False)
    
    # Upload skymap to grace db:
    if kwargs['trigger_destination'] != 'None':

        client.writeLog(graceEventDict['graceid'], 'skymap',  filename=skymap_path, tg_name='sky_loc')

if kwargs['triggerplot_directory'] != 'None':

    import matplotlib.pyplot as plt
    
    gpsstring=triggerfile.split('_')[1]
    detectors=triggerfile.split('_')[-1][-5]
    
    # Creating the strain plot
    thepod.plot(type_="strain")
    plt.savefig(f"{kwargs['triggerplot_directory']}/{eventDirectory}/T_{triggerfile.split('_')[-2]}_{triggerfile.split('_')[-1][:-5]}_strain.png")
    
    # Creating the correlation plot
    thepod.plot(type_="correlation")
    plt.savefig(
        f"{kwargs['triggerplot_directory']}/{eventDirectory}/T_{triggerfile.split('_')[-2]}_{triggerfile.split('_')[-1][:-5]}_correlation.png")

    # And if skymap is created we save the plot as png too.
    if kwargs['skymap']==True:
        buffer.plot(type_="skymap")
        plt.savefig(f"{kwargs['triggerplot_directory']}/{eventDirectory}/T_{triggerfile.split('_')[-2]}_{triggerfile.split('_')[-1][:-5]}_skymap.png")

raise SystemExit()

# if __name__ == "__main__":


#     main(**kwargs)

#     quit()
