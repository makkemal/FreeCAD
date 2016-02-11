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

#include "Mod/Fem/App/FemConstraintHeatflux.h"
#include "TaskFemConstraintHeatflux.h"
#include "ui_TaskFemConstraintHeatflux.h"
#include <App/Application.h>
#include <Gui/Command.h>

using namespace FemGui;
using namespace Gui;

/* TRANSLATOR FemGui::TaskFemConstraintHeatflux */

TaskFemConstraintHeatflux::TaskFemConstraintHeatflux(ViewProviderFemConstraintHeatflux *ConstraintView,QWidget *parent)
  : TaskFemConstraint(ConstraintView, parent, "fem-constraint-heatflux")
{
    proxy = new QWidget(this);
    ui = new Ui_TaskFemConstraintHeatflux();
    ui->setupUi(proxy);
    QMetaObject::connectSlotsByName(this);

    QAction* action = new QAction(tr("Delete"), ui->lw_references);
    action->connect(action, SIGNAL(triggered()), this, SLOT(onReferenceDeleted()));
    ui->lw_references->addAction(action);
    ui->lw_references->setContextMenuPolicy(Qt::ActionsContextMenu);

    connect(ui->if_ambienttemp, SIGNAL(valueChanged(double)),
            this, SLOT(onAmbientTempChanged(double)));
    connect(ui->if_facetemp, SIGNAL(valueChanged(double)),
            this, SLOT(onFaceTempChanged(double)));
    connect(ui->if_filmcoef, SIGNAL(valueChanged(double)),
            this, SLOT(onFilmCoefChanged(double)));
    connect(ui->b_add_reference, SIGNAL(pressed()),
            this, SLOT(onButtonReference()));

    this->groupLayout()->addWidget(proxy);

    // Temporarily prevent unnecessary feature recomputes
    ui->if_heatflux->blockSignals(true);
    ui->if_facetemp->blockSignals(true);
    ui->if_filmcoef->blockSignals(true);
    ui->lw_references->blockSignals(true);

    // Get the feature data
    Fem::ConstraintHeatflux* pcConstraint = static_cast<Fem::ConstraintHeatflux*>(ConstraintView->getObject());
    double at = pcConstraint->AmbientTemp.getValue();
    double ft = pcConstraint->FaceTemp.getValue();
    double fc = pcConstraint->FilmCoef.getValue();
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();

    // Fill data into dialog elements
    ui->if_ambienttemp->setMinimum(-273);
    ui->if_ambienttemp->setMaximum(FLOAT_MAX);
    ui->if_facetemp->setMinimum(-273);
    ui->if_facetemp->setMaximum(FLOAT_MAX);
    ui->if_filmcoef->setMinimum(0);
    ui->if_filmcoef->setMaximum(FLOAT_MAX);

    ui->if_ambienttemp->setValue(at);
    ui->if_facetemp->setValue(ft);
    ui->if_filmcoef->setValue(fc);
    
    ui->lw_references->clear();
    for (std::size_t i = 0; i < Objects.size(); i++) {
        ui->lw_references->addItem(makeRefText(Objects[i], SubElements[i]));
    }
    if (Objects.size() > 0) {
        ui->lw_references->setCurrentRow(0, QItemSelectionModel::ClearAndSelect);
    }

    ui->if_ambienttemp->blockSignals(false);
    ui->if_facetemp->blockSignals(false);
    ui->if_filmcoef->blockSignals(false);
    ui->lw_references->blockSignals(false);
    ui->b_add_reference->blockSignals(false);
    
    //Selection buttons
    connect(ui->btnAdd, SIGNAL(clicked()),  this, SLOT(addToSelection()));
    connect(ui->btnRemove, SIGNAL(clicked()),  this, SLOT(removeFromSelection()));

    updateUI();
}

TaskFemConstraintHeatflux::~TaskFemConstraintHeatflux()
{
    delete ui;
}

void TaskFemConstraintHeatflux::updateUI()
{
    if (ui->lw_references->model()->rowCount() == 0) {
        // Go into reference selection mode if no reference has been selected yet
        onButtonReference(true);
        return;
    }
}

void TaskFemConstraintHeatflux::onSelectionChanged(const Gui::SelectionChanges& msg)
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
    Fem::ConstraintHeatflux* pcConstraint = static_cast<Fem::ConstraintHeatflux*>(ConstraintView->getObject());
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

void TaskFemConstraintHeatflux::onAmbientTempChanged(const Base::Quantity& f)
{
    Fem::ConstraintHeatflux* pcConstraint = static_cast<Fem::ConstraintHeatflux*>(ConstraintView->getObject());
    double val = f.getValueAs(Base::Quantity::Centigrade);
    pcConstraint->AmbientTemp.setValue(val);
}

void TaskFemConstraintHeatflux::onFaceTempChanged(const Base::Quantity& f)
{
    Fem::ConstraintHeatflux* pcConstraint = static_cast<Fem::ConstraintHeatflux*>(ConstraintView->getObject());
    double val = f.getValueAs(Base::Quantity::Centigrade);
    pcConstraint->FaceTemp.setValue(val);
}

