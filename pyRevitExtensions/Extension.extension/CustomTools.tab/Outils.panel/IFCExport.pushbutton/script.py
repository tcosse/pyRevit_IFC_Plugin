#!/usr/bin/python
# -*- coding: latin-1 -*-

#  ___   __  __   ____     ___    ____    _____   ____
#  |_ _| |  \/  | |  _ \   / _ \  |  _ \  |_   _| / ___|
#   | |  | |\/| | | |_) | | | | | | |_) |   | |   \___ \
#   | |  | |  | | |  __/  | |_| | |  _ <    | |    ___) |
#  |___| |_|  |_| |_|      \___/  |_| \_\   |_|   |____/
# =========================================================


import clr
clr.AddReference("RevitServices")
clr.AddReference("System.Windows.Forms")
clr.AddReference("IronPython.Wpf")
clr.AddReference("Microsoft.WindowsAPICodePack")

from System import Windows
import wpf
from pyrevit import script, app
from pyrevit.revit import RevitWrapper as rw
import pyrevit.forms
import inspect
from shutil import copy2
from datetime import datetime
import os
import io
from RevitServices.Transactions import TransactionManager
from RevitServices.Persistence import DocumentManager
from Autodesk.Revit.ApplicationServices import Application
from Autodesk.Revit.DB import *
import json
from System.Windows.Forms import FolderBrowserDialog
from Microsoft.Win32 import OpenFileDialog
from Microsoft.WindowsAPICodePack.Dialogs import CommonOpenFileDialog

nooactivedoc_ui_file = script.get_bundle_file("NoActiveDoc.xaml")
activedoc_ui_file = script.get_bundle_file("Activedoc_IfcExport.xaml")

#   ____    _____   _____   ___   _   _   _____   ___    ___    _   _   ____
#  |  _ \  | ____| |  ___| |_ _| | \ | | |_   _| |_ _|  / _ \  | \ | | / ___|
#  | | | | |  _|   | |_     | |  |  \| |   | |    | |  | | | | |  \| | \___ \
#  | |_| | | |___  |  _|    | |  | |\  |   | |    | |  | |_| | | |\  |  ___) |
#  |____/  |_____| |_|     |___| |_| \_|   |_|   |___|  \___/  |_| \_| |____/
# ==============================================================================

def print_option(opt, arg):
    if opt[arg]:
        print("\t"+arg+' : True')
    else:
        print("\t"+arg+' : False')


