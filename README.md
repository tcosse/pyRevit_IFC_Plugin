This is a pyRevit custom extension I designed to help me out with some tasks.

The highlight of this pyRevit extension is the IFC Export tool. This utility enables the user to batch export multiple Revit Files. It takes as input a JSON export settings file and and IFC Mapping txt file.

# How to install
1- Clone this repo

2- Install the [pyRevit Plugin](https://github.com/eirannejad/pyRevit/releases) (free)

3- Go to the pyRevit Settings

 ![image](https://github.com/tcosse/pyRevit_IFC_Plugin/assets/52131424/a4308dd0-3fba-499a-b2c3-ac9ca335c8f2)

![image](https://github.com/tcosse/pyRevit_IFC_Plugin/assets/52131424/378377d5-35e0-4e2c-82c1-d948b9c62c0c)


4 - In the "Custom Extension Directories", and add the "pyRevitExtensions" folder you just cloned

![image](https://github.com/tcosse/pyRevit_IFC_Plugin/assets/52131424/56f0b3d7-b843-42e6-a50f-c6fad553c918)

5- Tada ! Now a new tab named "Custom Tools" should appear

![image](https://github.com/tcosse/pyRevit_IFC_Plugin/assets/52131424/56500b2d-e201-4ab5-bdc3-3d2219286ce1)


# How to use the IFC batch export tool

The tool has two different use cases :

-If there is one or more active documents in the session, only the active file will be exported

-If there is no active document, the user will be asked to select the revit files to export. These file will be opened and exported in the background.

For each file, the program exports all the views containing 'IFC' in their name. Each file is exported to the output folder prompted by the user with the following name : "revitfilename - viewname"

The script also creates a default view with settings that are specific to SNCF G&C's needs (medium detail level, no subcategories...)

The tool retrieves all the settings of the ifc export from the json file, the ifc mapping file and the output folder
    
Limitations : 
Only works for IFC 2x3 CV2 and default phase 
Option for exporting linked model files does not work
