# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2016 - Ofentse Kgoa <kgoaot@eskom.co.za>                *
# *   Based on the FemBeamSection by Bernd Hahnebach                        *
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

__title__ = "_TaskPanelFemFluidSection"
__author__ = "Ofentse Kgoa"
__url__ = "http://www.freecadweb.org"

## @package TaskPanelFemFluidSection
#  \ingroup FEM

import FreeCAD
import FreeCADGui
from PySide import QtGui
from PySide import QtCore
import _FemFluidSection


class _TaskPanelFemFluidSection:
    '''The TaskPanel for editing References property of FemFluidSection objects'''
    def __init__(self, obj):
        FreeCADGui.Selection.clearSelection()
        self.sel_server = None
        self.obj = obj

        self.form = FreeCADGui.PySideUic.loadUi(FreeCAD.getHomePath() + "Mod/Fem/TaskPanelFemFluidSection.ui")
        QtCore.QObject.connect(self.form.pushButton_Reference, QtCore.SIGNAL("clicked()"), self.add_references)
        QtCore.QObject.connect(self.form.cb_section_type, QtCore.SIGNAL("activated(int)"), self.sectiontype_changed)
        QtCore.QObject.connect(self.form.cb_liquid_section_type, QtCore.SIGNAL("activated(int)"), self.liquidsectiontype_changed)
        QtCore.QObject.connect(self.form.if_manning_area, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.manning_area_changed)
        QtCore.QObject.connect(self.form.if_manning_radius, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.manning_radius_changed)
        QtCore.QObject.connect(self.form.sb_manning_coefficient, QtCore.SIGNAL("valueChanged(double)"), self.manning_coefficient_changed)
        QtCore.QObject.connect(self.form.if_enlarge_area1, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.enlarge_area1_changed)
        QtCore.QObject.connect(self.form.if_enlarge_area2, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.enlarge_area2_changed)
        QtCore.QObject.connect(self.form.if_contract_area1, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.contract_area1_changed)
        QtCore.QObject.connect(self.form.if_contract_area2, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.contract_area2_changed)
        QtCore.QObject.connect(self.form.if_inletpressure, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.inlet_pressure_changed)
        QtCore.QObject.connect(self.form.if_outletpressure, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.outlet_pressure_changed)
        QtCore.QObject.connect(self.form.if_inletflowrate, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.inlet_flowrate_changed)
        QtCore.QObject.connect(self.form.if_outletflowrate, QtCore.SIGNAL("valueChanged(Base::Quantity)"), self.outlet_flowrate_changed)
        QtCore.QObject.connect(self.form.gb_inletpressure, QtCore.SIGNAL("clicked(bool)"), self.inlet_pressure_active)
        QtCore.QObject.connect(self.form.gb_outletpressure, QtCore.SIGNAL("clicked(bool)"), self.outlet_pressure_active)
        QtCore.QObject.connect(self.form.gb_inletflowrate, QtCore.SIGNAL("clicked(bool)"), self.inlet_flowrate_active)
        QtCore.QObject.connect(self.form.gb_outletflowrate, QtCore.SIGNAL("clicked(bool)"), self.outlet_flowrate_active)
        self.form.list_References.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.form.list_References.connect(self.form.list_References, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.references_list_right_clicked)
        self.form.cb_section_type.addItems(_FemFluidSection._FemFluidSection.known_fluid_types)
        self.form.cb_liquid_section_type.addItems(_FemFluidSection._FemFluidSection.known_liquid_types)
        self.form.cb_gas_section_type.addItems(_FemFluidSection._FemFluidSection.known_gas_types)
        self.form.cb_channel_section_type.addItems(_FemFluidSection._FemFluidSection.known_channel_types)

        self.get_fluidsection_props()
        self.update()

    def accept(self):
        self.set_fluidsection_props()
        if self.sel_server:
            FreeCADGui.Selection.removeObserver(self.sel_server)
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.recompute()
        return True

    def reject(self):
        if self.sel_server:
            FreeCADGui.Selection.removeObserver(self.sel_server)
        FreeCADGui.ActiveDocument.resetEdit()
        return True

    def get_fluidsection_props(self):
        self.references = []
        if self.obj.References:
            self.tuplereferences = self.obj.References
            self.get_references()
        self.SectionType = self.obj.SectionType
        self.LiquidSectionType = self.obj.LiquidSectionType
        self.ManningArea = self.obj.ManningArea
        self.ManningRadius = self.obj.ManningRadius
        self.ManningCoefficient = self.obj.ManningCoefficient
        self.EnlargeArea1 = self.obj.EnlargeArea1
        self.EnlargeArea2 = self.obj.EnlargeArea2
        self.ContractArea1 = self.obj.ContractArea1
        self.ContractArea2 = self.obj.ContractArea2
        self.OutletPressure = self.obj.OutletPressure
        self.InletPressure = self.obj.InletPressure
        self.OutletFlowRate = self.obj.OutletFlowRate
        self.InletFlowRate = self.obj.InletFlowRate
        self.OutletPressureActive = self.obj.OutletPressureActive
        self.InletPressureActive = self.obj.InletPressureActive
        self.OutletFlowRateActive = self.obj.OutletFlowRateActive
        self.InletFlowRateActive = self.obj.InletFlowRateActive

    def set_fluidsection_props(self):
        self.obj.References = self.references
        self.obj.LiquidSectionType = self.LiquidSectionType
        self.obj.SectionType = self.SectionType
        self.obj.ManningArea = self.ManningArea
        self.obj.ManningRadius = self.ManningRadius
        self.obj.ManningCoefficient = self.ManningCoefficient
        self.obj.EnlargeArea1 = self.EnlargeArea1
        self.obj.EnlargeArea2 = self.EnlargeArea2
        self.obj.ContractArea1 = self.ContractArea1
        self.obj.ContractArea2 = self.ContractArea2
        self.obj.OutletPressure = self.OutletPressure
        self.obj.InletPressure = self.InletPressure
        self.obj.OutletFlowRate = self.OutletFlowRate
        self.obj.InletFlowRate = self.InletFlowRate
        self.obj.OutletPressureActive = self.OutletPressureActive
        self.obj.InletPressureActive = self.InletPressureActive
        self.obj.OutletFlowRateActive = self.OutletFlowRateActive
        self.obj.InletFlowRateActive = self.InletFlowRateActive

    def update(self):
        'fills the widgets'
        index_sectiontype = self.form.cb_section_type.findText(self.SectionType)
        self.form.cb_section_type.setCurrentIndex(index_sectiontype)
        self.form.sw_section_type.setCurrentIndex(index_sectiontype)
        index_liquidsectiontype = self.form.cb_liquid_section_type.findText(self.LiquidSectionType)
        self.form.cb_liquid_section_type.setCurrentIndex(index_liquidsectiontype)
        self.form.sw_liquid_section_type.setCurrentIndex(index_liquidsectiontype)
        self.form.if_manning_area.setText(self.ManningArea.UserString)
        self.form.if_manning_radius.setText(self.ManningRadius.UserString)
        self.form.sb_manning_coefficient.setValue(self.ManningCoefficient)
        self.form.if_enlarge_area1.setText(self.EnlargeArea1.UserString)
        self.form.if_enlarge_area2.setText(self.EnlargeArea2.UserString)
        self.form.if_contract_area1.setText(self.ContractArea1.UserString)
        self.form.if_contract_area2.setText(self.ContractArea2.UserString)
        self.form.if_inletpressure.setText(FreeCAD.Units.Quantity(1000 * self.InletPressure, FreeCAD.Units.Pressure).UserString)
        self.form.if_outletpressure.setText(FreeCAD.Units.Quantity(1000 * self.OutletPressure, FreeCAD.Units.Pressure).UserString)
        self.form.if_inletflowrate.setText(str(self.InletFlowRate))
        self.form.if_outletflowrate.setText(str(self.OutletFlowRate))
        self.form.gb_inletpressure.setChecked(self.InletPressureActive)
        self.form.gb_outletpressure.setChecked(self.OutletPressureActive)
        self.form.gb_inletflowrate.setChecked(self.InletFlowRateActive)
        self.form.gb_outletflowrate.setChecked(self.OutletFlowRateActive)
        self.rebuild_list_References()

    def sectiontype_changed(self, index):
        if index < 0:
            return
        self.form.cb_section_type.setCurrentIndex(index)
        self.form.sw_section_type.setCurrentIndex(index)
        self.SectionType = str(self.form.cb_section_type.itemText(index))  # form returns unicode

    def liquidsectiontype_changed(self, index):
        if index < 0:
            return
        self.form.cb_liquid_section_type.setCurrentIndex(index)
        self.form.sw_liquid_section_type.setCurrentIndex(index)
        self.LiquidSectionType = str(self.form.cb_liquid_section_type.itemText(index))  # form returns unicode

    def manning_area_changed(self, base_quantity_value):
        self.ManningArea = base_quantity_value

    def manning_radius_changed(self, base_quantity_value):

        self.ManningRadius = base_quantity_value
    def manning_coefficient_changed(self, base_quantity_value):
        self.ManningCoefficient = base_quantity_value

    def enlarge_area1_changed(self, base_quantity_value):
        self.EnlargeArea1 = base_quantity_value

    def enlarge_area2_changed(self, base_quantity_value):
        self.EnlargeArea2 = base_quantity_value

    def contract_area1_changed(self, base_quantity_value):
        self.ContractArea1 = base_quantity_value

    def contract_area2_changed(self, base_quantity_value):
        self.ContractArea2 = base_quantity_value

    def inlet_pressure_changed(self, base_quantity_value):
        self.InletPressure = float(FreeCAD.Units.Quantity(base_quantity_value).getValueAs("MPa"))

    def outlet_pressure_changed(self, base_quantity_value):
        self.OutletPressure = float(FreeCAD.Units.Quantity(base_quantity_value).getValueAs("MPa"))

    def inlet_flowrate_changed(self, base_quantity_value):
        self.InletFlowRate = float(FreeCAD.Units.Quantity(base_quantity_value).getValueAs("kg/s"))

    def outlet_flowrate_changed(self, base_quantity_value):
        self.OutletFlowRate = float(FreeCAD.Units.Quantity(base_quantity_value).getValueAs("kg/s"))

    def inlet_pressure_active(self, active):
        self.InletPressureActive = active

    def outlet_pressure_active(self, active):
        self.OutletPressureActive = active

    def inlet_flowrate_active(self, active):
        self.InletFlowRateActive = active

    def outlet_flowrate_active(self, active):
        self.OutletFlowRateActive = active

    def get_references(self):
        for ref in self.tuplereferences:
            for elem in ref[1]:
                self.references.append((ref[0], elem))

    def references_list_right_clicked(self, QPos):
        self.form.contextMenu = QtGui.QMenu()
        menu_item = self.form.contextMenu.addAction("Remove Reference")
        if not self.references:
            menu_item.setDisabled(True)
        self.form.connect(menu_item, QtCore.SIGNAL("triggered()"), self.remove_reference)
        parentPosition = self.form.list_References.mapToGlobal(QtCore.QPoint(0, 0))
        self.form.contextMenu.move(parentPosition + QPos)
        self.form.contextMenu.show()

    def remove_reference(self):
        if not self.references:
            return
        currentItemName = str(self.form.list_References.currentItem().text())
        for ref in self.references:
            refname_to_compare_listentry = ref[0].Name + ':' + ref[1]
            if refname_to_compare_listentry == currentItemName:
                self.references.remove(ref)
        self.rebuild_list_References()

    def add_references(self):
        '''Called if Button add_reference is triggered'''
        # in constraints EditTaskPanel the selection is active as soon as the taskpanel is open
        # here the addReference button EditTaskPanel has to be triggered to start selection mode
        FreeCADGui.Selection.clearSelection()
        # start SelectionObserver and parse the function to add the References to the widget
        print_message = "Select Edges by single click on them to add them to the list"
        import FemSelectionObserver
        self.sel_server = FemSelectionObserver.FemSelectionObserver(self.selectionParser, print_message)

    def selectionParser(self, selection):
        # print('selection: ', selection[0].Shape.ShapeType, '  ', selection[0].Name, '  ', selection[1])
        if hasattr(selection[0], "Shape"):
            if selection[1]:
                elt = selection[0].Shape.getElement(selection[1])
                if elt.ShapeType == 'Edge':
                    if selection not in self.references:
                        self.references.append(selection)
                        self.rebuild_list_References()
                    else:
                        FreeCAD.Console.PrintMessage(selection[0].Name + ' --> ' + selection[1] + ' is in reference list already!\n')

    def rebuild_list_References(self):
        self.form.list_References.clear()
        items = []
        for ref in self.references:
            item_name = ref[0].Name + ':' + ref[1]
            items.append(item_name)
        for listItemName in sorted(items):
            self.form.list_References.addItem(listItemName)
