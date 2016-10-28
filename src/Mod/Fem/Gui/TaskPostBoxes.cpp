/***************************************************************************
 *   Copyright (c) 2015 Stefan Tröger <stefantroeger@gmx.net>              *
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
#endif

#include "ui_TaskPostDisplay.h"
#include "ui_TaskPostClip.h"
#include "ui_TaskPostLinearizedStresses.h"
#include "ui_TaskPostScalarClip.h"
#include "ui_TaskPostWarpVector.h"
#include "ui_TaskPostCut.h"
#include "TaskPostBoxes.h"
#include "ViewProviderFemPostObject.h"
#include "ViewProviderFemPostFunction.h"
#include "ViewProviderFemPostFilter.h"
#include <Mod/Fem/App/FemPostObject.h>
#include <Mod/Fem/App/FemPostFilter.h>
#include <Mod/Fem/App/FemPostPipeline.h>
#include <Gui/BitmapFactory.h>
#include <Gui/Application.h>
#include <Gui/Document.h>
#include <Gui/Command.h>
#include <Gui/Action.h>
#include <QMessageBox>
#include <QPushButton>
#include <Gui/View3DInventor.h>
#include <Gui/View3DInventorViewer.h>
# include <Inventor/events/SoMouseButtonEvent.h>

# include <sstream>
# include <QApplication>
# include <Inventor/SoPickedPoint.h>
# include <Inventor/nodes/SoAnnotation.h>
# include <Inventor/nodes/SoBaseColor.h>
# include <Inventor/nodes/SoFontStyle.h>
# include <Inventor/nodes/SoPickStyle.h>
# include <Inventor/nodes/SoText2.h>
# include <Inventor/nodes/SoTranslation.h>
# include <Inventor/nodes/SoCoordinate3.h>
# include <Inventor/nodes/SoIndexedLineSet.h>
# include <Inventor/nodes/SoMarkerSet.h>
# include <Inventor/nodes/SoDrawStyle.h>
#include <Gui/View3DInventorViewer.h>

#include <App/PropertyGeo.h>
#include <App/PropertyStandard.h>
#include <Base/Quantity.h>

using namespace FemGui;
using namespace Gui;

// ----------------------------------------------------------------------------

PointMarker::PointMarker(Gui::View3DInventorViewer* iv, const QString &text) : view(iv),
    vp(new ViewProviderPointMarker)
{
    view->addViewProvider(vp);
    m_name = text;
}

PointMarker::~PointMarker()
{
    view->removeViewProvider(vp);
    delete vp;
}

void PointMarker::addPoint(const SbVec3f& pt)
{
    int ct = countPoints();
    vp->pCoords->point.set1Value(ct, pt);
    vp->pMarker->numPoints=ct+1;
}

int PointMarker::countPoints() const
{
    return vp->pCoords->point.getNum();
}

void PointMarker::customEvent(QEvent*)
{
    const SbVec3f& pt1 = vp->pCoords->point[0];
    const SbVec3f& pt2 = vp->pCoords->point[1];

    Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Point1 = App.Vector(%f, %f, %f)", m_name.c_str(), pt1[0],pt1[1], pt1[2]);
    Gui::Command::doCommand(Gui::Command::Doc,"App.ActiveDocument.%s.Point2 = App.Vector(%f, %f, %f)", m_name.c_str(), pt2[0],pt2[1], pt2[2]);

}

PROPERTY_SOURCE(FemGui::ViewProviderPointMarker, Gui::ViewProviderDocumentObject)

ViewProviderPointMarker::ViewProviderPointMarker()
{
    pCoords = new SoCoordinate3();
    pCoords->ref();
    pCoords->point.setNum(0);
    pMarker = new SoMarkerSet();
    pMarker->markerIndex = SoMarkerSet::CROSS_9_9;
    pMarker->numPoints=0;
    pMarker->ref();

    SoGroup* grp = new SoGroup();
    grp->addChild(pCoords);
    grp->addChild(pMarker);
    addDisplayMaskMode(grp, "Base");
    setDisplayMaskMode("Base");
}

ViewProviderPointMarker::~ViewProviderPointMarker()
{
    pCoords->unref();
    pMarker->unref();
}

//**************************************************************************
//**************************************************************************
// TaskDialog
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TaskDlgPost::TaskDlgPost(Gui::ViewProviderDocumentObject *view,bool newObj)
    : TaskDialog(), m_view(view)
{
    assert(view);
}

TaskDlgPost::~TaskDlgPost()
{

}

QDialogButtonBox::StandardButtons TaskDlgPost::getStandardButtons(void) const {

    //check if we only have gui task boxes
    bool guionly = true;
    for(std::vector<TaskPostBox*>::const_iterator it = m_boxes.begin(); it != m_boxes.end(); ++it)
        guionly = guionly && (*it)->isGuiTaskOnly();

    if(!guionly)
        return QDialogButtonBox::Apply|QDialogButtonBox::Ok|QDialogButtonBox::Cancel;
    else
        return QDialogButtonBox::Ok;
}


void TaskDlgPost::appendBox(TaskPostBox* box) {

    m_boxes.push_back(box);
    Content.push_back(box);
}

void TaskDlgPost::open()
{
    // a transaction is already open at creation time of the pad
    QString msg = QObject::tr("Edit post processing object");
    Gui::Command::openCommand((const char*)msg.toUtf8());
}

void TaskDlgPost::clicked(int button)
{
    if(button == QDialogButtonBox::Apply)
        getView()->getObject()->getDocument()->recompute();
}

bool TaskDlgPost::accept()
{

    try {
        std::vector<TaskPostBox*>::iterator it = m_boxes.begin();
        for(;it != m_boxes.end(); ++it)
            (*it)->applyPythonCode();
    }
    catch (const Base::Exception& e) {
        QMessageBox::warning(NULL, tr("Input error"), QString::fromLatin1(e.what()));
        return false;
    }

    Gui::Command::doCommand(Gui::Command::Gui,"Gui.activeDocument().resetEdit()");
    return true;
}

bool TaskDlgPost::reject()
{
    // roll back the done things
    Gui::Command::abortCommand();
    Gui::Command::doCommand(Gui::Command::Gui,"Gui.activeDocument().resetEdit()");

    return true;
}

void TaskDlgPost::modifyStandardButtons(QDialogButtonBox* box) {

    if(box->button(QDialogButtonBox::Apply))
        box->button(QDialogButtonBox::Apply)->setDefault(true);
}
//############################################################################################

TaskPostBox::TaskPostBox(Gui::ViewProviderDocumentObject* view, const QPixmap &icon, const QString &title, QWidget* parent)
    : TaskBox(icon, title, true, parent) {

    m_view = view;
    m_object = view->getObject();
}

TaskPostBox::~TaskPostBox() {

}

bool TaskPostBox::autoApply() {

    ParameterGrp::handle pGroup = App::GetApplication().GetParameterGroupByPath("User parameter:BaseApp/Preferences/Mod/Fem");
    return pGroup->GetBool("PostAutoRecompute", false);
}

void TaskPostBox::recompute() {

    if(autoApply())
        App::GetApplication().getActiveDocument()->recompute();
}

void TaskPostBox::updateEnumerationList(App::PropertyEnumeration& prop, QComboBox* box) {

    box->clear();
    QStringList list;
    std::vector<std::string> vec = prop.getEnumVector();
    for(std::vector<std::string>::iterator it = vec.begin(); it != vec.end(); ++it ) {
        list.push_back(QString::fromStdString(*it));
    }

    box->insertItems(0, list);
    box->setCurrentIndex(prop.getValue());
}

void TaskPostBox::updateLinearizedEnumerationList(App::PropertyEnumeration& prop, QComboBox* box) {

    box->clear();
    QStringList list;
    std::vector<std::string> vec = prop.getEnumVector();
    int counter = 0;
    std::vector<int> disabledItems;
    for(std::vector<std::string>::iterator it = vec.begin(); it != vec.end(); ++it ) {
        if ((*it == "Temperature") || (*it == "Displacement") || (*it == "User Defined Results"))
            disabledItems.push_back(counter);
        list.push_back(QString::fromStdString(*it));
        ++counter;
    }

    box->insertItems(0, list);
    box->setCurrentIndex(prop.getValue());
    QVariant v(0);
    for (std::size_t i = 0; i < disabledItems.size(); i++)
        box->setItemData(disabledItems[i], v, Qt::UserRole -1);
}

//###########################################################################################################

TaskPostDisplay::TaskPostDisplay(Gui::ViewProviderDocumentObject* view, QWidget *parent)
    : TaskPostBox(view, Gui::BitmapFactory().pixmap("fem-fem-mesh-create-node-by-poly"), tr("Display options"), parent)
{
    //we need a separate container widget to add all controls to
    proxy = new QWidget(this);
    ui = new Ui_TaskPostDisplay();
    ui->setupUi(proxy);
    QMetaObject::connectSlotsByName(this);

    this->groupLayout()->addWidget(proxy);

    //update all fields
    updateEnumerationList(getTypedView<ViewProviderFemPostObject>()->DisplayMode, ui->Representation);
    updateEnumerationList(getTypedView<ViewProviderFemPostObject>()->Field, ui->Field);
    updateEnumerationList(getTypedView<ViewProviderFemPostObject>()->VectorMode, ui->VectorMode);
}

TaskPostDisplay::~TaskPostDisplay()
{
    delete ui;
}

void TaskPostDisplay::on_Representation_activated(int i) {

    getTypedView<ViewProviderFemPostObject>()->DisplayMode.setValue(i);
    updateEnumerationList(getTypedView<ViewProviderFemPostObject>()->Field, ui->Field);
    updateEnumerationList(getTypedView<ViewProviderFemPostObject>()->VectorMode, ui->VectorMode);
}

void TaskPostDisplay::on_Field_activated(int i) {

    getTypedView<ViewProviderFemPostObject>()->Field.setValue(i);
    updateEnumerationList(getTypedView<ViewProviderFemPostObject>()->VectorMode, ui->VectorMode);
}

void TaskPostDisplay::on_VectorMode_activated(int i) {

    getTypedView<ViewProviderFemPostObject>()->VectorMode.setValue(i);
}

void TaskPostDisplay::on_Transparency_valueChanged(int i) {

    getTypedView<ViewProviderFemPostObject>()->Transperency.setValue(i);
}

void TaskPostDisplay::applyPythonCode() {

}

//############################################################################################

TaskPostFunction::TaskPostFunction(ViewProviderDocumentObject* view, QWidget* parent): TaskPostBox(view, Gui::BitmapFactory().pixmap("fem-fem-mesh-create-node-by-poly"), tr("Implicit function"), parent) {

    assert(view->isDerivedFrom(ViewProviderFemPostFunction::getClassTypeId()));

    //we load the views widget
    FunctionWidget* w = getTypedView<ViewProviderFemPostFunction>()->createControlWidget();
    w->setParent(this);
    w->setViewProvider(getTypedView<ViewProviderFemPostFunction>());
    this->groupLayout()->addWidget(w);
}

TaskPostFunction::~TaskPostFunction() {

}

void TaskPostFunction::applyPythonCode() {

    //we apply the views widgets python code
}

//############################################################################################

TaskPostClip::TaskPostClip(ViewProviderDocumentObject* view, App::PropertyLink* function, QWidget* parent)
    : TaskPostBox(view,Gui::BitmapFactory().pixmap("fem-fem-mesh-create-node-by-poly"), tr("Choose implicit function"), parent) {

    assert(view->isDerivedFrom(ViewProviderFemPostClip::getClassTypeId()));
    assert(function);

    fwidget = NULL;

    //we load the views widget
    proxy = new QWidget(this);
    ui = new Ui_TaskPostClip();
    ui->setupUi(proxy);
    QMetaObject::connectSlotsByName(this);
    this->groupLayout()->addWidget(proxy);

    //the layout for the container widget
    QVBoxLayout *layout = new QVBoxLayout();
    ui->Container->setLayout(layout);

    //fill up the combo box with possible functions
    collectImplicitFunctions();

    //add the function creation command
    Gui::CommandManager &rcCmdMgr = Gui::Application::Instance->commandManager();
    rcCmdMgr.getCommandByName("Fem_PostCreateFunctions")->getAction()->addTo(ui->CreateButton);
    ui->CreateButton->setPopupMode(QToolButton::InstantPopup);

    //load the default values
    ui->CutCells->setChecked(static_cast<Fem::FemPostClipFilter*>(getObject())->CutCells.getValue());
    ui->InsideOut->setChecked(static_cast<Fem::FemPostClipFilter*>(getObject())->InsideOut.getValue());
}

TaskPostClip::~TaskPostClip() {

}

void TaskPostClip::applyPythonCode() {

}

void TaskPostClip::collectImplicitFunctions() {

    std::vector<Fem::FemPostPipeline*> pipelines;
    pipelines = App::GetApplication().getActiveDocument()->getObjectsOfType<Fem::FemPostPipeline>();
    if (!pipelines.empty()) {
        Fem::FemPostPipeline *pipeline = pipelines.front();
        if(pipeline->Functions.getValue() &&
           pipeline->Functions.getValue()->getTypeId() == Fem::FemPostFunctionProvider::getClassTypeId()) {

            ui->FunctionBox->clear();
            QStringList items;
            const std::vector<App::DocumentObject*>& funcs = static_cast<Fem::FemPostFunctionProvider*>(
                                                            pipeline->Functions.getValue())->Functions.getValues();
            for(std::size_t i=0; i<funcs.size(); ++i)
                items.push_back(QString::fromLatin1(funcs[i]->getNameInDocument()));

            ui->FunctionBox->addItems(items);
        }
    }
}

void TaskPostClip::on_CreateButton_triggered(QAction* a) {

    collectImplicitFunctions();
    recompute();
}

void TaskPostClip::on_FunctionBox_currentIndexChanged(int idx) {

    //set the correct property
    std::vector<Fem::FemPostPipeline*> pipelines;
    pipelines = App::GetApplication().getActiveDocument()->getObjectsOfType<Fem::FemPostPipeline>();
    if (!pipelines.empty()) {
        Fem::FemPostPipeline *pipeline = pipelines.front();
        if(pipeline->Functions.getValue() &&
           pipeline->Functions.getValue()->getTypeId() == Fem::FemPostFunctionProvider::getClassTypeId()) {

            const std::vector<App::DocumentObject*>& funcs = static_cast<Fem::FemPostFunctionProvider*>(
                                                            pipeline->Functions.getValue())->Functions.getValues();
            if(idx>=0)
                static_cast<Fem::FemPostClipFilter*>(getObject())->Function.setValue(funcs[idx]);
            else
                static_cast<Fem::FemPostClipFilter*>(getObject())->Function.setValue(NULL);
        }
    }

    //load the correct view
    Fem::FemPostFunction* fobj = static_cast<Fem::FemPostFunction*>(
                                    static_cast<Fem::FemPostClipFilter*>(getObject())->Function.getValue());
    Gui::ViewProvider* view = NULL;
    if(fobj)
        view = Gui::Application::Instance->activeDocument()->getViewProvider(fobj);

    if(fwidget)
        fwidget->deleteLater();

    if(view) {
        fwidget = static_cast<FemGui::ViewProviderFemPostFunction*>(view)->createControlWidget();
        fwidget->setParent(ui->Container);
        fwidget->setViewProvider(static_cast<FemGui::ViewProviderFemPostFunction*>(view));
        ui->Container->layout()->addWidget(fwidget);
    }
    recompute();
}

void TaskPostClip::on_CutCells_toggled(bool val) {

    static_cast<Fem::FemPostClipFilter*>(getObject())->CutCells.setValue(val);
    recompute();
}

void TaskPostClip::on_InsideOut_toggled(bool val) {

    static_cast<Fem::FemPostClipFilter*>(getObject())->InsideOut.setValue(val);
    recompute();
}
//############################################################################################

TaskPostLinearizedStresses::TaskPostLinearizedStresses(ViewProviderDocumentObject* view, App::PropertyLink* function, QWidget* parent)
    : TaskPostBox(view,Gui::BitmapFactory().pixmap("fem-fem-mesh-create-node-by-poly"), tr("Choose implicit function"), parent) {

    assert(view->isDerivedFrom(ViewProviderFemPostLinearizedStresses::getClassTypeId()));
    assert(function);

    fwidget = NULL;

    //we load the views widget
    proxy = new QWidget(this);
    ui = new Ui_TaskPostLinearizedStresses();
    ui->setupUi(proxy);
    QMetaObject::connectSlotsByName(this);
    this->groupLayout()->addWidget(proxy);

    //the layout for the container widget
    QVBoxLayout *layout = new QVBoxLayout();
    ui->Container->setLayout(layout);

    //fill up the combo box with possible functions
    collectImplicitFunctions();

    //add the function creation command
    Gui::CommandManager &rcCmdMgr = Gui::Application::Instance->commandManager();
    rcCmdMgr.getCommandByName("Fem_PostCreateLineFunction")->getAction()->addTo(ui->CreateButton);
    ui->CreateButton->setPopupMode(QToolButton::InstantPopup);

    //load the default values
    static_cast<Fem::FemPostLinearizedStressesFilter*>(getObject())->CutCells.setValue(1);
    static_cast<Fem::FemPostLinearizedStressesFilter*>(getObject())->InsideOut.setValue(1);
    recompute();

    //update all fields
    updateLinearizedEnumerationList(getTypedView<ViewProviderFemPostObject>()->DisplayMode, ui->Representation);
    updateLinearizedEnumerationList(getTypedView<ViewProviderFemPostObject>()->Field, ui->Field);
}

TaskPostLinearizedStresses::~TaskPostLinearizedStresses() {

}

void TaskPostLinearizedStresses::applyPythonCode() {

}

void TaskPostLinearizedStresses::collectImplicitFunctions() {

    std::vector<Fem::FemPostPipeline*> pipelines;
    pipelines = App::GetApplication().getActiveDocument()->getObjectsOfType<Fem::FemPostPipeline>();
    if (!pipelines.empty()) {
        Fem::FemPostPipeline *pipeline = pipelines.front();
        if(pipeline->Functions.getValue() &&
           pipeline->Functions.getValue()->getTypeId() == Fem::FemPostFunctionProvider::getClassTypeId()) {

            ui->FunctionBox->clear();
            QStringList items;
            const std::vector<App::DocumentObject*>& funcs = static_cast<Fem::FemPostFunctionProvider*>(
                                                            pipeline->Functions.getValue())->Functions.getValues();
            for(std::size_t i=0; i<funcs.size(); ++i)
                items.push_back(QString::fromLatin1(funcs[i]->getNameInDocument()));

            ui->FunctionBox->addItems(items);
        }
    }
}

void TaskPostLinearizedStresses::on_CreateButton_triggered(QAction* a) {

    collectImplicitFunctions();
    recompute();
}

void TaskPostLinearizedStresses::on_FunctionBox_currentIndexChanged(int idx) {

    //set the correct property
    std::vector<Fem::FemPostPipeline*> pipelines;
    pipelines = App::GetApplication().getActiveDocument()->getObjectsOfType<Fem::FemPostPipeline>();
    if (!pipelines.empty()) {
        Fem::FemPostPipeline *pipeline = pipelines.front();
        if(pipeline->Functions.getValue() &&
           pipeline->Functions.getValue()->getTypeId() == Fem::FemPostFunctionProvider::getClassTypeId()) {

            const std::vector<App::DocumentObject*>& funcs = static_cast<Fem::FemPostFunctionProvider*>(
                                                            pipeline->Functions.getValue())->Functions.getValues();
            if(idx>=0)
                static_cast<Fem::FemPostLinearizedStressesFilter*>(getObject())->Function.setValue(funcs[idx]);
            else
                static_cast<Fem::FemPostLinearizedStressesFilter*>(getObject())->Function.setValue(NULL);
        }
    }

    //load the correct view
    Fem::FemPostFunction* fobj = static_cast<Fem::FemPostFunction*>(
                                    static_cast<Fem::FemPostLinearizedStressesFilter*>(getObject())->Function.getValue());
    Gui::ViewProvider* view = NULL;
    if(fobj)
        view = Gui::Application::Instance->activeDocument()->getViewProvider(fobj);

    if(fwidget)
        fwidget->deleteLater();

    if(view) {
        fwidget = static_cast<FemGui::ViewProviderFemPostFunction*>(view)->createControlWidget();
        fwidget->setParent(ui->Container);
        fwidget->setViewProvider(static_cast<FemGui::ViewProviderFemPostFunction*>(view));
        ui->Container->layout()->addWidget(fwidget);
    }
    recompute();
}
// Yay for cheezy drawings!
/* XPM */
static const char * cursor_triangle[] = {
"32 32 3 1",
" 	c None",
".	c #FFFFFF",
"+	c #FF0000",
"      .                         ",
"      .                         ",
"      .                         ",
"      .                         ",
"      .                         ",
"                                ",
".....   .....                   ",
"                                ",
"      .                         ",
"      .                         ",
"      .        ++               ",
"      .       +  +              ",
"      .      + ++ +             ",
"            + ++++ +            ",
"           +  ++ ++ +           ",
"          + ++++++++ +          ",
"         ++  ++  ++  ++         "};
void TaskPostLinearizedStresses::on_SelectPoints_clicked() {

    Gui::Document* doc = Gui::Application::Instance->activeDocument();
    Gui::View3DInventor* view = static_cast<Gui::View3DInventor*>(doc->getActiveView());
    if (view) {
        Gui::View3DInventorViewer* viewer = view->getViewer();
        viewer->setEditing(true);
        viewer->setEditingCursor(QCursor(QPixmap(cursor_triangle), 7, 7));

        // Derives from QObject and we have a parent object, so we don't
        // require a delete.
        FemGui::PointMarker* marker = new FemGui::PointMarker(viewer, ui->FunctionBox->currentText());
        viewer->addEventCallback(SoMouseButtonEvent::getClassTypeId(),
            FemGui::ViewProviderFemPostLineFunction::pointCallback, marker);
     }
}

