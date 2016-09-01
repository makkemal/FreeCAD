/***************************************************************************
 *   Copyright (c) 2015 FreeCAD Developers                                 *
 *   Authors: Michael Hindley <hindlemp@eskom.co.za>                       *
 *            Ruan Olwagen <olwager@eskom.co.za>                           *
 *            Oswald van Ginkel <vginkeo@eskom.co.za>                      *
 *            Ofentse Kgoa <kgoaot@eskom.co.za>                            *
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
# include <BRepAdaptor_Curve.hxx>
# include <BRepAdaptor_Surface.hxx>
# include <Geom_Line.hxx>
# include <Geom_Plane.hxx>
# include <Precision.hxx>
# include <QMessageBox>
# include <QRegExp>
# include <QTextStream>
# include <TopoDS.hxx>
# include <gp_Ax1.hxx>
# include <gp_Lin.hxx>
# include <gp_Pln.hxx>
# include <sstream>
#endif

#include "Mod/Fem/App/FemConstraintTransform.h"
#include "TaskFemConstraintTransform.h"
#include "ui_TaskFemConstraintTransform.h"
#include <App/Application.h>
#include <Gui/Command.h>
#include <Base/Console.h>
#include <Mod/Part/App/PartFeature.h>
#include <Mod/Fem/App/FemTools.h>

#include <Gui/Selection.h>
#include <Gui/SelectionFilter.h>

#include <math.h>
#define PI (3.141592653589793238462643383279502884L)

using namespace FemGui;
using namespace Gui;

/* TRANSLATOR FemGui::TaskFemConstraintTransform */

