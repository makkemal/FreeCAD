# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 - Markus Hovorka <m.hovorka@live.de>               *
# *   Copyright (c) 2018 - Bernd Hahnebach <bernd@bimstatik.org>            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************


__title__ = "FEM Utilities"
__author__ = "Markus Hovorka, Bernd Hahnebach"
__url__ = "http://www.freecadweb.org"


import FreeCAD
import FreeCAD as App


def createObject(doc, name, proxy, viewProxy):
    obj = doc.addObject(proxy.BaseType, name)
    proxy(obj)
    if App.GuiUp:
        viewProxy(obj.ViewObject)
    return obj


def findAnalysisOfMember(member):
    if member is None:
        raise ValueError("Member must not be None")
    for obj in member.Document.Objects:
        if obj.isDerivedFrom("Fem::FemAnalysis"):
            if member in obj.Group:
                return obj
            if _searchGroups(member, obj.Group):
                return obj
    return None


def _searchGroups(member, objs):
    for o in objs:
        if o == member:
            return True
        if hasattr(o, "Group"):
            return _searchGroups(member, o.Group)
    return False


def getMember(analysis, t):
    if analysis is None:
        raise ValueError("Analysis must not be None")
    matching = []
    for m in analysis.Group:
        if isDerivedFrom(m, t):
            matching.append(m)
    return matching


def getSingleMember(analysis, t):
    objs = getMember(analysis, t)
    return objs[0] if objs else None


def typeOfObj(obj):
    '''returns objects TypeId (C++ objects) or Proxy.Type (Python objects)'''
    if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type"):
        return obj.Proxy.Type
    return obj.TypeId


def isOfTypeNew(obj, ty):
    '''returns if an object is of a given TypeId (C++ objects) or Proxy.Type (Python objects)'''
    if typeOfObj(obj) == ty:
        return True
    else:
        return False


def isOfType(obj, t):
    if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type"):
        return obj.Proxy.Type == t
    return obj.TypeId == t


def isDerivedFrom(obj, t):
    if (hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and
            obj.Proxy.Type == t):
        return True
    return obj.isDerivedFrom(t)


def getBoundBoxOfAllDocumentShapes(doc):
    overalboundbox = None
    for o in doc.Objects:
        # netgen mesh obj has an attribute Shape which is an Document obj, which has no BB
        if hasattr(o, 'Shape') and hasattr(o.Shape, 'BoundBox'):
            try:
                bb = o.Shape.BoundBox
            except:
                bb = None
            if bb.isValid():
                if not overalboundbox:
                    overalboundbox = bb
                overalboundbox.add(bb)
    return overalboundbox


def getSelectedFace(selectionex):
    aFace = None
    # print(selectionex)
    if len(selectionex) != 1:
        FreeCAD.Console.PrintMessage('none OR more than one object selected')
    else:
        sel = selectionex[0]
        if len(sel.SubObjects) != 1:
            FreeCAD.Console.PrintMessage('more than one element selected')
        else:
            aFace = sel.SubObjects[0]
            if aFace.ShapeType != 'Face':
                FreeCAD.Console.PrintMessage('not a Face selected')
            else:
                FreeCAD.Console.PrintMessage(':-)')
                return aFace
    return aFace