void TaskPostLinearizedStresses::on_PlotValues_clicked() {

    Gui::Command::doCommand(Gui::Command::Doc,LinearCalcs().c_str());
    recompute();
}

void TaskPostLinearizedStresses::on_Representation_activated(int i) {

    getTypedView<ViewProviderFemPostObject>()->DisplayMode.setValue(i);
    updateLinearizedEnumerationList(getTypedView<ViewProviderFemPostObject>()->Field, ui->Field);
}

void TaskPostLinearizedStresses::on_Field_activated(int i) {

    getTypedView<ViewProviderFemPostObject>()->Field.setValue(i);
}

std::string TaskPostLinearizedStresses::LinearCalcs() {

    return "t=0\n\
for i in range(len(StressPoints)):\n\
        for j in range(len(StressPoints)):\n\
                if i != j:\n\
                        d = ((StressPoints[i][0]-StressPoints[j][0])**2 + (StressPoints[i][1]-StressPoints[j][1])**2 + (StressPoints[i][2]-StressPoints[j][2])**2)**0.5\n\
                        if d>t:\n\
                                t = d\n\
                                x = StressPoints[i][0]\n\
                                y = StressPoints[i][1]\n\
                                z = StressPoints[i][2]\n\
                                first = [i,x,y,z]\n\
coords = [first]\n\
for i in range(len(StressPoints)):\n\
        p = 0\n\
        for j in range(len(coords)):\n\
                if ((coords[j][1]-StressPoints[i][0])**2 + (coords[j][2]-StressPoints[i][1])**2 + (coords[j][3]-StressPoints[i][2])**2)**0.5 > 0.2:\n\
                        p = p+1\n\
                if p == len(coords):\n\
                        x = StressPoints[i][0]\n\
                        y = StressPoints[i][1]\n\
                        z = StressPoints[i][2]\n\
                        entry = [i,x,y,z]\n\
                        coords.append(entry)\n\
for i in range(len(coords)-1):\n\
        d = t\n\
        pos = 0\n\
        for j in range(i+1, len(coords)):\n\
                dn = ((coords[i][1]-coords[j][1])**2 + (coords[i][2]-coords[j][2])**2 + (coords[i][3]-coords[j][3])**2)**0.5 \n\
                if dn < d:\n\
                        d = dn\n\
                        pos = j\n\
        temp = coords[i+1]\n\
        coords[i+1] =coords[pos]\n\
        coords[pos] = temp\n\
st = []\n\
for i in range(len(StressValues)): \n\
        for j in range(len(coords)):\n\
                if i == coords[j][0]:\n\
                        value = StressValues[i]\n\
                        entry = [i , value]\n\
                        st.append(entry)\n\
sValues = []\n\
for i in range(len(coords)):\n\
        for j in range(len(coords)):\n\
               if coords[i][0] == st[j][0]:\n\
                        sValues.append(st[j][1])\n\
t_coords = [-t/2]\n\
x = 0\n\
membrane = []\n\
for i in range(len(coords)): \n\
        if i != len(coords)-1:\n\
                d = ((coords[i][1]-coords[i+1][1])**2 + (coords[i][2]-coords[i+1][2])**2 + (coords[i][3]-coords[i+1][3])**2)**0.5\n\
                x = x +d\n\
                t_coords.append(x-(t/2))\n\
m = 0\n\
for i in range(len(sValues)-1):\n\
        m = m +(t_coords[i+1] - t_coords[i])*(sValues[i+1]+sValues[i])\n\
m = (1/t)*0.5*m\n\
for i in range(len(sValues)):\n\
        membrane.append(m)\n\
b = 0\n\
for i in range(len(sValues)-1):\n\
        d = (t_coords[i+1] - t_coords[i])\n\
        b = b + d*(-3/t**2)*(sValues[i+1]*t_coords[i+1] + sValues[i]*t_coords[i])\n\
b2 = -b\n\
bending =[]\n\
for i in range(len(t_coords)):\n\
        func = ((b2-b)/t)*t_coords[i]\n\
        bending.append(func)\n\
peak = []\n\
mb = []\n\
for i in range(len(sValues)):\n\
        peak.append(sValues[i])\n\
        mb.append(bending[i] + membrane[0])\n\
import FreeCAD\n\
import numpy as np\n\
from matplotlib import pyplot as plt\n\
plt.figure(1)\n\
plt.plot(t_coords, membrane, \"k--\")\n\
plt.plot(t_coords, mb, \"b*-\")\n\
plt.plot(t_coords, peak, \"r-x\")\n\
plt.legend([\"Membrane Stress\", \"Membrane and Bending\", \"Total Stress\"], loc = 4)\n\
plt.xlabel(\"Thickness [mm] \")\n\
plt.ylabel(\"Stress [MPa]\")\n\
plt.title(\"Linearized Stresses\")\n\
plt.grid()\n\
plt.show()\n";

}
//############################################################################################

