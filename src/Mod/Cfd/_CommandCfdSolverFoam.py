#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2015 - Qingfeng Xia <qingfeng.xia()eng.ox.ac.uk> *
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

__title__ = "Command to create CFD solver"
__author__ = "Qingfeng Xia"
__url__ = "http://www.freecadweb.org"


import FreeCAD
from FemCommands import FemCommands
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui

class _CommandSolverFoam(FemCommands):
    "Command to create OpenFOAM solver for CFD anlysis"
    def __init__(self):
        super(_CommandSolverFoam, self).__init__()
        self.resources = {'Pixmap': 'fem-solver',
                          'MenuText': QtCore.QT_TRANSLATE_NOOP("Fem_SolverFoam", "Create OpenFOAM solver"),
                          'Accel': "S, C",
                          'ToolTip': QtCore.QT_TRANSLATE_NOOP("Fem_SolverFoam", "Create OpenFOAM solver for CFD anlysis")}
        self.is_active = 'with_analysis'

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create OpenFOAM Solver")
        FreeCADGui.addModule("CfdSolverFoam")
        FreeCADGui.doCommand("FemGui.getActiveAnalysis().Member = FemGui.getActiveAnalysis().Member + [CfdSolverFoam.makeCfdSolverFoam()]")

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Fem_SolverFoam', _CommandSolverFoam())