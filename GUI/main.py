from functools import reduce
import os
import sys
import json
import math

import tkinter as tk
from tkinter import  Frame, Label, Entry, Button, Checkbutton, Scrollbar, Canvas, PhotoImage, StringVar
from PIL import ImageTk, Image

# Getting parent directory
global parentdir
global currentdir
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from scripts.script import run_analysis

# Variable Declaration

query_string = ""           # value of query
query_activations = []      # list to carry all entered tags value
tag_activations = []        # list to carry all selected tags value
person_number = 0           # Variable for person number filter
all_filters = {}            # contain filter_json object
all_image_info = {}         # contain result_json object

all_images = {}             # key: full_path of image | value: image 
reverse_all_images = {}     # key: image              | value: full path of image
tag_variables = {}          # key: tag                | value: stringVar connected to that tag 

# Restarts the Whole Window    
def restart():
    parent.destroy()
    os.startfile(os.path.join(parentdir,"GUI","main.py"))

# check for initial checking
def config_status():
    try:
        global image_folder_path
        configuration_object = json.load(open('configuration.json') )
        if len(configuration_object['image_folder_path']) > 0 and len(configuration_object['computer_vision_region']) and len(configuration_object['computer_vision_api_key']):
            return True
        else:
            False    
    except Exception as ex:
        print("Error : Getting Image folder Path : ",ex)

# update query_activation list
def update_query():
    '''
    query string reflected here and update query_activation
    then It calls fill_image_data to apply filter
    '''
    global query_activations
    query_activations = query_string.get().split(' ')
    print(query_activations)
    if query_activations[0] == '':
        query_activations = []
    fill_image_data(image_frame)    


# clear query_string and filter
def cancel_query():
    global query_activations
    query_string.set('')
    query_activations = []
    fill_image_data(image_frame)


# update tag_activation list
def update_tags():
    '''
    checkbox event reflected here and updates tag_activtion
    then It calls fill_image_data to apply filter
    '''
    global tag_activations
    tag_activations = []
    for tag in tag_variables:
        tag_value = tag_variables[tag].get()
        if  tag_value[:4] == '_off':
            pass
        else:
            tag_activations.append(tag_value)
    fill_image_data(image_frame)        


# clear tag filter
def clear_tags_filter():
    '''
    making tag_activations list empty
    then It calls fill_image_data to apply filter
    '''
    global tag_activations
    tag_activations = []
    fill_image_data(image_frame)


# call fill_image_data 
def update_person_number():
    '''
    will call by person number filter after updating person_number variable
    '''
    fill_image_data(image_frame)


# clear person_number filter
def clear_person_number():
    '''
    set person_number to -1 and call fill_image_data
    '''
    global person_number
    person_number.set(-1)
    fill_image_data(image_frame)


# returing query frame to embed in parent 
def return_query_frame(container):

    global query_string
    query_frame = Frame(container)

    query_label = Label(query_frame, text='SEARCH')
    query_label.place(relx=0, rely=0, relwidth=.2,relheight=1)

    query_entry = Entry(query_frame, textvariable=query_string)
    query_entry.place(relx=.2, rely=0, relwidth=.6,relheight=1)

    query_button = Button(query_frame, text='Search', command=update_query)
    query_button.place(relx=.8, rely=0, relwidth=.1,relheight=1)

    query_cancel_button = Button(query_frame, text='Cancel', command=cancel_query)
    query_cancel_button.place(relx=.9, rely=0, relwidth=.1,relheight=1)

    return query_frame


# returing tag_frame to embed in parent
def return_tag_frame(container):

    tag_frame = Frame(container)
    return tag_frame