TaskPostScalarClip::TaskPostScalarClip(ViewProviderDocumentObject* view, QWidget* parent) :
    TaskPostBox(view, Gui::BitmapFactory().pixmap("fem-fem-mesh-create-node-by-poly"), tr("Clip options"), parent) {

    assert(view->isDerivedFrom(ViewProviderFemPostScalarClip::getClassTypeId()));

    //we load the views widget
    proxy = new QWidget(this);
    ui = new Ui_TaskPostScalarClip();
    ui->setupUi(proxy);
    QMetaObject::connectSlotsByName(this);
    this->groupLayout()->addWidget(proxy);

    //load the default values
    updateEnumerationList(getTypedObject<Fem::FemPostScalarClipFilter>()->Scalars, ui->Scalar);
    ui->InsideOut->setChecked(static_cast<Fem::FemPostScalarClipFilter*>(getObject())->InsideOut.getValue());

    App::PropertyFloatConstraint& value = static_cast<Fem::FemPostScalarClipFilter*>(getObject())->Value;
    //don't forget to sync the slider
    ui->Value->blockSignals(true);
    ui->Value->setValue( value.getValue());
    ui->Value->blockSignals(false);
    //don't forget to sync the slider
    ui->Value->blockSignals(true);
    ui->Value->setValue( value.getConstraints()->UpperBound * (1-double(value.getValue())/100.)
                            + double(value.getValue())/100.*value.getConstraints()->UpperBound);
    ui->Value->blockSignals(false);
}

