#!/usr/bin/python
# -*- coding: latin-1 -*-

from pyrevit import HOST_APP
from Autodesk.Revit import DB
from Autodesk.Revit.DB import Transaction

def ifc_export_options():
    options = DB.IFCExportOptions()
    options.FileVersion = DB.IFCVersion.IFC2x3CV2
    options.AddOption("SitePlacement", "0")
    # 0:SharedCoordinates;1:SurveyPoint;2:BasePoint;3:InternalCoordinates
    options.WallAndColumnSplitting = False
    options.AddOption("VisibleElementsOfCurrentView", "false")
    options.AddOption("ExportLinkedFiles", "false")
    # options.AddOption("ExportRoomsInView", "false")
    options.AddOption("ExportInternalRevitPropertySets", "true")
    options.AddOption("ExportIFCCommonPropertySets", "true")
    options.ExportBaseQuantities = True
    options.AddOption("ExportSchedulesAsPsets", 'false')
    options.AddOption("ExportSpecificSchedules", 'false')
    options.AddOption("ExportUserDefinedPsets", 'false')
    # options.AddOption("ExportUserDefinedPsetsFileName",psetsfile)
    # options.AddOption("ExportUserDefinedParameterMapping", str(ifc_options["ExportUserDefinedParameterMapping"]))
    # options.AddOption("ExportUserDefinedParameterMappingFileName",ifc_options["ExportUserDefinedParameterMappingFileName"])
    # options.AddOption("TessellationLevelOfDetail", 0.5)
    # options.AddOption("ExportPartsAsBuildingElements", 'false')
    # options.AddOption("ExportSolidModelRep", 'false')
    # options.AddOption("UseActiveViewGeometry", 'false')
    # options.AddOption("Use2DRoomBoundaryForVolume", str(ifc_options["Use2DRoomBoundaryForVolume"]))
    # options.AddOption("UseFamilyAndTypeNameForReference", str(ifc_options["UseFamilyAndTypeNameForReference"]))
    # options.AddOption("ExportBoundingBox", str(ifc_options["ExportBoundingBox"]))
    options.AddOption("IncludeSiteElevation", 'true')
    # options.AddOption("StoreIFCGUID", 'false')

    return options

def IfcExport(doc, options,ifc_folder):
    name = doc.Title.replace('.rvt', '').replace('_détaché', "")
    print("\n"+"Starting export of file : "+doc.Title+".rvt"+"\n")
    t_IFC_Export = Transaction(doc, 'Export IFC')
    t_IFC_Export.Start()
    c = doc.Export(ifc_folder, name, options)
    if c:
        print("Exported  IFC File : "+name+".ifc")
        print("Folder : "+ifc_folder)
    else:
        print("Error during export of file " +name+".rvt")
    t_IFC_Export.Commit()

server_name = "SRV-PARIS"
detach_from_central = True
file_paths = [  
    "3948_THAL_CHOL_MIXT/3948-PAT-ARC-MAQ-P&I-1910.rvt",
    "3948_THAL_CHOL_MIXT/3948-PAT-ARC-MAQ-R&D-1910.rvt",
    "3948_THAL_CHOL_MIXT/3948-PAT-ARC-MAQ-RES-1910.rvt",
    "3948_THAL_CHOL_MIXT/3948-PAT-ARC-MAQ-SIT-1910.rvt",
    "3948_THAL_CHOL_MIXT/3948-PAT-ARC-MAQ-CH2-1910.rvt",
    "3948_THAL_CHOL_MIXT/3948-PAT-CVC-MAQ-P&I-1930.rvt",
    "3948_THAL_CHOL_MIXT/3948-PAT-CVC-MAQ-R&D-1930.rvt",                
    "3948_THAL_CHOL_MIXT/3948-PAT-CVC-MAQ-RES-1930.rvt",                
    "3948_THAL_CHOL_MIXT/3948-PAT-ELE-MAQ-P&I-1940.rvt",                
    "3948_THAL_CHOL_MIXT/3948-PAT-ELE-MAQ-R&D-1940.rvt",                
    "3948_THAL_CHOL_MIXT/3948-PAT-ELE-MAQ-RES-1940.rvt",                
    "3948_THAL_CHOL_MIXT/3948-PAT-ELE-MAQ-A01-1960.rvt",                
    "3948_THAL_CHOL_MIXT/3948-PAT-STR-MAQ-P&I-1920.rvt",                
    "3948_THAL_CHOL_MIXT/3948-PAT-STR-MAQ-R&D-1920.rvt",                
    "3948_THAL_CHOL_MIXT/3948-PAT-STR-MAQ-RES-1920.rvt"
            ]

ifc_folder = "C:\\Users\\t.cosse\\Documents\\Affaires\\3948-THAL_CHOL_MIXT\\IFC"


for file_path in file_paths:
    model_path = DB.ServerPath(server_name, file_path)
    open_options = DB.OpenOptions()
    if detach_from_central:
        open_options.DetachFromCentralOption = DB.DetachFromCentralOption.DetachAndPreserveWorksets
    open_options.SetOpenWorksetsDefault(DB.WorksetConfiguration(DB.WorksetConfigurationOption.OpenAllWorksets))  # OpenAllWorksets, CloseAllWorksets or OpenLastViewed available
    doc = HOST_APP.app.OpenDocumentFile(model_path,open_options)
    IfcExport(doc,ifc_export_options(),ifc_folder)
    doc.Close(False)
