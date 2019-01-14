import sys
import os.path
import argparse
from datetime import datetime
import shutil
import json

import vidTools
import gfycatAPI

# Constants
TEMP_DIRECTORY = ".tmp/"
TEMP_FILE = "tmp.mp4"
AUTH_FILE = "auth.json"

def main(args):

    if(args.nogfy and (args.savelocal == None)):
        print("Error: Must set --savelocal to use -nogfy option")
        exit(-1)

    if(not os.path.isfile(args.source)):
        print("Error: Source file \"{}\" does not exist".format(args.source))
        exit(-1)

    try:
        sourceDuration = vidTools.getVideoDuration(args.source)
        timeDelta = validateTimes(args.start, args.end, sourceDuration)
    except ValueError as error:
        print("Error: {}".format(error.args[0]))
        exit(-1)

    if(not args.nogfy and timeDelta.total_seconds() > 60):
        print("Error: Clip too long - gfycat only supports maximum 60 second clips")
        exit(-1)

    if(args.savelocal != None and os.path.isfile(args.savelocal)):
        print("Output file \"{}\" already exists. Overwrite? [y/n]".format(args.savelocal))
        overwriteResp = input()
        if('y' not in overwriteResp.lower()):
            print("Not overwriting - exiting")
            exit(-1)

    if(args.savelocal == None):
        localOutput = TEMP_FILE
    else:
        localOutput = args.savelocal

    tmpDir = os.path.join(os.path.abspath(os.path.dirname(__file__)), TEMP_DIRECTORY)

    if(not os.path.exists(tmpDir)):
        os.mkdir(tmpDir)
    tmpOutput = os.path.join(tmpDir, localOutput)

    try: 
        vidTools.cutVideo(args.source, args.start, str(timeDelta), tmpOutput)
    except Exception as error:
        print("Error: {}".format(error.args[0]))
        shutil.rmtree(tmpDir)
        exit(-1)

    if(args.savelocal != None):
        shutil.copy(tmpOutput, localOutput)

    if(not args.nogfy):
        try:
            if(not os.path.isfile(AUTH_FILE)):
                raise Exception("Authentication file \"{}\" is missing.".format(AUTH_FILE))

            with open(AUTH_FILE) as authFile:
                authData = json.load(authFile)
                clientID = authData["gfycat"]["client_id"]
                clientSecret = authData["gfycat"]["client_secret"]
                username = authData["gfycat"]["username"]
                password = authData["gfycat"]["password"]

            if(args.anon):
                accessToken = gfycatAPI.getAccessTokenAnon(clientID,clientSecret)
            else:
                accessToken = gfycatAPI.getAccessTokenUser(clientID,clientSecret,username,password)

            gfyURL = gfycatAPI.uploadFile(accessToken, tmpOutput)

        except Exception as error:
            print("Error: {}".format(error.args[0]))
            shutil.rmtree(tmpDir)
            exit(-1)

    shutil.rmtree(tmpDir)

    if(not args.nogfy):
        print("Upload successful!\nAvailable at: {}".format(gfyURL))
    
    if(args.savelocal != None):
        print("Local copy at: {}".format(localOutput))
    

    
def validateTimes(start, end, sourceDuration):
    try:
        startTime = validateTimeFormat(start)
    except ValueError as error:
        raise ValueError("In start time - {}".format(error.args[0]))

    try:
        endTime = validateTimeFormat(end)
    except ValueError as error:
        raise ValueError("In end time - {}".format(error.args[0]))

    timeDelta = endTime - startTime

    if(timeDelta.total_seconds() <= 0):
        raise ValueError("End time must be after start time")

    if((sourceDuration - startTime).total_seconds() < 0):
        raise ValueError("Start time cannot be after end of video")

    if((sourceDuration - endTime).total_seconds() < 0):
        raise ValueError("End time cannot be after end of video")

    return timeDelta


def validateTimeFormat(inputTime):
    timeSplit = inputTime.split(':')
    numTimeArgs = len(timeSplit)

    if(numTimeArgs < 2 or numTimeArgs > 3):
        raise ValueError("Invalid time format")

    # could be MM:SS.m or MM:SS
    if(numTimeArgs == 2):
        # must be MM:SS.m
        if('.' in timeSplit[1]):
            outTime = datetime.strptime(inputTime, "%M:%S.%f")
        # must be MM:SS
        else:
            outTime = datetime.strptime(inputTime, "%M:%S")
    # could be HH:MM:SS.m or HH:MM:SS
    else:
        # must be HH:MM:SS.m
        if('.' in timeSplit[2]):
            outTime = datetime.strptime(inputTime, "%H:%M:%S.%f")
        # must be HH:MM:SS
        else:
            outTime = datetime.strptime(inputTime, "%H:%M:%S")

    return outTime


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="the source video")
    parser.add_argument("start", help="the start time of the clip, in [HH:]MM:SS[.m...] format")
    parser.add_argument("end", help="the end time of the clip, in [HH:]MM:SS[.m...] format")
    parser.add_argument("-sl", "--savelocal", metavar="[output filename]", help="save a local copy of the clip")
    parser.add_argument("-nogfy", action="store_true", help="don't upload to gfycat")
    parser.add_argument("-a", "--anon", action="store_true", help="upload anonymously")

    args = parser.parse_args()
    main(args)