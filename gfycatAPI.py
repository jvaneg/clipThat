import requests
from pathlib import Path
import time
from progress.spinner import Spinner

# Constants
URL_API = "https://api.gfycat.com/v1"
URL_API_TOKEN = URL_API + "/oauth/token"
URL_UPLOAD = "https://filedrop.gfycat.com"
URL_API_CREATE_GFY = URL_API + "/gfycats"
URL_UPLOAD_STATUS = URL_API_CREATE_GFY + "/fetch/status"
URL_GFY = "https://gfycat.com"
URL_GFY_DIRECT = "https://giant.gfycat.com"

GFY_MAX_SECONDS = 60


def getAccessTokenAnon(client_id, client_secret):

    requestPayload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(URL_API_TOKEN, data=str(requestPayload))
    responseJson = response.json()
    if not "access_token" in responseJson:
        raise Exception("Gfycat API is currently unavailable")

    return responseJson["access_token"]


def getAccessTokenUser(client_id, client_secret, username, password):
    
    requestPayload = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password
    }

    response = requests.post(URL_API_TOKEN, data=str(requestPayload))
    responseJson = response.json()
    if not "access_token" in responseJson:
        raise Exception("Gfycat API is currently unavailable")

    return responseJson["access_token"]


def uploadFile(accessToken, fileName):

    requestHeaders = { 
        "Authorization": "Bearer {}".format(accessToken) 
    }

    requestPayload = {
        "noMd5": "true"
    }

    response = requests.post(URL_API_CREATE_GFY, data=str(requestPayload), headers=requestHeaders)
    responseJson = response.json()
    if not "gfyname" in responseJson:
        raise Exception("Gfycat API is currently unavailable")

    gfyname = responseJson["gfyname"]

    inputFile = Path(fileName)
    newFile = inputFile.parent.joinpath(gfyname)
    inputFile.rename(newFile)

    with newFile.open(mode="rb") as fileUpload:
        fileResponse = requests.put("{}/{}".format(URL_UPLOAD,gfyname), fileUpload)

    #check if fileresponse is 200
    if(fileResponse.status_code != 200):
        raise Exception("Problem uploading to gfycat filedrop")

    waitForUpload(gfyname)

    gfyURL = "{}/{}".format(URL_GFY,gfyname)
    directURL = "{}/{}.webm".format(URL_GFY_DIRECT,gfyname)

    return gfyURL, directURL


def waitForUpload(gfyname):
    uploading = True
    spinner = Spinner("Uploading ")
    while(uploading):
        progressResponse = requests.get("{}/{}".format(URL_UPLOAD_STATUS, gfyname))
        responseJson = progressResponse.json()

        if(responseJson["task"] == "error" or responseJson["task"] == "NotFoundo" ):
            raise Exception("Failed to upload to gfycat")
        elif(responseJson["task"] == "encoding"):
            spinner.next()
            time.sleep(1)
        elif(responseJson["task"] == "complete"):
            break

    print("")

    return responseJson["gfyname"]