TaskFemConstraintTransform::TaskFemConstraintTransform(ViewProviderFemConstraintTransform *ConstraintView,QWidget *parent)
  : TaskFemConstraint(ConstraintView, parent, "fem-constraint-transform")
{
    proxy = new QWidget(this);
    ui = new Ui_TaskFemConstraintTransform();
    ui->setupUi(proxy);
    QMetaObject::connectSlotsByName(this);

    //Rectangular
    QAction* actionRect = new QAction(tr("Delete"), ui->lw_Rect);
    actionRect->connect(actionRect, SIGNAL(triggered()), this, SLOT(onReferenceDeletedRect()));
    ui->lw_Rect->addAction(actionRect);
    ui->lw_Rect->setContextMenuPolicy(Qt::ActionsContextMenu);

    connect(ui->lw_Rect, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
        this, SLOT(setSelection(QListWidgetItem*)));

    //Cylindrical
    QAction* actionCylin = new QAction(tr("Delete"), ui->lw_Cylin);
    actionCylin->connect(actionCylin, SIGNAL(triggered()), this, SLOT(onReferenceDeletedCylin()));
    ui->lw_Cylin->addAction(actionCylin);
    ui->lw_Cylin->setContextMenuPolicy(Qt::ActionsContextMenu);
    
    connect(ui->lw_Cylin, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
        this, SLOT(setSelection(QListWidgetItem*)));

    connect(ui->lw_displobj, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
        this, SLOT(setSelection(QListWidgetItem*)));

    this->groupLayout()->addWidget(proxy);

    connect(ui->gbx_Rectangular, SIGNAL(clicked(bool)),  this, SLOT(Rect()));
    connect(ui->gbx_Cylindrical, SIGNAL(clicked(bool)),  this, SLOT(Cyl()));

    connect(ui->sp_X, SIGNAL(valueChanged(int)), this, SLOT(x_Changed(int)));
    connect(ui->sp_Y, SIGNAL(valueChanged(int)), this, SLOT(y_Changed(int)));
    connect(ui->sp_Z, SIGNAL(valueChanged(int)), this, SLOT(z_Changed(int)));

/* Note: */
    // Get the feature data
    Fem::ConstraintTransform* pcConstraint = static_cast<Fem::ConstraintTransform*>(ConstraintView->getObject());

    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();

    // Fill data into dialog elements
    ui->sp_X->setValue(pcConstraint->X_rot.getValue());
    ui->sp_Y->setValue(pcConstraint->Y_rot.getValue());
    ui->sp_Z->setValue(pcConstraint->Z_rot.getValue());

    ui->gbx_Rectangular->setChecked(pcConstraint->Rectangular.getValue());
    ui->gbx_Cylindrical->setChecked(pcConstraint->Cylindrical.getValue());
/* */

    ui->lw_Rect->clear();
    ui->lw_Cylin->clear();
    ui->lw_displobj->clear();
    ui->lw_Cylin->clear();

    //Transformable surfaces
    ui->lw_displobj->clear();
    Gui::Command::doCommand(Gui::Command::Doc,TaskFemConstraintTransform::getDisplcementReferences((static_cast<Fem::Constraint*>(ConstraintView->getObject()))->getNameInDocument()).c_str());
    std::vector<App::DocumentObject*> ObjDispl = pcConstraint->RefDispl.getValues();
    std::vector<App::DocumentObject*> nDispl = pcConstraint->NameDispl.getValues();
    std::vector<std::string> SubElemDispl = pcConstraint->RefDispl.getSubValues();

    for (std::size_t i = 0; i < ObjDispl.size(); i++) {
        ui->lw_displobj->addItem(makeRefText(ObjDispl[i], SubElemDispl[i]));
        ui->lw_dis->addItem(makeText(nDispl[i]));
    }

    if (Objects.size() > 0){   
        if (pcConstraint->Rectangular.getValue())  {
            for (std::size_t i = 0; i < Objects.size(); i++) {
                ui->lw_Rect->addItem(makeRefText(Objects[i], SubElements[i]));
            }
        }
        else {
            for (std::size_t i = 0; i < (Objects.size()); i++) {
                ui->lw_Cylin->addItem(makeRefText(Objects[i], SubElements[i]));
            }
        }
    }
    
    int p = 0;
    for (std::size_t i = 0; i < ObjDispl.size(); i++) {
        for (std::size_t j = 0; j < Objects.size(); j++) {
            if ((makeRefText(ObjDispl[i], SubElemDispl[i]))==(makeRefText(Objects[j], SubElements[j]))){
                p++;
            }
        }
    }
    //Selection buttons
    connect(ui->btnAddRect, SIGNAL(clicked()),  this, SLOT(addToSelectionRect()));
    connect(ui->btnRemoveRect, SIGNAL(clicked()),  this, SLOT(removeFromSelectionRect()));

    connect(ui->btnAddCylin, SIGNAL(clicked()),  this, SLOT(addToSelectionCylin()));
    connect(ui->btnRemoveCylin, SIGNAL(clicked()),  this, SLOT(removeFromSelectionCylin()));


    updateUI();
    if ((p==0) && (Objects.size() > 0)) {
        QMessageBox::warning(this, tr("Constraint update error"), tr("The transformable faces have changed. Please add only the transformable faces and remove non-transformable faces!"));
        return;
    }
}

TaskFemConstraintTransform::~TaskFemConstraintTransform()
{
    delete ui;
}

const QString TaskFemConstraintTransform::makeText(const App::DocumentObject* obj) const
{
    return QString::fromUtf8((std::string(obj->getNameInDocument())).c_str());
}

void TaskFemConstraintTransform::updateUI()
{
    if (ui->lw_Rect->model()->rowCount() == 0) {
        // Go into reference selection mode if no reference has been selected yet
        onButtonReference(true);
        return;
    }

    if (ui->lw_Cylin->model()->rowCount() == 0) {
        // Go into reference selection mode if no reference has been selected yet
        onButtonReference(true);
        return;
    }
}

void TaskFemConstraintTransform::x_Changed(int i){
    Fem::ConstraintTransform* pcConstraint = static_cast<Fem::ConstraintTransform*>(ConstraintView->getObject());
    double x = i;
    pcConstraint->X_rot.setValue(x);
    std::string name = ConstraintView->getObject()->getNameInDocument();
    Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.X_rot = %f", name.c_str(), x);
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
    pcConstraint->References.setValues(Objects,SubElements);
}