# filling tags in tag_frame
def fill_tag_data(tag_frame):

    global tag_variables
    
    def data():
        '''
        taking tags name from all_filters
        creating dynamic checkbuttons list
        filling them in checkbutton
        '''
        
        all_filters_sorted = list(all_filters['tags'].keys())
        all_filters_sorted.sort()
        
        for i,tag in enumerate(all_filters_sorted):
            Label(checkbox_frame,text=tag).grid(row=i,column=1)
            checkbutton = Checkbutton(
                checkbox_frame,
                command=update_tags, 
                variable=tag_variables[tag], 
                onvalue=tag, 
                offvalue='_off'+tag
                )
            checkbutton.deselect()
            checkbutton.grid(row=i, column=2)

    def bindFunction(event):
        tag_canvas.configure(scrollregion=tag_canvas.bbox("all"), height=1000)

    tags_label = Label(tag_frame, text='Filter Tags')
    tags_label.pack()

    # creating canvas and frame to hold checkbuttons
    tag_canvas = Canvas(tag_frame)
    checkbox_frame = Frame(tag_canvas)
    tag_scrollbar = Scrollbar(tag_frame, orient=tk.VERTICAL, command=tag_canvas.yview)
    tag_canvas.configure(yscrollcommand=tag_scrollbar.set)

    tag_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tag_canvas.pack(side=tk.LEFT)
   
    tag_canvas.create_window((0,0),window=checkbox_frame,anchor='nw')
    checkbox_frame.bind("<Configure>",bindFunction)
    data() 


# returing image_frame to embed in parent
def return_image_frame(container):

    image_frame = Frame(container)
    return image_frame   


 # fillin images in image_frame   
def fill_image_data(image_frame):     
    
    def data():
        '''
        taking images from all_images
        applying tags filter on it
        applying person_number fiter on it
        fillin images into image_frame
        '''
        all_images_list = []
        # applying tags filter
        if tag_activations:
            all_images_list = []
            for tag in tag_activations:
                print(tag)
                for path_key in all_filters['tags'][tag]:
                    print(path_key)
                    all_images_list.append(all_images[path_key])
            print(all_images_list)
        else:
            all_images_list = list(all_images.values())

        # applying person_number filter
        person_number_value = person_number.get()    
        if person_number_value in all_filters["number_of_person"].keys() and person_number_value!='-1':
            all_path_list = all_filters["number_of_person"][person_number_value]
            all_images_list = [all_images[path_key] for path_key in all_path_list ]
        all_images_list = list(set(all_images_list))

        # applying query filter
        if query_activations:
            all_images_list = []
            all_path_sets = []
            for tag in query_activations:
                path_set = set({})
                for path in all_filters['tags'][tag]:
                    path_set.add(path)
                all_path_sets.append(path_set)
            for path in reduce(lambda a,b: a&b, all_path_sets):
                print(all_images[path])
                all_images_list.append(all_images[path])


        # filling images in image_frame
        image_row = 0
        image_count = 0
        for i in range(0, len(all_images_list), 4):
            for j in range(4):
                if image_count == len(all_images_list):
                    break
                canvas = Canvas(image_grid_frame, width=200, height=200)
                canvas.grid(row=image_row,column=j)
                canvas.create_image(100, 100, anchor=tk.CENTER, image=all_images_list[image_count])
                image_count += 1 
            image_row += 1    
 
    def bindFunction(event):
        image_canvas.configure(scrollregion=image_canvas.bbox("all"), height=1000)

    # creating canvas and frame to hold images
    image_canvas = Canvas(image_frame, bg='black')
    image_grid_frame = Frame(image_canvas)
    image_scrollbar = Scrollbar(image_frame, orient=tk.VERTICAL, command=image_canvas.yview)
    image_canvas.configure(yscrollcommand=image_scrollbar.set)

    image_scrollbar.place(relx=0.98, rely=0, relheight=1)
    image_canvas.place(relx=0, rely=0, relheight=1, relwidth=1)
   
    image_canvas.create_window((0,0),window=image_grid_frame,anchor='nw')
    image_grid_frame.bind("<Configure>",bindFunction)
    data() 


