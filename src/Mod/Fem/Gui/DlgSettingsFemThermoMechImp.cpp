/***************************************************************************
 *   Copyright (c) 2015 FreeCAD Developers                                 *
 *   Author: Przemo Firszt <przemo@firszt.eu>                              *
 *   Based on src/Mod/Raytracing/Gui/DlgSettingsRayImp.cpp                 *
 *                                                                         *
 *   This file is part of the FreeCAD CAx development system.              *
 *                                                                         *
 *   This library is free software; you can redistribute it and/or         *
 *   modify it under the terms of the GNU Library General Public           *
 *   License as published by the Free Software Foundation; either          *
 *   version 2 of the License, or (at your option) any later version.      *
 *                                                                         *
 *   This library  is distributed in the hope that it will be useful,      *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU Library General Public License for more details.                  *
 *                                                                         *
 *   You should have received a copy of the GNU Library General Public     *
 *   License along with this library; see the file COPYING.LIB. If not,    *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,         *
 *   Suite 330, Boston, MA  02111-1307, USA                                *
 *                                                                         *
 ***************************************************************************/


#include "PreCompiled.h"

#include "Gui/Application.h"
#include "DlgSettingsFemThermoMechImp.h"
#include <Gui/PrefWidgets.h>

using namespace FemGui;

DlgSettingsFemThermoMechImp::DlgSettingsFemThermoMechImp( QWidget* parent )
  : PreferencePage( parent )
{
    this->setupUi(this);
}

DlgSettingsFemThermoMechImp::~DlgSettingsFemThermoMechImp()
{
    // no need to delete child widgets, Qt does it all for us
}

void DlgSettingsFemThermoMechImp::saveSettings()
{
    //ParameterGrp::handle hGrp = App::GetApplication().GetParameterGroupByPath
    //    ("User parameter:BaseApp/Preferences/Mod/Fem/ThermoMech");
    
    //OvG: Solver settings for thermo mechanical analysis
    sb_num_increments->onSave();        //Number of increments
    
    //OvG: Material property defaults
    dsb_density_kgm3->onSave();         //Density
    dsb_PR->onSave();                   //Poison Ration
    dsb_SH_JkgK->onSave();              //Specific Heat
    dsb_TEC_mmK->onSave();              //Thermal Expansion Coefficient
    dsb_TC_WmK->onSave();               //Thermal Conductivity
    dsb_YM_Pa->onSave();                //Young's modulus
}

void DlgSettingsFemThermoMechImp::loadSettings()
{
    //OvG: Solver settings for thermo mechanical analysis
    sb_num_increments->onRestore();     //Number of increments
    
    //OvG: Material property defaults
    dsb_density_kgm3->onRestore();      //Density
    dsb_PR->onRestore();                //Poison Ration
    dsb_SH_JkgK->onRestore();           //Specific Heat
    dsb_TEC_mmK->onRestore();           //Thermal Expansion Coefficient
    dsb_TC_WmK->onRestore();            //Thermal Conductivity
    dsb_YM_Pa->onRestore();             //Young's modulus

    //ParameterGrp::handle hGrp = App::GetApplication().GetParameterGroupByPath
    //    ("User parameter:BaseApp/Preferences/Mod/Fem/ThermoMech");
}

/**
 * Sets the strings of the subwidgets using the current language.
 */
void DlgSettingsFemImp::changeEvent(QEvent *e)
{
    if (e->type() == QEvent::LanguageChange) {
    }
    else {
        QWidget::changeEvent(e);
    }
}

#include "moc_DlgSettingsFemThermoMechImp.cpp"
