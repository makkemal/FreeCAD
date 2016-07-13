# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2015 - Przemo Firszt <przemo@firszt.eu>                 *
# *   Copyright (c) 2015 - Bernd Hahnebach <bernd@bimstatik.org>            *
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


__title__ = "FemInputWriterCcx"
__author__ = "Przemo Firszt, Bernd Hahnebach"
__url__ = "http://www.freecadweb.org"


import FreeCAD
import os
import sys
import time
import FemMeshTools
import FemInputWriter


class FemInputWriterCcx(FemInputWriter.FemInputWriter):
    def __init__(self, analysis_obj, solver_obj,
                 mesh_obj, mat_obj,
                 fixed_obj,
                 force_obj, pressure_obj,
                 displacement_obj,
                 temperature_obj,
                 heatflux_obj,
                 initialtemperature_obj, 
                 planerotation_obj,
                 contact_obj,
                 beamsection_obj, shellthickness_obj,
                 analysis_type=None, eigenmode_parameters=None,
                 dir_name=None):
        FemInputWriter.FemInputWriter.__init__(self, analysis_obj, solver_obj,
                                               mesh_obj, mat_obj,
                                               fixed_obj,
                                               force_obj, pressure_obj,
                                               displacement_obj,
                                               temperature_obj,
                                               heatflux_obj,
                                               initialtemperature_obj, 
                                               planerotation_obj,
                                               contact_obj,
                                               beamsection_obj, shellthickness_obj,
                                               analysis_type, eigenmode_parameters,
                                               dir_name)
        self.file_name = self.dir_name + '/' + self.mesh_object.Name + '.inp'
        print('FemInputWriterCcx --> self.dir_name  -->  ' + self.dir_name)
        print('FemInputWriterCcx --> self.file_name  -->  ' + self.file_name)

    def write_calculix_input_file(self):
        name = ""
        for i in range(len(self.file_name)-4):
            name = name + self.file_name[i] 
        self.mesh_object.FemMesh.writeABAQUS(name+ "_Nodes_elem.inp")
        # reopen file with "append" and add the analysis definition
        inpfile = open(self.file_name, 'w')
        inpfile.write('\n')
        inpfile.write('**Nodes and Elements\n')
        inpfile.write('** written by write_nodes_elements \n')
        inpfile.write('*INCLUDE,INPUT=' +name+ '_Nodes_elem.inp \n')
        self.write_element_sets_material_and_femelement_type(inpfile)
        inpfile.close()
        inpfile = open(name+ "_Node_sets.inp", 'w')
        self.write_node_sets_constraints_fixed(inpfile)
        self.write_node_sets_constraints_displacement(inpfile)
        self.write_node_sets_constraints_planerotation(inpfile)
        self.write_surfaces_contraints_contact(inpfile)
        inpfile = open(self.file_name, 'a')
        inpfile.write('\n***********************************************************\n')
        inpfile.write('** Node set(s) for fixed constraint\n')
        for femobj in self.fixed_objects:
            inpfile.write('   **' + femobj['Object'].Name + '\n')        
        inpfile.write('** Node set(s) for PlaneRotation constraint\n')
        for femobj in self.planerotation_objects:
            inpfile.write('   **' + femobj['Object'].Name + '\n')
        inpfile.write('** Node set(s) for prescribed displacement constraint\n')
        for femobj in self.displacement_objects:
            inpfile.write('   **' + femobj['Object'].Name + '\n')
        inpfile.write('** Node set(s) for loads\n')
        for femobj in self.force_objects:
            inpfile.write('   **' + femobj['Object'].Name + '\n')
        inpfile.write('** Node set(s) for temperature constraint\n')
        for femobj in self.temperature_objects:
            inpfile.write('   **' + femobj['Object'].Name + '\n')
        inpfile.write('** written by write_node_sets_constraints \n')
        inpfile.write('*INCLUDE,INPUT=' +name+ "_Node_sets.inp \n")
        if self.analysis_type == "thermomech": # OvG: placed under thermomech analysis
            inpfileNodes = open(name+ "_Node_sets.inp", 'a')  
            self.write_temperature_nodes(inpfileNodes)
            self.write_node_sets_constraints_force(inpfileNodes) #SvdW: Add the node set to thermomech analysis
            inpfileNodes.close()
        if self.analysis_type is None or self.analysis_type == "static":
            inpfileNodes = open(name+ "_Node_sets.inp", 'a')
            self.write_node_sets_constraints_force(inpfileNodes)
            inpfileNodes.close()
        inpfile = open(self.file_name, 'a')
        self.write_materials(inpfile) 
        if self.analysis_type == "thermomech": # OvG: placed under thermomech analysis
            self.write_initialtemperature(inpfile)
        self.write_femelementsets(inpfile)
        self.write_constraints_planerotation(inpfile)
        self.write_constraints_contact(inpfile)
        if self.analysis_type == "thermomech": # OvG: placed under thermomech analysis
            self.write_step_begin_thermomech(inpfile)
            self.write_thermomech(inpfile)
        else:
            self.write_step_begin(inpfile)
        self.write_constraints_fixed(inpfile)
        self.write_constraints_displacement(inpfile)        
        if self.analysis_type == "thermomech": # OvG: placed under thermomech analysis
            self.write_temperature(inpfile)
            inpfile.write('\n***********************************************************\n')
            inpfile.write('** Convective heat transfer (heat flux)\n')
            inpfile.write('** written by write_heatflux\n')            
            inpfile.write('*INCLUDE,INPUT=' +name+ "_Heatflux.inp \n\n")
            inpfileHeatflux = open(name + "_Heatflux.inp","w")            
            self.write_heatflux(inpfileHeatflux)
            inpfileHeatflux.close()
            inpfile.write('\n***********************************************************\n')
            inpfile.write('** Node loads\n')
            inpfile.write('** written by write_constraints_force\n')
            inpfile.write('*INCLUDE,INPUT=' +name+ "_Contraints_Force.inp \n\n")
            inpfileForce = open(name+ "_Contraints_Force.inp","w")
            self.write_constraints_force(inpfileForce)
            inpfileForce.close()
            inpfile.write('\n***********************************************************\n')
            inpfile.write('** Element + CalculiX face + load in [MPa]\n')
            inpfile.write('** written by write_constraints_pressure\n')
            inpfile.write('*INCLUDE,INPUT=' +name+ "_Contraints_Pressure.inp \n\n")
            inpfilePressure = open(name+ "_Contraints_Pressure.inp","w")
            self.write_constraints_pressure(inpfilePressure)
            inpfilePressure.close()
        if self.analysis_type is None or self.analysis_type == "static":
            inpfile.write('\n***********************************************************\n')
            inpfile.write('** Node loads\n')
            inpfile.write('** written by write_constraints_force\n')
            inpfile.write('*INCLUDE,INPUT=' +name+ "_Contraints_Force.inp \n\n")
            inpfileForce = open(name+ "_Contraints_Force.inp","w")
            self.write_constraints_force(inpfileForce)
            inpfileForce.close()
            inpfile.write('\n***********************************************************\n')
            inpfile.write('** Element + CalculiX face + load in [MPa]\n')
            inpfile.write('** written by write_constraints_pressure\n')
            inpfile.write('*INCLUDE,INPUT=' +name+ "_Contraints_Pressure.inp \n\n")
            inpfilePressure = open(name+ "_Contraints_Pressure.inp","w")
            self.write_constraints_pressure(inpfilePressure)
            inpfilePressure.close()
        elif self.analysis_type == "frequency":
            self.write_frequency(inpfile)
        self.write_outputs_types(inpfile)
        self.write_step_end(inpfile)
        self.write_footer(inpfile)
        inpfile.close()
        return self.file_name

    def write_element_sets_material_and_femelement_type(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Element sets for materials and FEM element type (solid, shell, beam)\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        if len(self.material_objects) == 1:
            if self.beamsection_objects and len(self.beamsection_objects) == 1:          # single mat, single beam
                self.get_ccx_elsets_single_mat_single_beam()
            elif self.beamsection_objects and len(self.beamsection_objects) > 1:         # single mat, multiple beams
                self.get_ccx_elsets_single_mat_multiple_beam()
            elif self.shellthickness_objects and len(self.shellthickness_objects) == 1:  # single mat, single shell
                self.get_ccx_elsets_single_mat_single_shell()
            elif self.shellthickness_objects and len(self.shellthickness_objects) > 1:   # single mat, multiple shells
                self.get_ccx_elsets_single_mat_multiple_shell()
            else:                                                                        # single mat, solid
                self.get_ccx_elsets_single_mat_solid()
        else:
            if self.beamsection_objects and len(self.beamsection_objects) == 1:         # multiple mats, single beam
                self.get_ccx_elsets_multiple_mat_single_beam()
            elif self.beamsection_objects and len(self.beamsection_objects) > 1:        # multiple mats, multiple beams
                self.get_ccx_elsets_multiple_mat_multiple_beam()
            elif self.shellthickness_objects and len(self.shellthickness_objects) == 1:   # multiple mats, single shell
                self.get_ccx_elsets_multiple_mat_single_shell()
            elif self.shellthickness_objects and len(self.shellthickness_objects) > 1:  # multiple mats, multiple shells
                self.get_ccx_elsets_multiple_mat_multiple_shell()
            else:                                                                       # multiple mats, solid
                self.get_ccx_elsets_multiple_mat_solid()
        for ccx_elset in self.ccx_elsets:
            f.write('*ELSET,ELSET=' + ccx_elset['ccx_elset_name'] + '\n')
            if ccx_elset['ccx_elset']:
                if ccx_elset['ccx_elset'] == self.ccx_eall:
                    f.write(self.ccx_eall + '\n')
                else:
                    for elid in ccx_elset['ccx_elset']:
                        f.write(str(elid) + ',\n')
            else:
                f.write('**No elements found for these objects\n')

    def write_node_sets_constraints_fixed(self, f):
        # get nodes
        self.get_constraints_fixed_nodes()
        # write nodes to file
        f.write('\n***********************************************************\n')
        f.write('** Node set for fixed constraint\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        for femobj in self.fixed_objects:
            f.write('*NSET,NSET=' + femobj['Object'].Name + '\n')
            for n in femobj['Nodes']:
                f.write(str(n) + ',\n')

    def write_node_sets_constraints_planerotation(self, f):
        # self.constraint_conflict_nodes is used to check if MPC and fixed constraint share same nodes,
        # because MPC's and fixed constriants can't share same nodes.
        if not self.femnodes_mesh:
            self.femnodes_mesh = self.femmesh.Nodes
        f.write('\n\n')
        # get nodes and write them to file
        f.write('\n***********************************************************\n')
        f.write('** Node set for plane rotation constraint\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        for femobj in self.planerotation_objects:
            l_nodes = []
            fric_obj = femobj['Object']
            f.write('*NSET,NSET=' + fric_obj.Name + '\n')
            for o, elem_tup in fric_obj.References:
                for elem in elem_tup:
                    fo = o.Shape.getElement(elem)
                    n = []
                    if fo.ShapeType == 'Face':
                        n = self.mesh_object.FemMesh.getNodesByFace(fo)
                    for i in n:
                        l_nodes.append(i)
                # Code to extract nodes and coordinates on the PlaneRotation support face
                nodes_coords = []
                for node in l_nodes:
                    nodes_coords.append((node, self.femnodes_mesh[node].x, self.femnodes_mesh[node].y, self.femnodes_mesh[node].z))
                node_planerotation = get_three_non_colinear_nodes(nodes_coords)
                for i in range(len(l_nodes)):
                    #if (l_nodes[i] != node_1) and (l_nodes[i] != node_2) and (l_nodes[i] != node_3):
                    if l_nodes[i] not in node_planerotation:
                        node_planerotation.append(l_nodes[i])
                MPC_nodes = []
                for i in range(len(node_planerotation)):
                    cnt = 0
                    for j in range(len(self.constraint_conflict_nodes)):
                        if node_planerotation[i] == self.constraint_conflict_nodes[j]:
                            cnt = cnt + 1
                    if cnt == 0:
                        MPC = node_planerotation[i]
                        MPC_nodes.append(MPC)

                for i in range(len(MPC_nodes)):
                    f.write(str(MPC_nodes[i]) + ',\n')

    def write_node_sets_constraints_displacement(self, f):
        # get nodes
        self.get_constraints_displacement_nodes()
        # write nodes to file
        f.write('\n***********************************************************\n')
        f.write('** Node sets for prescribed displacement constraint\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        for femobj in self.displacement_objects:
            f.write('*NSET,NSET=' + femobj['Object'].Name + '\n')
            for n in femobj['Nodes']:
                f.write(str(n) + ',\n')

    def write_surfaces_contraints_contact(self, f):
        # get surface nodes and write them to file
        f.write('\n***********************************************************\n')
        f.write('** Surfaces for contact constraint\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        obj = 0
        for fobj in self.contact_objects:
            contact_obj = fobj['Object']
            cnt = 0
            obj = obj + 1
            for o, elem_tup in contact_obj.References:
                for elem in elem_tup:
                    ref_shape = o.Shape.getElement(elem)
                    cnt = cnt + 1
                    if ref_shape.ShapeType == 'Face':
                        if cnt == 1:
                            name = "DEP" + str(obj)
                        else:
                            name = "IND" + str(obj)
                        f.write('*SURFACE, NAME =' + name + '\n')
                        v = self.mesh_object.FemMesh.getccxVolumesByFace(ref_shape)
                        for i in v:
                            f.write("{},S{}\n".format(i[0], i[1]))
 
    def write_temperature_nodes(self,f): #Fixed temperature
        for ftobj in self.temperature_objects:
            fixedtemp_obj = ftobj['Object']
            f.write('*NSET,NSET='+fixedtemp_obj.Name + '\n')
            for o, elem_tup in fixedtemp_obj.References:
                for elem in elem_tup:
                    fto = o.Shape.getElement(elem)
                    n = []
                    if fto.ShapeType == 'Face':
                        n = self.mesh_object.FemMesh.getNodesByFace(fto)
                    elif fto.ShapeType == 'Edge':
                        n = self.mesh_object.FemMesh.getNodesByEdge(fto)
                    elif fto.ShapeType == 'Vertex':
                        n = self.mesh_object.FemMesh.getNodesByVertex(fto)
                    for i in n:
                        f.write(str(i) + ',\n')

    def write_materials(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Materials\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        f.write('** Young\'s modulus unit is MPa = N/mm2\n')
        f.write('** Density\'s unit is t/mm^3\n')
        f.write('** Thermal conductivity unit is kW/mm/K = t*mm/K*s^3\n')
        f.write('** Specific Heat unit is kJ/t/K = mm^2/s^2/K\n')
        for m in self.material_objects:
            mat_obj = m['Object']
            # get material properties - Currently in SI units: M/kg/s/Kelvin
            YM_in_MPa = 1
            TC_in_WmK = 1
            TEC_in_mmK = 1
            SH_in_JkgK = 1
            PR = 1
            density_in_tonne_per_mm3 = 1
            try:
                YM = FreeCAD.Units.Quantity(mat_obj.Material['YoungsModulus'])
                YM_in_MPa = YM.getValueAs('MPa')
            except:
                FreeCAD.Console.PrintError("No YoungsModulus defined for material: default used\n")
            try:
                PR = float(mat_obj.Material['PoissonRatio'])
            except:
                FreeCAD.Console.PrintError("No PoissonRatio defined for material: default used\n")
            try:
                TC = FreeCAD.Units.Quantity(mat_obj.Material['ThermalConductivity'])
                TC_in_WmK = TC.getValueAs('W/m/K') #SvdW: Add factor to force units to results' base units of t/mm/s/K - W/m/K results in no factor needed
            except:
                FreeCAD.Console.PrintError("No ThermalConductivity defined for material: default used\n")
            try:
                TEC = FreeCAD.Units.Quantity(mat_obj.Material['ThermalExpansionCoefficient'])
                TEC_in_mmK = TEC.getValueAs('mm/mm/K')
            except:
                FreeCAD.Console.PrintError("No ThermalExpansionCoefficient defined for material: default used\n")
            try:
                SH = FreeCAD.Units.Quantity(mat_obj.Material['SpecificHeat'])
                SH_in_JkgK = SH.getValueAs('J/kg/K')*1e+06 #SvdW: Add factor to force units to results' base units of t/mm/s/K
            except:
                FreeCAD.Console.PrintError("No SpecificHeat defined for material: default used\n")
            mat_info_name = mat_obj.Material['Name']
            mat_name = mat_obj.Name
            # write material properties
            f.write('**FreeCAD material name: ' + mat_info_name + '\n')
            f.write('*MATERIAL, NAME=' + mat_name + '\n')
            f.write('*ELASTIC \n')
            f.write('{},  '.format(YM_in_MPa))
            f.write('{0:.3f}\n'.format(PR))
            try:
                density = FreeCAD.Units.Quantity(mat_obj.Material['Density'])
                density_in_tonne_per_mm3 = float(density.getValueAs('t/mm^3'))
            except:
                FreeCAD.Console.PrintError("No Density defined for material: default used\n")
            f.write('*DENSITY \n')
            f.write('{0:.3e}, \n'.format(density_in_tonne_per_mm3))
            f.write('*CONDUCTIVITY \n')
            f.write('{}, \n'.format(TC_in_WmK))
            f.write('*EXPANSION \n')
            f.write('{}, \n'.format(TEC_in_mmK))
            f.write('*SPECIFIC HEAT \n')
            f.write('{}, \n'.format(SH_in_JkgK))

    def write_femelementsets(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Sections\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        for ccx_elset in self.ccx_elsets:
            if ccx_elset['ccx_elset']:
                if 'beamsection_obj'in ccx_elset:  # beam mesh
                    beamsec_obj = ccx_elset['beamsection_obj']
                    elsetdef = 'ELSET=' + ccx_elset['ccx_elset_name'] + ', '
                    material = 'MATERIAL=' + ccx_elset['mat_obj_name']
                    height = beamsec_obj.Height.getValueAs('mm')
                    width = beamsec_obj.Width.getValueAs('mm')
                    if width == 0:
                        section_type = ', SECTION=CIRC'
                        setion_geo = str(height) + '\n'
                    else:
                        section_type = ', SECTION=RECT'
                        setion_geo = str(height) + ', ' + str(width) + '\n'
                    setion_def = '*BEAM SECTION, ' + elsetdef + material + section_type + '\n'
                    f.write(setion_def)
                    f.write(setion_geo)
                elif 'shellthickness_obj'in ccx_elset:  # shell mesh
                    shellth_obj = ccx_elset['shellthickness_obj']
                    elsetdef = 'ELSET=' + ccx_elset['ccx_elset_name'] + ', '
                    material = 'MATERIAL=' + ccx_elset['mat_obj_name']
                    setion_def = '*SHELL SECTION, ' + elsetdef + material + '\n'
                    setion_geo = str(shellth_obj.Thickness.getValueAs('mm')) + '\n'
                    f.write(setion_def)
                    f.write(setion_geo)
                else:  # solid mesh
                    elsetdef = 'ELSET=' + ccx_elset['ccx_elset_name'] + ', '
                    material = 'MATERIAL=' + ccx_elset['mat_obj_name']
                    setion_def = '*SOLID SECTION, ' + elsetdef + material + '\n'
                    f.write(setion_def)

    def write_step_begin(self, f):
        f.write('\n***********************************************************\n')
        f.write('** One step is needed to calculate the mechanical analysis of FreeCAD\n')
        f.write('** loads are applied quasi-static, means without involving the time dimension\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        if hasattr(self.solver_obj, "GeometricalNonlinearity") and self.solver_obj.GeometricalNonlinearity == "nonlinear" and self.analysis_type == 'static':
            f.write('*STEP, NLGEOM\n')   # https://www.comsol.com/blogs/what-is-geometric-nonlinearity/
        elif hasattr(self.solver_obj, "GeometricalNonlinearity") and self.solver_obj.GeometricalNonlinearity == "nonlinear" and self.analysis_type == 'frequency':
            print('Analysis type frequency and geometrical nonlinear analyis are not allowed together, linear is used instead!')
            f.write('*STEP\n')
        else:
            f.write('\n')
        f.write('*STATIC')
        if calculixprefs.MatrixSolverType== "default":
            f.write('\n')
        elif calculixprefs.MatrixSolverType== "spooles":
             f.write(',SOLVER=SPOOLES\n')
        elif calculixprefs.MatrixSolverType== "iterativescaling":
             f.write(',SOLVER=ITERATIVE SCALING\n')
        elif calculixprefs.MatrixSolverType== "iterativecholesky":
             f.write(',SOLVER=ITERATIVE CHOLESKY\n')

    def write_step_begin_thermomech(self, f):
        f.write('\n***********************************************************\n')
        f.write('** One step is needed to calculate the mechanical analysis of FreeCAD\n')
        f.write('** loads are applied quasi-static, means without involving the time dimension\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        f.write('*STEP')
        if calculixprefs.NonLinearGeometry:
            f.write(',NLGEOM')
        f.write(',INC={}\n'.format(calculixprefs.Maxiterations)) 

    def write_constraints_fixed(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Constraints\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        for femobj in self.fixed_objects:  # femobj --> dict, FreeCAD document object is femobj['Object']
            fix_obj_name = femobj['Object'].Name
            f.write('*BOUNDARY\n')
            f.write(fix_obj_name + ',1\n')
            f.write(fix_obj_name + ',2\n')
            f.write(fix_obj_name + ',3\n')
            if self.beamsection_objects or self.shellthickness_objects:
                f.write(fix_obj_name + ',4\n')
                f.write(fix_obj_name + ',5\n')
                f.write(fix_obj_name + ',6\n')
            f.write('\n')

    def write_constraints_displacement(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Displacement constraint applied\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        for femobj in self.displacement_objects:  # femobj --> dict, FreeCAD document object is femobj['Object']
            disp_obj = femobj['Object']
            disp_obj_name = disp_obj.Name
            f.write('*BOUNDARY\n')
            if disp_obj.xFix:
                f.write(disp_obj_name + ',1\n')
            elif not disp_obj.xFree:
                f.write(disp_obj_name + ',1,1,' + str(disp_obj.xDisplacement) + '\n')
            if disp_obj.yFix:
                f.write(disp_obj_name + ',2\n')
            elif not disp_obj.yFree:
                f.write(disp_obj_name + ',2,2,' + str(disp_obj.yDisplacement) + '\n')
            if disp_obj.zFix:
                f.write(disp_obj_name + ',3\n')
            elif not disp_obj.zFree:
                f.write(disp_obj_name + ',3,3,' + str(disp_obj.zDisplacement) + '\n')

            if self.beamsection_objects or self.shellthickness_objects:
                if disp_obj.rotxFix:
                    f.write(disp_obj_name + ',4\n')
                elif not disp_obj.rotxFree:
                    f.write(disp_obj_name + ',4,4,' + str(disp_obj.xRotation) + '\n')
                if disp_obj.rotyFix:
                    f.write(disp_obj_name + ',5\n')
                elif not disp_obj.rotyFree:
                    f.write(disp_obj_name + ',5,5,' + str(disp_obj.yRotation) + '\n')
                if disp_obj.rotzFix:
                    f.write(disp_obj_name + ',6\n')
                elif not disp_obj.rotzFree:
                    f.write(disp_obj_name + ',6,6,' + str(disp_obj.zRotation) + '\n')
        f.write('\n')

    def write_constraints_planerotation(self, f):
        f.write('\n***********************************************************\n')
        f.write('** PlaneRotation Constraints\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        for fric_object in self.planerotation_objects:
            fric_obj_name = fric_object['Object'].Name
            f.write('*MPC\n')
            f.write('PLANE,' + fric_obj_name + '\n')
            f.write('\n')

    def write_constraints_contact(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Contact Constraints\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        obj = 0
        for contact_object in self.contact_objects:
            obj = obj + 1
            ctct_obj = contact_object['Object']
            f.write('*CONTACT PAIR, INTERACTION=INT' + str(obj) + ',TYPE=SURFACE TO SURFACE\n')
            ind_surf = "IND" + str(obj)
            dep_surf = "DEP" + str(obj)
            f.write(dep_surf + ',' + ind_surf + '\n')
            f.write('*SURFACE INTERACTION, NAME=INT' + str(obj) + '\n')
            f.write('*SURFACE BEHAVIOR,PRESSURE-OVERCLOSURE=LINEAR\n')
            Slope = ctct_obj.Slope
            f.write(str(Slope) + ' \n')
            F = ctct_obj.Friction
            if F > 0:
                f.write('*FRICTION \n')
                F = str(F)
                stick = (Slope / 10.0)
                f.write(F + ', ' + str(stick) + ' \n')

    def write_temperature(self,f):
        f.write('\n***********************************************************\n')
        f.write('** Fixed temperature constraint applied\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))        
        for ftobj in self.temperature_objects:
            fixedtemp_obj = ftobj['Object']
            f.write('*BOUNDARY\n')
            f.write('{},11,11,{}\n'.format(fixedtemp_obj.Name,fixedtemp_obj.Temperature))
            f.write('\n')

    def write_constraints_force(self, f):
        # check shape type of reference shape and get node loads
        self.get_constraints_force_nodeloads()
        # write node loads to file
        f.write('\n***********************************************************\n')
        f.write('** Node loads\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        f.write('*CLOAD\n')
        for femobj in self.force_objects:  # femobj --> dict, FreeCAD document object is femobj['Object']
            frc_obj_name = femobj['Object'].Name
            direction_vec = femobj['Object'].DirectionVector
            f.write('** ' + frc_obj_name + '\n')
            for ref_shape in femobj['NodeLoadTable']:
                f.write('** ' + ref_shape[0] + '\n')
                for n in sorted(ref_shape[1]):
                    node_load = ref_shape[1][n]
                    if (direction_vec.x != 0.0):
                        v1 = "{:.13E}".format(direction_vec.x * node_load)
                        f.write(str(n) + ',1,' + v1 + '\n')
                    if (direction_vec.y != 0.0):
                        v2 = "{:.13E}".format(direction_vec.y * node_load)
                        f.write(str(n) + ',2,' + v2 + '\n')
                    if (direction_vec.z != 0.0):
                        v3 = "{:.13E}".format(direction_vec.z * node_load)
                        f.write(str(n) + ',3,' + v3 + '\n')
                f.write('\n')
            f.write('\n')

    def write_constraints_pressure(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Element + CalculiX face + load in [MPa]\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        for femobj in self.pressure_objects:
            prs_obj = femobj['Object']
            f.write('*DLOAD\n')
            for o, elem_tup in prs_obj.References:
                rev = -1 if prs_obj.Reversed else 1
                for elem in elem_tup:
                    ref_shape = o.Shape.getElement(elem)
                    if ref_shape.ShapeType == 'Face':
                        v = self.femmesh.getccxVolumesByFace(ref_shape)
                        f.write("** Load on face {}\n".format(elem))
                        for i in v:
                            f.write("{},P{},{}\n".format(i[0], i[1], rev * prs_obj.Pressure))

    def write_heatflux(self, f): # OvG Implemented writing out heatflux to calculix input file
        for hfobj in self.heatflux_objects:
            heatflux_obj = hfobj['Object']
            f.write('*FILM\n')
            for o, elem_tup in heatflux_obj.References:
                for elem in elem_tup:
                    ho = o.Shape.getElement(elem)
                    if ho.ShapeType == 'Face':
                        v = self.mesh_object.FemMesh.getccxVolumesByFace(ho)
                        f.write("** Heat flux on face {}\n".format(elem))
                        for i in v:
                            f.write("{},F{},{},{}\n".format(i[0], i[1], heatflux_obj.AmbientTemp, heatflux_obj.FilmCoef*0.001))#SvdW add factor to force heatflux to units system of t/mm/s/K # OvG: Only write out the VolumeIDs linked to a particular face
        
    def write_frequency(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Frequency analysis\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        f.write('*FREQUENCY\n')
        f.write('{},{},{}\n'.format(self.no_of_eigenfrequencies, self.eigenfrequeny_range_low, self.eigenfrequeny_range_high))

    def write_thermomech(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Un-Coupled temperature displacement analysis\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        f.write('*UNCOUPLED TEMPERATURE-DISPLACEMENT')
        if calculixprefs.MatrixSolverType== "default":
            f.write('')
        elif calculixprefs.MatrixSolverType== "spooles":
             f.write(',SOLVER=SPOOLES')
        elif calculixprefs.MatrixSolverType== "iterativescaling":
             f.write(',SOLVER=ITERATIVE SCALING')
        elif calculixprefs.MatrixSolverType== "iterativecholesky":
             f.write(',SOLVER=ITERATIVE CHOLESKY')
        if calculixprefs.SteadyState:
            f.write(',STEADY STATE\n')
            calculixprefs.InitialTimeStep=1.0  #Set time to 1 and ignore user imputs for steady state
            calculixprefs.EndTime=1.0
        else:
            f.write('\n')     
        f.write('{},{}\n'.format(calculixprefs.InitialTimeStep,calculixprefs.EndTime))# OvG: 1.0 increment, total time 1 for steady state wil cut back automatically

    def write_initialtemperature(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Coupled temperature displacement analysis\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        f.write('*INITIAL CONDITIONS,TYPE=TEMPERATURE\n')
        for itobj in self.initialtemperature_objects: #Should only be one
            inittemp_obj = itobj['Object']
            f.write('Nall,{}\n'.format(inittemp_obj.initialTemperature)); # OvG: Initial temperature

    def write_outputs_types(self, f):
        f.write('\n***********************************************************\n')
        f.write('** Outputs --> frd file\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        if self.beamsection_objects or self.shellthickness_objects:
            f.write('*NODE FILE, OUTPUT=2d\n')
        else:
            f.write('*NODE FILE\n')
        if self.analysis_type == "thermomech": #MPH write out nodal temperatures is thermomechanical 
            f.write('U, NT\n')
        else:
            f.write('U \n')
        f.write('*EL FILE\n')
        f.write('S, E\n')
        f.write('** outputs --> dat file\n')
        f.write('*NODE PRINT , NSET=Nall \n')
        f.write('U \n')
        f.write('*EL PRINT , ELSET=Eall \n')
        f.write('S \n')

    def write_step_end(self, f):
        f.write('\n***********************************************************\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        f.write('*END STEP \n')

    def write_footer(self, f):
        f.write('\n***********************************************************\n')
        f.write('** CalculiX Input file\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        f.write('**   written by    --> FreeCAD ' + self.fc_ver[0] + '.' + self.fc_ver[1] + '.' + self.fc_ver[2] + '\n')
        f.write('**   written on    --> ' + time.ctime() + '\n')
        f.write('**   file name     --> ' + os.path.basename(FreeCAD.ActiveDocument.FileName) + '\n')
        f.write('**   analysis name --> ' + self.analysis.Name + '\n')
        f.write('**\n')
        f.write('**\n')
        f.write('**\n')
        f.write('**   Units\n')
        f.write('**\n')
        f.write('**   Geometry (mesh data)        --> mm\n')
        f.write("**   Materials (Young's modulus) --> N/mm2 = MPa\n")
        f.write('**   Loads (nodal loads)         --> N\n')
        f.write('**\n')

    # self.ccx_elsets = [ {
    #                        'beamsection_obj' : 'beamsection_obj'       if exists
    #                        'shellthickness_obj' : shellthickness_obj'  if exists
    #                        'ccx_elset' : [e1, e2, e3, ... , en] or string self.ccx_eall
    #                        'ccx_elset_name' : 'ccx_identifier_elset'
    #                        'mat_obj_name' : 'mat_obj.Name'
    #                        'ccx_mat_name' : 'mat_obj.Material['Name']'   !!! not unique !!!
    #                     },
    #                     {}, ... , {} ]
    def get_ccx_elsets_single_mat_single_beam(self):
        mat_obj = self.material_objects[0]['Object']
        beamsec_obj = self.beamsection_objects[0]['Object']
        ccx_elset = {}
        ccx_elset['beamsection_obj'] = beamsec_obj
        ccx_elset['ccx_elset'] = self.ccx_eall
        ccx_elset['ccx_elset_name'] = get_ccx_elset_beam_name(mat_obj.Name, beamsec_obj.Name)
        ccx_elset['mat_obj_name'] = mat_obj.Name
        ccx_elset['ccx_mat_name'] = mat_obj.Material['Name']
        self.ccx_elsets.append(ccx_elset)

    def get_ccx_elsets_single_mat_single_shell(self):
        mat_obj = self.material_objects[0]['Object']
        shellth_obj = self.shellthickness_objects[0]['Object']
        ccx_elset = {}
        ccx_elset['shellthickness_obj'] = shellth_obj
        ccx_elset['ccx_elset'] = self.ccx_eall
        ccx_elset['ccx_elset_name'] = get_ccx_elset_shell_name(mat_obj.Name, shellth_obj.Name)
        ccx_elset['mat_obj_name'] = mat_obj.Name
        ccx_elset['ccx_mat_name'] = mat_obj.Material['Name']
        self.ccx_elsets.append(ccx_elset)

    def get_ccx_elsets_single_mat_solid(self):
        mat_obj = self.material_objects[0]['Object']
        ccx_elset = {}
        ccx_elset['ccx_elset'] = self.ccx_eall
        ccx_elset['ccx_elset_name'] = get_ccx_elset_solid_name(mat_obj.Name)
        ccx_elset['mat_obj_name'] = mat_obj.Name
        ccx_elset['ccx_mat_name'] = mat_obj.Material['Name']
        self.ccx_elsets.append(ccx_elset)

    def get_ccx_elsets_single_mat_multiple_beam(self):
        if not self.femelement_table:
            self.femelement_table = FemMeshTools.get_femelement_table(self.femmesh)
        mat_obj = self.material_objects[0]['Object']
        FemMeshTools.get_femelement_sets(self.femmesh, self.femelement_table, self.beamsection_objects)
        for beamsec_data in self.beamsection_objects:
            beamsec_obj = beamsec_data['Object']
            ccx_elset = {}
            ccx_elset['beamsection_obj'] = beamsec_obj
            ccx_elset['ccx_elset'] = beamsec_data['FEMElements']
            ccx_elset['ccx_elset_name'] = get_ccx_elset_beam_name(mat_obj.Name, beamsec_obj.Name, None, beamsec_data['ShortName'])
            ccx_elset['mat_obj_name'] = mat_obj.Name
            ccx_elset['ccx_mat_name'] = mat_obj.Material['Name']
            self.ccx_elsets.append(ccx_elset)

    def get_ccx_elsets_single_mat_multiple_shell(self):
        if not self.femelement_table:
            self.femelement_table = FemMeshTools.get_femelement_table(self.femmesh)
        mat_obj = self.material_objects[0]['Object']
        FemMeshTools.get_femelement_sets(self.femmesh, self.femelement_table, self.shellthickness_objects)
        for shellth_data in self.shellthickness_objects:
            shellth_obj = shellth_data['Object']
            ccx_elset = {}
            ccx_elset['shellthickness_obj'] = shellth_obj
            ccx_elset['ccx_elset'] = shellth_data['FEMElements']
            ccx_elset['ccx_elset_name'] = get_ccx_elset_shell_name(mat_obj.Name, shellth_obj.Name, None, shellth_data['ShortName'])
            ccx_elset['mat_obj_name'] = mat_obj.Name
            ccx_elset['ccx_mat_name'] = mat_obj.Material['Name']
            self.ccx_elsets.append(ccx_elset)

    def get_ccx_elsets_multiple_mat_single_beam(self):
        if not self.femelement_table:
            self.femelement_table = FemMeshTools.get_femelement_table(self.femmesh)
        beamsec_obj = self.beamsection_objects[0]['Object']
        FemMeshTools.get_femelement_sets(self.femmesh, self.femelement_table, self.material_objects)
        for mat_data in self.material_objects:
            mat_obj = mat_data['Object']
            ccx_elset = {}
            ccx_elset['beamsection_obj'] = beamsec_obj
            ccx_elset['ccx_elset'] = mat_data['FEMElements']
            ccx_elset['ccx_elset_name'] = get_ccx_elset_beam_name(mat_obj.Name, beamsec_obj.Name, mat_data['ShortName'])
            ccx_elset['mat_obj_name'] = mat_obj.Name
            ccx_elset['ccx_mat_name'] = mat_obj.Material['Name']
            self.ccx_elsets.append(ccx_elset)

    def get_ccx_elsets_multiple_mat_single_shell(self):
        if not self.femelement_table:
            self.femelement_table = FemMeshTools.get_femelement_table(self.femmesh)
        shellth_obj = self.shellthickness_objects[0]['Object']
        FemMeshTools.get_femelement_sets(self.femmesh, self.femelement_table, self.material_objects)
        for mat_data in self.material_objects:
            mat_obj = mat_data['Object']
            ccx_elset = {}
            ccx_elset['shellthickness_obj'] = shellth_obj
            ccx_elset['ccx_elset'] = mat_data['FEMElements']
            ccx_elset['ccx_elset_name'] = get_ccx_elset_shell_name(mat_obj.Name, shellth_obj.Name, mat_data['ShortName'])
            ccx_elset['mat_obj_name'] = mat_obj.Name
            ccx_elset['ccx_mat_name'] = mat_obj.Material['Name']
            self.ccx_elsets.append(ccx_elset)

    def get_ccx_elsets_multiple_mat_solid(self):
        if not self.femelement_table:
            self.femelement_table = FemMeshTools.get_femelement_table(self.femmesh)
        FemMeshTools.get_femelement_sets(self.femmesh, self.femelement_table, self.material_objects)
        for mat_data in self.material_objects:
            mat_obj = mat_data['Object']
            ccx_elset = {}
            ccx_elset['ccx_elset'] = mat_data['FEMElements']
            ccx_elset['ccx_elset_name'] = get_ccx_elset_solid_name(mat_obj.Name, None, mat_data['ShortName'])
            ccx_elset['mat_obj_name'] = mat_obj.Name
            ccx_elset['ccx_mat_name'] = mat_obj.Material['Name']
            self.ccx_elsets.append(ccx_elset)

    def get_ccx_elsets_multiple_mat_multiple_beam(self):
        if not self.femelement_table:
            self.femelement_table = FemMeshTools.get_femelement_table(self.femmesh)
        FemMeshTools.get_femelement_sets(self.femmesh, self.femelement_table, self.beamsection_objects)
        FemMeshTools.get_femelement_sets(self.femmesh, self.femelement_table, self.material_objects)
        for beamsec_data in self.beamsection_objects:
            beamsec_obj = beamsec_data['Object']
            for mat_data in self.material_objects:
                mat_obj = mat_data['Object']
                ccx_elset = {}
                ccx_elset['beamsection_obj'] = beamsec_obj
                elemids = []
                for elemid in beamsec_data['FEMElements']:
                    if elemid in mat_data['FEMElements']:
                        elemids.append(elemid)
                ccx_elset['ccx_elset'] = elemids
                ccx_elset['ccx_elset_name'] = get_ccx_elset_beam_name(mat_obj.Name, beamsec_obj.Name, mat_data['ShortName'], beamsec_data['ShortName'])
                ccx_elset['mat_obj_name'] = mat_obj.Name
                ccx_elset['ccx_mat_name'] = mat_obj.Material['Name']
                self.ccx_elsets.append(ccx_elset)

    def get_ccx_elsets_multiple_mat_multiple_shell(self):
        if not self.femelement_table:
            self.femelement_table = FemMeshTools.get_femelement_table(self.femmesh)
        FemMeshTools.get_femelement_sets(self.femmesh, self.femelement_table, self.shellthickness_objects)
        FemMeshTools.get_femelement_sets(self.femmesh, self.femelement_table, self.material_objects)
        for shellth_data in self.shellthickness_objects:
            shellth_obj = shellth_data['Object']
            for mat_data in self.material_objects:
                mat_obj = mat_data['Object']
                ccx_elset = {}
                ccx_elset['shellthickness_obj'] = shellth_obj
                elemids = []
                for elemid in shellth_data['FEMElements']:
                    if elemid in mat_data['FEMElements']:
                        elemids.append(elemid)
                ccx_elset['ccx_elset'] = elemids
                ccx_elset['ccx_elset_name'] = get_ccx_elset_shell_name(mat_obj.Name, shellth_obj.Name, mat_data['ShortName'], shellth_data['ShortName'])
                ccx_elset['mat_obj_name'] = mat_obj.Name
                ccx_elset['ccx_mat_name'] = mat_obj.Material['Name']
                self.ccx_elsets.append(ccx_elset)


# Helpers
def get_ccx_elset_beam_name(mat_name, beamsec_name, mat_short_name=None, beamsec_short_name=None):
    if not mat_short_name:
        mat_short_name = 'Mat0'
    if not beamsec_short_name:
        beamsec_short_name = 'Beam0'
    if len(mat_name + beamsec_name) > 20:   # max identifier lenght in CalculiX for beam elsets
        return mat_short_name + beamsec_short_name
    else:
        return mat_name + beamsec_name


def get_ccx_elset_shell_name(mat_name, shellth_name, mat_short_name=None, shellth_short_name=None):
    if not mat_short_name:
        mat_short_name = 'Mat0'
    if not shellth_short_name:
        shellth_short_name = 'Shell0'
    if len(mat_name + shellth_name) > 80:   # standard max identifier lenght in CalculiX
        return mat_short_name + shellth_short_name
    else:
        return mat_name + shellth_name


def get_ccx_elset_solid_name(mat_name, solid_name=None, mat_short_name=None):
    if not solid_name:
        solid_name = 'Solid'
    if not mat_short_name:
        mat_short_name = 'Mat0'
    if len(mat_name + solid_name) > 80:   # standard max identifier lenght in CalculiX
        return mat_short_name + solid_name
    else:
        return mat_name + solid_name


def get_three_non_colinear_nodes(nodes_coords):
    # Code to obtain three non-colinear nodes on the PlaneRotation support face
    # nodes_coords --> [(nodenumber, x, y, z), (nodenumber, x, y, z), ...]
    print(len(nodes_coords))
    if nodes_coords:
        print(nodes_coords[0])
        print(nodes_coords[1])
        print(nodes_coords[2])
    else:
        print('Error: No nodes in nodes_coords')
        return []
    dum_max = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    for i in range(len(nodes_coords)):
        for j in range(len(nodes_coords) - 1 - i):
            x_1 = nodes_coords[j][1]
            x_2 = nodes_coords[j + 1][1]
            y_1 = nodes_coords[j][2]
            y_2 = nodes_coords[j + 1][2]
            z_1 = nodes_coords[j][3]
            z_2 = nodes_coords[j + 1][3]
            node_1 = nodes_coords[j][0]
            node_2 = nodes_coords[j + 1][0]
            distance = ((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2 + (z_1 - z_2) ** 2) ** 0.5
            if distance > dum_max[8]:
                dum_max = [node_1, x_1, y_1, z_1, node_2, x_2, y_2, z_2, distance]
    node_dis = [1, 0]
    for i in range(len(nodes_coords)):
        x_1 = dum_max[1]
        x_2 = dum_max[5]
        x_3 = nodes_coords[i][1]
        y_1 = dum_max[2]
        y_2 = dum_max[6]
        y_3 = nodes_coords[i][2]
        z_1 = dum_max[3]
        z_2 = dum_max[7]
        z_3 = nodes_coords[i][3]
        node_3 = int(nodes_coords[j][0])
        distance_1 = ((x_1 - x_3) ** 2 + (y_1 - y_3) ** 2 + (z_1 - z_3) ** 2) ** 0.5
        distance_2 = ((x_3 - x_2) ** 2 + (y_3 - y_2) ** 2 + (z_3 - z_2) ** 2) ** 0.5
        tot = distance_1 + distance_2
        if tot > node_dis[1]:
            node_dis = [node_3, tot]
    node_1 = int(dum_max[0])
    node_2 = int(dum_max[4])
    print([node_1, node_2, node_3])
    return [node_1, node_2, node_3]
