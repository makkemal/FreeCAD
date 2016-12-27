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

__title__ = "Cfd Result Control Task Panel"
__author__ = "Juergen Riegel, Qingfeng Xia"
__url__ = "http://www.freecadweb.org"

import os.path

import FreeCAD
import FemTools
import CfdTools
import numpy as np

if FreeCAD.GuiUp:
    import FreeCADGui
    import FemGui
    from PySide import QtCore, QtGui
    from PySide.QtCore import Qt
    from PySide.QtGui import QApplication


class _TaskPanelCfdResult:
    '''The task panel for the post-processing'''
    def __init__(self):
        ui_path = os.path.dirname(__file__) + os.path.sep + "TaskPanelCfdResult.ui"
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)
        self.fem_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Fem")
        self.restore_result_settings_in_dialog = self.fem_prefs.GetBool("RestoreResultDialog", True)

        # Connect Signals and Slots
        QtCore.QObject.connect(self.form.rb_none, QtCore.SIGNAL("toggled(bool)"), self.none_selected)
        QtCore.QObject.connect(self.form.rb_x_velocity, QtCore.SIGNAL("toggled(bool)"), self.x_velocity_selected)
        QtCore.QObject.connect(self.form.rb_y_velocity, QtCore.SIGNAL("toggled(bool)"), self.y_velocity_selected)
        QtCore.QObject.connect(self.form.rb_z_velocity, QtCore.SIGNAL("toggled(bool)"), self.z_velocity_selected)
        QtCore.QObject.connect(self.form.rb_mag_velocity, QtCore.SIGNAL("toggled(bool)"), self.mag_velocity_selected)
        QtCore.QObject.connect(self.form.rb_pressure, QtCore.SIGNAL("toggled(bool)"), self.pressure_selected)
        QtCore.QObject.connect(self.form.rb_temperature, QtCore.SIGNAL("toggled(bool)"), self.temperature_selected)

        #
        """
        # could be remove later if vector displacement will not be implemented
        #QtCore.QObject.connect(self.form.user_def_eq, QtCore.SIGNAL("textchanged()"), self.user_defined_text)
        QtCore.QObject.connect(self.form.calculate, QtCore.SIGNAL("clicked()"), self.calculate)
        QtCore.QObject.connect(self.form.cb_show_velocity, QtCore.SIGNAL("clicked(bool)"), self.show_velocity)
        QtCore.QObject.connect(self.form.hsb_velocity_factor, QtCore.SIGNAL("valueChanged(int)"), self.hsb_vel_factor_changed)
        QtCore.QObject.connect(self.form.sb_velocity_factor, QtCore.SIGNAL("valueChanged(int)"), self.sb_vel_factor_changed)
        QtCore.QObject.connect(self.form.sb_velocity_factor_max, QtCore.SIGNAL("valueChanged(int)"), self.sb_vel_factor_max_changed)
        """
        self.update()
        if self.restore_result_settings_in_dialog:
            self.restore_result_dialog()
        else:
            self.restore_initial_result_dialog()

    def restore_result_dialog(self):
        try:
            rt = FreeCAD.FEM_dialog["results_type"]
            if rt == "None":
                self.form.rb_none.setChecked(True)
                self.none_selected(True)
            elif rt == "Umag":
                self.form.rb_mag_velocity.setChecked(True)
                self.mag_velocity_selected(True)
                """
                elif rt == "Ux":
                    self.form.rb_x_velocity.setChecked(True)
                    self.x_velocity_selected(True)
                elif rt == "Uy":
                    self.form.rb_y_velocity.setChecked(True)
                    self.y_velocity_selected(True)
                elif rt == "Uz":
                    self.form.rb_z_velocity.setChecked(True)
                    self.z_velocity_selected(True)
                """
            elif rt == "Pressure":
                self.form.rb_pressure.setChecked(True)
                self.pressure_selected(True)
            elif rt == "Temperature":
                self.form.rb_temperature.setChecked(True)
                self.rb_temperature(True)
            elif rt == "TurbulenceViscosity":
                self.form.rb_turbulence_viscosity.setChecked(True)
                self.rb_turbulence_viscosity(True)
            elif rt == "TurbulenceEnergy":
                self.form.rb_turbulence_energy.setChecked(True)
                self.rb_turbulence_energy(True)
            elif rt == "DissipationRate":
                self.form.rb_turbulence_dissipation_rate.setChecked(True)
                self.rb_turbulence_dissipation_rate(True)
                """
                sd = FreeCAD.FEM_dialog["show_vel"]
                self.form.cb_show_velocity.setChecked(sd)
                self.show_velocity(sd)

                df = FreeCAD.FEM_dialog["vel_factor"]
                dfm = FreeCAD.FEM_dialog["vel_factor_max"]
                self.form.hsb_velocity_factor.setMaximum(dfm)
                self.form.hsb_velocity_factor.setValue(df)
                self.form.sb_velocity_factor_max.setValue(dfm)
                self.form.sb_velocity_factor.setValue(df)
                """
        except:
            self.restore_initial_result_dialog()

    def restore_initial_result_dialog(self):
        FreeCAD.FEM_dialog = {"results_type": "None", "show_vel": False,
                              "vel_factor": 0, "vel_factor_max": 100}
        fea = FemTools.FemTools()
        fea.reset_mesh_color()
        fea.reset_mesh_deformation()

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Close)

    def get_result_stats(self, type_name, analysis=None):
        if "Stats" in self.result_object.PropertiesList:
                Stats = self.result_object.Stats
                match_table = {"Ux": (Stats[0], Stats[1], Stats[2]),
                               "Uy": (Stats[3], Stats[4], Stats[5]),
                               "Uz": (Stats[6], Stats[7], Stats[8]),
                               "Umag": (Stats[9], Stats[10], Stats[11]),
                               "Pressure": (Stats[12], Stats[13], Stats[14]),
                               "Temperature": (Stats[15], Stats[16], Stats[17]),
                               "Turbulence": (Stats[18], Stats[19], Stats[20]),
                               "TurbulenceEnergyViscosity": (Stats[21], Stats[22], Stats[23]),
                               "TurbulenceDissipationRate": (Stats[24], Stats[25], Stats[26]),
                               "TurbulenceSpecificDissipation": (Stats[27], Stats[28], Stats[29]),
                               "None": (0.0, 0.0, 0.0)}
                return match_table[type_name]
        return (0.0, 0.0, 0.0)

    def none_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "None"
        self.set_result_stats("mm", 0.0, 0.0, 0.0)
        fea = FemTools.FemTools()
        fea.reset_mesh_color()

    def mag_velocity_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "Umag"
        self.select_velocity_type("Umag")

    def x_velocity_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "Ux"
        self.select_velocity_type("Ux")

    def y_velocity_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "Uy"
        self.select_velocity_type("Uy")

    def z_velocity_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "Uz"
        self.select_velocity_type("Uz")

    def pressure_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "Pressure"
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.suitable_results:
            self.MeshObject.ViewObject.setNodeColorByScalars(self.result_object.NodeNumbers, self.result_object.Pressure)
        (minm, avg, maxm) = self.get_result_stats("Pressure")
        self.set_result_stats("Pa", minm, avg, maxm)
        QtGui.qApp.restoreOverrideCursor()

    def temperature_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "Temperature"
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.suitable_results:
            self.MeshObject.ViewObject.setNodeColorByScalars(self.result_object.NodeNumbers, self.result_object.Temperature)
        minm = min(self.result_object.Temperature)
        avg = sum(self.result_object.Temperature) / len(self.result_object.Temperature)
        maxm = max(self.result_object.Temperature)
        self.set_result_stats("K", minm, avg, maxm)
        QtGui.qApp.restoreOverrideCursor()

    def turbulence_energy_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "TurbulenceEnergy"
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.suitable_results:
            self.MeshObject.ViewObject.setNodeColorByScalars(self.result_object.NodeNumbers, self.result_object.TurbulenceEnergy)
        (minm, avg, maxm) = self.get_result_stats("MTurbulenceEnergy")
        self.set_result_stats("Unit?", minm, avg, maxm)
        QtGui.qApp.restoreOverrideCursor()

    def turbulence_dissipation_rate_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "TurbulenceDissipationRate"
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.suitable_results:
            self.MeshObject.ViewObject.setNodeColorByScalars(self.result_object.NodeNumbers, self.result_object.TurbulenceDissipationRate)
        (minm, avg, maxm) = self.get_result_stats("TurbulenceDissipationRate")
        self.set_result_stats("Unit?", minm, avg, maxm)
        QtGui.qApp.restoreOverrideCursor()
    """
    def turbulence_dissipation_rate_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "TurbulenceSpecificDissipation"
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.suitable_results:
            self.MeshObject.ViewObject.setNodeColorByScalars(self.result_object.NodeNumbers, self.result_object.TurbulenceSpecificDissipation)
        (minm, avg, maxm) = self.get_result_stats("TurbulenceSpecificDissipation")
        self.set_result_stats("Unit?", minm, avg, maxm)
        QtGui.qApp.restoreOverrideCursor()
    """
    def turbulence_viscosity_selected(self, state):
        FreeCAD.FEM_dialog["results_type"] = "TurbulenceViscosity"
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.suitable_results:
            self.MeshObject.ViewObject.setNodeColorByScalars(self.result_object.NodeNumbers, self.result_object.TurbulenceViscosity)
        (minm, avg, maxm) = self.get_result_stats("TurbulenceViscosity")
        self.set_result_stats("Unit?", minm, avg, maxm)
        QtGui.qApp.restoreOverrideCursor()

    def user_defined_text(self, equation):
        FreeCAD.FEM_dialog["results_type"] = "user"
        self.form.user_def_eq.toPlainText()
    """
    def calculate(self):
        FreeCAD.FEM_dialog["results_type"] = "None"
        self.update()
        self.restore_result_dialog()
        # Convert existing values to numpy array
        P1 = np.array(self.result_object.PrincipalMax)
        P2 = np.array(self.result_object.PrincipalMed)
        P3 = np.array(self.result_object.PrincipalMin)

        p = np.array(self.result_object.StressValues)
        T = np.array(self.result_object.Temperature)
        vel_vectors = np.array(self.result_object.DisplacementVectors)
        Ux = np.array(vel_vectors[:, 0])
        Uy = np.array(vel_vectors[:, 1])
        Uz = np.array(vel_vectors[:, 2])

        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.suitable_results:
            self.MeshObject.ViewObject.setNodeColorByScalars(self.result_object.NodeNumbers, UserDefinedFormula)
        self.set_result_stats("", minm, avg, maxm)
        QtGui.qApp.restoreOverrideCursor()
    """
    def select_velocity_type(self, vel_type):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if vel_type == "Umag":
            if self.suitable_results:
                velMag = [v.Length for v in self.result_object.Velocity]
                self.MeshObject.ViewObject.setNodeColorByScalars(self.result_object.NodeNumbers, velMag)
        else:
            match = {"Ux": 0, "Uy": 1, "Uz": 2}
            d = zip(*self.result_object.Velocity)  # DisplacementVectors -> VelocityVectors
            velocity = list(d[match[vel_type]])
            if self.suitable_results:
                self.MeshObject.ViewObject.setNodeColorByScalars(self.result_object.NodeNumbers, velocity)
        (minm, avg, maxm) = self.get_result_stats(vel_type)
        self.set_result_stats("m/s", minm, avg, maxm)
        QtGui.qApp.restoreOverrideCursor()

    def set_result_stats(self, unit, minm, avg, maxm):
        self.form.le_min.setProperty("unit", unit)
        self.form.le_min.setText("{:.6} {}".format(minm, unit))
        self.form.le_avg.setProperty("unit", unit)
        self.form.le_avg.setText("{:.6} {}".format(avg, unit))
        self.form.le_max.setProperty("unit", unit)
        self.form.le_max.setText("{:.6} {}".format(maxm, unit))


    def update(self):
        self.MeshObject = None
        self.result_object = CfdTools.getResultObject()  # return the first one, or the currently selected result object
        # Disable temperature radio button if it does not exist in results
        if len(self.result_object.Temperature) == 1:
                self.form.rb_temperature.setEnabled(0)
        #
        for i in FemGui.getActiveAnalysis().Member:
            if i.isDerivedFrom("Fem::FemMeshObject"):
                self.MeshObject = i
                break

        self.suitable_results = False
        if self.result_object:
            if (self.MeshObject.FemMesh.NodeCount == len(self.result_object.NodeNumbers)):
                self.suitable_results = True
            else:
                if not self.MeshObject.FemMesh.VolumeCount:
                    FreeCAD.Console.PrintError('Only 3D FEM or CFD Meshes are supported!\n')
                else:
                    FreeCAD.Console.PrintError('Result node numbers are not equal to FEM Mesh NodeCount!\n')

    def accept(self):
        FreeCADGui.Control.closeDialog()

    def reject(self):
        FreeCADGui.Control.closeDialog()