TaskPostScalarClip::~TaskPostScalarClip() {

}

void TaskPostScalarClip::applyPythonCode() {

}

void TaskPostScalarClip::on_Scalar_currentIndexChanged(int idx) {

    static_cast<Fem::FemPostScalarClipFilter*>(getObject())->Scalars.setValue(idx);
    recompute();

    //update constraints and values
    App::PropertyFloatConstraint& value = static_cast<Fem::FemPostScalarClipFilter*>(getObject())->Value;
    ui->Maximum->setText(QString::number(value.getConstraints()->UpperBound));
    ui->Minimum->setText(QString::number(value.getConstraints()->LowerBound));

    //don't forget to sync the slider
    ui->Value->blockSignals(true);
    ui->Value->setValue( value.getValue());
    ui->Value->blockSignals(false);
    //don't forget to sync the slider
    ui->Value->blockSignals(true);
    ui->Value->setValue( value.getConstraints()->UpperBound * (1-double(value.getValue())/100.)
                            + double(value.getValue())/100.*value.getConstraints()->UpperBound);
    ui->Value->blockSignals(false);
}

void TaskPostScalarClip::on_Slider_valueChanged(int v) {

    App::PropertyFloatConstraint& value = static_cast<Fem::FemPostScalarClipFilter*>(getObject())->Value;
    double val = value.getConstraints()->LowerBound * (1-double(v)/100.) + double(v)/100.*value.getConstraints()->UpperBound;

    value.setValue(val);
    recompute();

    //don't forget to sync the spinbox
    ui->Value->blockSignals(true);
    ui->Value->setValue( val );
    ui->Value->blockSignals(false);
}