void TaskFemConstraintTransform::y_Changed(int i){
    Fem::ConstraintTransform* pcConstraint = static_cast<Fem::ConstraintTransform*>(ConstraintView->getObject());
    double y = i;
    pcConstraint->Y_rot.setValue(y);
    std::string name = ConstraintView->getObject()->getNameInDocument();
    Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Y_rot = %f", name.c_str(), y);
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
    pcConstraint->References.setValues(Objects,SubElements);
}

void TaskFemConstraintTransform::z_Changed(int i){
    Fem::ConstraintTransform* pcConstraint = static_cast<Fem::ConstraintTransform*>(ConstraintView->getObject());
    double z = i;
    pcConstraint->Z_rot.setValue(z);
    std::string name = ConstraintView->getObject()->getNameInDocument();
    Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Z_rot = %f", name.c_str(), z);
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
    pcConstraint->References.setValues(Objects,SubElements);
}

void TaskFemConstraintTransform::Rect(){
    ui->gbx_Cylindrical->setChecked(false);
    ui->lw_Cylin->blockSignals(true);
}

void TaskFemConstraintTransform::Cyl(){
    ui->gbx_Rectangular->setChecked(false);
    ui->sp_X->blockSignals(true);
    ui->sp_Y->blockSignals(true);
    ui->sp_Z->blockSignals(true);
    ui->lw_Rect->blockSignals(true);
}


void TaskFemConstraintTransform::addToSelectionRect()
{
    int rows = ui->lw_Rect->model()->rowCount();
    std::vector<Gui::SelectionObject> selection = Gui::Selection().getSelectionEx(); //gets vector of selected objects of active document
    if (selection.size()==0){
        QMessageBox::warning(this, tr("Selection error"), tr("Nothing selected!"));
        return;
    }

    if (rows==1){
        QMessageBox::warning(this, tr("Selection error"), tr("Only one face for rectangular transform constraint!"));
        Gui::Selection().clearSelection();
        return;	
    } 
        
    if ((rows==0) && (selection.size()>=2)){
        QMessageBox::warning(this, tr("Selection error"), tr("Only one face for rectangular transform constraint!"));
        Gui::Selection().clearSelection();
        return;	
    }      

    Fem::ConstraintTransform* pcConstraint = static_cast<Fem::ConstraintTransform*>(ConstraintView->getObject());
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
    
    std::vector<App::DocumentObject*> ObjDispl = pcConstraint->RefDispl.getValues();
    std::vector<std::string> SubElemDispl = pcConstraint->RefDispl.getSubValues();
    for (std::vector<Gui::SelectionObject>::iterator it = selection.begin();  it != selection.end(); ++it){//for every selected object
        if (static_cast<std::string>(it->getTypeName()).substr(0,4).compare(std::string("Part"))!=0){
            QMessageBox::warning(this, tr("Selection error"),tr("Selected object is not a part!"));
            return;
        }

        std::vector<std::string> subNames=it->getSubNames();
        App::DocumentObject* obj = ConstraintView->getObject()->getDocument()->getObject(it->getFeatName());
        if (subNames.size()!=1){
            QMessageBox::warning(this, tr("Selection error"), tr("Only one face for rectangular transform constraint!"));
            Gui::Selection().clearSelection();
            return;
        }
        for (unsigned int subIt=0;subIt<(subNames.size());++subIt){// for every selected sub element
            bool addMe=true;
            if (subNames[subIt].substr(0,4) != "Face") {
                QMessageBox::warning(this, tr("Selection error"), tr("Only faces can be picked"));
                return;
            }
            for (std::vector<std::string>::iterator itr=std::find(SubElements.begin(),SubElements.end(),subNames[subIt]);
                   itr!= SubElements.end();
                   itr =  std::find(++itr,SubElements.end(),subNames[subIt]))
            {// for every sub element in selection that matches one in old list
                if (obj==Objects[std::distance(SubElements.begin(),itr)]){//if selected sub element's object equals the one in old list then it was added before so don't add
                    addMe=false;
                }
            }
            if (addMe){
                disconnect(ui->lw_Rect, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
                    this, SLOT(setSelection(QListWidgetItem*)));
                for (std::size_t i = 0; i < ObjDispl.size(); i++) {
                    if ((makeRefText(ObjDispl[i], SubElemDispl[i]))==(makeRefText(obj, subNames[subIt]))){
                        Objects.push_back(obj);  
                        SubElements.push_back(subNames[subIt]);
                        ui->lw_Rect->addItem(makeRefText(obj, subNames[subIt]));
                        connect(ui->lw_Rect, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
                            this, SLOT(setSelection(QListWidgetItem*)));
                    }
                }
                if (Objects.size() == 0){
                    QMessageBox::warning(this, tr("Selection error"), tr("Only transformable faces can be selected!"));
                    Gui::Selection().clearSelection();
                    return;    
                }
            }
        }
    }
    //Update UI
    pcConstraint->References.setValues(Objects,SubElements);
    updateUI();
    Base::Vector3d normal = pcConstraint->NormalDirection.getValue();
    double n = normal.x;
    double m = normal.y;
    double l = normal.z;
    //about Z-axis
    double about_z;
    double mag_norm_z = sqrt(n*n +m*m) ;  //normal vector mapped onto XY plane
    if (mag_norm_z ==0) {
        about_z = 0;
    } else {
        about_z = (-1*(acos(m/mag_norm_z) * 180/PI) +180);
    }
    if (n>0) {
        about_z = about_z*(-1);
    }
    //rotation to ZY plane
    double m_p = n*sin(about_z*PI/180) + m*cos(about_z*PI/180) ;
    double l_p = l;

    //about X-axis 
    double about_x;
    double mag_norm_x = sqrt(m_p*m_p + l_p*l_p) ;
    if (mag_norm_x ==0){
        about_x = 0;
    } else {
        about_x = -(acos(l_p/mag_norm_x) * 180/PI); //rotation to the Z axis
    }
    ui->sp_X->setValue(round(about_x));
    ui->sp_Z->setValue(round(about_z));
}