def import_options_fromjson(ifc_options):
    options = IFCExportOptions()
    # options.AddOption("ExportInternalRevitPropertySets",str(ifc_options["ExportInternalRevitPropertySets"]))

    options.FileVersion = IFCVersion.IFC2x3CV2
    print("\nIFC Export Settings : ")
    print("\nGeneral Settings Tab")
    print("\tIFC Version : IFC2X3 CV2 (this script can only export in IFC2X3CV) ")
    options.SpaceBoundaryLevel = ifc_options["SpaceBoundaries"]
    print("\tSpace Boundaries Level : "+str(ifc_options["SpaceBoundaries"]))
    options.AddOption("SitePlacement", str(ifc_options["SitePlacement"]))
    print("\tFileType : IFC")
    if ifc_options["SitePlacement"] == 0:
        print("\tCoordinates Base : Shared Coordinates")
    if ifc_options["SitePlacement"] == 1:
        print("\tCoordinates Base : Survey Point")
    if ifc_options["SitePlacement"] == 2:
        print("\tCoordinates Base : Project Base Point")
    if ifc_options["SitePlacement"] == 3:
        print("\tCoordinates Base : Internal Coordinates")
    # 0:SharedCoordinates;1:SurveyPoint;2:BasePoint;3:InternalCoordinates
    options.WallAndColumnSplitting = ifc_options["SplitWallsAndColumns"]
    print_option(ifc_options, "SplitWallsAndColumns")

    print("\tPhase : Default Phase")
    # Setting a phase can return an unknown error, this option has therefore been deactivated
    # PhaseName=doc.GetElement(ElementId(ifc_options["ActivePhaseId"]["IntegerValue"])).Name
    # options.AddOption("ActivePhase",PhaseName)

    print("\nAdditonal Content Tab")
    options.AddOption("VisibleElementsOfCurrentView", str(ifc_options["VisibleElementsOfCurrentView"]))
    print_option(ifc_options, "VisibleElementsOfCurrentView")

    options.AddOption("Export2DElements", str(ifc_options["Export2DElements"]))
    print_option(ifc_options, "Export2DElements")

    options.AddOption("ExportLinkedFiles", "true")
    print("\tExportLinkedFiles : True ")

    #print("\tExportLinkedFiles : False (True is disabled using this tool)")
    # True doesn't work. It would be necessary to use OpenInBackground method.
    options.AddOption("ExportRoomsInView", str(ifc_options["ExportRoomsInView"]))
    print_option(ifc_options, "ExportRoomsInView")

    # True doesn't work. It would be necessary to use OpenInBackground method.

    print("\nProperty Sets Tab")
    options.AddOption("ExportInternalRevitPropertySets", str(ifc_options["ExportInternalRevitPropertySets"]))
    print_option(ifc_options, "ExportInternalRevitPropertySets")
    options.AddOption("ExportIFCCommonPropertySets", str(ifc_options["ExportIFCCommonPropertySets"]))
    print_option(ifc_options, "ExportIFCCommonPropertySets")
    options.ExportBaseQuantities = ifc_options["ExportBaseQuantities"]
    print_option(ifc_options, "ExportBaseQuantities")
    options.AddOption("ExportSchedulesAsPsets", str(ifc_options["ExportSchedulesAsPsets"]))
    print_option(ifc_options, "ExportSchedulesAsPsets")
    options.AddOption("ExportSpecificSchedules", str(ifc_options["ExportSpecificSchedules"]))
    print_option(ifc_options, "ExportSpecificSchedules")
    options.AddOption("ExportUserDefinedPsets", str(ifc_options["ExportUserDefinedPsets"]))
    print_option(ifc_options, "ExportUserDefinedPsets")
    psetsfile=ifc_options["ExportUserDefinedPsetsFileName"]
    options.AddOption("ExportUserDefinedPsetsFileName",psetsfile)
    if not os.path.exists(psetsfile):
        pyrevit.forms.alert("The path of the User Defined Psets file in the Json is not valid",exitscript=True)
    print("\tExportUserDefinedPsetsFileName : "+ifc_options["ExportUserDefinedPsetsFileName"])
    options.AddOption("ExportUserDefinedParameterMapping", str(ifc_options["ExportUserDefinedParameterMapping"]))
    print_option(ifc_options, "ExportUserDefinedParameterMapping")
    options.AddOption("ExportUserDefinedParameterMappingFileName",ifc_options["ExportUserDefinedParameterMappingFileName"])
    print("\tExportUserDefinedParameterMappingFileName : "+ifc_options["ExportUserDefinedParameterMappingFileName"])

    print("\nLevel of Detail Tab")
    options.AddOption("TessellationLevelOfDetail", str(ifc_options["TessellationLevelOfDetail"]))
    print("\tTessellationLevelOfDetail : "+str(ifc_options["TessellationLevelOfDetail"]))

    print("\nAdvanced Tab")
    options.AddOption("ExportPartsAsBuildingElements", str(ifc_options["ExportPartsAsBuildingElements"]))
    print_option(ifc_options, "ExportPartsAsBuildingElements")
    options.AddOption("ExportSolidModelRep", str(ifc_options["ExportSolidModelRep"]))
    print_option(ifc_options, "ExportSolidModelRep")
    options.AddOption("UseActiveViewGeometry", str(ifc_options["UseActiveViewGeometry"]))
    print_option(ifc_options, "UseActiveViewGeometry")
    options.AddOption("Use2DRoomBoundaryForVolume", str(ifc_options["Use2DRoomBoundaryForVolume"]))
    print_option(ifc_options, "Use2DRoomBoundaryForVolume")
    options.AddOption("UseFamilyAndTypeNameForReference", str(ifc_options["UseFamilyAndTypeNameForReference"]))
    print_option(ifc_options, "UseFamilyAndTypeNameForReference")
    options.AddOption("ExportBoundingBox", str(ifc_options["ExportBoundingBox"]))
    print_option(ifc_options, "ExportBoundingBox")
    options.AddOption("IncludeSiteElevation", str(ifc_options["IncludeSiteElevation"]))
    print_option(ifc_options, "IncludeSiteElevation")
    options.AddOption("StoreIFCGUID", str(ifc_options["StoreIFCGUID"]))
    print_option(ifc_options, "StoreIFCGUID")

    return options


