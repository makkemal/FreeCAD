/***************************************************************************
 *   Copyright (c) 2015 FreeCAD Developers                                 *
 *   Authors: Michael Hindley <hindlemp@eskom.co.za>                       *
 *            Ruan Olwagen <olwager@eskom.co.za>                           *
 *            Oswald van Ginkel <vginkeo@eskom.co.za>                      *
 *   Based on Force constraint by Jan Rheinländer                          *
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
# include <Standard_math.hxx>
# include <Inventor/nodes/SoSeparator.h>
# include <Inventor/nodes/SoTranslation.h>
# include <Inventor/nodes/SoRotation.h>
# include <Inventor/nodes/SoMultipleCopy.h>
# include <Inventor/nodes/SoCylinder.h>
# include <Inventor/nodes/SoSphere.h>
# include <Inventor/nodes/SoText3.h>
# include <Inventor/nodes/SoFont.h>
# include <Inventor/nodes/SoMaterial.h>
# include <Inventor/nodes/SoMaterialBinding.h>
# include <Inventor/nodes/SoScale.h>
# include <Precision.hxx>
#endif

#include "Mod/Fem/App/FemConstraint1dpipeflow.h"
#include "TaskFemConstraint1dpipeflow.h"
#include "ViewProviderFemConstraint1dpipeflow.h"
#include <Base/Console.h>
#include <Gui/Control.h>

using namespace FemGui;

PROPERTY_SOURCE(FemGui::ViewProviderFemConstraint1dpipeflow, FemGui::ViewProviderFemConstraint)

ViewProviderFemConstraint1dpipeflow::ViewProviderFemConstraint1dpipeflow()
{
    sPixmap = "fem-constraint-1dpipeflow";
    //Note change "1dpipeflow" in line above to new constraint name, make sure it is the same as in taskFem* cpp file
    ADD_PROPERTY(FaceColor,(0.2f,0.3f,0.2f));
}

ViewProviderFemConstraint1dpipeflow::~ViewProviderFemConstraint1dpipeflow()
{
}

//FIXME setEdit needs a careful review
bool ViewProviderFemConstraint1dpipeflow::setEdit(int ModNum)
{
    if (ModNum == ViewProvider::Default) {
        // When double-clicking on the item for this constraint the
        // object unsets and sets its edit mode without closing
        // the task panel
        Gui::TaskView::TaskDialog *dlg = Gui::Control().activeDialog();
        TaskDlgFemConstraint1dpipeflow *constrDlg = qobject_cast<TaskDlgFemConstraint1dpipeflow *>(dlg);
        if (constrDlg && constrDlg->getConstraintView() != this)
            constrDlg = 0; // another constraint left open its task panel
        if (dlg && !constrDlg) {
            if (constraintDialog != NULL) {
                // Ignore the request to open another dialog
                return false;
            } else {
                constraintDialog = new TaskFemConstraint1dpipeflow(this);
                return true;
            }
        }

        // clear the selection (convenience)
        Gui::Selection().clearSelection();

        // start the edit dialog
        if (constrDlg)
            Gui::Control().showDialog(constrDlg);
        else
            Gui::Control().showDialog(new TaskDlgFemConstraint1dpipeflow(this));
        return true;
    }
    else {
        return ViewProviderDocumentObject::setEdit(ModNum);
    }
}

#define HEIGHT (1.5)
#define RADIUS (0.3)
//#define USE_MULTIPLE_COPY  //OvG: MULTICOPY fails to update scaled display on initial drawing - so disable

void ViewProviderFemConstraint1dpipeflow::updateData(const App::Property* prop)
{
    // Gets called whenever a property of the attached object changes
    Fem::Constraint1dpipeflow* pcConstraint = static_cast<Fem::Constraint1dpipeflow*>(this->getObject());
    float scaledradius = RADIUS * pcConstraint->Scale.getValue(); //OvG: Calculate scaled values once only
    float scaledheight = HEIGHT * pcConstraint->Scale.getValue();

    if (strcmp(prop->getName(),"Points") == 0) {
        const std::vector<Base::Vector3d>& points = pcConstraint->Points.getValues();
        const std::vector<Base::Vector3d>& normals = pcConstraint->Normals.getValues();
        if (points.size() != normals.size())
            return;
        std::vector<Base::Vector3d>::const_iterator n = normals.begin();

        // Points and Normals are always updated together
        pShapeSep->removeAllChildren();

        for (std::vector<Base::Vector3d>::const_iterator p = points.begin(); p != points.end(); p++) {
            //Define base and normal directions
            SbVec3f base(p->x, p->y, p->z);
            SbVec3f dir(n->x, n->y, n->z);//normal
 
 /* Note:
  * This next part draws a temperature gauge in 3D to indicate the constraint visually.
  * This serves as an example. Change or remove as needs be. 
  * It is possible to draw almost any basic 3D shape. See inventor's documentation
  * This gets drawn at every point.
  *  */
            
			///Visual indication
			//define separator
			SoSeparator* sep = new SoSeparator();
			
			///draw a temp gauge,with sphere and a cylinder
			//first move to correct postion
			SoTranslation* trans = new SoTranslation();
			SbVec3f newPos=base+scaledradius*dir*0.7;
			trans->translation.setValue(newPos);
			sep->addChild(trans);
			
			//adjust orientation
			SoRotation* rot = new SoRotation();
			rot->rotation.setValue(SbRotation(SbVec3f(0,1,0),dir));
			sep->addChild(rot);
			
			//define color of shape
			SoMaterial* myMaterial = new SoMaterial;
			myMaterial->diffuseColor.set1Value(0,SbColor(1,0,0));//RGB
			//myMaterial->diffuseColor.set1Value(1,SbColor(0,0,1));//possible to adjust sides separately
			sep->addChild(myMaterial);
			
			//draw a sphere
			SoSphere* sph = new SoSphere();
			sph->radius.setValue(scaledradius*0.75);
			sep->addChild(sph);
			//translate postion
			SoTranslation* trans2 = new SoTranslation();
			trans2->translation.setValue(SbVec3f(0,scaledheight*0.375,0));
			sep->addChild(trans2);
			//draw a cylinder
			SoCylinder* cyl = new SoCylinder();
			cyl->height.setValue(scaledheight*0.5);
			cyl->radius.setValue(scaledradius*0.375);
			sep->addChild(cyl);
			//translate postion
			SoTranslation* trans3 = new SoTranslation();
			trans3->translation.setValue(SbVec3f(0,scaledheight*0.375,0));
			sep->addChild(trans3);
			//define color of shape
			SoMaterial *myMaterial2 = new SoMaterial;
			myMaterial2->diffuseColor.set1Value(0,SbColor(1,1,1));//RGB
			sep->addChild(myMaterial2);
			//draw a cylinder
			SoCylinder* cyl2 = new SoCylinder();
			cyl2->height.setValue(scaledheight*0.25);
			cyl2->radius.setValue(scaledradius*0.375);
			sep->addChild(cyl2);
			
			pShapeSep->addChild(sep);
			
            n++;
        }
    }
    // Gets called whenever a property of the attached object changes
    ViewProviderFemConstraint::updateData(prop);
}
