/***************************************************************************
 *   Copyright (c) 2008 Jürgen Riegel (juergen.riegel@web.de)              *
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
# include <QApplication>
# include <QMessageBox>
#endif

#include <sstream>

#include <Mod/Part/App/TopoShape.h>
#include <Mod/Part/App/PartFeature.h>
#include <Mod/Points/App/Structured.h>
#include <Mod/Mesh/App/MeshFeature.h>
#include <Mod/Mesh/App/Core/Approximation.h>

#include <Gui/Application.h>
#include <Gui/Command.h>
#include <Gui/Control.h>
#include <Gui/MainWindow.h>
#include <Gui/FileDialog.h>
#include <Gui/Selection.h>
#include <Base/CoordinateSystem.h>

#include "../App/ApproxSurface.h"
#include "FitBSplineSurface.h"
#include "Poisson.h"

using namespace std;

DEF_STD_CMD_A(CmdApproxSurface);

CmdApproxSurface::CmdApproxSurface()
  : Command("Reen_ApproxSurface")
{
    sAppModule      = "Reen";
    sGroup          = QT_TR_NOOP("Reverse Engineering");
    sMenuText       = QT_TR_NOOP("Approximate B-Spline surface...");
    sToolTipText    = QT_TR_NOOP("Approximate a B-Spline surface");
    sWhatsThis      = "Reen_ApproxSurface";
    sStatusTip      = sToolTipText;
    sPixmap         = "actions/FitSurface";
}

void CmdApproxSurface::activated(int iMsg)
{
    App::DocumentObjectT objT;
    std::vector<App::DocumentObject*> obj = Gui::Selection().getObjectsOfType(Points::Feature::getClassTypeId());
    if (obj.size() != 1) {
        QMessageBox::warning(Gui::getMainWindow(),
            qApp->translate("Reen_ApproxSurface", "Wrong selection"),
            qApp->translate("Reen_ApproxSurface", "Please select a single point cloud.")
        );
        return;
    }

    objT = obj.front();
    Gui::Control().showDialog(new ReenGui::TaskFitBSplineSurface(objT));
}

bool CmdApproxSurface::isActive(void)
{
    return (hasActiveDocument() && !Gui::Control().activeDialog());
}

DEF_STD_CMD_A(CmdApproxPlane);

CmdApproxPlane::CmdApproxPlane()
  : Command("Reen_ApproxPlane")
{
    sAppModule      = "Reen";
    sGroup          = QT_TR_NOOP("Reverse Engineering");
    sMenuText       = QT_TR_NOOP("Approximate plane...");
    sToolTipText    = QT_TR_NOOP("Approximate a plane");
    sWhatsThis      = "Reen_ApproxPlane";
    sStatusTip      = sToolTipText;
}

void CmdApproxPlane::activated(int iMsg)
{
    std::vector<App::GeoFeature*> obj = Gui::Selection().getObjectsOfType<App::GeoFeature>();
    for (std::vector<App::GeoFeature*>::iterator it = obj.begin(); it != obj.end(); ++it) {
        std::map<std::string, App::Property*> Map;
        (*it)->getPropertyMap(Map);
        for (std::map<std::string, App::Property*>::iterator jt = Map.begin(); jt != Map.end(); ++jt) {
            if (jt->second->getTypeId().isDerivedFrom(App::PropertyComplexGeoData::getClassTypeId())) {
                std::vector<Base::Vector3d> aPoints;
                std::vector<Data::ComplexGeoData::Facet> aTopo;
                static_cast<App::PropertyComplexGeoData*>(jt->second)->getFaces(aPoints, aTopo,0.01f);

                // get a reference normal for the plane fit
                Base::Vector3f refNormal(0,0,0);
                if (!aTopo.empty()) {
                    Data::ComplexGeoData::Facet f = aTopo.front();
                    Base::Vector3d v1 = aPoints[f.I2] - aPoints[f.I1];
                    Base::Vector3d v2 = aPoints[f.I3] - aPoints[f.I1];
                    refNormal = Base::convertTo<Base::Vector3f>(v1 % v2);
                }

                std::vector<Base::Vector3f> aData;
                aData.reserve(aPoints.size());
                for (std::vector<Base::Vector3d>::iterator jt = aPoints.begin(); jt != aPoints.end(); ++jt)
                    aData.push_back(Base::toVector<float>(*jt));
                MeshCore::PlaneFit fit;
                fit.AddPoints(aData);
                float sigma = fit.Fit();
                Base::Vector3f base = fit.GetBase();
                Base::Vector3f dirU = fit.GetDirU();
                Base::Vector3f dirV = fit.GetDirV();
                Base::Vector3f norm = fit.GetNormal();

                // if the dot product of the reference with the plane normal is negative
                // a flip must be done
                if (refNormal * norm < 0) {
                    norm = -norm;
                    dirU = -dirU;
                }

                float width, length;
                fit.Dimension(width, length);

                // move to the corner point
                base = base - (0.5f * length * dirU + 0.5f * width * dirV);

                Base::CoordinateSystem cs;
                cs.setPosition(Base::convertTo<Base::Vector3d>(base));
                cs.setAxes(Base::convertTo<Base::Vector3d>(norm),
                           Base::convertTo<Base::Vector3d>(dirU));
                Base::Placement pm = Base::CoordinateSystem().displacement(cs);
                double q0, q1, q2, q3;
                pm.getRotation().getValue(q0, q1, q2, q3);

                Base::Console().Log("RMS value for plane fit with %lu points: %.4f\n", aData.size(), sigma);
                Base::Console().Log("  Plane base(%.4f, %.4f, %.4f)\n", base.x, base.y, base.z);
                Base::Console().Log("  Plane normal(%.4f, %.4f, %.4f)\n", norm.x, norm.y, norm.z);

                std::stringstream str;
                str << "from FreeCAD import Base" << std::endl;
                str << "App.ActiveDocument.addObject('Part::Plane','Plane_fit')" << std::endl;
                str << "App.ActiveDocument.ActiveObject.Length = " << length << std::endl;
                str << "App.ActiveDocument.ActiveObject.Width = " << width << std::endl;
                str << "App.ActiveDocument.ActiveObject.Placement = Base.Placement("
                    << "Base.Vector(" << base.x << "," << base.y << "," << base.z << "),"
                    << "Base.Rotation(" << q0 << "," << q1 << "," << q2 << "," << q3 << "))" << std::endl;
                
                openCommand("Fit plane");
                doCommand(Gui::Command::Doc, str.str().c_str());
                commitCommand(); 
                updateActive();
            }
        }
    }
}

bool CmdApproxPlane::isActive(void)
{
    if (getSelection().countObjectsOfType(App::GeoFeature::getClassTypeId()) == 1)
        return true;
    return false;
}

DEF_STD_CMD_A(CmdPoissonReconstruction);

CmdPoissonReconstruction::CmdPoissonReconstruction()
  : Command("Reen_PoissonReconstruction")
{
    sAppModule      = "Reen";
    sGroup          = QT_TR_NOOP("Reverse Engineering");
    sMenuText       = QT_TR_NOOP("Poisson...");
    sToolTipText    = QT_TR_NOOP("Poisson surface reconstruction");
    sWhatsThis      = "Reen_PoissonReconstruction";
    sStatusTip      = sToolTipText;
}

void CmdPoissonReconstruction::activated(int iMsg)
{
    App::DocumentObjectT objT;
    std::vector<App::DocumentObject*> obj = Gui::Selection().getObjectsOfType(Points::Feature::getClassTypeId());
    if (obj.size() != 1) {
        QMessageBox::warning(Gui::getMainWindow(),
            qApp->translate("Reen_ApproxSurface", "Wrong selection"),
            qApp->translate("Reen_ApproxSurface", "Please select a single point cloud.")
        );
        return;
    }

    objT = obj.front();
    Gui::Control().showDialog(new ReenGui::TaskPoisson(objT));
}

bool CmdPoissonReconstruction::isActive(void)
{
    return (hasActiveDocument() && !Gui::Control().activeDialog());
}

DEF_STD_CMD_A(CmdViewTriangulation);

CmdViewTriangulation::CmdViewTriangulation()
  : Command("Reen_ViewTriangulation")
{
    sAppModule      = "Reen";
    sGroup          = QT_TR_NOOP("Reverse Engineering");
    sMenuText       = QT_TR_NOOP("Structured point clouds");
    sToolTipText    = QT_TR_NOOP("Triangulation of structured point clouds");
    sToolTipText    = QT_TR_NOOP("Triangulation of structured point clouds");
    sWhatsThis      = "Reen_ViewTriangulation";
}

void CmdViewTriangulation::activated(int iMsg)
{
    std::vector<App::DocumentObject*> obj = Gui::Selection().getObjectsOfType(Points::Structured::getClassTypeId());
    addModule(App,"ReverseEngineering");
    openCommand("View triangulation");
    try {
        for (std::vector<App::DocumentObject*>::iterator it = obj.begin(); it != obj.end(); ++it) {
            App::DocumentObjectT objT(*it);
            QString document = QString::fromStdString(objT.getDocumentPython());
            QString object = QString::fromStdString(objT.getObjectPython());

            QString command = QString::fromLatin1("%1.addObject('Mesh::Feature', 'View mesh').Mesh = ReverseEngineering.viewTriangulation("
                "Points=%2.Points,"
                "Width=%2.Width,"
                "Height=%2.Height)"
            )
            .arg(document)
            .arg(object)
            ;
            doCommand(Doc, command.toLatin1());
        }

        commitCommand();
        updateActive();
    }
    catch (const Base::Exception& e) {
        abortCommand();
        QMessageBox::warning(Gui::getMainWindow(),
            qApp->translate("Reen_ViewTriangulation", "View triangulation failed"),
            QString::fromLatin1(e.what())
        );
    }
}

bool CmdViewTriangulation::isActive(void)
{
    return  (Gui::Selection().countObjectsOfType(Points::Structured::getClassTypeId()) > 0);
}

void CreateReverseEngineeringCommands(void)
{
    Gui::CommandManager &rcCmdMgr = Gui::Application::Instance->commandManager();
    rcCmdMgr.addCommand(new CmdApproxSurface());
    rcCmdMgr.addCommand(new CmdApproxPlane());
    rcCmdMgr.addCommand(new CmdPoissonReconstruction());
    rcCmdMgr.addCommand(new CmdViewTriangulation());
}
