import enum
import os, sys
from unittest import result
from PIL import Image, ImageDraw
from matplotlib import image
import matplotlib.pyplot as plt
from cmath import exp
from tkinter import image_types
from dotenv import load_dotenv
import json

# Helper Modules Imports
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from AzureInteraction.azure_client import azure_vision_client


# Azure Imports
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes

result_json = {}
filter_json = {}
filter_json['description'] = {}
filter_json['tags'] = {}
filter_json['image_type'] = {}
filter_json['number_of_person'] = {}

def run_analysis():

    global result_json
    global filter_json


    # GET  
    # image_folder_path = path of image containing folder
    try:
        global image_folder_path
        configuration_object = json.load(open('configuration.json') )
        image_folder_path = configuration_object['image_folder_path']
    except Exception as ex:
        print("Error : Getting Image folder Path : ",ex)

    
    # MAIN CODE
    try:

        
        # GET
        # vision_client = azure client to interact with azure 
        vision_client = azure_vision_client()

        
        # GET
        # result_json = result of already analysed images 
        # filter_json = filters of already analysed images
        # cache_images = full path of images that are already analysed
        try:
            result_json = json.load(open('Data/result_json.json'))
            filter_json = json.load(open('Data/filter_json.json'))
            cache_images = result_json['cache_images']
        except Exception as ex:
            print('Creating result_json file')   
            cache_images = [] 

        
        # CALL
        # calling api on all New Images    
        for i,image_file in enumerate(os.listdir(image_folder_path)):
            image_file_path = os.path.join(image_folder_path, image_file)
            if image_file_path not in cache_images:
                print(i, end='-')
                print(image_file_path)

                # calling azure api for analyse the images
                analysis_image( image_file_path, vision_client ) 

        
        # EXPORT
        # saving results  
        all_images = list(result_json.keys())
        if 'cache_images' in all_images:
            all_images.remove('cache_images')
        result_json['cache_images'] = all_images   
        result_json_file = json.dumps(result_json, indent=4)
        json_file = open('Data/result_json.json','w')
        json_file.write(result_json_file)
        json_file.close()

        
        # EXPORT
        # saving filters
        filter_data_file = json.dumps(filter_json, indent=4)
        filter_file = open('Data/filter_json.json','w')
        filter_file.write(filter_data_file)
        filter_file.close()
    
    except Exception as ex:
        print(ex)


def analysis_image(image_file, vision_client):
    global result_json
    result_json[image_file] = {}

    global filter_json
    
    
    # CALL
    # calling vision api from azure
    features = [VisualFeatureTypes.description,
            VisualFeatureTypes.tags,
            VisualFeatureTypes.categories,
            VisualFeatureTypes.objects,
            VisualFeatureTypes.color,
            VisualFeatureTypes.image_type
            ]
    with open(image_file, mode="rb") as image_data:
        analysis = vision_client.analyze_image_in_stream(image_data , features)

    
    # GET
    # fetching description of image
    for caption in analysis.description.captions:
        try:
            
            # Feeding result_json
            result_json[image_file]['description'] = {}
            result_json[image_file]['description']['caption'] = caption.text
            result_json[image_file]['description']['confidence'] = caption.confidence
            
            # Feeding filter_json
            if caption.text in filter_json['description'].keys():
                filter_json['description'][caption.text].append(image_file)
            else:
                filter_json['description'][caption.text] = [image_file]    

        except Exception as ex:
            print("Description Error ", ex)    

    
    # GET
    # fetching tags on image
    if (len(analysis.tags) > 0):
        result_json[image_file]['tags'] = {}
        try:
            for tag in analysis.tags:

                # Feeding result_json
                result_json[image_file]['tags'][tag.name] = tag.confidence

                # Feeding filter_json
                if  tag.name in filter_json['tags'].keys():
                    filter_json['tags'][tag.name].append(image_file)
                else:
                    filter_json['tags'][tag.name] = [image_file] 

        except Exception as ex:
            print("Image Tags Error ",ex)
    
    
    # GET 
    # fetching colors on image 
    try:
        result_json[image_file]['color'] = {}
        result_json[image_file]['color']['dominant_color_foreground'] = analysis.color.dominant_color_foreground
        result_json[image_file]['color']['dominant_color_background'] = analysis.color.dominant_color_background
        result_json[image_file]['color']['dominant_colors'] = analysis.color.dominant_colors
        result_json[image_file]['color']['accent_color'] = analysis.color.accent_color
    except Exception as ex:
        print("Color Error ",ex)    

    
    # GET 
    # fetching object and number of persons
    try:
        if len(analysis.objects) > 0:
            result_json[image_file]['objects'] = {}
            result_json[image_file]['number_of_person'] = 0
            for i, detected_object in enumerate(analysis.objects):
                result_json[image_file]['objects'][i] = {}
                result_json[image_file]['objects'][i]['name'] = detected_object.object_property
                result_json[image_file]['objects'][i]['confidence'] = detected_object.confidence
                rectangle = detected_object.rectangle
                result_json[image_file]['objects'][i]['coordinates'] = {}
                result_json[image_file]['objects'][i]['coordinates']['x'] = rectangle.x
                result_json[image_file]['objects'][i]['coordinates']['y'] = rectangle.y
                result_json[image_file]['objects'][i]['dimension'] = {}
                result_json[image_file]['objects'][i]['dimension']['width'] = rectangle.w
                result_json[image_file]['objects'][i]['dimension']['height'] = rectangle.h

                if detected_object.object_property == 'person':
                    result_json[image_file]['number_of_person'] += 1

            # Feeding filter_json
            if str(result_json[image_file]['number_of_person']) in filter_json['number_of_person'].keys():
                filter_json['number_of_person'][str(result_json[image_file]['number_of_person'])].append(image_file)
            else:    
                filter_json['number_of_person'][str(result_json[image_file]['number_of_person'])] = [image_file]

                    
    except Exception as ex :
        print(ex)

    # GET
    # fetching image type
    try:

        # Feeding result_json
        result_json[image_file]['image_type'] = {}
        result_json[image_file]['image_type']['clip_art'] = True if analysis.image_type.clip_art_type > 0 else False
        result_json[image_file]['image_type']['line_drawing'] = True if analysis.image_type.line_drawing_type > 0 else False

        # Feeding filter_json
        if result_json[image_file]['image_type']['clip_art']:
            if 'clip_art' in filter_json['image_type'].keys():
                filter_json['image_type']['clip_art'].append(image_file)
            else:
                filter_json['image_type']['clip_art'] = [image_file]

        if result_json[image_file]['image_type']['line_drawing']:
            if  'line_drawing' in filter_json['image_type'].keys():
                filter_json['image_type']['line_drawing'].append(image_file)
            else:
                filter_json['image_type']['line_drawing'] = [image_file]



    except Exception as ex:
        print(ex)

    
# if __name__=="__main__":
#     main()