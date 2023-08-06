import boto3
import convertapi
import requests
import json
import logging

log = logging.getLogger()
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.INFO)

def convertDoc(khcredentials, letterURL, docFileName):
    SECRET = khcredentials.convertapiSecret
    #convertapi.api_secret = SECRET

    payload = {
        "Parameters": [
            {
                "Name": "File",
                "FileValue": {
                    "Url": letterURL
                }
            },
            {
                "Name": "StoreFile",
                "Value": True
            },
            {
                "Name": "HideElements",
                "Value": ".d-print-none"
            },
            {
                "Name": "Background",
                "Value": False
            },
            {
                "Name": "PageSize",
                "Value": "a4"
            }
        ]
    }
    headers = {
        "Content-Type": "application/json",
    }
    url = "https://v2.convertapi.com/convert/html/to/pdf?Secret="+SECRET+"&StoreFile=true&HideElements=.d-print-none&Background=false&PageSize=a4"
    log.info("patientSessionTranscript letterURL - "+str(letterURL))
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    log.info("patientSessionTranscript response - "+str(response))
    log.info("patientSessionTranscript response.text - "+str(response.text))

    if response.status_code == 200:
        result = response.json()
        ConversionCost = result["ConversionCost"]
        link = result["Files"][0]["Url"]

    else:
        return False, str(response.text)

    #result = convertapi.convert('pdf', { 'File': url, 'PageSize': 'a4', 'Background': 'false', 'HideElements': '.d-print-none' }, from_format = 'html')

    # save to file
    #result.file.save("/tmp/"+docFileName)
    docData = requests.get(link)
    bytesFile = docData.content

    client = boto3.client("s3", aws_access_key_id=khcredentials.awsAccessKeyId, aws_secret_access_key=khcredentials.awsSecretAccessKey)

    client.put_object(Body=bytesFile,Key=docFileName,Bucket=khcredentials.bucketNameDocs)

    docLink = "https://"+khcredentials.bucketNameDocs+".s3.us-east-1.amazonaws.com/"+docFileName

    GCLOUD = """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(khcredentials.bucketNameDocs)
    blob = bucket.blob(docFileName)
    blob.upload_from_filename("/tmp/"+docFileName)
    os.remove("/tmp/"+docFileName)

    docLink = "https://storage.googleapis.com/"+str(khcredentials.bucketNameDocs)+"/"+str(docFileName)
    log.info("docLink - "+docLink)
    """
    return docLink, bytesFile
