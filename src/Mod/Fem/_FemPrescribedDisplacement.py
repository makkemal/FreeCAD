#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2013-2015 - Juergen Riegel <FreeCAD@juergen-riegel.net> *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

__title__ = "Command Prescribed Displacement"
__author__ = "Alfred Bogaers and Michael Hindley"
__url__ = "http://www.freecadweb.org"

class _FemPrescribedDisplacement:

    # def __init__(self, obj,objectComponent):
    def __init__(self):
        import FreeCAD
        if FreeCAD.GuiUp:
           import FreeCADGui
           import FemGui
        from PySide import QtGui
        from PySide import QtCore
        from _ViewProviderFemPrescribedDisplacement import _ViewProviderFemPrescribedDisplacement

        selection = FreeCADGui.Selection.getSelectionEx()

        #obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "FemConstraintDisplacement")
        #obj = FreeCAD.ActiveDocument.addObject("Fem::FemSolverObjectPython", "FemConstraintDisplacement") 
        obj = FreeCAD.ActiveDocument.addObject("Fem::ConstraintPrescribedDisplacement", "FemConstraintDisplacement")
        
        
        
#        obj.addProperty("App::PropertyLink", "Object", "DisplacementSettings")
#        obj.addProperty("App::PropertyStringList", "partNameList", "DisplacementSettings")
        
        

        # Define variables used
#        obj.addProperty("App::PropertyFloat", "xDisplacement", "DisplacementSettings",
#                        "x Displacement").xDisplacement = 0.0
#        obj.addProperty("App::PropertyFloat", "yDisplacement", "DisplacementSettings",
#                        "y Displacement").yDisplacement = 0.0
#        obj.addProperty("App::PropertyFloat", "zDisplacement", "DisplacementSettings",
#                        "z Displacement").zDisplacement = 0.0
#        obj.addProperty("App::PropertyFloat", "xRotation", "DisplacementSettings", "x Rotation").xRotation = 0.0
#        obj.addProperty("App::PropertyFloat", "yRotation", "DisplacementSettings", "y Rotation").yRotation = 0.0
#        obj.addProperty("App::PropertyFloat", "zRotation", "DisplacementSettings", "z Rotation").zRotation = 0.0
#        obj.addProperty("App::PropertyBool", "xFree", "DisplacementSettings", "x Free").xFree = True
#        obj.addProperty("App::PropertyBool", "yFree", "DisplacementSettings", "y Free").yFree = True
#        obj.addProperty("App::PropertyBool", "zFree", "DisplacementSettings", "z Free").zFree = True
#        obj.addProperty("App::PropertyBool", "xFix", "DisplacementSettings", "x Fix").xFix = False
#        obj.addProperty("App::PropertyBool", "yFix", "DisplacementSettings", "y Fix").yFix = False
#        obj.addProperty("App::PropertyBool", "zFix", "DisplacementSettings", "z Fix").zFix = False
#        obj.addProperty("App::PropertyBool", "rotxFree", "DisplacementSettings", "rot x Free").rotxFree = True
#        obj.addProperty("App::PropertyBool", "rotyFree", "DisplacementSettings", "rot y Free").rotyFree = True
#        obj.addProperty("App::PropertyBool", "rotzFree", "DisplacementSettings", "rot z Free").rotzFree = True
#        obj.addProperty("App::PropertyBool", "rotxFix", "DisplacementSettings", "rot x Fix").rotxFix = False
#        obj.addProperty("App::PropertyBool", "rotyFix", "DisplacementSettings", "rot y Fix").rotyFix = False
#        obj.addProperty("App::PropertyBool", "rotzFix", "DisplacementSettings", "rot z Fix").rotzFix = False
#        obj.addProperty("App::PropertyBool", "element", "DisplacementSettings", "element").element = False

        # Define part settings
        # obj.addProperty("App::PropertyStringList","subPartLink","DisplacementSettings")
#        obj.addProperty("Part::PropertyPartShape", "Shape", "DisplacementSettings")
#
#        obj.Proxy = self
#
#        obj.setEditorMode("Object", 2)
#        obj.setEditorMode("partNameList", 1)
#        # obj.setEditorMode("subPartLink",2)
#        # obj.setEditorMode("Shape",0)
#        #Assume no object selected
#        partNameList = []
#        obj.partNameList = partNameList
#
#
#        objectComponent = selection[0]
#        subComponents = objectComponent.SubElementNames
#        for i in range(len(subComponents)):
#            partNameList.append(str(subComponents[i]))
#        obj.Object = objectComponent.Object
#
#        _ViewProviderFemPrescribedDisplacement(obj.ViewObject)


#    def execute(self, fp):
#        import Part
#        import Fem
#        import FemGui
#        listOfShapes = []
#        if len(fp.partNameList) >= 1:
#            for i in range(len(fp.partNameList)):
#                if fp.partNameList[i][0:4] == 'Face':
#                    ind = int(fp.partNameList[i][4::]) - 1
#                    listOfShapes.append(fp.Object.Shape.Faces[ind])
#                if fp.partNameList[i][0:4] == 'Edge':
#                    ind = int(fp.partNameList[i][4::]) - 1
#                    listOfShapes.append(fp.Object.Shape.Edges[ind])
#                if fp.partNameList[i][0:4] == "Vert":
#                    ind = int(fp.partNameList[i][6::]) - 1
#                    listOfShapes.append(fp.Object.Shape.Vertexes[ind])
#            if len(listOfShapes) > 0:
#               fp.Shape = Part.makeCompound(listOfShapes)
#            else:
#               fp.Shape = Part.Shape()
#
#        return
