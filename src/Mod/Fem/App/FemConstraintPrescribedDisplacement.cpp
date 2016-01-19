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
#include <gp_Pnt.hxx>
#include <gp_Pln.hxx>
#include <gp_Lin.hxx>
#include <BRepAdaptor_Curve.hxx>
#include <BRepAdaptor_Surface.hxx>
#include <GCPnts_AbscissaPoint.hxx>
#include <Adaptor3d_IsoCurve.hxx>
#include <Adaptor3d_HSurface.hxx>
#include <BRepAdaptor_HSurface.hxx>
#include <GProp_GProps.hxx>
#include <BRepGProp.hxx>
#include <TopoDS_Vertex.hxx>
#include <TopoDS.hxx>
#include <BRepClass_FaceClassifier.hxx>
#include <BRep_Tool.hxx>
#include <Precision.hxx>
#endif

#include "FemConstraintFixed.h"

#include <Mod/Part/App/PartFeature.h>
#include <Base/Console.h>

using namespace Fem;

PROPERTY_SOURCE(Fem::ConstraintPrescribedDisplacement, Fem::Constraint);

ConstraintPrescribedDisplacement::ConstraintPrescribedDisplacement()
{
    ADD_PROPERTY_TYPE(Points,(Base::Vector3d()),"ConstraintPrescribedDisplacement",App::PropertyType(App::Prop_ReadOnly|App::Prop_Output),
                      "Points where symbols are drawn");
    ADD_PROPERTY_TYPE(Normals,(Base::Vector3d()),"ConstraintPrescribedDisplacement",App::PropertyType(App::Prop_ReadOnly|App::Prop_Output),
                                                                             "Normals where symbols are drawn");
    Points.setValues(std::vector<Base::Vector3d>());
    Normals.setValues(std::vector<Base::Vector3d>());
    
    xDisplacement = 0.0; //0.0
    yDisplacement = 0.0; //0.0
    zDisplacement= 0.0; //0.0
    xRotation= 0.0;
    yRotation= 0.0;
    zRotation= 0.0;
    xFree = true;
    yFree = true;
    zFree = true;
    xFix = false;
    yFix = false;
    zFix = false;
    rotxFree = true;
    rotyFree = true;
    rotzFree = true;
    rotxFix = false;
    rotyFix = false;
    rotzFix = false;
    element = false;
}

App::DocumentObjectExecReturn *ConstraintPrescribedDisplacement::execute(void)
{
    return Constraint::execute();
}

void ConstraintPrescribedDisplacement::onChanged(const App::Property* prop)
{
    // Note: If we call this at the end, then the symbols are not oriented correctly initially
    // because the NormalDirection has not been calculated yet
    Constraint::onChanged(prop);

    if (prop == &References) {
        std::vector<Base::Vector3d> points;
        std::vector<Base::Vector3d> normals;
        if (getPoints(points, normals)) {
            Points.setValues(points);
            Normals.setValues(normals);
            Points.touch(); // This triggers ViewProvider::updateData()
        }
    }
}