void TaskPostScalarClip::on_Value_valueChanged(double v) {

    App::PropertyFloatConstraint& value = static_cast<Fem::FemPostScalarClipFilter*>(getObject())->Value;
    value.setValue(v);
    recompute();

    //don't forget to sync the slider
    ui->Slider->blockSignals(true);
    ui->Slider->setValue(int(((v- value.getConstraints()->LowerBound)/(value.getConstraints()->UpperBound - value.getConstraints()->LowerBound))*100.));
    ui->Slider->blockSignals(false);
}

void TaskPostScalarClip::on_InsideOut_toggled(bool val) {

    static_cast<Fem::FemPostScalarClipFilter*>(getObject())->InsideOut.setValue(val);
    recompute();
}


//############################################################################################

TaskPostWarpVector::TaskPostWarpVector(ViewProviderDocumentObject* view, QWidget* parent) :
    TaskPostBox(view, Gui::BitmapFactory().pixmap("fem-fem-mesh-create-node-by-poly"), tr("Clip options"), parent) {

    assert(view->isDerivedFrom(ViewProviderFemPostWarpVector::getClassTypeId()));

    //we load the views widget
    proxy = new QWidget(this);
    ui = new Ui_TaskPostWarpVector();
    ui->setupUi(proxy);
    QMetaObject::connectSlotsByName(this);
    this->groupLayout()->addWidget(proxy);

    //load the default values
    updateEnumerationList(getTypedObject<Fem::FemPostWarpVectorFilter>()->Vector, ui->Vector);

    double value = static_cast<Fem::FemPostWarpVectorFilter*>(getObject())->Factor.getValue();
        //don't forget to sync the slider
    ui->Value->blockSignals(true);
    ui->Value->setValue( value);
    ui->Value->blockSignals(false);
    //don't forget to sync the slider
    ui->Max->blockSignals(true);
    ui->Max->setValue( value==0 ? 1 : value * 10.);
    ui->Max->blockSignals(false);
    ui->Min->blockSignals(true);
    ui->Min->setValue( value==0 ? 0 : value / 10.);
    ui->Min->blockSignals(false);
    ui->Slider->blockSignals(true);
    ui->Slider->setValue((value - ui->Min->value()) / (ui->Max->value() - ui->Min->value())*100.);
    ui->Slider->blockSignals(false);
}

