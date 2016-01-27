/***************************************************************************
 *   Copyright (c) 2015 FreeCAD Developers                                 *
 *   Author: Przemo Firszt <przemo@firszt.eu>                              *
 *   Based on Force constraint by Jan Rheinl채nder                          *
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

#include "Mod/Fem/App/FemConstraintPrescribedDisplacement.h"
#include "TaskFemConstraintPrescribedDisplacement.h"
#include "ui_TaskFemConstraintPrescribedDisplacement.h"
#include <App/Application.h>
#include <Gui/Command.h>

using namespace FemGui;
using namespace Gui;

/* TRANSLATOR FemGui::TaskFemConstraintPrescribedDisplacement */

TaskFemConstraintPrescribedDisplacement::TaskFemConstraintPrescribedDisplacement(ViewProviderFemConstraintPrescribedDisplacement *ConstraintView,QWidget *parent)
  : TaskFemConstraint(ConstraintView, parent, "fem-constraint-prescribed-displacement")
{
    proxy = new QWidget(this);
    ui = new Ui_TaskFemConstraintPrescribedDisplacement();
    ui->setupUi(proxy);
    QMetaObject::connectSlotsByName(this);

    QAction* action = new QAction(tr("Delete"), ui->lw_references);
    action->connect(action, SIGNAL(triggered()), this, SLOT(onReferenceDeleted()));
    ui->lw_references->addAction(action);
    ui->lw_references->setContextMenuPolicy(Qt::ActionsContextMenu);
    
    this->groupLayout()->addWidget(proxy);
    
    // Connect decimal value inputs
    connect(ui->spinxDisplacement, SIGNAL(valueChanged(double)),  this, SLOT(x_changed(double)));
    connect(ui->spinyDisplacement, SIGNAL("valueChanged(double)"),  this, SLOT(y_changed(double)));
    connect(ui->spinzDisplacement, SIGNAL("valueChanged(double)"),  this, SLOT(z_changed(double)));
    connect(ui->rotxv, SIGNAL("valueChanged(double)"),  this, SLOT(x_rot(double)));
    connect(ui->rotyv, SIGNAL("valueChanged(double)"),  this, SLOT(y_rot(double)));
    connect(ui->rotzv, SIGNAL("valueChanged(double)"),  this, SLOT(z_rot(double)));
    // Connect check box values displacements
    connect(ui->localcoord, SIGNAL("stateChanged(int)"),  this, SLOT(localcoord(int)));
    connect(ui->dispxfix, SIGNAL("stateChanged(int)"),  this, SLOT(fixx(int)));
    connect(ui->dispxfree, SIGNAL("stateChanged(int)"),  this, SLOT(freex(int)));
    connect(ui->dispyfix, SIGNAL("stateChanged(int)"),  this, SLOT(fixy(int)));
    connect(ui->dispyfree, SIGNAL("stateChanged(int)"),  this, SLOT(freey(int)));
    connect(ui->dispzfix, SIGNAL("stateChanged(int)"),  this, SLOT(fixz(int)));
    connect(ui->dispzfree, SIGNAL("stateChanged(int)"),  this, SLOT(freez(int)));
    // Connect to check box values for rotations
    connect(ui->rotxfix, SIGNAL("stateChanged(int)"),  this, SLOT(rotfixx(int)));
    connect(ui->rotxfree, SIGNAL("stateChanged(int)"),  this, SLOT(rotfreex(int)));
    connect(ui->rotyfix, SIGNAL("stateChanged(int)"),  this, SLOT(rotfixy(int)));
    connect(ui->rotyfree, SIGNAL("stateChanged(int)"),  this, SLOT(rotfreey(int)));
    connect(ui->rotzfix, SIGNAL("stateChanged(int)"),  this, SLOT(rotfixz(int)));
    connect(ui->rotzfree, SIGNAL("stateChanged(int)"),  this, SLOT(rotfreez(int)));
    
    // Temporarily prevent unnecessary feature recomputes
    ui->spinxDisplacement->blockSignals(true);
    ui->spinyDisplacement->blockSignals(true);
    ui->spinzDisplacement->blockSignals(true);
    ui->rotxv->blockSignals(true);
    ui->rotyv->blockSignals(true);
    ui->rotzv->blockSignals(true);
    ui->localcoord->blockSignals(true);
    ui->dispxfix->blockSignals(true);
    ui->dispxfree->blockSignals(true);
    ui->dispyfix->blockSignals(true);
    ui->dispyfree->blockSignals(true);
    ui->dispzfix->blockSignals(true);
    ui->dispzfree->blockSignals(true);
    ui->rotxfix->blockSignals(true);
    ui->rotxfree->blockSignals(true);
    ui->rotyfix->blockSignals(true);
    ui->rotyfree->blockSignals(true);
    ui->rotzfix->blockSignals(true);
    ui->rotzfree->blockSignals(true);

    // Get the feature data
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    double fStates[6];
    bool bStates[13];
    fStates[0]=pcConstraint->xDisplacement.getValue();
    fStates[1]=pcConstraint->yDisplacement.getValue();
    fStates[2]=pcConstraint->zDisplacement.getValue();
    fStates[3]=pcConstraint->xRotation.getValue();
    fStates[4]=pcConstraint->yRotation.getValue();
    fStates[5]=pcConstraint->zRotation.getValue();
    bStates[1]=pcConstraint->xFix.getValue();
    bStates[2]=pcConstraint->xFree.getValue();
    bStates[3]=pcConstraint->yFix.getValue();
    bStates[4]=pcConstraint->yFree.getValue();
    bStates[5]=pcConstraint->zFix.getValue();
    bStates[6]=pcConstraint->zFree.getValue();
    bStates[7]=pcConstraint->rotxFix.getValue();
    bStates[8]=pcConstraint->rotxFree.getValue();
    bStates[9]=pcConstraint->rotyFix.getValue();
    bStates[10]=pcConstraint->rotyFree.getValue();
    bStates[11]=pcConstraint->rotzFix.getValue();
    bStates[12]=pcConstraint->rotzFree.getValue();
    
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
    
    // Fill data into dialog elements
    ui->spinxDisplacement->setValue(fStates[0]);
    ui->spinyDisplacement->setValue(fStates[1]);
    ui->spinzDisplacement->setValue(fStates[2]);
    ui->rotxv->setValue(fStates[3]);
    ui->rotyv->setValue(fStates[4]);
    ui->rotzv->setValue(fStates[5]);
    ui->dispxfix->setChecked(bStates[1]);
    ui->dispxfree->setChecked(bStates[2]);
    ui->dispyfix->setChecked(bStates[3]);
    ui->dispyfree->setChecked(bStates[4]);
    ui->dispzfix->setChecked(bStates[5]);
    ui->dispzfree->setChecked(bStates[6]);
    ui->rotxfix->setChecked(bStates[7]);
    ui->rotxfree->setChecked(bStates[8]);
    ui->rotyfix->setChecked(bStates[9]);
    ui->rotyfree->setChecked(bStates[10]);
    ui->rotzfix->setChecked(bStates[11]);
    ui->rotzfree->setChecked(bStates[12]);
    
    ui->lw_references->clear();
    for (std::size_t i = 0; i < Objects.size(); i++) {
        ui->lw_references->addItem(makeRefText(Objects[i], SubElements[i]));
    }
    if (Objects.size() > 0) {
        ui->lw_references->setCurrentRow(0, QItemSelectionModel::ClearAndSelect);
    }
   
    //Allow signals again
    ui->spinxDisplacement->blockSignals(false);
    ui->spinyDisplacement->blockSignals(false);
    ui->spinzDisplacement->blockSignals(false);
    ui->rotxv->blockSignals(false);
    ui->rotyv->blockSignals(false);
    ui->rotzv->blockSignals(false);
    ui->localcoord->blockSignals(false);
    ui->dispxfix->blockSignals(false);
    ui->dispxfree->blockSignals(false);
    ui->dispyfix->blockSignals(false);
    ui->dispyfree->blockSignals(false);
    ui->dispzfix->blockSignals(false);
    ui->dispzfree->blockSignals(false);
    ui->rotxfix->blockSignals(false);
    ui->rotxfree->blockSignals(false);
    ui->rotyfix->blockSignals(false);
    ui->rotyfree->blockSignals(false);
    ui->rotzfix->blockSignals(false);
    ui->rotzfree->blockSignals(false);

    updateUI();
}

