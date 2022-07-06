# GalleryAI
A python application build with Azure Vision Services to filter Images based on it's content same as Google Photos. 

## Setup & Configuration

> **Requirements**
> - Azure Vision Service KEY and REGION

> **Setup**
> - Run GUI/main.py
> - Enter KEY, REGION and FOLDER PATH containing Images
> - :warning: Only keep images in the folder you have selected and images must be less than 4mb
> - Wait, as It will take some time to analyse images from that folder (It's one time process as it will store analysis data of current images)
> - You will see the GUI after some Time

## Filters
> **Tags**
> - Select Tags you want in images
> - It works as OR operation. If you will select 5 tags It will give you all images containing atleast one of those 5 tags

> **Search**
> - You have to write tags in this field 
> - It works as AND operation. If you will write 5 tags It will give you images containing all those 5 tags

> **Number Of person**
> - Enter number of person you want in am image

## Refresh

> - You can hit refresh button after entering more images in folder (You have selected)
> - Again It will take some time and restarts the program


