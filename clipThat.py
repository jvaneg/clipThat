import argparse
from datetime import datetime
import shutil
from pathlib import Path
import toml

import vidTools
import gfycatAPI

# Constants
TEMP_DIRECTORY = Path(".tmp")
TEMP_FILE = Path("tmp.mp4")
AUTH_FILE = Path("config.cfg")

def main(args):

    try:
        timeDelta = checkArgs(args)
    except Exception as error:
        print("Error: {}".format(error.args[0]))
        exit(-1)

    if(args.savelocal != None and Path(args.savelocal).is_file()):
        print("Output file \"{}\" already exists. Overwrite? [y/n]".format(args.savelocal))
        overwriteResp = input()
        if('y' not in overwriteResp.lower()):
            print("Not overwriting - exiting")
            exit(-1)

    if(args.savelocal == None):
        localOutput = TEMP_FILE
    else:
        localOutput = Path(args.savelocal)

    tmpDir, tmpOutput = setupDirectories(localOutput)

    try: 
        vidTools.cutVideo(args.source, args.start, str(timeDelta), str(tmpOutput))
    except Exception as error:
        print("Error: {}".format(error.args[0]))
        shutil.rmtree(tmpDir)
        exit(-1)

    if(args.savelocal != None):
        shutil.copy(tmpOutput, localOutput)

    if(not args.nogfy):
        try:
            gfyURL, directURL = uploadGfycat(AUTH_FILE,tmpOutput)
            print("Upload successful!")
            print("Available at:\t{}".format(gfyURL))
            print("Direct link at:\t{}".format(directURL))

        except Exception as error:
            print("Error: {}".format(error.args[0]))
            shutil.rmtree(tmpDir)
            exit(-1)

    shutil.rmtree(tmpDir)
    
    if(args.savelocal != None):
        print("Local copy at:\t{}".format(localOutput.absolute()))


def checkArgs(args):
    if(args.nogfy and (args.savelocal == None)):
        raise Exception("Must set --savelocal to use -nogfy option")

    if(not Path(args.source).is_file()):
        raise Exception("Source file \"{}\" does not exist".format(args.source))

    sourceDuration = vidTools.getVideoDuration(args.source)
    timeDelta = validateTimes(args.start, args.end, sourceDuration)
    
    if(not args.nogfy and timeDelta.total_seconds() > gfycatAPI.GFY_MAX_SECONDS):
        raise Exception("Clip too long - gfycat only supports maximum {} second clips".format(gfycatAPI.GFY_MAX_SECONDS))

    return timeDelta
    
   
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


def setupDirectories(localOutput):
    tmpDir = Path(__file__).parent.joinpath(TEMP_DIRECTORY)

    if(not tmpDir.is_dir()):
        tmpDir.mkdir(parents=True)
    tmpOutput = tmpDir.joinpath(localOutput.name)

    if(args.savelocal != None and not localOutput.parent.is_dir()):
            localOutput.parent.mkdir(parents=True)

    return tmpDir, tmpOutput


def uploadGfycat(authFileName, uploadFileName):
    if(not Path(authFileName).is_file()):
        raise Exception("Config file \"{}\" is missing.".format(AUTH_FILE))

    with Path(authFileName).open() as authFile:
        authData = toml.load(authFile)
        clientID = authData["auth"]["gfycat"]["client_id"]
        clientSecret = authData["auth"]["gfycat"]["client_secret"]
        username = authData["auth"]["gfycat"]["username"]
        password = authData["auth"]["gfycat"]["password"]

    if(args.anon):
        accessToken = gfycatAPI.getAccessTokenAnon(clientID,clientSecret)
    else:
        accessToken = gfycatAPI.getAccessTokenUser(clientID,clientSecret,username,password)

    gfyURL, directURL = gfycatAPI.uploadFile(accessToken, uploadFileName)

    return gfyURL, directURL


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