TaskFemConstraintPrescribedDisplacement::~TaskFemConstraintPrescribedDisplacement()
{
    delete ui;
}

void TaskFemConstraintPrescribedDisplacement::updateUI()
{
    if (ui->lw_references->model()->rowCount() == 0) {
        // Go into reference selection mode if no reference has been selected yet
        onButtonReference(true);
        return;
    }
}

void TaskFemConstraintPrescribedDisplacement::onSelectionChanged(const Gui::SelectionChanges& msg)
{
    if ((msg.Type != Gui::SelectionChanges::AddSelection) ||
        // Don't allow selection in other document
        (strcmp(msg.pDocName, ConstraintView->getObject()->getDocument()->getName()) != 0) ||
        // Don't allow selection mode none
        (selectionMode != selref) ||
        // Don't allow empty smenu/submenu
        (!msg.pSubName || msg.pSubName[0] == '\0')) {
        return;
    }

    std::string subName(msg.pSubName);
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    App::DocumentObject* obj = ConstraintView->getObject()->getDocument()->getObject(msg.pObjectName);

    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();

    if (subName.substr(0,4) != "Face") {
        QMessageBox::warning(this, tr("Selection error"), tr("Only faces can be picked"));
        return;
    }
    // Avoid duplicates
    std::size_t pos = 0;
    for (; pos < Objects.size(); pos++) {
        if (obj == Objects[pos])
            break;
    }

    if (pos != Objects.size()) {
        if (subName == SubElements[pos])
            return;
    }

    // add the new reference
    Objects.push_back(obj);
    SubElements.push_back(subName);
    pcConstraint->References.setValues(Objects,SubElements);
    ui->lw_references->addItem(makeRefText(obj, subName));

    // Turn off reference selection mode
    //onButtonReference(false);
    //Gui::Selection().clearSelection();
    updateUI();
}

