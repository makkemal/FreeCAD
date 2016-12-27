# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2013-2015 - Juergen Riegel <FreeCAD@juergen-riegel.net> *
# *   Portions Copyright (c) 2016 - CSIR, South Africa                      *
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

__title__ = "Command New Fluid Material"
__author__ = "Juergen Riegel, Alfred Bogaers"
__url__ = "http://www.freecadweb.org"

import FreeCAD
from FemCommands import FemCommands

if FreeCAD.GuiUp:
    import FreeCADGui
    import FemGui


class setFluidPropertyCommand(FemCommands):
    def __init__(self):
        # Neat little command from FemCommands to only activate when solver or analysis is active i.e. in this case OF
        #self.is_active = 'with_solver'
        self.is_active = 'with_analysis'

    def Activated(self):
        #selection = FreeCADGui.Selection.getSelectionEx()
        #selectedObj = FreeCADGui.Selection.getSelection()[0]

        FreeCAD.Console.PrintMessage("Set fluid properties \n")

        FreeCAD.ActiveDocument.openTransaction("Set FluidMaterialProperty")
        FreeCADGui.addModule("FluidMaterial")
        FreeCADGui.doCommand("FluidMaterial.makeFluidMaterial('FluidProperties')")

        # The CFD WB is still currently a member of FemGui
        FreeCADGui.doCommand("App.activeDocument()." + FemGui.getActiveAnalysis().Name + ".Member = App.activeDocument()." + FemGui.getActiveAnalysis().Name + ".Member + [App.ActiveDocument.ActiveObject]")
        FreeCADGui.doCommand("Gui.activeDocument().setEdit(App.ActiveDocument.ActiveObject.Name)")

    def GetResources(self):
        return \
            {
                'Pixmap': ':/icons/fem-material.svg',
                'MenuText': 'Add fluid properties',
                'ToolTip': 'Add fluid properties'
            }

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('setFluidProperties', setFluidPropertyCommand())