def SaveAsWorksharedFile(doc, fullFileName):
    result = True
    try:
        workSharingSaveAsOption = WorksharingSaveAsOptions()
        workSharingSaveAsOption.OpenWorksetsDefault = SimpleWorksetConfiguration.AskUserToSpecify
        workSharingSaveAsOption.SaveAsCentral = True
        saveOption = SaveAsOptions()
        saveOption.OverwriteExistingFile = True
        saveOption.SetWorksharingOptions(workSharingSaveAsOption)
        saveOption.MaximumBackups = 2
        saveOption.Compact = True
        doc.SaveAs(fullFileName, saveOption)
    except Exception:
        result = False
    return result


def SyncFile(doc, compactCentralFile=False):
    returnvalue = True
    # set up sync settings
    ro = RelinquishOptions(True)
    transActOptions = TransactWithCentralOptions()
    sync = SynchronizeWithCentralOptions()
    sync.Comment = 'Synchronised by Revit Batch Processor'
    sync.Compact = compactCentralFile
    sync.SetRelinquishOptions(ro)
    # Synch it
    try:
        # save local first ( this seems to prevent intermittend crash on sync(?))
        doc.Save()
        doc.SynchronizeWithCentral(transActOptions, sync)
        # relinquish all
        WorksharingUtils.RelinquishOwnership(doc, ro, transActOptions)
    except Exception as e:
        returnvalue = False
    return returnvalue


def getsubcategories(item):
    if hasattr(item, 'SubCategories'):
        return [x for x in item.SubCategories]
    else:
        return []

class NoActiveDocWindow(Windows.Window):

    def __init__(self,prev_wind):
        wpf.LoadComponent(self, nooactivedoc_ui_file)
        self.RunBatchIFCExport = False
        self.isclosed=False
        if prev_wind :
            try :
                self.RVTfilePaths.Text="\n".join(prev_wind["rvt_file_paths"])
                self.rvt_file_paths = prev_wind["rvt_file_paths"]
            except:
                pass
            self.IFCMappingFilePath.Text=prev_wind["ifc_mapping_file_path"]
            self.ifc_mapping_file_path=prev_wind["ifc_mapping_file_path"]
            self.JsonFilePath.Text=prev_wind["Json_file_path"]
            self.Json_file_path=prev_wind["Json_file_path"]
            self.OutputFolderPath.Text=prev_wind["Output_folder_path"]
            self.Output_folder_path=prev_wind["Output_folder_path"]

    def RVTFileButton_Click(self, sender, args):
        openFileDlg = OpenFileDialog()
        openFileDlg.Multiselect = True
        if openFileDlg.ShowDialog():
            self.rvt_file_paths = openFileDlg.FileNames
            self.RVTfilePaths.Text = "\n".join(self.rvt_file_paths)

    def IFCMappingFileButton_Click(self, sender, args):
        openFileDlg = OpenFileDialog()
        if openFileDlg.ShowDialog():
            self.IFCMappingFilePath.Text = openFileDlg.FileName

    def JSONFileButton_Click(self, sender, args):
        openFileDlg = OpenFileDialog()
        if openFileDlg.ShowDialog():
            self.JsonFilePath.Text = openFileDlg.FileName

    def OutputFolder_Click(self, sender, args):
        openFolderDlg = CommonOpenFileDialog()
        openFolderDlg.IsFolderPicker = True
        if openFolderDlg.ShowDialog():
            self.OutputFolderPath.Text = openFolderDlg.FileName

    def RunBatchIFCExport_Click(self, sender, args):
        self.Output_folder_path = self.OutputFolderPath.Text
        self.Json_file_path=self.JsonFilePath.Text
        self.ifc_mapping_file_path = self.IFCMappingFilePath.Text
        self.Close()
        self.RunBatchIFCExport = True

    def WindowClosed(self, sender, args):
        self.isclosed=True

