# ***************************************************************************
# *   Copyright (c) 2015 - FreeCAD Developers                               *
# *   Author: Przemo Firszt <przemo@firszt.eu>                              *
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

__title__ = "importCcxDatResults"
__author__ = "Przemo Firszt, Bernd Hahnebach"
__url__ = "http://www.freecadweb.org"

## @package importCcxDatResults
#  \ingroup FEM
#  \brief FreeCAD Calculix DAT reader for FEM workbench

import FreeCAD
import os
import numpy as np

EIGENVALUE_OUTPUT_SECTION = "     E I G E N V A L U E   O U T P U T"
INTERNAL_STATE_VAR= "internal state variables"
volume_foundstr="volume (element, volume)"

# ********* generic FreeCAD import and export methods *********
if open.__module__ == '__builtin__':
    # because we'll redefine open below (Python2)
    pyopen = open
elif open.__module__ == 'io':
    # because we'll redefine open below (Python3)
    pyopen = open


def open(
    filename
):
    "called when freecad opens a file"
    docname = os.path.splitext(os.path.basename(filename))[0]
    insert(filename, docname)


def insert(
    filename,
    docname
):
    "called when freecad wants to import a file"
    try:
        doc = FreeCAD.getDocument(docname)
    except NameError:
        doc = FreeCAD.newDocument(docname)
    FreeCAD.ActiveDocument = doc
    import_dat(filename)


# ********* module specific methods *********
def import_dat(
    r = readResult(filename)
    # print("Results {}".format(r))
    return r


# read a calculix result file and extract the data
def readResult(dat_input):
    print('Read ccx results from dat file: ' + dat_input)
    with pyopen(dat_input, "a") as myfile:
        myfile.write('end \n')  # Add extra line to indicate end
        myfile.close()
    dat_file = pyopen(dat_input, "r")
    eigenvalue_output_section_found = False
    mode_reading = False
    results = []      
    state_variables_found =False
    volume_found=False
    delim=' '
    empty=0
    step=0
    vstep=0
    cols = {}
    cells = []
    time = []
    m = {}



    for line in dat_file:
        if EIGENVALUE_OUTPUT_SECTION in line:
            # Found EIGENVALUE_OUTPUT_SECTION
            eigenvalue_output_section_found = True
        if eigenvalue_output_section_found:
            try:
                mode = int(line[0:7])
                mode_frequency = float(line[39:55])
                m = {}
                m['eigenmode'] = mode
                m['frequency'] = mode_frequency
                results.append(m)
                mode_reading = True
            except:
                if mode_reading:
                    # Conversion error after mode reading started, so it's the end of section
                    eigenvalue_output_section_found = False
                    mode_reading = False

        if INTERNAL_STATE_VAR in line:
            # Found state variables
            state_variables_found =True
            time = float(line[75:89])
            cells =[]   
            newcells=[]     
          
            continue          
        if state_variables_found:  
            if line == '\n' or line == 'end \n': 
                empty=empty+1
                if empty == 2 or line == 'end \n':  
                    cells = np.array(cells)
                    elnums=np.unique(cells[:,0]) #Get unique Element numbers
                    newcells = np.zeros([len(elnums),np.shape(cells)[1]])
                    idx=0
                    for elnum in elnums:
                        subcel=cells[np.where(cells[:,0] == elnum)]
                        subcel=(subcel.mean(axis=0))
                        subcel=np.reshape(subcel,[1,len(subcel)])
                        newcells[int(idx),:] = subcel
                        idx+=1                   
                    time_array = np.ones([len(newcells),1])*time  
                    newcells = np.hstack([time_array,newcells])
                    m['state'+str(step)] = newcells
                    results.append(m)
                    empty=0
                    step+= 1
                    state_variables_found =False             
            elif line != 'end \n':
                cells.append([np.float(x) for x in line.split(delim) if x != ''])
        if volume_foundstr in line:
            # Found volume
            volume_found =True
            time = float(line[50:63])
            vcells =[] 
            vnewcells=[]
          
            continue          
        if volume_found:  
            if line == '\n' or line == 'end \n': 
                empty=empty+1
                if empty == 2 or line == 'end \n':  
                    
                    vcells = np.array(vcells)
                    elnums=np.unique(vcells[:,0]) #Get unique Element numbers
                    vnewcells = np.zeros([len(elnums),np.shape(vcells)[1]])
                    idx=0
                    for elnum in elnums:
                        subcel=vcells[np.where(vcells[:,0] == elnum)]
                        vnewcells[int(idx),:] = subcel
                        idx+=1                   
                    time_array = np.ones([len(vnewcells),1])*time  
                    vnewcells = np.hstack([time_array,vnewcells])
                    m['vol'+str(vstep)] = vnewcells
                    results.append(m)
                    empty=0
                    vstep+= 1
                    volume_found =False          
            elif line != 'end \n':
                vcells.append([np.float(x) for x in line.split(delim) if x != ''])



    dat_file.close()
    return results
