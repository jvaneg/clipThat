import sys
import os

import argparse
from datetime import datetime

def main(args):
    print(args.source)
    print(args.start)
    print(args.end)
    if(args.savelocal != None):
        print(args.savelocal)
    print(args.nogfy)

    if(args.nogfy and (args.savelocal == None)):
        print("Error: Must set --savelocal to use -nogfy option")
        exit(-1)

    try:
        validateTimes(args.start, args.end)
    except ValueError as error:
        print("Error: {}".format(error.args[0]))

    
def validateTimes(start, end):
    try:
        startTime = validateTime(start)
    except ValueError as error:
        raise ValueError("In start time - {}".format(error.args[0]))

    try:
        endTime = validateTime(end)
    except ValueError as error:
        raise ValueError("In end time - {}".format(error.args[0]))

    print(startTime)
    print(endTime)

def validateTime(inputTime):
    timeSplit = inputTime.split(':')
    numTimeArgs = len(timeSplit)


    if(numTimeArgs < 2 or numTimeArgs > 3):
        raise ValueError("Invalid time format")

    # could be MM:SS.m or MM:SS
    if(numTimeArgs == 2):
        # must be MM:SS.m
        if('.' in timeSplit[1]):
            if(validateMinutes(timeSplit[0]) and validateSeconds(timeSplit[1])):
                print("MM:SS.m")
                outTime = datetime.strptime(inputTime, "%M:%S.%f")
            else:
                raise ValueError("Invalid time format")
        # must be MM:SS
        else:
            if(validateMinutes(timeSplit[0]) and validateSeconds(timeSplit[1])):
                print("MM:SS")
                outTime = datetime.strptime(inputTime, "%M:%S")
            else:
                raise ValueError("Invalid time format")
    # could be HH:MM:SS.m or HH:MM:SS
    else:
        # must be HH:MM:SS.m
        if('.' in timeSplit[2]):
            if(validateHours(timeSplit[0]) and validateMinutes(timeSplit[1]) and validateSeconds(timeSplit[2])):
                print("HH:MM:SS.m")
                outTime = datetime.strptime(inputTime, "%H:%M:%S.%f")
            else:
                raise ValueError("Invalid time format")
        # must be HH:MM:SS
        else:
            if(validateHours(timeSplit[0]) and validateMinutes(timeSplit[1]) and validateSeconds(timeSplit[2])):
                print("HH:MM:SS")
                outTime = datetime.strptime(inputTime, "%H:%M:%S")
            else:
                raise ValueError("Invalid time format")

    return outTime


def validateHours(hoursString):
    validHours = True
    try:
        hours = int(hoursString)
        if(hours > 23 or hours < 0):
            validHours = False
    except ValueError:
        validHours = False

    return validHours

def validateMinutes(minutesString):
    validMinutes = True
    try:
        minutes = int(minutesString)
        if(minutes > 59 or minutes < 0):
            validMinutes = False
    except ValueError:
        validMinutes = False

    return validMinutes

def validateSeconds(secondsString):
    validSeconds = True
    try:
        seconds = float(secondsString)
        if(seconds >= 60 or  seconds < 0):
            validSeconds = False
    except ValueError:
        validSeconds = False

    return validSeconds
    



    

   

# constants and python main thing
WORDS_FILENAME = "words.txt"    #file containing list of password "words"
PWORD_FILENAME = "passwords.txt"    #file containing usernames and passwords
HASH_SIZE_IN_BYTES = 32

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="the source video")
    parser.add_argument("start", help="the start time of the clip, in [HH:]MM:SS[.m...] format")
    parser.add_argument("end", help="the end time of the clip, in [HH:]MM:SS[.m...] format")
    parser.add_argument("-sl", "--savelocal", metavar="[output filename]", help="save a local copy of the clip")
    parser.add_argument("-nogfy", action="store_true", help="don't upload to gfycat")

    args = parser.parse_args()
    main(args)