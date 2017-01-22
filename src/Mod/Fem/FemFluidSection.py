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

__title__ = "FemFluidSection"
__author__ = "Ofentse Kgoa"
__url__ = "http://www.freecadweb.org"

## \addtogroup FEM
#  @{

import FreeCAD
import _FemFluidSection


def makeFemFluidSection(name="FluidSection"):
    '''makeFemFluidSection([name]): creates an Fluid section object to define 1D flow'''
    obj = FreeCAD.ActiveDocument.addObject("Fem::FeaturePython", name)
    _FemFluidSection._FemFluidSection(obj)
    if FreeCAD.GuiUp:
        import _ViewProviderFemFluidSection
        _ViewProviderFemFluidSection._ViewProviderFemFluidSection(obj.ViewObject)
    return obj

#  @}
