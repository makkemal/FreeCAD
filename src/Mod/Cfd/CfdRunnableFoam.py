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

__title__ = "Classes for New CFD solver"
__author__ = "Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

import os.path

import FreeCAD

import CfdCaseWriterFoam
import CfdTools


class CfdRunnable(object):
    ##  run the solver and read the result, corresponding to FemTools class
    #  @param analysis - analysis object to be used as the core object.
    #  "__init__" tries to use current active analysis in analysis is left empty.
    #  Rises exception if analysis is not set and there is no active analysis
    #  The constructur of FemTools is for use of analysis without solver object
    def __init__(self, analysis=None, solver=None):
        if analysis and analysis.isDerivedFrom("Fem::FemAnalysisPython"):
            ## @var analysis
            #  FEM analysis - the core object. Has to be present.
            #  It's set to analysis passed in "__init__" or set to current active analysis by default if nothing has been passed to "__init__"
            self.analysis = analysis
        else:
            if FreeCAD.GuiUp:
                import FemGui
                self.analysis = FemGui.getActiveAnalysis()

        self.solver = None
        if solver and solver.isDerivedFrom("Fem::FemSolverObjectPython"):
            ## @var solver
            #  solver of the analysis. Used to store the active solver and analysis parameters
            self.solver = solver
        else:
            if analysis:
                self.solver = CfdTools.getSolver(self.analysis)
            if self.solver == None:
                FreeCAD.Console.printMessage("FemSolver object is missing from Analysis Object")

        if self.analysis:
            self.results_present = False
            self.result_object = None
        else:
            raise Exception('FEM: No active analysis found!')

    def check_prerequisites(self):
        return ""

    def edit_case(self):
        case_path = self.solver.WorkingDir + os.path.sep + self.solver.InputCaseName
        FreeCAD.Console.PrintMessage("Please edit the case input files externally at: {}".format(case_path))
        self.writer.builder.editCase()


#  Concrete Class for CfdRunnable for OpenFOAM
#  implemented write_case() and solver_case(), not yet for load_result()
class CfdRunnableFoam(CfdRunnable):
    def __init__(self, analysis=None, solver=None):
        super(CfdRunnableFoam, self).__init__(analysis, solver)
        self.writer = CfdCaseWriterFoam.CfdCaseWriterFoam(self.analysis)

    def check_prerequisites(self):
        return ""

    def write_case(self):
        return self.writer.write_case()

    def get_solver_cmd(self):
        cmd = self.writer.builder.getSolverCmd()
        FreeCAD.Console.PrintMessage("Please run the command in new terminal: \n" + cmd)
        return cmd

    def _view_result_externally(self):
        self.writer.builder.viewResult()

    def view_result(self):
        #  foamToVTK will write result into VTK data files
        #result = self.writer.builder.exportResult()
        result = "/home/qingfeng/Documents/TestCase/VTK/TestCase_345.vtk"
        from CfdResultFoamVTK import importVTK
        importVTK(result, self.analysis)