void TaskFemConstraintHeatflux::onFilmCoefChanged(const Base::Quantity& f)
{
    Fem::ConstraintHeatflux* pcConstraint = static_cast<Fem::ConstraintHeatflux*>(ConstraintView->getObject());
    double val = f.getValue(); // [W]/[[degC].[m^2]]
    pcConstraint->FilmCoef.setValue(val);
}

void TaskFemConstraintHeatflux::addToSelection()
{
    std::vector<Gui::SelectionObject> selection = Gui::Selection().getSelectionEx(); //gets vector of selected objects of active document
    if (selection.size()==0){
        QMessageBox::warning(this, tr("Selection error"), tr("Nothing selected!"));
        return;
    }

    Fem::ConstraintDisplacement* pcConstraint = static_cast<Fem::ConstraintDisplacement*>(ConstraintView->getObject());
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
    
    for (std::vector<Gui::SelectionObject>::iterator it = selection.begin();  it != selection.end(); ++it){//for every selected object
        if (static_cast<std::string>(it->getTypeName()).substr(0,4).compare(std::string("Part"))!=0){
            QMessageBox::warning(this, tr("Selection error"),tr("Selected object is not a part!"));
            return;
        }

        std::vector<std::string> subNames=it->getSubNames();

        if (subNames.size()>0){
            for (unsigned int subIt=0;subIt<(subNames.size());++subIt){
                if (subNames[subIt].substr(0,4).compare(std::string("Face"))!=0){
                    QMessageBox::warning(this, tr("Selection error"),tr("Selection must only consist of faces!"));
                    return;
                }
            }
        }
        else{
            //fix me, if an object is selected completely, getSelectionEx does not return any SubElements
        }

        App::DocumentObject* obj = ConstraintView->getObject()->getDocument()->getObject(it->getFeatName());
        for (unsigned int subIt=0;subIt<(subNames.size());++subIt){// for every selected sub element
            bool addMe=true;
            for (std::vector<std::string>::iterator itr=std::find(SubElements.begin(),SubElements.end(),subNames[subIt]);
                   itr!= SubElements.end();
                   itr =  std::find(++itr,SubElements.end(),subNames[subIt]))
            {// for every sub element in selection that matches one in old list
                if (obj==Objects[std::distance(SubElements.begin(),itr)]){//if selected sub element's object equals the one in old list then it was added before so don't add
                    addMe=false;
                }
            }
            if (addMe){
                Objects.push_back(obj);
                SubElements.push_back(subNames[subIt]);
                ui->lw_references->addItem(makeRefText(obj, subNames[subIt]));
            }
        }
    }
    //Update UI
    pcConstraint->References.setValues(Objects,SubElements);
    updateUI();
}

void TaskFemConstraintHeatflux::removeFromSelection()
{
    std::vector<Gui::SelectionObject> selection = Gui::Selection().getSelectionEx(); //gets vector of selected objects of active document
    if (selection.size()==0){
        QMessageBox::warning(this, tr("Selection error"), tr("Nothing selected!"));
        return;
    }

    Fem::ConstraintDisplacement* pcConstraint = static_cast<Fem::ConstraintDisplacement*>(ConstraintView->getObject());
    std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
    std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
    std::vector<int> itemsToDel;
    for (std::vector<Gui::SelectionObject>::iterator it = selection.begin();  it != selection.end(); ++it){//for every selected object
        if (static_cast<std::string>(it->getTypeName()).substr(0,4).compare(std::string("Part"))!=0){
            QMessageBox::warning(this, tr("Selection error"),tr("Selected object is not a part!"));
            return;
        }
        
        std::vector<std::string> subNames=it->getSubNames();

        if (subNames.size()>0){
            for (unsigned int subIt=0;subIt<(subNames.size());++subIt){
                if (subNames[subIt].substr(0,4).compare(std::string("Face"))!=0){
                    QMessageBox::warning(this, tr("Selection error"),tr("Selection must only consist of faces!"));
                    return;
                }
            }
        }
        else{
            //fix me, if an object is selected completely, getSelectionEx does not return any SubElements
        }
        
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
    
    while (itemsToDel.size()>0){
        Objects.erase(Objects.begin()+itemsToDel.back());
        SubElements.erase(SubElements.begin()+itemsToDel.back());
        itemsToDel.pop_back();
    }
    //Update UI
    disconnect(ui->lw_references, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
        this, SLOT(setSelection(QListWidgetItem*)));
    
    ui->lw_references->clear();
    for (unsigned int j=0;j<Objects.size();j++){
        ui->lw_references->addItem(makeRefText(Objects[j], SubElements[j]));
    }
    connect(ui->lw_references, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),
        this, SLOT(setSelection(QListWidgetItem*)));
    
    pcConstraint->References.setValues(Objects,SubElements);
    updateUI();
}