void TaskFemConstraintPrescribedDisplacement::x_changed(double val){
    if (val!=0)
    {
        ui->dispxfree->setChecked(false);
        ui->dispxfix->setChecked(false); 
    }
    else
    {  ui->dispxfree->setChecked(true);}
}

void TaskFemConstraintPrescribedDisplacement::y_changed(double val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->yDisplacement.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::z_changed(double val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->zDisplacement.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::x_rot(double val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->xRotation.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::y_rot(double val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->yRotation.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::z_rot(double val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->zRotation.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::fixx(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->xFix.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::freex(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->xFree.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::fixy(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->yFix.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::freey(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->yFree.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::fixz(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->zFix.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::freez(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->zFree.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::rotfixx(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->rotxFix.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::rotfreex(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->rotxFree.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::rotfixy(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->rotyFix.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::rotfreey(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->rotyFree.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::rotfixz(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->rotzFix.setValue(val);
}

void TaskFemConstraintPrescribedDisplacement::rotfreez(int val){
    Fem::ConstraintPrescribedDisplacement* pcConstraint = static_cast<Fem::ConstraintPrescribedDisplacement*>(ConstraintView->getObject());
    pcConstraint->rotzFree.setValue(val);
}


void TaskFemConstraintPrescribedDisplacement::onReferenceDeleted() {
    int row = ui->lw_references->currentIndex().row();
    TaskFemConstraint::onReferenceDeleted(row);
    ui->lw_references->model()->removeRow(row);
    ui->lw_references->setCurrentRow(0, QItemSelectionModel::ClearAndSelect);
}

const std::string TaskFemConstraintPrescribedDisplacement::getReferences() const
{
    int rows = ui->lw_references->model()->rowCount();
    std::vector<std::string> items;
    for (int r = 0; r < rows; r++) {
        items.push_back(ui->lw_references->item(r)->text().toStdString());
    }
    return TaskFemConstraint::getReferences(items);
}

double TaskFemConstraintPrescribedDisplacement::get_spinxDisplacement() const{return ui->spinxDisplacement->value();}
double TaskFemConstraintPrescribedDisplacement::get_spinyDisplacement() const{return ui->spinyDisplacement->value();}
double TaskFemConstraintPrescribedDisplacement::get_spinzDisplacement() const{return ui->spinzDisplacement->value();}
double TaskFemConstraintPrescribedDisplacement::get_rotxv() const{return ui->rotxv->value();}
double TaskFemConstraintPrescribedDisplacement::get_rotyv() const{return ui->rotyv->value();}
double TaskFemConstraintPrescribedDisplacement::get_rotzv() const{return ui->rotzv->value();}

bool TaskFemConstraintPrescribedDisplacement::get_dispxfix() const{return ui->dispxfix->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_dispxfree() const{return ui->dispxfree->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_dispyfix() const{return ui->dispyfix->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_dispyfree() const{return ui->dispyfree->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_dispzfix() const{return ui->dispzfix->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_dispzfree() const{return ui->dispzfree->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_rotxfix() const{return ui->rotxfix->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_rotxfree() const{return ui->rotxfree->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_rotyfix() const{return ui->rotyfix->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_rotyfree() const{return ui->rotyfree->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_rotzfix() const{return ui->rotzfix->isChecked();}
bool TaskFemConstraintPrescribedDisplacement::get_rotzfree() const{return ui->rotzfree->isChecked();}

//double TaskFemConstraintPrescribedDisplacement::getPressure(void) const
//{
//    Base::Quantity pressure =  ui->if_pressure->getQuantity();
//    double pressure_in_MPa = pressure.getValueAs(Base::Quantity::MegaPascal);
//    return pressure_in_MPa;
//}
//
//bool TaskFemConstraintPrescribedDisplacement::getReverse() const
//{
//    return ui->cb_reverse_direction->isChecked();
//}

void TaskFemConstraintPrescribedDisplacement::changeEvent(QEvent *e)
{
//    TaskBox::changeEvent(e);
//    if (e->type() == QEvent::LanguageChange) {
//        ui->if_pressure->blockSignals(true);
//        ui->retranslateUi(proxy);
//        ui->if_pressure->blockSignals(false);
//    }
}

//**************************************************************************
// TaskDialog
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TaskDlgFemConstraintPrescribedDisplacement::TaskDlgFemConstraintPrescribedDisplacement(ViewProviderFemConstraintPrescribedDisplacement *ConstraintView)
{
    this->ConstraintView = ConstraintView;
    assert(ConstraintView);
    this->parameter = new TaskFemConstraintPrescribedDisplacement(ConstraintView);;

    Content.push_back(parameter);
}

//==== calls from the TaskView ===============================================================

void TaskDlgFemConstraintPrescribedDisplacement::open()
{
    // a transaction is already open at creation time of the panel
    if (!Gui::Command::hasPendingCommand()) {
        QString msg = QObject::tr("Constraint normal stress");
        Gui::Command::openCommand((const char*)msg.toUtf8());
    }
}

bool TaskDlgFemConstraintPrescribedDisplacement::accept()
{
    std::string name = ConstraintView->getObject()->getNameInDocument();
    const TaskFemConstraintPrescribedDisplacement* parameterDisplacement = static_cast<const TaskFemConstraintPrescribedDisplacement*>(parameter);

    try {
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.xDisplacement = %f",
            name.c_str(), parameterDisplacement->get_spinxDisplacement());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.yDisplacement = %f",
            name.c_str(), parameterDisplacement->get_spinyDisplacement());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.zDisplacement = %f",
            name.c_str(), parameterDisplacement->get_spinzDisplacement());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.xRotation = %f",
            name.c_str(), parameterDisplacement->get_rotxv());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.yRotation = %f",
            name.c_str(), parameterDisplacement->get_rotyv());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.zRotation = %f",
            name.c_str(), parameterDisplacement->get_rotzv());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.xFree = %s",
            name.c_str(), parameterDisplacement->get_dispxfree() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.xFix = %s",
            name.c_str(), parameterDisplacement->get_dispxfix() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.yFree = %s",
            name.c_str(), parameterDisplacement->get_dispyfree() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.yFix = %s",
            name.c_str(), parameterDisplacement->get_dispyfix() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.zFree = %s",
            name.c_str(), parameterDisplacement->get_dispzfree() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.zFix = %s",
            name.c_str(), parameterDisplacement->get_dispzfix() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.rotxFree = %s",
            name.c_str(), parameterDisplacement->get_rotxfree() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.rotxFix = %s",
            name.c_str(), parameterDisplacement->get_rotxfix() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.rotyFree = %s",
            name.c_str(), parameterDisplacement->get_rotyfree() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.rotyFix = %s",
            name.c_str(), parameterDisplacement->get_rotyfix() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.rotzFree = %s",
            name.c_str(), parameterDisplacement->get_rotzfree() ? "True" : "False");
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.rotzFix = %s",
            name.c_str(), parameterDisplacement->get_rotzfix() ? "True" : "False");
    }
    catch (const Base::Exception& e) {
        QMessageBox::warning(parameter, tr("Input error"), QString::fromLatin1(e.what()));
        return false;
    }

    return TaskDlgFemConstraint::accept();
}

bool TaskDlgFemConstraintPrescribedDisplacement::reject()
{
    Gui::Command::abortCommand();
    Gui::Command::doCommand(Gui::Command::Gui,"Gui.activeDocument().resetEdit()");
    Gui::Command::updateActive();

    return true;
}

#include "moc_TaskFemConstraintPrescribedDisplacement.cpp"