void TaskFemConstraintTransform::removeFromSelectionRect()
{
    std::vector<Gui::SelectionObject> selection = Gui::Selection().getSelectionEx(); //gets vector of selected objects of active document
    if (selection.size()==0){
        QMessageBox::warning(this, tr("Selection error"), tr("Nothing selected!"));
        return;
    }

    Fem::ConstraintTransform* pcConstraint = static_cast<Fem::ConstraintTransform*>(ConstraintView->getObject());
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
    std::vector<int> itemsToDel;
    for (std::vector<Gui::SelectionObject>::iterator it = selection.begin();  it != selection.end(); ++it){//for every selected object
        if (static_cast<std::string>(it->getTypeName()).substr(0,4).compare(std::string("Part"))!=0){
            QMessageBox::warning(this, tr("Selection error"),tr("Selected object is not a part!"));
            return;
        }

        std::vector<std::string> subNames=it->getSubNames();
        App::DocumentObject* obj = ConstraintView->getObject()->getDocument()->getObject(it->getFeatName());

        for (unsigned int subIt=0;subIt<(subNames.size());++subIt){// for every selected sub element
            for (std::vector<std::string>::iterator itr=std::find(SubElements.begin(),SubElements.end(),subNames[subIt]);
                itr!= SubElements.end();
                itr =  std::find(++itr,SubElements.end(),subNames[subIt]))
            {// for every sub element in selection that matches one in old list
                if (obj==Objects[std::distance(SubElements.begin(),itr)]){//if selected sub element's object equals the one in old list then it was added before so mark for deletion
                    itemsToDel.push_back(std::distance(SubElements.begin(),itr));
                }
            }
        }
    }

    std::sort(itemsToDel.begin(),itemsToDel.end());
    while (itemsToDel.size()>0){
        Objects.erase(Objects.begin()+itemsToDel.back());
        SubElements.erase(SubElements.begin()+itemsToDel.back());
        itemsToDel.pop_back();
    }
    //Update UI
    disconnect(ui->lw_Rect, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
        this, SLOT(setSelection(QListWidgetItem*)));

    ui->lw_Rect->clear();
    connect(ui->lw_Rect, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
        this, SLOT(setSelection(QListWidgetItem*)));

    pcConstraint->References.setValues(Objects,SubElements);
    updateUI();
    ui->sp_X->setValue(0);
    ui->sp_Y->setValue(0);
    ui->sp_Z->setValue(0);
}