class AddAutoContact(slope,friction):
    import FreeCADGui, FreeCAD 
    import numpy as np
    import femmesh.meshtools
    import FemGui
    import ObjectsFem
    locations = []
    locationsub = []
    objnames = []
    dicti = {}
    # Variables
    num = 0  # Number of nearest neigbours to be found 
    Slope = slope  # Contact stiffness
    Friction = friction  # Friction 
    Scale = 1  # Scale

    def find_index_of_nearest(array, idx,num ):
        xpoint=array[idx,0]
        ypoint=array[idx,1]
        zpoint=array[idx,2]
        distance = []
        for i in range(array.shape[0]):
            distance.append((array[i,0]-xpoint)**2 + (array[i,1]-ypoint)**2+ (array[i,2]-zpoint)**2)       
        idxmin = np.argpartition(np.array(distance), num)
        idxmin=np.array(idxmin[0:num])
        idxmin=np.delete(idxmin,np.where(idxmin==idx))  
        return idxmin
    
    def get_all_close_surfaces(array, num):
        store = []
        for i in range(array.shape[0]):
            store.append(find_index_of_nearest(array,i,num))    
        return store
    
    
    def addcontactobjects(array,geom):
        idxfaces=[]
        iidx=0
        idxi=0
        for i in array:
            for j in i:
                FreeCAD.activeDocument().addObject("Fem::ConstraintContact","FemConstraintContact")
                idxfaces=np.append(idxfaces,[iidx,j])
            iidx+=1
        idxfaces=idxfaces.reshape(int(len(idxfaces)/2),2)    
        #print(idxfaces.shape)
        for obj in FreeCAD.ActiveDocument.Objects:
            if (obj.isDerivedFrom('Fem::ConstraintContact')):
                objName = obj.Name
                #print(objName)
                obj.Slope = Slope
                obj.Friction = Friction
                obj.Scale = Scale
                face1='Face'+str(idxfaces[idxi,0]+1)
                #print(face1)
                face2='Face'+str(idxfaces[idxi,1]+1)
                #print(face2)
                obj.References = [(geom,face1), (geom,face2)]  
                idxi+=1
    
    def get_same_surfaces(mainarray,rowsub):
        indx=0
        for row in mainarray:
            if np.array_equal(row, rowsub):
                #print("Got it",row,rowsub,indx)
                idxr=indx
            indx+=1
        return idxr
    
    def multidelete(values,todelete):
       todelete=np.array(todelete)
       shift=np.triu((todelete>=todelete[:,None]),1).sum(0)
       return np.delete(values,todelete+shift)
    
    
    def remove_same_sol_face(array,locidx):
        rownew=[]
        newmat=[]
        #indx=0
        for i in range(array.shape[0]):
            solnum=locidx[i]
            toremove=np.array(np.where(locidx == solnum)[0])
            row=np.array(array[i,:])
            delistidx=[]
            for i in toremove:
                rownew = np.array(np.where(row==i)[0] )
                if len(rownew) >= 1:
                    delistidx=np.append(delistidx,rownew[0])
            delistidx=np.sort(delistidx)[::-1]    
            newrow=multidelete(row,delistidx)
            newmat.append(newrow)
        #print(newmat)
        return newmat
    
    
    try:
        for obj in FreeCAD.ActiveDocument.Objects:  # seach all objects in document
            objName = obj.Name
            objLabel = obj.Label
            try:
                if obj.Shape.Faces:  # is a face then
                    print( objLabel, objName, len(obj.Shape.Faces), " face(s)")
                    FreeCADGui.Selection.addSelection(FreeCAD.ActiveDocument.getObject(obj.Name))  # select the object with face
                    if 'Compound' in objName: 
                        print('Getting vector list for nearest neighbours contact form Compound \n ', objName)
                        objcomp=obj
                        for face in range(len(obj.Shape.Faces)):  # list the face(s) of object
    #                         print(face)
                             surfaceloc=np.array(obj.Shape.Faces[face].CenterOfMass)  # center point
                             locations.append(surfaceloc)
    #                        print(surfaceloc)                        
                             
                                                              
                    else:
                       print("No object found to apply contact ",objName)
                       locationsub = []
                       if len(obj.Shape.Faces) > num:
                           num = len(obj.Shape.Faces)
                       for face in range(len(obj.Shape.Faces)):  # list the face(s) of object
                           #print(face)
                           surfaceloc=np.array(obj.Shape.Faces[face].CenterOfMass)  # center point
                           locationsub.append(surfaceloc)
                       name= objName+'coords' 
                       dicti[str(name)] = np.array(locationsub) 
                       
            except Exception:
                print("Not Shape")
    except Exception:
        print("Not object")
    locations = np.array(locations)
    num=num+3 #select at least 3 more faces tahn biggest subobject has 
    results = np.array(get_all_close_surfaces(locations,num))
    #np.save("resultmat.npy",results)
    #print(results)
    #now subobjects
    idx=0
    locsub=np.zeros(len(locations))
    for key,val in dicti.items():
        for row in val:
             index=get_same_surfaces(locations,row)   
             locsub[index]=idx
        idx+=1     
    uniqueres=remove_same_sol_face(results,locsub)
    addcontactobjects(uniqueres,objcomp)    
