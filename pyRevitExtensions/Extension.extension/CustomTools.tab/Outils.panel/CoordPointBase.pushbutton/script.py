__title__="""Model Coordinates"""
__doc__="""T"""

import clr
clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from math import pi
from Autodesk.Revit import DB

app = __revit__.Application 
docs=app.Documents

active_docs=[]

for d in docs :
    if not d.IsLinked : 
        active_docs.append(d)

for doc in active_docs :
    
    print("\nFile : "+doc.Title)

    basepoint=DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ProjectBasePoint).WhereElementIsNotElementType().ToElements()[0]
    internal_origin=DB.FilteredElementCollector(doc).OfClass(DB.InternalOrigin).WhereElementIsNotElementType().ToElements()[0]
    survey_point=DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_SharedBasePoint).WhereElementIsNotElementType().ToElements()[0]
    
    #1 foot = 0.3048m
    foot2meter=0.3048
    bp_coord_x=basepoint.get_Parameter(DB.BuiltInParameter.BASEPOINT_EASTWEST_PARAM).AsDouble()*foot2meter
    bp_coord_y=basepoint.get_Parameter(DB.BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM).AsDouble()*foot2meter
    bp_coord_z=basepoint.get_Parameter(DB.BuiltInParameter.BASEPOINT_ELEVATION_PARAM).AsDouble()*foot2meter

    north_angle_rad=basepoint.get_Parameter(DB.BuiltInParameter.BASEPOINT_ANGLETON_PARAM).AsDouble()
    north_angle_deg=180*north_angle_rad/pi

    sp_coord_x=survey_point.get_Parameter(DB.BuiltInParameter.BASEPOINT_EASTWEST_PARAM).AsDouble()*foot2meter
    sp_coord_y=survey_point.get_Parameter(DB.BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM).AsDouble()*foot2meter
    sp_coord_z=basepoint.get_Parameter(DB.BuiltInParameter.BASEPOINT_ELEVATION_PARAM).AsDouble()*foot2meter

    print("North angle : {}".format(north_angle_deg))

    print("Base Point Coordinates : ")
    print("\tX : {}".format(bp_coord_x))
    print("\tY : {}".format(bp_coord_y))
    print("\tZ : {}".format(bp_coord_z))

    coord_internal_origin=internal_origin.SharedPosition
    internal_origin_coord_x=coord_internal_origin[0]*foot2meter
    internal_origin_coord_y=coord_internal_origin[1]*foot2meter
    internal_origin_coord_z=coord_internal_origin[2]*foot2meter

    if bp_coord_x==internal_origin_coord_x and bp_coord_y==internal_origin_coord_y and bp_coord_z==internal_origin_coord_z :
        print("Base Point and Internal Origin coordinates identical") 
    else : 
        print("\nOrigin Shared Coordinates : ")
        print("\tX : {}".format(internal_origin_coord_x))
        print("\tY : {}".format(internal_origin_coord_y))
        print("\tZ : {}".format(internal_origin_coord_z))

    if sp_coord_x==0 and sp_coord_y==0 and sp_coord_z==0 : 
        print("Survey Point is at 0,0,0")
    else : 
        print("Survey Point not on 0,0,0. Survey Point Shared Coordinates : ")
        print("\tX : {}".format(sp_coord_x))
        print("\tY : {}".format(sp_coord_y))
        print("\tZ : {}".format(sp_coord_z))