TaskPostWarpVector::~TaskPostWarpVector() {

}

void TaskPostWarpVector::applyPythonCode() {

}

void TaskPostWarpVector::on_Vector_currentIndexChanged(int idx) {

    static_cast<Fem::FemPostWarpVectorFilter*>(getObject())->Vector.setValue(idx);
    recompute();
}

void TaskPostWarpVector::on_Slider_valueChanged(int v) {

    double val = ui->Min->value() + (ui->Max->value()-ui->Min->value())/100.*v;
    static_cast<Fem::FemPostWarpVectorFilter*>(getObject())->Factor.setValue(val);
    recompute();

    //don't forget to sync the spinbox
    ui->Value->blockSignals(true);
    ui->Value->setValue( val );
    ui->Value->blockSignals(false);
}

void TaskPostWarpVector::on_Value_valueChanged(double v) {

    static_cast<Fem::FemPostWarpVectorFilter*>(getObject())->Factor.setValue(v);
    recompute();

    //don't forget to sync the slider
    ui->Slider->blockSignals(true);
    ui->Slider->setValue(int((v - ui->Min->value()) / (ui->Max->value() - ui->Min->value())*100.));
    ui->Slider->blockSignals(false);
}

void TaskPostWarpVector::on_Max_valueChanged(double v) {

    ui->Slider->blockSignals(true);
    ui->Slider->setValue((ui->Value->value() - ui->Min->value()) / (ui->Max->value() - ui->Min->value())*100.);
    ui->Slider->blockSignals(false);
}

