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
# include <Precision.hxx>
#endif

#include "Mod/Fem/App/FemConstraintHeatflux.h"
#include "TaskFemConstraintHeatflux.h"
#include "ViewProviderFemConstraintHeatflux.h"
#include <Base/Console.h>
#include <Gui/Control.h>

using namespace FemGui;

PROPERTY_SOURCE(FemGui::ViewProviderFemConstraintHeatflux, FemGui::ViewProviderFemConstraint)

ViewProviderFemConstraintHeatflux::ViewProviderFemConstraintHeatflux()
{
    sPixmap = "fem-constraint-heatflux";
    ADD_PROPERTY(FaceColor,(0.2f,0.3f,0.2f));
}

ViewProviderFemConstraintHeatflux::~ViewProviderFemConstraintHeatflux()
{
}

//FIXME setEdit needs a careful review
bool ViewProviderFemConstraintHeatflux::setEdit(int ModNum)
{
    if (ModNum == ViewProvider::Default) {
        // When double-clicking on the item for this constraint the
        // object unsets and sets its edit mode without closing
        // the task panel
        Gui::TaskView::TaskDialog *dlg = Gui::Control().activeDialog();
        TaskDlgFemConstraintHeatflux *constrDlg = qobject_cast<TaskDlgFemConstraintHeatflux *>(dlg);
        if (constrDlg && constrDlg->getConstraintView() != this)
            constrDlg = 0; // another constraint left open its task panel
        if (dlg && !constrDlg) {
            if (constraintDialog != NULL) {
                // Ignore the request to open another dialog
                return false;
            } else {
                constraintDialog = new TaskFemConstraintHeatflux(this);
                return true;
            }
        }

        // clear the selection (convenience)
        Gui::Selection().clearSelection();

        // start the edit dialog
        if (constrDlg)
            Gui::Control().showDialog(constrDlg);
        else
            Gui::Control().showDialog(new TaskDlgFemConstraintHeatflux(this));
        return true;
    }
    else {
        return ViewProviderDocumentObject::setEdit(ModNum);
    }
}

#define HEIGHT (1.5)
#define RADIUS (0.3)
//#define USE_MULTIPLE_COPY  //OvG: MULTICOPY fails to update scaled display on initial drawing - so disable

