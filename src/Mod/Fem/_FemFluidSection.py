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

__title__ = "_FemFluidSection"
__author__ = "Ofentse Kgoa"
__url__ = "http://www.freecadweb.org"

## @package FemFluidSection
#  \ingroup FEM


class _FemFluidSection:
    "The FemFluidSection object"
    
    known_fluid_types = ['Liquid', 'Gas', 'Open Channel']
    known_liquid_types = ['PIPE MANNING', 'PIPE ENLARGEMENT', 'PIPE CONTRACTION', 'PIPE INLET', 'PIPE OUTLET']
    known_gas_types = ['NONE']
    known_channel_types = ['NONE']

    def __init__(self, obj):
        obj.addProperty("App::PropertyLinkSubList", "References", "FluidSection", "List of fluid section shapes")
        obj.addProperty("App::PropertyEnumeration", "SectionType", "FluidSection", "select fluid section type")
        obj.addProperty("App::PropertyEnumeration", "LiquidSectionType", "LiquidSection", "select liquid section type")
        obj.addProperty("App::PropertyArea", "ManningArea", "LiquidManning", "set area of the manning fluid section")
        obj.addProperty("App::PropertyLength", "ManningRadius", "LiquidManning", "set hydraulic radius of manning fluid section")
        obj.addProperty("App::PropertyFloat", "ManningCoefficient", "LiquidManning", "set coefficient of manning fluid section")
        obj.addProperty("App::PropertyArea", "EnlargeArea1", "LiquidEnlargement", "set intial area of the enlargement fluid section")
        obj.addProperty("App::PropertyArea", "EnlargeArea2", "LiquidEnlargement", "set enlarged area of enlargement fluid section")
        obj.addProperty("App::PropertyArea", "ContractArea1", "LiquidContraction", "set intial area of the contraction fluid section")
        obj.addProperty("App::PropertyArea", "ContractArea2", "LiquidContraction", "set contracted area of contraction fluid section")
        obj.addProperty("App::PropertyFloat", "InletPressure", "LiquidInlet", "set inlet pressure for fluid section")
        obj.addProperty("App::PropertyFloat", "OutletPressure", "LiquidOutlet", "set outlet pressure for fluid section")
        obj.addProperty("App::PropertyFloat", "InletFlowRate", "LiquidInlet", "set inlet mass flow rate for fluid section")
        obj.addProperty("App::PropertyFloat", "OutletFlowRate", "LiquidOutlet", "set outlet mass flow rate for fluid section")
        obj.addProperty("App::PropertyBool", "InletPressureActive", "LiquidInlet", "activates or deactivates inlet pressure for fluid section")
        obj.addProperty("App::PropertyBool", "OutletPressureActive", "LiquidOutlet", "activates or deactivates outlet pressure for fluid section")
        obj.addProperty("App::PropertyBool", "InletFlowRateActive", "LiquidInlet", "activates or deactivates inlet flow rate for fluid section")
        obj.addProperty("App::PropertyBool", "OutletFlowRateActive", "LiquidOutlet", "activates or deactivates outlet flow rate for fluid section")
        obj.addProperty("App::PropertyEnumeration", "GasSectionType", "GasSection", "select gas section type")
        obj.addProperty("App::PropertyEnumeration", "ChannelSectionType", "ChannelSection", "select channel section type")

        # set property default values
        obj.SectionType = _FemFluidSection.known_fluid_types
        obj.SectionType = 'Liquid'
        obj.LiquidSectionType = _FemFluidSection.known_liquid_types
        obj.LiquidSectionType = 'PIPE INLET'
        obj.GasSectionType = _FemFluidSection.known_gas_types
        obj.GasSectionType = 'NONE'
        obj.ChannelSectionType = _FemFluidSection.known_channel_types
        obj.ChannelSectionType = 'NONE'
        obj.ManningArea = 10.0
        obj.ManningRadius = 1.0
        obj.ManningCoefficient = 0.5
        obj.EnlargeArea1 = 10.0
        obj.EnlargeArea2 = 20.0
        obj.ContractArea1 = 20.0
        obj.ContractArea2 = 10.0
        obj.ContractArea2 = 10.0
        obj.InletPressure = 1.0
        obj.OutletPressure = 1.0
        obj.InletFlowRate = 1.0
        obj.OutletFlowRate = 1.0
        obj.InletPressureActive = True
        obj.OutletPressureActive = True
        obj.InletFlowRateActive = False
        obj.OutletFlowRateActive = False
        obj.Proxy = self
        self.Type = "FemFluidSection"

    def execute(self, obj):
        return
