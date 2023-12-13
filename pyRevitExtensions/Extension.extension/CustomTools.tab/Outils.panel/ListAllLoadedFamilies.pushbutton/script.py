import clr
clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from Autodesk.Revit import DB

app = __revit__.Application 
docs=app.Documents

active_docs=[]

for d in docs :
    if not d.IsLinked : 
        active_docs.append(d)

for doc in active_docs :
    
    print("\nFile : "+doc.Title)

    allfamilies=DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    
    for a in allfamilies : print(a.Name)