class ActiveDoc_Window(Windows.Window):
    def __init__(self,prev_wind):
        wpf.LoadComponent(self, activedoc_ui_file)
        self.RunBatchIFCExport = False
        self.isclosed=False
        if prev_wind :
            self.IFCMappingFilePath.Text=prev_wind["ifc_mapping_file_path"]
            self.ifc_mapping_file_path=prev_wind["ifc_mapping_file_path"]
            self.JsonFilePath.Text=prev_wind["Json_file_path"]
            self.Json_file_path=prev_wind["Json_file_path"]
            self.OutputFolderPath.Text=prev_wind["Output_folder_path"]
            self.Output_folder_path=prev_wind["Output_folder_path"]

    def IFCMappingFileButton_Click(self, sender, args):
        openFileDlg = OpenFileDialog()
        if openFileDlg.ShowDialog():
            self.ifc_mapping_file_path = openFileDlg.FileName
            self.IFCMappingFilePath.Text = self.ifc_mapping_file_path

    def JSONFileButton_Click(self, sender, args):
        openFileDlg = OpenFileDialog()
        if openFileDlg.ShowDialog():
            self.Json_file_path = openFileDlg.FileName
            self.JsonFilePath.Text = self.Json_file_path

    def OutputFolder_Click(self, sender, args):
        openFolderDlg = CommonOpenFileDialog()
        openFolderDlg.IsFolderPicker = True
        if openFolderDlg.ShowDialog():
            self.Output_folder_path = openFolderDlg.FileName
            self.OutputFolderPath.Text = self.Output_folder_path

    def RunBatchIFCExport_Click(self, sender, args):
        self.Close()
        self.RunBatchIFCExport = True

    def WindowClosed(self, sender, args):
        self.isclosed=True