# return person_number frame to embed in parent
def return_number_filter(container):
    global person_number

    number_filter_frame = Frame(container)

    tags_filter_clear = Button(number_filter_frame, text='Clear Tags Filter', command=clear_tags_filter)
    tags_filter_clear.pack(side=tk.LEFT)

    number_button_clear = Button(number_filter_frame, text='Clear', command=clear_person_number)
    number_button_clear.pack(side=tk.RIGHT)

    number_filter_button = Button(number_filter_frame, text='Filter', command=update_person_number)
    number_filter_button.pack(side=tk.RIGHT)

    person_number_entry = Entry(number_filter_frame, textvariable=person_number)
    person_number_entry.pack(side=tk.RIGHT)
    
    number_filter_label = Label(number_filter_frame, text='Person Number')
    number_filter_label.pack(side=tk.RIGHT)

    return number_filter_frame


# return init window frame to embed in parent
def return_init_window(container):
    key_value=""
    region_value=""
    path_value=""
    try:
        configuration_object = json.load(open('configuration.json') )
        key_value = configuration_object['computer_vision_api_key']
        region_value = configuration_object['computer_vision_region']
        path_value = configuration_object['image_folder_path']
    except Exception as ex:
        print("Error : Getting Image folder Path : ",ex)    
    
    init_window = Frame(container)
    key_string = StringVar()
    region_string = StringVar()
    path_string = StringVar()

    def save_config():
        configuration_object['computer_vision_api_key'] = key_string.get()
        configuration_object['computer_vision_region'] = region_string.get()
        configuration_object['image_folder_path'] = path_string.get()

        config_file = open( os.path.join(parentdir, 'configuration.json'), 'w' )
        config_file.write( json.dumps(configuration_object,  indent=4))

        restart()

    head_label = Label(container, text="Set Configuration Variables", font=("Arial", 20))
    head_label.place(relx=0.30, rely=0.1, relheight=0.2, relwidth=0.4)

    key_frame = Frame(init_window)
    key_label = Label(key_frame,text="Vision API Key")
    key_entry = Entry(key_frame, textvariable=key_string)
    key_string.set(key_value)
    key_label.place(relx=0.1, rely=0.0, relheight=0.2, relwidth=0.3)
    key_entry.place(relx=0.5, rely=0.0, relheight=0.2, relwidth=0.3)
    key_frame.place(relx=0.0, rely=0.3, relheight=0.2, relwidth=1)

    region_frame = Frame(init_window)
    region_label = Label(region_frame,text="Vision API Region")
    region_entry = Entry(region_frame, textvariable=region_string)
    region_string.set(region_value)
    region_label.place(relx=0.1, rely=0.0, relheight=0.2, relwidth=0.3)
    region_entry.place(relx=0.5, rely=0.0, relheight=0.2, relwidth=0.3)
    region_frame.place(relx=0.0, rely=0.4, relheight=0.2, relwidth=1)

    path_frame = Frame(init_window)
    path_label = Label(path_frame,text="Image Folder Path")
    path_entry = Entry(path_frame, textvariable=path_string)
    path_string.set(path_value)
    path_label.place(relx=0.1, rely=0.0, relheight=0.2, relwidth=0.3)
    path_entry.place(relx=0.5, rely=0.0, relheight=0.2, relwidth=0.3)
    path_frame.place(relx=0.0, rely=0.5, relheight=0.2, relwidth=1)

    config_button = Button(init_window, text="Save", command=save_config)
    config_button.place(relx=0.5, rely=0.6, relheight=0.05, relwidth=0.3)

    return init_window

def refresh_images():
    run_analysis()
    restart()