void ViewProviderFemConstraintHeatflux::updateData(const App::Property* prop)
{
    // Gets called whenever a property of the attached object changes
    Fem::ConstraintHeatflux* pcConstraint = static_cast<Fem::ConstraintHeatflux*>(this->getObject());
    float scaledradius = RADIUS * pcConstraint->Scale.getValue(); //OvG: Calculate scaled values once only
    float scaledheight = HEIGHT * pcConstraint->Scale.getValue();
    float ambienttemp = pcConstraint->AmbientTemp.getValue();
    //float facetemp = pcConstraint->FaceTemp.getValue();
    float filmcoef = pcConstraint->FilmCoef.getValue();

    if (strcmp(prop->getName(),"Points") == 0) {
        const std::vector<Base::Vector3d>& points = pcConstraint->Points.getValues();
        const std::vector<Base::Vector3d>& normals = pcConstraint->Normals.getValues();
        if (points.size() != normals.size())
            return;
        std::vector<Base::Vector3d>::const_iterator n = normals.begin();

        // Note: Points and Normals are always updated together
        pShapeSep->removeAllChildren();

        for (std::vector<Base::Vector3d>::const_iterator p = points.begin(); p != points.end(); p++) {
            SbVec3f base(p->x, p->y, p->z);
            SbVec3f dir(n->x, n->y, n->z);
            SbRotation r(SbVec3f(-1,0,0), dir);
            
            //Heatflux indication
            SoSeparator* sep = new SoSeparator();
            
            ////draw a temp gauge,with sphere and a cylinder
            //first move to correct postion and orientation
            SoTranslation* trans = new SoTranslation();
            SbVec3f newPos=base+scaledradius*2*dir;
            trans->translation.setValue(newPos);
            sep->addChild(trans);
            SoRotation* rot = new SoRotation();
            rot->rotation.setValue(r);
            sep->addChild(rot);
            
            //experiment
            SoMaterial        *myMaterial = new SoMaterial;
            SoMaterialBinding *myBinding = new SoMaterialBinding;
            myMaterial->diffuseColor.set1Value(0,SbColor(1,0,0));
            //myMaterial->diffuseColor.set1Value(1,SbColor(.1,.1,.1));
            myBinding->value = SoMaterialBinding::PER_PART;
            sep->addChild(myMaterial);
            sep->addChild(myBinding);
            
            //now draw a sphere
            SoSphere* sph = new SoSphere();
            sph->radius.setValue(scaledradius*2);
            sep->addChild(sph);
            //now translate postion
            SoTranslation* trans2 = new SoTranslation();
            trans2->translation.setValue(SbVec3f(0,scaledheight*0.6,0));
            sep->addChild(trans2);
            //now draw a cylinder
            SoCylinder* cyl = new SoCylinder();
            cyl->height.setValue(scaledheight);
            cyl->radius.setValue(scaledradius);
            sep->addChild(cyl);
            //now translate postion
            SoTranslation* trans3 = new SoTranslation();
            trans3->translation.setValue(SbVec3f(0,0,scaledradius*1.8));
            sep->addChild(trans3);
            {
                //now for some tildes
                    //fix orientation
                SoTranslation* trans4 = new SoTranslation();
                trans4->translation.setValue(SbVec3f(0,0,scaledradius*0.1));
                sep->addChild(trans4);
                SoRotation* rot2 = new SoRotation();
                SbRotation r2(SbVec3f(1,0,0), dir);
                rot2->rotation.setValue(r2);
                sep->addChild(rot2);
                    //first determine font and size
                SoFont* font=new SoFont();
                font->name.setValue("Times-Roman");
                font->size.setValue(0.3*scaledheight);
                sep->addChild(font);
                    //draw text 
                SoText3* txt3D = new SoText3();
                std::ostringstream strs;
                std::string strToDisp = "~";
                txt3D->parts = SoText3::ALL;
                txt3D->string.setValue(strToDisp.c_str());
                sep->addChild(txt3D);
            }
            if (p == points.begin())//at first point add text
            {
                //now for some text
                    //fix orientation
                SoTranslation* trans5 = new SoTranslation();
                trans5->translation.setValue(SbVec3f(0,0,scaledradius*0.4));
                sep->addChild(trans5);
                SoRotation* rot2 = new SoRotation();
                SbRotation r2(SbVec3f(1,0,0), dir);
                rot2->rotation.setValue(r2);
                sep->addChild(rot2);
                    //first determine font and size
                SoFont* font=new SoFont();
                font->name.setValue("Times-Roman");
                font->size.setValue(0.2*scaledheight);
                sep->addChild(font);
                    //draw text 
                SoText3* txt3D = new SoText3();
                std::ostringstream strsAmb;
                std::ostringstream strsFace;
                std::ostringstream strsCoef;
                strsAmb << ambienttemp;
                //strsFace << facetemp;
                strsCoef << filmcoef;
                std::string strToDisp = "Ta: ";
                strToDisp += strsAmb.str();
                strToDisp += "°C ";
                //strToDisp += "Tf: ";
                //strToDisp += strsFace.str();
                //strToDisp +="°C\n";
                strToDisp += "coef: ";
                strToDisp += strsCoef.str();
                strToDisp +="W/(°C.m^2)";
                txt3D->parts = SoText3::ALL;
                txt3D->string.setValue(strToDisp.c_str());
                sep->addChild(txt3D);
            }
            
            pShapeSep->addChild(sep);
            
            n++;
        }
    }
    // Gets called whenever a property of the attached object changes
    ViewProviderFemConstraint::updateData(prop);
}