#Export ifc of document
def IfcExport(doc):

    print("\n"+"Starting export of file : "+name+".rvt"+"\n")

    # Get all 3D views types in order to get default 3d view type
    viewtypes = FilteredElementCollector(doc).OfClass(ViewFamilyType)
    _3dviewtypes = []
    for elem in viewtypes:
        if elem.ViewFamily == ViewFamily.ThreeDimensional:
            _3dviewtypes.append(elem)

    # Find all views containing 'IFC' in them
    exportviews = []
    Default_export_view = None
    views = FilteredElementCollector(doc).OfCategory(
        BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
    for i in views:
        if i.ViewType == ViewType.ThreeD and 'IFC' in i.Name:
            exportviews.append(i)
        if i.ViewType == ViewType.ThreeD and i.Name == 'IFC Default':
            Default_export_view = i

    # If there are views to export (view with IFC in their name) then an IFC is exported for each of these views
    if exportviews:
        for i in exportviews:
            options.FilterViewId = i.Id
            viewname = i.Name
            t_IFC_Export = Transaction(doc, 'Export IFC')
            t_IFC_Export.Start()
            c = doc.Export(ifc_folder, name + "_" + viewname, options)
            t_IFC_Export.Commit()
            if c:
                print("\n"+"IFC Exported from 3D View: "+viewname)
                print("Exported File : "+name+"_"+viewname+".ifc")
                print("Folder : "+ifc_folder)
            else:
                print("Error during export of file " +
                name+".rvt using view "+viewname)

    if Default_export_view is None:
        # Get specific subcategories AREP in order to hide them
        catnames = [BuiltInCategory.OST_CommunicationDevices, BuiltInCategory.OST_PlumbingFixtures, BuiltInCategory.OST_SecurityDevices,
                    BuiltInCategory.OST_SpecialityEquipment, BuiltInCategory.OST_Casework, BuiltInCategory.OST_Furniture, BuiltInCategory.OST_GenericModel, BuiltInCategory.OST_Doors]
        _getSpecificCategories = [Category.GetCategory(doc, i) for i in catnames]
        _getSubCategories = map(lambda x: getsubcategories(x), _getSpecificCategories)
        _getSpecificSubCategories = [s for s in [g for h in _getSubCategories for g in h] if 'ESPACE' in s.Name or 'MASSIF' in s.Name or 'TEXTE' in s.Name]

        # Change detail level of 3D to Fine for categories Pipes and Pipe Fittings
        cats_Fine_Detail = [
            BuiltInCategory.OST_PipeCurves, BuiltInCategory.OST_PipeFitting]
        get_cats_fine_detail = [Category.GetCategory(
            doc, i) for i in cats_Fine_Detail]
        ogs = OverrideGraphicSettings()
        ogs.SetDetailLevel(ViewDetailLevel.Fine)

        # Create new 3d view with medium detail level
        t_new_view = Transaction(doc, 'Create new 3D view')
        t_new_view.Start()
        new3dview = View3D.CreateIsometric(doc, _3dviewtypes[0].Id)
        new3dview.DetailLevel = ViewDetailLevel.Medium
        new3dview.Name = "IFC Default"
        print("\nView created : IFC Default")

        # Hide specific AREP subcategories in view
        for i in _getSpecificSubCategories:
            try: new3dview.SetCategoryHidden(i.Id, True)
            except: pass

        # Apply Fine Detail Level for categories Pipe Fitting and Pipe Curves to new 3D view
        for v in get_cats_fine_detail:
            new3dview.SetCategoryOverrides(v.Id, ogs)
        t_new_view.Commit()

        # Export IFC using new 3d view
        options.FilterViewId = new3dview.Id
        t_IFC_Export = Transaction(doc, 'Export IFC')
        t_IFC_Export.Start()
        c = doc.Export(ifc_folder, name, options)
        t_IFC_Export.Commit()
        if c:
            print("\n"+"DefaultIFCExport. Exported File: "+name+".ifc")
            print("Folder : "+ifc_folder)
        else:
            print("Error during export of file "+name + ".rvt")

#   __  __      _      ___   _   _
#  |  \/  |    / \    |_ _| | \ | |
#  | |\/| |   / _ \    | |  |  \| |
#  | |  | |  / ___ \   | |  | |\  |
#  |_|  |_| /_/   \_\ |___| |_| \_|
# =========================================================

#Check if there is an open document
try :
    doc = __revit__.ActiveUIDocument.Document
    activedoc=True
    doc_list=[doc]
except :
    activedoc=False

#If the script has already been run, then load the previous input filepaths from the json file. The inputs will later be shown in the wpf window
json_file=script.get_universal_data_file('PreviousInputs','json',True)
try:
    with open(json_file,'r') as f:
        prev_wind=json.load(f)
except:
    prev_wind={}


#If a document is already opened then open the activedoc window
if activedoc :

    #Open wpf window with the previous input filepaths
    active_doc_window = ActiveDoc_Window(prev_wind)
    active_doc_window.ShowDialog()

    #If the 'run batch ifc export' button was selected
    if active_doc_window.RunBatchIFCExport:

        #retrieve the inputs and store them in variables
        Config_json = active_doc_window.Json_file_path
        output_folder = active_doc_window.Output_folder_path
        ifc_mapping_file_path = active_doc_window.ifc_mapping_file_path

        inputs= {"Json_file_path" : Config_json,
        "Output_folder_path": output_folder,
        "ifc_mapping_file_path": ifc_mapping_file_path}

        #Export the inputs to the previous inputs json for new time
        out_file=open(json_file,"w")
        jsonstring=json.dumps(inputs,ensure_ascii=False)
        out_file.write(jsonstring)
        out_file.close()

    #If the window was closed by the user then stop the script and show a dialog
    if active_doc_window.isclosed and not active_doc_window.RunBatchIFCExport:
        script.exit()

#If there is no active document then open the noactivedoc window
else :
    noactivedoc_window = NoActiveDocWindow(prev_wind)
    noactivedoc_window.ShowDialog()

    if noactivedoc_window.RunBatchIFCExport:

        doc_list = noactivedoc_window.rvt_file_paths
        Config_json = noactivedoc_window.Json_file_path
        output_folder = noactivedoc_window.Output_folder_path
        ifc_mapping_file_path = noactivedoc_window.ifc_mapping_file_path

        inputs={"Json_file_path" : Config_json,
        "Output_folder_path":output_folder,
        'rvt_file_paths': [i for i in doc_list],
        "ifc_mapping_file_path":ifc_mapping_file_path}

        out_file=open(json_file,"w")
        jsonstring=json.dumps(inputs,ensure_ascii=False)
        out_file.write(jsonstring)
        out_file.close()

    #If the window was closed by the user then stop the script and show a dialog
    # if noactivedoc_window.isclosed and not noactivedoc_window.RunBatchIFCExport:
    #     script.exit()

#If the file is a json file then the load options. If not end execution
json_file_extension=os.path.splitext(Config_json)[-1].lower()
if json_file_extension=='.json':
    f=io.open(Config_json,mode='r', encoding='utf-8')
    ifc_options = json.loads(f.read())
    f.close()
else :
    pyrevit.forms.alert('Json configuration file is not a Json file')
    script.exit()

#create output folder if the folder does not exist
ifc_folder = output_folder+"\\IFC"
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

#create Ifc folder in the output folder the folder does not exist
if not os.path.exists(ifc_folder):
    os.mkdir(ifc_folder)

# Import options from json
options = import_options_fromjson(ifc_options)
options.FamilyMappingFile = ifc_mapping_file_path
print('\nIFC Mapping File : ' + ifc_mapping_file_path+"\n")

if activedoc :
    name = doc.Title.replace('.rvt', '').replace('_détaché', "")
    IfcExport(doc)
else :
    for doc_path in doc_list:
        # Open doc

        doc = rw.open_doc(doc_path)
        name = doc.Title.replace('.rvt', '').replace('_détaché', "")

        IfcExport(doc)

        rw.close_doc(doc)

# # Get the file path of this python script
# src_file_path = inspect.getfile(lambda: None)

# # Copy the IFC Mapping txt file and the UserDefinedPsets File to the "ifcexportsettings" folder in the output folder
# ifcexportsettingsfolder = output_folder+"\\ifcexportsettings"
# if not os.path.exists(ifcexportsettingsfolder):
#     os.mkdir(ifcexportsettingsfolder)
# copy2(ifc_mapping_file_path, ifcexportsettingsfolder)
# copy2(ifc_options["ExportUserDefinedPsetsFileName"],ifcexportsettingsfolder)
# copy2(Config_json, ifcexportsettingsfolder)

# # Copy the list of the exported files to a txt file named exportedfiles.txt in the ifcexportsettings folder
# if not activedoc:
#     exportdata_path = ifcexportsettingsfolder+"\\exportedfiles.txt"
#     with open(exportdata_path, "a") as file:
#         file.write('Time :'+str(datetime.now())+"\n")
#         for doc_path in doc_list:
#             file.write("Exported file : "+doc_path+"\n")
#             file.write('IFC exported to'+ifc_folder+"\\"+name+".ifc"+"\n")
#         file.close()
