import ffmpeg
import datetime

def cutVideo(inputFile, startTime, endTime, outputFile):
    stream = ffmpeg.input(inputFile, ss=startTime)
    stream = ffmpeg.output(stream, outputFile, to=endTime, c="copy")
    ffmpeg.run(stream, quiet=True, overwrite_output=True)

def getVideoDuration(inputFile):
    fileInfo = ffmpeg.probe(inputFile)
    durationDelta = datetime.timedelta(seconds=float(fileInfo["streams"][0]["duration"]))
    
    # must be HH:MM:SS.m
    if('.' in str(durationDelta)):
        durationTime = datetime.datetime.strptime(str(durationDelta), "%H:%M:%S.%f")
    # must be HH:MM:SS
    else:
        durationTime = datetime.datetime.strptime(str(durationDelta), "%H:%M:%S")

    return durationTime
