# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2013-2015 - Juergen Riegel <FreeCAD@juergen-riegel.net> *
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

__title__ = "Command Prescribed Displacement"
__author__ = "Alfred Bogaers and Michael Hindley"
__url__ = "http://www.freecadweb.org"

import FreeCAD
from FemCommands import FemCommands

if FreeCAD.GuiUp:
    import FreeCADGui
    import FemGui

from PySide import QtGui
from PySide import QtCore

from _FemPrescribedDisplacement import _FemPrescribedDisplacement
from _TaskPanelFemPrescribedDisplacement import _TaskPanelFemPrescribedDisplacement
from _ViewProviderFemPrescribedDisplacement import _ViewProviderFemPrescribedDisplacement

class _CommandFemPrescribedDisplacement:
    def GetResources(self):
        return {'Pixmap': 'fem-constraint-displacement',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Fem_Prescribed_Displacement", "Create FEM prescribed displacement constraint"),
                'Accel': "C, D",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Fem_Prescribed_Displacement", "Create FEM prescribed displacement constraint")}

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create FEM prescribed displacement constraint")
        #FreeCADGui.addModule("FemGui")
        #sel = FreeCADGui.Selection.getSelection()

        feature=FreeCAD.ActiveDocument.findObjects("Part::Feature")[-1]

        selection = FreeCADGui.Selection.getSelectionEx()
        FreeCADGui.activeDocument().getObject("feature.Name")
        #FreeCAD.Console.PrintMessage("selection \n")
        #FreeCAD.Console.PrintMessage(str(selection) + " ")
        #FreeCAD.Console.PrintMessage(str(selection[0].SubElementNames) + " ")
        #FreeCAD.Console.PrintMessage(str(len(selection)) + " \n")
        
        #get list of analysis memebers
        members=FreeCAD.ActiveDocument.MechanicalAnalysis.Member

        for member in members:
            if "FemConstraintDisplacement" in  member.Name:  #If member is a displacement constraint 
                #Set active status for all members
                member.ViewObject.Visibility=True


        #check selection
        if len(selection) != 1 or (len(selection[0].SubElementNames)== 0):
            FreeCADGui.Selection.clearSelection()
            #FreeCAD.Console.PrintMessage("No selection \n")
            feature=FreeCAD.ActiveDocument.findObjects("Part::Feature")[-1]
            strcommand="FreeCAD.ActiveDocument."+feature.Name
            FreeCADGui.activeDocument().getObject("feature.Name")
            FreeCADGui.Selection.addSelection(eval(strcommand),"Vertex1")
            selection = FreeCADGui.Selection.getSelectionEx()
            FreeCADGui.doCommand("App.activeDocument().recompute()")


        # Assign displacement to selected geometry
        if len(selection) == 1 and selection[0].Object.isDerivedFrom("Part::Feature") and not (
                    "DisplacementSettings" in selection[0].Object.Content):

            subComponents = selection[0].SubElementNames
            mainObj = selection[0].ObjectName


            _FemPrescribedDisplacement()
            FreeCADGui.doCommand(
                "App.activeDocument()." + FemGui.getActiveAnalysis().Name + ".Member = App.activeDocument()." + FemGui.getActiveAnalysis().Name + ".Member + [App.ActiveDocument.ActiveObject]")

            FreeCADGui.doCommand("Gui.activeDocument().setEdit(App.ActiveDocument.ActiveObject.Name,0)")
            FreeCADGui.doCommand("App.activeDocument().recompute()")


        elif len(selection) == 1 and ("DisplacementSettings" in selection[0].Object.Content):
            selection = FreeCADGui.Selection.getSelectionEx()
            label = selection[0].Object.Label
            FreeCADGui.doCommand("Gui.activeDocument().setEdit('" + str(label) + "',0)")
            FreeCADGui.doCommand("App.activeDocument().recompute()")


    def execute():
        return 0

    def IsActive(self):
        if FemGui.getActiveAnalysis():
            return True
        else:
            return False


class _CommandFemPrescribedDisplacementEdit:
    def GetResources(self):
        return {'Pixmap': 'fem-constraint-displacement',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Fem_Prescribed_Displacement_Edit", "Edits a FEM prescribed displacement constraint"),
                'Accel': "C, D",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Fem_Prescribed_Displacement_Edit", "Edits a FEM prescribed displacement constraint")}

    def Activated(self):
        selection = FreeCADGui.Selection.getSelectionEx()
        label = selection[0].Object.Label
        FreeCADGui.doCommand("Gui.activeDocument().setEdit('" + str(label) + "',0)")

    def execute():
        return 0

    def IsActive(self):
        if FemGui.getActiveAnalysis():
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Fem_PrescribedDisp', _CommandFemPrescribedDisplacement())
    FreeCADGui.addCommand('Fem_PrescribedDispEdit', _CommandFemPrescribedDisplacementEdit())
