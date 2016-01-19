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


#ifndef FEM_CONSTRAINTFIXED_H
#define FEM_CONSTRAINTFIXED_H

#include <App/DocumentObject.h>
#include <App/PropertyLinks.h>
#include <App/PropertyGeo.h>

#include "FemConstraint.h"

namespace Fem
{

class AppFemExport ConstraintPrescribedDisplacement : public Fem::Constraint
{
    PROPERTY_HEADER(Fem::ConstraintPrescribedDisplacement);

public:
    /// Constructor
    ConstraintPrescribedDisplacement(void);

    // Read-only (calculated values). These trigger changes in the ViewProvider
    App::PropertyVectorList Points;
    App::PropertyVectorList Normals;

    //Displacement settings
    App::PropertyFloat  xDisplacement; //0.0
    App::PropertyFloat yDisplacement; //0.0
    App::PropertyFloat zDisplacement; //0.0
    App::PropertyFloat xRotation;
    App::PropertyFloat yRotation;
    App::PropertyFloat zRotation;
    App::PropertyBool xFree;
    App::PropertyBool yFree;
    App::PropertyBool zFree;
    App::PropertyBool xFix;
    App::PropertyBool yFix;
    App::PropertyBool zFix;
    App::PropertyBool rotxFree;
    App::PropertyBool rotyFree;
    App::PropertyBool rotzFree;
    App::PropertyBool rotxFix;
    App::PropertyBool rotyFix;
    App::PropertyBool rotzFix;
    App::PropertyBool element;

    /// recalculate the object
    virtual App::DocumentObjectExecReturn *execute(void);

    /// returns the type name of the ViewProvider
    const char* getViewProviderName(void) const {
        return "FemGui::ViewProviderFemConstraintPrescribedDisplacement";
    }

protected:
    virtual void onChanged(const App::Property* prop);
};

} //namespace Fem


#endif // FEM_CONSTRAINTFIXED_H
