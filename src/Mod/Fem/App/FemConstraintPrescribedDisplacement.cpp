/***************************************************************************
 *   Copyright (c) 2013 Jan Rheinl채nder <jrheinlaender[at]users.sourceforge.net>     *
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

#ifndef _PreComp_
#include <BRepAdaptor_Curve.hxx>
#include <BRepAdaptor_Surface.hxx>
#include <Precision.hxx>
#include <TopoDS.hxx>
#include <gp_Lin.hxx>
#include <gp_Pln.hxx>
#include <gp_Pnt.hxx>
#endif

#include "FemConstraintPrescribedDisplacement.h"

using namespace Fem;

PROPERTY_SOURCE(Fem::ConstraintPrescribedDisplacement, Fem::Constraint);

ConstraintPrescribedDisplacement::ConstraintPrescribedDisplacement()
{
    ADD_PROPERTY(xDisplacement,(0.0)); 
    ADD_PROPERTY(yDisplacement,(0.0)); 
    ADD_PROPERTY(zDisplacement,(0.0)); 
    ADD_PROPERTY(xRotation,(0.0)); 
    ADD_PROPERTY(yRotation,(0.0)); 
    ADD_PROPERTY(zRotation,(0.0)); 
    ADD_PROPERTY(xFree,(1)); 
    ADD_PROPERTY(yFree,(1)); 
    ADD_PROPERTY(zFree,(1)); 
    ADD_PROPERTY(xFix,(0)); 
    ADD_PROPERTY(yFix,(0)); 
    ADD_PROPERTY(zFix,(0)); 
    ADD_PROPERTY(rotxFree,(1)); 
    ADD_PROPERTY(rotyFree,(1)); 
    ADD_PROPERTY(rotzFree,(1)); 
    ADD_PROPERTY(rotxFix,(0));
    ADD_PROPERTY(rotyFix,(0));
    ADD_PROPERTY(rotzFix,(0));
}

App::DocumentObjectExecReturn *ConstraintPrescribedDisplacement::execute(void)
{
    return Constraint::execute();
}

const char* ConstraintPrescribedDisplacement::getViewProviderName(void) const
{
	return "FemGui::ViewProviderFemConstraintPrescribedDisplacement";
}
