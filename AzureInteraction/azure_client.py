from dotenv import load_dotenv
import os
import json
# Azure Imports
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

def azure_vision_client():
        try:
            global key
            global region
            configuration_object = json.load(open('configuration.json') )
            key = configuration_object['computer_vision_api_key']
            region = configuration_object['computer_vision_region']
        except Exception as ex:
            print("Error : Getting key and region of Azure serive : ",ex)

        # authenticating credentials
        credentials = CognitiveServicesCredentials(key)
        client = ComputerVisionClient(
            endpoint="https://" + region + ".api.cognitive.microsoft.com/",
            credentials=credentials
        )

        return client
    