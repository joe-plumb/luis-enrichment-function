import json
import logging
import os
import traceback

from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials

import azure.functions as func

def main(inputblob: func.InputStream, outputblob: func.Out[bytes], erroroutputblob: func.Out[bytes]):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {inputblob.name}\n"
                 f"Blob Size: {inputblob.length} bytes")
    try:
        body = json.loads(inputblob.read(size=-1))
        body_enriched = get_luis(body)
        outputblob.set(json.dumps(body_enriched))
    except Exception as e:
        logging.error(f"Encountered error processing {inputblob.name} :")
        logging.error(e)
        erroroutputblob.set(inputblob.read(size=-1))    

# Initialize LUIS client and py functions
LUIS_RUNTIME_KEY = os.environ["LUIS_RUNTIME_KEY"]
LUIS_RUNTIME_ENDPOINT = os.environ["LUIS_RUNTIME_ENDPOINT"]
LUIS_RUNTIME_APPID = os.environ["LUIS_RUNTIME_APPID"]

clientRuntime = LUISRuntimeClient(LUIS_RUNTIME_ENDPOINT, CognitiveServicesCredentials(LUIS_RUNTIME_KEY))

def predict(app_id, slot_name, query):
    request = { "query" : str(query) }
    # Note be sure to specify, using the slot_name parameter, whether your application is in staging or production.
    resp = clientRuntime.prediction.get_slot_prediction(app_id=app_id, slot_name=slot_name, prediction_request=request)
    return (resp)

def loadjson(transcription):
    try:
        return (0, transcription['AudioFileResults'][0]['SegmentResults'])
    except:
        try:
            return (1, transcription["Segments"])
        except Exception as e:
            logging.error(f"Cannot load JSON transcription from BatchTranscription Service. \n"
                          f"Check JSON transcription format and amend loadjson function. \n"
                          f"Error: ", e)

def get_luis(transcription):
    jsontype, utterances = loadjson(transcription)    
    if jsontype == 0:
        for i in utterances:
            i["NBest"][0]["LuisResponse"] = predict(LUIS_RUNTIME_APPID,'staging',i["NBest"][0]["ITN"]).as_dict()
        transcription['AudioFileResults'][0]['SegmentResults'] = utterances
        return transcription
    if jsontype == 1:
        for i in utterances:
            utterance = i["ITN"]
            # Limit utterance to first 500 characters
            if len(utterance) > 500:
                utterance=utterance[0:500]
            i["LuisResponse"] = predict(LUIS_RUNTIME_APPID,'staging',utterance).as_dict()
        transcription["Segments"] = utterances
        return transcription