void TaskFemConstraintTransform::addToSelectionCylin()
{
    int rows = ui->lw_Cylin->model()->rowCount();
    std::vector<Gui::SelectionObject> selection = Gui::Selection().getSelectionEx(); //gets vector of selected objects of active document
    if (selection.size()==0){
        QMessageBox::warning(this, tr("Selection error"), tr("Nothing selected!"));
        return;
    }

    if (rows==1){
        QMessageBox::warning(this, tr("Selection error"), tr("Only one cylindrical face for cylindrical transform constraint!"));
        Gui::Selection().clearSelection();
        return;
    } 

    if ((rows==0) && (selection.size()>=2)){
        QMessageBox::warning(this, tr("Selection error"), tr("Only one cylindrical face for cylindrical transform constraint!"));
        Gui::Selection().clearSelection();
        return;
    }

    Fem::ConstraintTransform* pcConstraint = static_cast<Fem::ConstraintTransform*>(ConstraintView->getObject());
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();

    std::vector<App::DocumentObject*> ObjDispl = pcConstraint->RefDispl.getValues();
    std::vector<std::string> SubElemDispl = pcConstraint->RefDispl.getSubValues();
    for (std::vector<Gui::SelectionObject>::iterator it = selection.begin();  it != selection.end(); ++it){//for every selected object
        if (static_cast<std::string>(it->getTypeName()).substr(0,4).compare(std::string("Part"))!=0){
            QMessageBox::warning(this, tr("Selection error"),tr("Selected object is not a part!"));
            return;
        }

        std::vector<std::string> subNames=it->getSubNames();
        App::DocumentObject* obj = ConstraintView->getObject()->getDocument()->getObject(it->getFeatName());
        if (subNames.size()!=1){ 
            QMessageBox::warning(this, tr("Selection error"), tr("Only one cylindrical face for cylindrical transform constraint!"));
            Gui::Selection().clearSelection();
            return;
        }
        for (unsigned int subIt=0;subIt<(subNames.size());++subIt){// for every selected sub element
            bool addMe=true;
            if (subNames[subIt].substr(0,4) == "Face") {
                Part::Feature* feat = static_cast<Part::Feature*>(obj);
                TopoDS_Shape ref = feat->Shape.getShape().getSubShape(subNames[subIt].c_str());
                BRepAdaptor_Surface surface(TopoDS::Face(ref));
                if (surface.GetType() != GeomAbs_Cylinder) {
                    QMessageBox::warning(this, tr("Selection error"), tr("Only cylindrical faces can be picked"));
                    return;
                }
            }
            for (std::vector<std::string>::iterator itr=std::find(SubElements.begin(),SubElements.end(),subNames[subIt]);
                   itr!= SubElements.end();
                   itr =  std::find(++itr,SubElements.end(),subNames[subIt]))
            {// for every sub element in selection that matches one in old list
                if (obj==Objects[std::distance(SubElements.begin(),itr)]){//if selected sub element's object equals the one in old list then it was added before so don't add
                    addMe=false;
                }
            }
            if (addMe){
                disconnect(ui->lw_Cylin, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
                    this, SLOT(setSelection(QListWidgetItem*)));
                for (std::size_t i = 0; i < ObjDispl.size(); i++) {
                    if ((makeRefText(ObjDispl[i], SubElemDispl[i]))==(makeRefText(obj, subNames[subIt]))){
                        Objects.push_back(obj);  
                        SubElements.push_back(subNames[subIt]);
                        ui->lw_Cylin->addItem(makeRefText(obj, subNames[subIt]));
                        connect(ui->lw_Cylin, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
                            this, SLOT(setSelection(QListWidgetItem*)));
                    }
                }
                if (Objects.size() == 0){
                    QMessageBox::warning(this, tr("Selection error"), tr("Only transformable faces can be selected!"));
                    Gui::Selection().clearSelection();
                    return;
                }
            }
        }
    }
    //Update UI
    pcConstraint->References.setValues(Objects,SubElements);
    updateUI();

}

