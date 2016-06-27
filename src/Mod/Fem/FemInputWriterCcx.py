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
import FreeCAD
import os
import sys
import time
import FemMeshTools
import FemInputWriter
import PySide
from PySide import QtCore, QtGui

global switch ; switch = 0
global path
#path = your_directory_path                # your directory path
#path = FreeCAD.ConfigGet("AppHomePath")   # path FreeCAD installation
path = FreeCAD.ConfigGet("UserAppData")    # path FreeCAD User data

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
#Get anlysis preferences from document object       
members=FreeCAD.ActiveDocument.Analysis.Member
for member in members:
     if member.isDerivedFrom("Fem::FemSolverObject"):
        calculixprefs=member  
        
class FemInputWriterCcx(FemInputWriter.FemInputWriter):
    def __init__(self, analysis_obj, solver_obj, mesh_obj, mat_obj,
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
        self.dir_name = dir_name
        self.analysis = analysis_obj
        self.solver = solver_obj
        self.mesh_object = mesh_obj
        self.material_objects = mat_obj
        self.fixed_objects = fixed_obj
        self.force_objects = force_obj
        self.pressure_objects = pressure_obj
        self.displacement_objects = displacement_obj
        self.temperature_objects = temperature_obj
        self.heatflux_objects = heatflux_obj
        self.initialtemperature_objects = initialtemperature_obj
        self.planerotation_objects = planerotation_obj
        self.contact_objects = contact_obj
        if eigenmode_parameters:
            self.no_of_eigenfrequencies = eigenmode_parameters[0]
            self.eigenfrequeny_range_low = eigenmode_parameters[1]
            self.eigenfrequeny_range_high = eigenmode_parameters[2]
        self.analysis_type = analysis_type
        self.beamsection_objects = beamsection_obj
        self.shellthickness_objects = shellthickness_obj
        if not dir_name:
            self.dir_name = FreeCAD.ActiveDocument.TransientDir.replace('\\', '/') + '/FemAnl_' + analysis_obj.Uid[-4:]
        if not os.path.isdir(self.dir_name):
            os.mkdir(self.dir_name)
        FemInputWriter.FemInputWriter.__init__(self, analysis_obj, solver_obj, mesh_obj, mat_obj,
                                               fixed_obj,
                                               force_obj, pressure_obj,
                                               displacement_obj, temperature_obj,
                                               heatflux_obj, initialtemperature_obj,
                                               planerotation_obj,
                                               contact_obj,
                                               beamsection_obj, shellthickness_obj,analysis_type,
                                               eigenmode_parameters, dir_name)
        self.file_name = self.dir_name + '/' + self.mesh_object.Name + '.inp'
        self.fc_ver = FreeCAD.Version()
        self.ccx_eall = 'Eall'
        self.ccx_elsets = []
        self.fem_mesh_nodes = {}
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
        g = open("conflict.txt", 'w') #This file is used to check if MPC and fixed constraint share same nodes, because MPC's and fixed constriants can't share same nodes.
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
                g.write(str(n) + '\n')
        g.close()

    def get_all_nodes(self):
        #obtain all the nodes with their coordinates
        name = ""
        for i in range(len(self.file_name)-4):
            name = name + self.file_name[i] 
        f = open(name+ "_Nodes_elem.inp",'r')
        s_line = f.readline()
        s_line = f.readline()
        l_table = []
        while s_line[0] != "*":
            l_coords = []
            dummy = ""
            for i in range(len(s_line)):
                if (s_line[i] != ",") and (s_line[i] != " "):
                    dummy = dummy + s_line[i]
                elif s_line[i] == ",":
                    dummy = float(dummy)                    
                    l_coords.append(dummy)
                    dummy = ""
            dummy = float(dummy)
            l_coords.append(dummy)
            l_table.append(l_coords)
            s_line = f.readline()     
        return l_table
        
    def write_nodes_elements(self, f,b):
        s_line = f.readline()
        files = open(b+ "_Nodes_elem.inp", 'w')
        while s_line[0] != "B":
            files.write(s_line)
            s_line = f.readline()  
        files.close()
    
    def get_conflict_nodes(self):
        g = open("conflict.txt", 'r')
        testt = g.readline()
        conflict_nodes = []        
        while testt != "":
            testt = int(testt)
            conflict_nodes.append(testt)
            testt = g.readline()
        g.close() 
        import os
        os.remove("conflict.txt")
        return conflict_nodes
        
    def write_node_sets_constraints_planerotation(self, f):
        nodes = self.get_all_nodes()
        conflict_nodes = self.get_conflict_nodes() #conflict nodes obtained for comparison with MPC nodes               
        f.write('\n\n')
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
                #Code to extract nodes and coordinates on the PlaneRotation support face
                nodes_coords = []
                for i in range(len(nodes)):
                    for j in range(len(n)):
                        if nodes[i][0] == l_nodes[j]:
                            nodes_coords.append(nodes[i])
                #Code to obtain three non-colinear nodes on the PlaneRotation support face
                dum_max = [1,2,3,4,5,6,7,8,0]
                for i in range(len(nodes_coords)):
                    for j in range(len(nodes_coords)-1-i):
                        x_1 = nodes_coords[j][1]
                        x_2 = nodes_coords[j+1][1]
                        y_1 = nodes_coords[j][2]
                        y_2 = nodes_coords[j+1][2]
                        z_1 = nodes_coords[j][3]
                        z_2 = nodes_coords[j+1][3]
                        node_1 = nodes_coords[j][0] 
                        node_2 = nodes_coords[j+1][0]
                        distance = ((x_1-x_2)**2 + (y_1-y_2)**2 + (z_1-z_2)**2)**0.5
                        if distance> dum_max[8]:
                            dum_max = [node_1,x_1,y_1,z_1,node_2,x_2,y_2,z_2,distance]
                node_dis = [1,0]
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
                    distance_1 = ((x_1-x_3)**2 + (y_1-y_3)**2 + (z_1-z_3)**2)**0.5
                    distance_2 = ((x_3-x_2)**2 + (y_3-y_2)**2 + (z_3-z_2)**2)**0.5
                    tot = distance_1 + distance_2
                    if tot>node_dis[1]:
                        node_dis = [node_3,tot]
                node_1 = int(dum_max[0])
                node_2 = int(dum_max[4])
                node_planerotation = [node_1,node_2,node_3]
                for i in range(len(l_nodes)):
                    if (l_nodes[i] != node_1) and (l_nodes[i] != node_2) and (l_nodes[i] != node_3):
                        node_planerotation.append(l_nodes[i])
                MPC_nodes = []
                for i in range(len(node_planerotation)):
                    cnt = 0
                    for j in range(len(conflict_nodes)):
                        if node_planerotation[i] == conflict_nodes[j]:
                            cnt = cnt+1
                    if cnt == 0:
                        MPC = node_planerotation[i]                    
                        MPC_nodes.append(MPC)
            
                for i in range(len(MPC_nodes)):
                    f.write(str(MPC_nodes[i]) + ',\n')
                           
    def write_surfaces_contraints_contact(self, f):
        obj = 0        
        for femobj in self.contact_objects:
            contact_obj = femobj['Object']
            cnt = 0
            obj = obj + 1
            for o, elem_tup in contact_obj.References:
                for elem in elem_tup:
                    scc = o.Shape.getElement(elem)
                    cnt = cnt +1                
                    if scc.ShapeType == 'Face':
                        if cnt == 1:
                            name = "DEP" + str(obj)
                        else: 
                            name = "IND" + str(obj)
                        f.write('*SURFACE, NAME =' + name + '\n')                    
                        v = self.mesh_object.FemMesh.getccxVolumesByFace(scc)
                        for i in v:
                            f.write("{},S{}\n".format(i[0], i[1]))                
        
    def write_node_sets_constraints_displacement(self, f):
        g = open("conflict.txt", 'a')
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
                g.write(str(n) + '\n')
        g.close()

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

    def write_node_sets_constraints_force(self, f):
        # check shape type of reference shape
        for femobj in self.force_objects:  # femobj --> dict, FreeCAD document object is femobj['Object']
            frc_obj = femobj['Object']
            # in GUI defined frc_obj all ref_shape have the same shape type
            # TODO in FemTools: check if all RefShapes really have the same type an write type to dictionary
            femobj['RefShapeType'] = ''
            if frc_obj.References:
                first_ref_obj = frc_obj.References[0]
                first_ref_shape = first_ref_obj[0].Shape.getElement(first_ref_obj[1][0])
                femobj['RefShapeType'] = first_ref_shape.ShapeType
            else:
                # frc_obj.References could be empty ! # TODO in FemTools: check
                FreeCAD.Console.PrintError('At least one Force Object has empty References!\n')
            if femobj['RefShapeType'] == 'Vertex':
                #print("load on vertices --> we do not need the femelement_table and femnodes_mesh for node load calculation")
                pass
            elif femobj['RefShapeType'] == 'Face' and FemMeshTools.is_solid_femmesh(self.femmesh) and not FemMeshTools.has_no_face_data(self.femmesh):
                #print("solid_mesh with face data --> we do not need the femelement_table but we need the femnodes_mesh for node load calculation")
                if not self.femnodes_mesh:
                    self.femnodes_mesh = self.femmesh.Nodes
            else:
                #print("mesh without needed data --> we need the femelement_table and femnodes_mesh for node load calculation")
                if not self.femnodes_mesh:
                    self.femnodes_mesh = self.femmesh.Nodes
                if not self.femelement_table:
                    self.femelement_table = FemMeshTools.get_femelement_table(self.femmesh)
        # get node loads
        for femobj in self.force_objects:  # femobj --> dict, FreeCAD document object is femobj['Object']
            frc_obj = femobj['Object']
            if frc_obj.Force == 0:
                print('  Warning --> Force = 0')
            if femobj['RefShapeType'] == 'Vertex':  # point load on vertieces
                femobj['NodeLoadTable'] = FemMeshTools.get_force_obj_vertex_nodeload_table(self.femmesh, frc_obj)
            elif femobj['RefShapeType'] == 'Edge':  # line load on edges
                femobj['NodeLoadTable'] = FemMeshTools.get_force_obj_edge_nodeload_table(self.femmesh, self.femelement_table, self.femnodes_mesh, frc_obj)
            elif femobj['RefShapeType'] == 'Face':  # area load on faces
                femobj['NodeLoadTable'] = FemMeshTools.get_force_obj_face_nodeload_table(self.femmesh, self.femelement_table, self.femnodes_mesh, frc_obj)




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
            density_in_ton_per_mm3 = 1
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
                density_in_ton_per_mm3 = float(density.getValueAs('t/mm^3'))
            except:
                FreeCAD.Console.PrintError("No Density defined for material: default used\n")
            f.write('*DENSITY \n')
            f.write('{0:.3e}, \n'.format(density_in_ton_per_mm3))
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
        f.write('*STEP')
        if calculixprefs.NonLinearGeometry:
            f.write(',NLGEOM\n')
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
        for fixed_object in self.fixed_objects:
            fix_obj_name = fixed_object['Object'].Name
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

    def write_constraints_planerotation(self,f):
        dummy = 0
        for fric_object in self.planerotation_objects:
            dummy = dummy +1
            fric_obj_name = fric_object['Object'].Name
            f.write('*MPC\n')
            f.write('PLANE,' + fric_obj_name  +'\n')
            f.write('\n')
        if dummy >= 1:
            f.write('\n***********************************************************\n')
            f.write('** PlaneRotation Constraints\n')
            f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
    
    def write_constraints_contact(self,f):
        f.write('\n***********************************************************\n')
        f.write('** Contact Constraints\n')
        f.write('** written by {} function\n'.format(sys._getframe().f_code.co_name))
        obj = 0        
        for contact_object in self.contact_objects:
            obj = obj + 1            
            ctct_obj = contact_object['Object']             
            f.write('*CONTACT PAIR, INTERACTION=INT' + str(obj) +',TYPE=SURFACE TO SURFACE\n')
            ind_surf = "IND" + str(obj)
            dep_surf = "DEP" + str(obj)            
            f.write(dep_surf+',' + ind_surf+ '\n')
            f.write('*SURFACE INTERACTION, NAME=INT' + str(obj) +'\n')
            f.write('*SURFACE BEHAVIOR,PRESSURE-OVERCLOSURE=LINEAR\n')
            Slope = ctct_obj.Slope 
            f.write(str(Slope) + ' \n')
            F = ctct_obj.Friction
            if F > 0:
                f.write('*FRICTION \n')
                F = str(F)
                stick =(Slope/10.0)                 
                f.write(F +', ' +str(stick)+ ' \n')

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

    def get_femelement_sets(self, fem_objects):
        # get femelements for reference shapes of each obj.References
        if not hasattr(self, 'fem_element_table'):
            self.fem_element_table = getFemElementTable(self.mesh_object.FemMesh)
        count_femelements = 0
        referenced_femelements = []
        has_remaining_femelements = None
        for fem_object_i, fem_object in enumerate(fem_objects):
            obj = fem_object['Object']
            fem_object['ShortName'] = get_ccx_elset_short_name(obj, fem_object_i)  # unique short ccx_identifier
            if obj.References:
                ref_shape_femelements = []
                for ref in obj.References:
                    femnodes = []
                    femelements = []
                    if ref[1]:
                        r = ref[0].Shape.getElement(ref[1])
                    else:
                        r = ref[0].Shape
                    # print('  ReferenceShape : ', r.ShapeType, ', ', ref[0].Name, ', ', ref[0].Label, ' --> ', ref[1])
                    if r.ShapeType == 'Edge':
                        femnodes = self.mesh_object.FemMesh.getNodesByEdge(r)
                    elif r.ShapeType == 'Face':
                        femnodes = self.mesh_object.FemMesh.getNodesByFace(r)
                    elif r.ShapeType == 'Solid':
                        femnodes = self.mesh_object.FemMesh.getNodesBySolid(r)
                    else:
                        print('  No Edge, Face or Solid as reference shapes!')
                    femelements = getFemElementsByNodes(self.fem_element_table, femnodes)
                    ref_shape_femelements += femelements
                    referenced_femelements += femelements
                    count_femelements += len(femelements)
                fem_object['FEMElements'] = ref_shape_femelements
            else:
                has_remaining_femelements = obj.Name
        # get remaining femelements for the fem_objects
        if has_remaining_femelements:
            remaining_femelements = []
            for elemid in self.fem_element_table:
                if elemid not in referenced_femelements:
                    remaining_femelements.append(elemid)
            count_femelements += len(remaining_femelements)
            for fem_object in fem_objects:
                obj = fem_object['Object']
                if obj.Name == has_remaining_femelements:
                    fem_object['FEMElements'] = sorted(remaining_femelements)
        # check if all worked out well
        if not femelements_count_ok(self.fem_element_table, count_femelements):
            FreeCAD.Console.PrintError('Error in get_femelement_sets -- > femelements_count_ok failed!\n')

    def get_refedge_node_table(self, refedge):
        edge_table = {}  # { meshedgeID : ( nodeID, ... , nodeID ) }
        refedge_nodes = self.mesh_object.FemMesh.getNodesByEdge(refedge)
        if is_solid_mesh(self.mesh_object.FemMesh):
            refedge_fem_volumeelements = []
            # if at least two nodes of a femvolumeelement are in refedge_nodes the volume is added to refedge_fem_volumeelements
            for elem in self.fem_element_table:
                nodecount = 0
                for node in self.fem_element_table[elem]:
                    if node in refedge_nodes:
                        nodecount += 1
                if nodecount > 1:
                    refedge_fem_volumeelements.append(elem)
            # for every refedge_fem_volumeelement look which of his nodes is in refedge_nodes --> add all these nodes to edge_table
            for elem in refedge_fem_volumeelements:
                fe_refedge_nodes = []
                for node in self.fem_element_table[elem]:
                    if node in refedge_nodes:
                        fe_refedge_nodes.append(node)
                    edge_table[elem] = fe_refedge_nodes  # { volumeID : ( edgenodeID, ... , edgenodeID  )} # only the refedge nodes
            #  FIXME duplicate_mesh_elements: as soon as contact ans springs are supported the user should decide on which edge the load is applied
            edge_table = delete_duplicate_mesh_elements(edge_table)
        elif is_shell_mesh(self.mesh_object.FemMesh):
            refedge_fem_faceelements = []
            # if at least two nodes of a femfaceelement are in refedge_nodes the volume is added to refedge_fem_volumeelements
            for elem in self.fem_element_table:
                nodecount = 0
                for node in self.fem_element_table[elem]:
                    if node in refedge_nodes:
                        nodecount += 1
                if nodecount > 1:
                    refedge_fem_faceelements.append(elem)
            # for every refedge_fem_faceelement look which of his nodes is in refedge_nodes --> add all these nodes to edge_table
            for elem in refedge_fem_faceelements:
                fe_refedge_nodes = []
                for node in self.fem_element_table[elem]:
                    if node in refedge_nodes:
                        fe_refedge_nodes.append(node)
                    edge_table[elem] = fe_refedge_nodes  # { faceID : ( edgenodeID, ... , edgenodeID  )} # only the refedge nodes
            #  FIXME duplicate_mesh_elements: as soon as contact ans springs are supported the user should decide on which edge the load is applied
            edge_table = delete_duplicate_mesh_elements(edge_table)
        elif is_beam_mesh(self.mesh_object.FemMesh):
            refedge_fem_edgeelements = getFemElementsByNodes(self.fem_element_table, refedge_nodes)
            for elem in refedge_fem_edgeelements:
                edge_table[elem] = self.fem_element_table[elem]  # { edgeID : ( nodeID, ... , nodeID  )} # all nodes off this femedgeelement
        return edge_table

    def get_ref_face_node_table(self, ref_face):
        face_table = {}  # { meshfaceID : ( nodeID, ... , nodeID ) }
        if is_solid_mesh(self.mesh_object.FemMesh):
            if has_no_face_data(self.mesh_object.FemMesh):
                # there is no face data, the volumeID is used as key { volumeID : ( facenodeID, ... , facenodeID ) } only the ref_face nodes
                ref_face_volume_elements = self.mesh_object.FemMesh.getccxVolumesByFace(ref_face)  # list of tupels (mv, ccx_face_nr)
                ref_face_nodes = self.mesh_object.FemMesh.getNodesByFace(ref_face)
                for ve in ref_face_volume_elements:
                    veID = ve[0]
                    ve_ref_face_nodes = []
                    for nodeID in self.fem_element_table[veID]:
                        if nodeID in ref_face_nodes:
                            ve_ref_face_nodes.append(nodeID)
                    face_table[veID] = ve_ref_face_nodes  # { volumeID : ( facenodeID, ... , facenodeID ) } only the ref_face nodes
            else:  # the femmesh has face_data
                volume_faces = self.mesh_object.FemMesh.getVolumesByFace(ref_face)   # (mv, mf)
                for mv, mf in volume_faces:
                    face_table[mf] = self.mesh_object.FemMesh.getElementNodes(mf)
        elif is_shell_mesh(self.mesh_object.FemMesh):
            ref_face_nodes = self.mesh_object.FemMesh.getNodesByFace(ref_face)
            ref_face_elements = getFemElementsByNodes(self.fem_element_table, ref_face_nodes)
            for mf in ref_face_elements:
                face_table[mf] = self.fem_element_table[mf]
        return face_table

    def get_refedge_node_lengths(self, edge_table):
        # calulate the appropriate node_length for every node of every mesh edge (me)
        # G. Lakshmi Narasaiah, Finite Element Analysis, p206ff

        #  [ (nodeID, length), ... , (nodeID, length) ]  some nodes will have more than one entry
        node_length_table = []
        mesh_edge_length = 0
        if not self.fem_mesh_nodes:
            self.fem_mesh_nodes = self.mesh_object.FemMesh.Nodes
        # print(len(edge_table))
        for me in edge_table:
            if len(edge_table[me]) == 2:  # 2 node mesh edge
                # end_node_length = mesh_edge_length / 2
                #    ______
                #  P1      P2
                P1 = self.fem_mesh_nodes[edge_table[me][0]]
                P2 = self.fem_mesh_nodes[edge_table[me][1]]
                edge_vec = P2 - P1
                mesh_edge_length = edge_vec.Length
                # print(mesh_edge_length)
                end_node_length = mesh_edge_length / 2.0
                node_length_table.append((edge_table[me][0], end_node_length))
                node_length_table.append((edge_table[me][1], end_node_length))

            elif len(edge_table[me]) == 3:  # 3 node mesh edge
                # end_node_length = mesh_edge_length / 6
                # middle_node_length = mesh_face_area * 2 / 3
                #   _______ _______
                # P1       P3      P2
                P1 = self.fem_mesh_nodes[edge_table[me][0]]
                P2 = self.fem_mesh_nodes[edge_table[me][1]]
                P3 = self.fem_mesh_nodes[edge_table[me][2]]
                edge_vec1 = P3 - P1
                edge_vec2 = P2 - P3
                mesh_edge_length = edge_vec1.Length + edge_vec2.Length
                # print(me, ' --> ', mesh_edge_length)
                end_node_length = mesh_edge_length / 6.0
                middle_node_length = mesh_edge_length * 2.0 / 3.0
                node_length_table.append((edge_table[me][0], end_node_length))
                node_length_table.append((edge_table[me][1], end_node_length))
                node_length_table.append((edge_table[me][2], middle_node_length))
        return node_length_table

    def get_ref_face_node_areas(self, face_table):
        # calulate the appropriate node_areas for every node of every mesh face (mf)
        # G. Lakshmi Narasaiah, Finite Element Analysis, p206ff
        # FIXME only gives exact results in case of a real triangle. If for S6 or C3D10 elements
        # the midnodes are not on the line between the end nodes the area will not be a triangle
        # see http://forum.freecadweb.org/viewtopic.php?f=18&t=10939&start=40#p91355  and ff

        #  [ (nodeID,Area), ... , (nodeID,Area) ]  some nodes will have more than one entry
        node_area_table = []
        mesh_face_area = 0
        if not self.fem_mesh_nodes:
            self.fem_mesh_nodes = self.mesh_object.FemMesh.Nodes
        for mf in face_table:
            if len(face_table[mf]) == 3:  # 3 node mesh face triangle
                # corner_node_area = mesh_face_area / 3.0
                #      P3
                #      /\
                #     /  \
                #    /____\
                #  P1      P2
                P1 = self.fem_mesh_nodes[face_table[mf][0]]
                P2 = self.fem_mesh_nodes[face_table[mf][1]]
                P3 = self.fem_mesh_nodes[face_table[mf][2]]

                mesh_face_area = getTriangleArea(P1, P2, P3)
                corner_node_area = mesh_face_area / 3.0

                node_area_table.append((face_table[mf][0], corner_node_area))
                node_area_table.append((face_table[mf][1], corner_node_area))
                node_area_table.append((face_table[mf][2], corner_node_area))

            elif len(face_table[mf]) == 4:  # 4 node mesh face quad
                FreeCAD.Console.PrintError('Face load on 4 node quad faces are not supported\n')

            elif len(face_table[mf]) == 6:  # 6 node mesh face triangle
                # corner_node_area = 0
                # middle_node_area = mesh_face_area / 3.0
                #         P3
                #         /\
                #        /t3\
                #       /    \
                #     P6------P5
                #     / \ t4 / \
                #    /t1 \  /t2 \
                #   /_____\/_____\
                # P1      P4      P2
                P1 = self.fem_mesh_nodes[face_table[mf][0]]
                P2 = self.fem_mesh_nodes[face_table[mf][1]]
                P3 = self.fem_mesh_nodes[face_table[mf][2]]
                P4 = self.fem_mesh_nodes[face_table[mf][3]]
                P5 = self.fem_mesh_nodes[face_table[mf][4]]
                P6 = self.fem_mesh_nodes[face_table[mf][5]]

                mesh_face_t1_area = getTriangleArea(P1, P4, P6)
                mesh_face_t2_area = getTriangleArea(P2, P5, P4)
                mesh_face_t3_area = getTriangleArea(P3, P6, P5)
                mesh_face_t4_area = getTriangleArea(P4, P5, P6)
                mesh_face_area = mesh_face_t1_area + mesh_face_t2_area + mesh_face_t3_area + mesh_face_t4_area
                middle_node_area = mesh_face_area / 3.0

                node_area_table.append((face_table[mf][0], 0))
                node_area_table.append((face_table[mf][1], 0))
                node_area_table.append((face_table[mf][2], 0))
                node_area_table.append((face_table[mf][3], middle_node_area))
                node_area_table.append((face_table[mf][4], middle_node_area))
                node_area_table.append((face_table[mf][5], middle_node_area))

            elif len(face_table[mf]) == 8:  # 8 node mesh face quad
                FreeCAD.Console.PrintError('Face load on 8 node quad faces are not supported\n')
        return node_area_table

    def get_ref_shape_node_sum_geom_table(self, node_geom_table):
        # shape could be Edge or Face, geom could be lenght or area
        # summ of legth or area for each node of the ref_shape
        node_sum_geom_table = {}
        for n, A in node_geom_table:
            # print(n, ' --> ', A)
            if n in node_sum_geom_table:
                node_sum_geom_table[n] = node_sum_geom_table[n] + A
            else:
                node_sum_geom_table[n] = A
        return node_sum_geom_table


# Helpers
def getTriangleArea(P1, P2, P3):
    vec1 = P2 - P1
    vec2 = P3 - P1
    vec3 = vec1.cross(vec2)
    return 0.5 * vec3.Length


def getFemElementTable(fem_mesh):
    """ getFemElementTable(fem_mesh): { elementid : [ nodeid, nodeid, ... , nodeid ] }"""
    fem_element_table = {}
    if is_solid_mesh(fem_mesh):
        for i in fem_mesh.Volumes:
            fem_element_table[i] = fem_mesh.getElementNodes(i)
    elif is_shell_mesh(fem_mesh):
        for i in fem_mesh.Faces:
            fem_element_table[i] = fem_mesh.getElementNodes(i)
    elif is_beam_mesh(fem_mesh):
        for i in fem_mesh.Edges:
            fem_element_table[i] = fem_mesh.getElementNodes(i)
    else:
        FreeCAD.Console.PrintError('Neither solid nor shell nor beam mesh!\n')
    return fem_element_table


def getFemElementsByNodes(fem_element_table, node_list):
    '''for every fem_element of fem_element_table
    if all nodes of the fem_element are in node_list,
    the fem_element is added to the list which is returned
    e: elementlist
    nodes: nodelist '''
    e = []  # elementlist
    for elementID in sorted(fem_element_table):
        nodecount = 0
        for nodeID in fem_element_table[elementID]:
            if nodeID in node_list:
                nodecount = nodecount + 1
        if nodecount == len(fem_element_table[elementID]):   # all nodes of the element are in the node_list!
            e.append(elementID)
    return e


def is_solid_mesh(fem_mesh):
    if fem_mesh.VolumeCount > 0:  # solid mesh
        return True


def has_no_face_data(fem_mesh):
    if fem_mesh.FaceCount == 0:   # mesh has no face data, could be a beam mesh or a solid mesh without face data
        return True


def is_shell_mesh(fem_mesh):
    if fem_mesh.VolumeCount == 0 and fem_mesh.FaceCount > 0:  # shell mesh
        return True


def is_beam_mesh(fem_mesh):
    if fem_mesh.VolumeCount == 0 and fem_mesh.FaceCount == 0 and fem_mesh.EdgeCount > 0:  # beam mesh
        return True


def femelements_count_ok(fem_element_table, count_femelements):
    if count_femelements == len(fem_element_table):
        # print('Count Elements written to CalculiX file: ', count_femelements)
        # print('Count Elements of the FreeCAD FEM Mesh:  ', len(fem_element_table))
        return True
    else:
        print('ERROR: self.fem_element_table != count_femelements')
        print('Count Elements written to CalculiX file: ', count_femelements)
        print('Count Elements of the FreeCAD FEM Mesh:  ', len(fem_element_table))
        return False


def delete_duplicate_mesh_elements(refelement_table):
    new_refelement_table = {}  # duplicates deleted
    for elem, nodes in refelement_table.items():
        if sorted(nodes) not in sortlistoflistvalues(new_refelement_table.values()):
            new_refelement_table[elem] = nodes
    return new_refelement_table


def sortlistoflistvalues(listoflists):
    new_list = []
    for l in listoflists:
        new_list.append(sorted(l))
    return new_list


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


def get_ccx_elset_short_name(obj, i):
    if hasattr(obj, "Proxy") and obj.Proxy.Type == 'MechanicalMaterial':
        return 'Mat' + str(i)
    elif hasattr(obj, "Proxy") and obj.Proxy.Type == 'FemBeamSection':
        return 'Beam' + str(i)
    elif hasattr(obj, "Proxy") and obj.Proxy.Type == 'FemShellThickness':
        return 'Shell' + str(i)
    else:
        print('Error: ', obj.Name, ' --> ', obj.Proxy.Type)