# Parent Window
def root():

    global parent
    # Initialization parent window
    parent = tk.Tk()
    parent.title('Gallery AI')
    parent.geometry('1037x600')
    parent.resizable(False, False)    

    if config_status():
        global all_images
        global all_filters
        global reverse_all_images
        global all_image_info
        global query_string 
        global tag_variables
        global person_number
        global image_frame

        try:
            global image_folder_path
            configuration_object = json.load(open('configuration.json') )
            image_folder_path = configuration_object['image_folder_path']
        except Exception as ex:
            print("Error : Getting Image folder Path : ",ex)
            
        # Assingin StringVar
        query_string = StringVar()
        person_number = StringVar()

        if os.path.exists(os.path.join(parentdir,'Data','filter_json.json')) and os.path.exists(os.path.join(parentdir,'Data','result_json.json')):
            pass
        else:
            run_analysis()


        # Taking all filters in all_filters
        all_filters = json.load(open(os.path.join(parentdir,'Data','filter_json.json')))
        for tag in all_filters['tags'].keys():
            tag_variables[tag] = StringVar()

        # Taking all images in all_images
        all_image_info = json.load(open(os.path.join(parentdir,'Data','result_json.json')))
        all_images_path = list(all_image_info.keys())
        if 'cache_images' in all_images_path:
            all_images_path.remove('cache_images')
        for i,full_path in enumerate(all_images_path):
            image_data= Image.open(full_path)
            basewidth = 300
            current_width = image_data.size[0]
            current_hight = image_data.size[1]
            reduced_by = float(current_hight/200) if current_hight < current_width else float(current_width/200)
            new_width = math.floor(current_width/reduced_by)
            new_height = math.floor(current_hight/reduced_by)
            resized_image = image_data
            resized_image = image_data.resize((new_width, new_height), Image.ANTIALIAS)
            img_data = ImageTk.PhotoImage(resized_image)
            all_images[full_path] = img_data 
            reverse_all_images[img_data] = full_path

        def main_window():
            global query_frame
            global tag_frame
            global image_frame
            global person_number_filter
            
            # Query Section
            query_frame = return_query_frame(parent)
            query_frame.place(relx=0, rely=0, relheight=0.05, relwidth=1)
        
            # Tag Section
            tag_frame = return_tag_frame(parent)
            tag_frame.place(relx=0, rely=0.05, relheight=0.9, relwidth=.2)
            fill_tag_data(tag_frame)
            
            # Image Section
            image_frame = return_image_frame(parent)
            image_frame.place(relx=.2, rely=0.05, relheight=0.9, relwidth=.8)
            fill_image_data(image_frame)

            # Person Filter Section
            person_number_filter = return_number_filter(parent)
            person_number_filter.place(relx=0, rely=0.95, relheight=0.05, relwidth=1)

            # Refresh Images
            refresh_button = Button(parent, text='Refresh', command=refresh_images)
            refresh_button.place(relx=0.35, rely=0.95, relheight=0.05, relwidth=0.3)

        # Start Page Initiate
        welcome_full_path = os.path.join(parentdir, 'Data', 'welcome.png')
        welcome_image_data = ImageTk.PhotoImage(Image.open(welcome_full_path))
        welcome_canvas = Canvas(parent, width=200, height=200)
        welcome_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        welcome_canvas.create_image(0, 0, anchor=tk.NW, image=welcome_image_data)

        # Calling Main Window after 4 Seconds
        welcome_canvas.after(3000 ,main_window)

    else:
        def init_window():
            init_window = return_init_window(parent)
            init_window.place(relx=0, rely=0, relheight=1, relwidth=1)    

        # Start Page Initiate
        welcome_full_path = os.path.join(parentdir, 'Data', 'welcome.png')
        welcome_image_data = ImageTk.PhotoImage(Image.open(welcome_full_path))
        welcome_canvas = Canvas(parent, width=200, height=200)
        welcome_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        welcome_canvas.create_image(0, 0, anchor=tk.NW, image=welcome_image_data)

        # Calling Main Window after 4 Seconds
        welcome_canvas.after(2000 ,init_window)

    parent.mainloop()


if __name__=="__main__":
    root()    