void TaskFemConstraintTransform::removeFromSelectionCylin()
{
    std::vector<Gui::SelectionObject> selection = Gui::Selection().getSelectionEx(); //gets vector of selected objects of active document
    if (selection.size()==0){
        QMessageBox::warning(this, tr("Selection error"), tr("Nothing selected!"));
        return;
    }

    Fem::ConstraintTransform* pcConstraint = static_cast<Fem::ConstraintTransform*>(ConstraintView->getObject());
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
    std::vector<int> itemsToDel;
    for (std::vector<Gui::SelectionObject>::iterator it = selection.begin();  it != selection.end(); ++it){//for every selected object
        if (static_cast<std::string>(it->getTypeName()).substr(0,4).compare(std::string("Part"))!=0){
            QMessageBox::warning(this, tr("Selection error"),tr("Selected object is not a part!"));
            return;
        }

        std::vector<std::string> subNames=it->getSubNames();
        App::DocumentObject* obj = ConstraintView->getObject()->getDocument()->getObject(it->getFeatName());

        for (unsigned int subIt=0;subIt<(subNames.size());++subIt){// for every selected sub element
            for (std::vector<std::string>::iterator itr=std::find(SubElements.begin(),SubElements.end(),subNames[subIt]);
                itr!= SubElements.end();
                itr =  std::find(++itr,SubElements.end(),subNames[subIt]))
            {// for every sub element in selection that matches one in old list
                if (obj==Objects[std::distance(SubElements.begin(),itr)]){//if selected sub element's object equals the one in old list then it was added before so mark for deletion
                    itemsToDel.push_back(std::distance(SubElements.begin(),itr));
                }
            }
        }
    }

    std::sort(itemsToDel.begin(),itemsToDel.end());
    while (itemsToDel.size()>0){
        Objects.erase(Objects.begin()+itemsToDel.back());
        SubElements.erase(SubElements.begin()+itemsToDel.back());
        itemsToDel.pop_back();
    }
    //Update UI
    disconnect(ui->lw_Cylin, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
        this, SLOT(setSelection(QListWidgetItem*)));

    ui->lw_Cylin->clear();
    connect(ui->lw_Cylin, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
        this, SLOT(setSelection(QListWidgetItem*)));

    pcConstraint->References.setValues(Objects,SubElements);
    updateUI();

}

void TaskFemConstraintTransform::setSelection(QListWidgetItem* item){
    std::string docName=ConstraintView->getObject()->getDocument()->getName();
    
    std::string s = item->text().toStdString();
    std::string delimiter = ":";

    size_t pos = 0;
    std::string objName;
    std::string subName;
    pos = s.find(delimiter);
    objName = s.substr(0, pos);
    s.erase(0, pos + delimiter.length());
    subName=s;

    Gui::Selection().clearSelection();
    Gui::Selection().addSelection(docName.c_str(),objName.c_str(),subName.c_str(),0,0,0);
}

const std::string TaskFemConstraintTransform::getReferences() const
{
    std::vector<std::string> items;
    if (ui->gbx_Rectangular->isChecked()== 1) {
        int rowsRect = ui->lw_Rect->model()->rowCount();

        for (int r = 0; r < rowsRect; r++) {
           items.push_back(ui->lw_Rect->item(r)->text().toStdString());
        }
    }
    else {
        int rowsCylin = ui->lw_Cylin->model()->rowCount();
        for (int r = 0; r < rowsCylin; r++) {
            items.push_back(ui->lw_Cylin->item(r)->text().toStdString());
        }
    }
    return TaskFemConstraint::getReferences(items);
}

void TaskFemConstraintTransform::onReferenceDeletedRect() {
    TaskFemConstraintTransform::removeFromSelectionRect();
}

void TaskFemConstraintTransform::onReferenceDeletedCylin() {
    TaskFemConstraintTransform::removeFromSelectionCylin();
}

