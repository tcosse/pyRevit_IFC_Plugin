#!/usr/bin/python
# -*- coding: latin-1 -*-

__title__="Get Latitude and Longitude"
__doc__="""Prints Latitude and Longitude of model in degrees"""

from Autodesk.Revit import DB
from math import pi

doc = __revit__.ActiveUIDocument.Document

loc=doc.SiteLocation

lat=loc.Latitude*180/pi
long=loc.Longitude*180/pi

print("Latitude : "+str(lat)+" degrees")
print("Longitude "+str(long)+" degrees")