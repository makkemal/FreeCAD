# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2015 - FreeCAD             *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "The constraint Auto Contact"
__author__ = "Michael Hindley"
__url__ = "http://www.freecadweb.org"

## @package FemConstraintSelfWeight
#  \ingroup FEM


class _FemConstraintAutoContact:
    "The FemConstraintAutoContact object"
    def __init__(self, obj):
        obj.addProperty("App::PropertyFloat", "stiffness", "stiffness", "Stifness for all auto constraints")
        obj.addProperty("App::PropertyFloat", "friction", "friction", "Friction for all autoconstraints")
        obj.Proxy = self
        self.Type = "Fem::ConstraintAutoContact"

    def execute(self, obj):
        return