std::string TaskFemConstraintTransform::getDisplcementReferences(std::string showConstr="")
{
    return "members=FreeCAD.ActiveDocument.Analysis.Member\n\
A = []\n\
i = 0\n\
ss = []\n\
for member in members:\n\
        if member.isDerivedFrom(\"Fem::ConstraintDisplacement\"):\n\
                m = member.References\n\
                A.append(m)\n\
                if i >0:\n\
                        p = p + m[0][1]\n\
                        x = (A[0][0][0],p)\n\
                        for t in range(len(m[0][1])):\n\
                                ss.append(member)\n\
                else:\n\
                        p = A[i][0][1]\n\
                        x = (A[0][0][0],p)\n\
                        for t in range(len(m[0][1])):\n\
                                ss.append(member)\n\
                i = i+1\n\
if i>0:\n\
        App.ActiveDocument."+showConstr+".RefDispl = [x]\n\
        App.ActiveDocument."+showConstr+".NameDispl = ss\n";
}

/* Note: */
double TaskFemConstraintTransform::get_X_rot() const{return ui->sp_X->value();}
double TaskFemConstraintTransform::get_Y_rot() const{return ui->sp_Y->value();}
double TaskFemConstraintTransform::get_Z_rot() const{return ui->sp_Z->value();}
bool TaskFemConstraintTransform::get_rectangular() const{return ui->gbx_Rectangular->isChecked();}
bool TaskFemConstraintTransform::get_cylindrical() const{return ui->gbx_Cylindrical->isChecked();}

void TaskFemConstraintTransform::changeEvent(QEvent *e){
}

//**************************************************************************
// TaskDialog
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TaskDlgFemConstraintTransform::TaskDlgFemConstraintTransform(ViewProviderFemConstraintTransform *ConstraintView)
{
    this->ConstraintView = ConstraintView;
    assert(ConstraintView);
    this->parameter = new TaskFemConstraintTransform(ConstraintView);;

    Content.push_back(parameter);
}

//==== calls from the TaskView ===============================================================

void TaskDlgFemConstraintTransform::open()
{
    // a transaction is already open at creation time of the panel
    if (!Gui::Command::hasPendingCommand()) {
        QString msg = QObject::tr("Constraint transform");
        Gui::Command::openCommand((const char*)msg.toUtf8());
        ConstraintView->setVisible(true);
        Gui::Command::doCommand(Gui::Command::Doc,ViewProviderFemConstraint::gethideMeshShowPartStr((static_cast<Fem::Constraint*>(ConstraintView->getObject()))->getNameInDocument()).c_str()); //OvG: Hide meshes and show parts
    }
}

bool TaskDlgFemConstraintTransform::accept()
{
/* Note: */
    std::string name = ConstraintView->getObject()->getNameInDocument();
    const TaskFemConstraintTransform* parameters = static_cast<const TaskFemConstraintTransform*>(parameter);

    try {
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.X_rot = %f",
            name.c_str(), parameters->get_X_rot());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Y_rot = %f",
            name.c_str(), parameters->get_Y_rot());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Z_rot = %f",
            name.c_str(), parameters->get_Z_rot());     
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Rectangular = %s",
            name.c_str(), parameters->get_rectangular() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Cylindrical = %s",
            name.c_str(), parameters->get_cylindrical() ? "True" : "False");
        std::string scale = parameters->getScale();  //OvG: determine modified scale
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Scale = %s", name.c_str(), scale.c_str()); //OvG: implement modified scale

    }
    catch (const Base::Exception& e) {
        QMessageBox::warning(parameter, tr("Input error"), QString::fromLatin1(e.what()));
        return false;
    }
/* */
    return TaskDlgFemConstraint::accept();
}

bool TaskDlgFemConstraintTransform::reject()
{
    Gui::Command::abortCommand();
    Gui::Command::doCommand(Gui::Command::Gui,"Gui.activeDocument().resetEdit()");
    Gui::Command::updateActive();

    return true;
}

#include "moc_TaskFemConstraintTransform.cpp"