void TaskPostWarpVector::on_Min_valueChanged(double v) {

    ui->Slider->blockSignals(true);
    ui->Slider->setValue((ui->Value->value() - ui->Min->value()) / (ui->Max->value() - ui->Min->value())*100.);
    ui->Slider->blockSignals(false);
}

//############################################################################################

TaskPostCut::TaskPostCut(ViewProviderDocumentObject* view, App::PropertyLink* function, QWidget* parent)
    : TaskPostBox(view,Gui::BitmapFactory().pixmap("fem-fem-mesh-create-node-by-poly"), tr("Choose implicit function"), parent) {

    assert(view->isDerivedFrom(ViewProviderFemPostCut::getClassTypeId()));
    assert(function);

    fwidget = NULL;

    //we load the views widget
    proxy = new QWidget(this);
    ui = new Ui_TaskPostCut();
    ui->setupUi(proxy);
    QMetaObject::connectSlotsByName(this);
    this->groupLayout()->addWidget(proxy);

    //the layout for the container widget
    QVBoxLayout *layout = new QVBoxLayout();
    ui->Container->setLayout(layout);

    //fill up the combo box with possible functions
    collectImplicitFunctions();

    //add the function creation command
    Gui::CommandManager &rcCmdMgr = Gui::Application::Instance->commandManager();
    rcCmdMgr.getCommandByName("Fem_PostCreateFunctions")->getAction()->addTo(ui->CreateButton);
    ui->CreateButton->setPopupMode(QToolButton::InstantPopup);
}

