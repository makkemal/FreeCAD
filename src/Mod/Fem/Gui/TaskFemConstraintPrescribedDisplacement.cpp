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

//    QAction* action = new QAction(tr("Delete"), ui->lw_references);
//    action->connect(action, SIGNAL(triggered()), this, SLOT(onReferenceDeleted()));
//    ui->lw_references->addAction(action);
//    ui->lw_references->setContextMenuPolicy(Qt::ActionsContextMenu);

//    connect(ui->if_pressure, SIGNAL(valueChanged(Base::Quantity)),
//            this, SLOT(onPressureChanged(Base::Quantity)));
//    connect(ui->b_add_reference, SIGNAL(pressed()),
//            this, SLOT(onButtonReference()));
//    connect(ui->cb_reverse_direction, SIGNAL(toggled(bool)),
//            this, SLOT(onCheckReverse(bool)));
//
//    this->groupLayout()->addWidget(proxy);
//
//    // Temporarily prevent unnecessary feature recomputes
//    ui->if_pressure->blockSignals(true);
//    ui->lw_references->blockSignals(true);
//    ui->b_add_reference->blockSignals(true);
//    ui->cb_reverse_direction->blockSignals(true);
//
//    // Get the feature data
//    Fem::ConstraintPressure* pcConstraint = static_cast<Fem::ConstraintPressure*>(ConstraintView->getObject());
//    double f = pcConstraint->Pressure.getValue();
//    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
//    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
//    bool reversed = pcConstraint->Reversed.getValue();
//
//    // Fill data into dialog elements
//    ui->if_pressure->setMinimum(0);
//    ui->if_pressure->setMaximum(FLOAT_MAX);
//    //1000 because FreeCAD used kPa internally
//    Base::Quantity p = Base::Quantity(1000 * f, Base::Unit::Stress);
//    ui->if_pressure->setValue(p);
//    ui->lw_references->clear();
//    for (std::size_t i = 0; i < Objects.size(); i++) {
//        ui->lw_references->addItem(makeRefText(Objects[i], SubElements[i]));
//    }
//    if (Objects.size() > 0) {
//        ui->lw_references->setCurrentRow(0, QItemSelectionModel::ClearAndSelect);
//    }
//    ui->cb_reverse_direction->setChecked(reversed);
//
//    ui->if_pressure->blockSignals(false);
//    ui->lw_references->blockSignals(false);
//    ui->b_add_reference->blockSignals(false);
//    ui->cb_reverse_direction->blockSignals(false);

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
    onButtonReference(false);
    Gui::Selection().clearSelection();
    updateUI();
}

//void TaskFemConstraintPrescribedDisplacement::onPressureChanged(const Base::Quantity& f)
//{
//    Fem::ConstraintPressure* pcConstraint = static_cast<Fem::ConstraintPressure*>(ConstraintView->getObject());
//    double val = f.getValueAs(Base::Quantity::MegaPascal);
//    pcConstraint->Pressure.setValue(val);
//}

void TaskFemConstraintPrescribedDisplacement::onReferenceDeleted() {
    int row = ui->lw_references->currentIndex().row();
    TaskFemConstraint::onReferenceDeleted(row);
    ui->lw_references->model()->removeRow(row);
    ui->lw_references->setCurrentRow(0, QItemSelectionModel::ClearAndSelect);
}

//void TaskFemConstraintPrescribedDisplacement::onCheckReverse(const bool pressed)
//{
//    Fem::ConstraintPressure* pcConstraint = static_cast<Fem::ConstraintPressure*>(ConstraintView->getObject());
//    pcConstraint->Reversed.setValue(pressed);
//}

const std::string TaskFemConstraintPrescribedDisplacement::getReferences() const
{
    int rows = ui->lw_references->model()->rowCount();
    std::vector<std::string> items;
    for (int r = 0; r < rows; r++) {
        items.push_back(ui->lw_references->item(r)->text().toStdString());
    }
    return TaskFemConstraint::getReferences(items);
}

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
    TaskBox::changeEvent(e);
    if (e->type() == QEvent::LanguageChange) {
        ui->if_pressure->blockSignals(true);
        ui->retranslateUi(proxy);
        ui->if_pressure->blockSignals(false);
    }
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
//    std::string name = ConstraintView->getObject()->getNameInDocument();
//    const TaskFemConstraintPrescribedDisplacement* parameterPressure = static_cast<const TaskFemConstraintPrescribedDisplacement*>(parameter);
//
//    try {
//        
//         if (parameterPressure->getPressure()<=0)
//        {
//          QMessageBox::warning(parameter, tr("Input error"), tr("Please specify a pressure greater than 0"));  
//            return false;
//        }
//        else
//        {
//            Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Pressure = %f",
//            name.c_str(), parameterPressure->getPressure());
//            
//        }
//        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Reversed = %s",
//            name.c_str(), parameterPressure->getReverse() ? "True" : "False");
//    }
//    catch (const Base::Exception& e) {
//        QMessageBox::warning(parameter, tr("Input error"), QString::fromLatin1(e.what()));
//        return false;
//    }

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