void TaskFemConstraintHeatflux::setSelection(QListWidgetItem* item){
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

void TaskFemConstraintHeatflux::onReferenceDeleted() {
    int row = ui->lw_references->currentIndex().row();
    TaskFemConstraint::onReferenceDeleted(row);
    ui->lw_references->model()->removeRow(row);
    ui->lw_references->setCurrentRow(0, QItemSelectionModel::ClearAndSelect);
}

const std::string TaskFemConstraintHeatflux::getReferences() const
{
    int rows = ui->lw_references->model()->rowCount();
    std::vector<std::string> items;
    for (int r = 0; r < rows; r++) {
        items.push_back(ui->lw_references->item(r)->text().toStdString());
    }
    return TaskFemConstraint::getReferences(items);
}

double TaskFemConstraintHeatflux::getHeatflux(void) const
{
    Base::Quantity ambienttemp =  ui->if_heatflux->getQuantity();
    double ambienttemp_in_degC = heatflux.getValueAs(Base::Quantity::MegaPascal);
    return heatflux_in_MPa;
}

double TaskFemConstraintHeatflux::getHeatflux(void) const
{
    Base::Quantity heatflux =  ui->if_heatflux->getQuantity();
    double heatflux_in_MPa = heatflux.getValueAs(Base::Quantity::MegaPascal);
    return heatflux_in_MPa;
}

double TaskFemConstraintHeatflux::getAmbientTemp(void) const
{
    Base::Quantity ambienttemp =  ui->if_ambienttemp->getQuantity();
    double ambienttemp_in_degC = heatflux.getValueAs(Base::Quantity::Centigrade);
    return ambienttemp_in_degC;
}

double TaskFemConstraintHeatflux::getHeatflux(void) const
{
    Base::Quantity facetemp =  ui->if_facetemp->getQuantity();
    double facetemp_in_degC = facetemp.getValueAs(Base::Quantity::Centigrade);
    return facetemp_in_degC;
}

double TaskFemConstraintHeatflux::getHeatflux(void) const
{
    Base::Quantity filmcoef =  ui->if_filmcoef->getQuantity();
    double filmcoef_in_WpdegCMsqrd = filmcoef.getValue(); // [W]/[[degC].[m^2]]
    return filmcoef_in_WpdegCMsqrd;
}

void TaskFemConstraintHeatflux::changeEvent(QEvent *e)
{
    TaskBox::changeEvent(e);
    if (e->type() == QEvent::LanguageChange) {
        ui->if_ambienttemp->blockSignals(true);
        ui->if_facetemp->blockSignals(true);
        ui->if_filmcoef->blockSignals(true);
        ui->retranslateUi(proxy);
        ui->if_heatflux->blockSignals(false);
        ui->if_facetemp->blockSignals(false);
        ui->if_filmcoef->blockSignals(false);
    }
}

//**************************************************************************
// TaskDialog
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TaskDlgFemConstraintHeatflux::TaskDlgFemConstraintHeatflux(ViewProviderFemConstraintHeatflux *ConstraintView)
{
    this->ConstraintView = ConstraintView;
    assert(ConstraintView);
    this->parameter = new TaskFemConstraintHeatflux(ConstraintView);;

    Content.push_back(parameter);
}

//==== calls from the TaskView ===============================================================

void TaskDlgFemConstraintHeatflux::open()
{
    // a transaction is already open at creation time of the panel
    if (!Gui::Command::hasPendingCommand()) {
        QString msg = QObject::tr("Constraint heatflux");
        Gui::Command::openCommand((const char*)msg.toUtf8());
    }
}

bool TaskDlgFemConstraintHeatflux::accept()
{
    std::string name = ConstraintView->getObject()->getNameInDocument();
    const TaskFemConstraintHeatflux* parameterHeatflux = static_cast<const TaskFemConstraintHeatflux*>(parameter);
    std::string scale = "1";
    
    try {
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.AmbientTemp = %f",
            name.c_str(), parameterHeatflux->getAmbientTemp());
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.FaceTemp = %f",
            name.c_str(), parameterHeatflux->getFaceTemp()); 
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.FilmCoef = %f",
            name.c_str(), parameterHeatflux->getFilmCoef()); 
        
        scale = parameterHeatflux->getScale();  //OvG: determine modified scale
        Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Scale = %s",
            name.c_str(), scale.c_str()); //OvG: implement modified scale
    }
    catch (const Base::Exception& e) {
        QMessageBox::warning(parameter, tr("Input error"), QString::fromLatin1(e.what()));
        return false;
    }

    return TaskDlgFemConstraint::accept();
}

bool TaskDlgFemConstraintHeatflux::reject()
{
    Gui::Command::abortCommand();
    Gui::Command::doCommand(Gui::Command::Gui,"Gui.activeDocument().resetEdit()");
    Gui::Command::updateActive();

    return true;
}

#include "moc_TaskFemConstraintHeatflux.cpp"