TaskPostCut::~TaskPostCut() {

}

void TaskPostCut::applyPythonCode() {

}

void TaskPostCut::collectImplicitFunctions() {

    std::vector<Fem::FemPostPipeline*> pipelines;
    pipelines = App::GetApplication().getActiveDocument()->getObjectsOfType<Fem::FemPostPipeline>();
    if (!pipelines.empty()) {
        Fem::FemPostPipeline *pipeline = pipelines.front();
        if(pipeline->Functions.getValue() &&
           pipeline->Functions.getValue()->getTypeId() == Fem::FemPostFunctionProvider::getClassTypeId()) {

            ui->FunctionBox->clear();
            QStringList items;
            const std::vector<App::DocumentObject*>& funcs = static_cast<Fem::FemPostFunctionProvider*>(
                                                            pipeline->Functions.getValue())->Functions.getValues();
            for(std::size_t i=0; i<funcs.size(); ++i)
                items.push_back(QString::fromLatin1(funcs[i]->getNameInDocument()));

            ui->FunctionBox->addItems(items);
        }
    }
}

void TaskPostCut::on_CreateButton_triggered(QAction* a) {

    collectImplicitFunctions();
    recompute();
}

void TaskPostCut::on_FunctionBox_currentIndexChanged(int idx) {

    //set the correct property
    std::vector<Fem::FemPostPipeline*> pipelines;
    pipelines = App::GetApplication().getActiveDocument()->getObjectsOfType<Fem::FemPostPipeline>();
    if (!pipelines.empty()) {
        Fem::FemPostPipeline *pipeline = pipelines.front();
        if(pipeline->Functions.getValue() &&
           pipeline->Functions.getValue()->getTypeId() == Fem::FemPostFunctionProvider::getClassTypeId()) {

            const std::vector<App::DocumentObject*>& funcs = static_cast<Fem::FemPostFunctionProvider*>(
                                                            pipeline->Functions.getValue())->Functions.getValues();
            if(idx>=0)
                static_cast<Fem::FemPostCutFilter*>(getObject())->Function.setValue(funcs[idx]);
            else
                static_cast<Fem::FemPostCutFilter*>(getObject())->Function.setValue(NULL);
        }
    }

    //load the correct view
    Fem::FemPostFunction* fobj = static_cast<Fem::FemPostFunction*>(
                                    static_cast<Fem::FemPostCutFilter*>(getObject())->Function.getValue());
    Gui::ViewProvider* view = NULL;
    if(fobj)
        view = Gui::Application::Instance->activeDocument()->getViewProvider(fobj);

    if(fwidget)
        fwidget->deleteLater();

    if(view) {
        fwidget = static_cast<FemGui::ViewProviderFemPostFunction*>(view)->createControlWidget();
        fwidget->setParent(ui->Container);
        fwidget->setViewProvider(static_cast<FemGui::ViewProviderFemPostFunction*>(view));
        ui->Container->layout()->addWidget(fwidget);
    }
    recompute();
}

#include "moc_TaskPostBoxes.cpp"
