import sys
import FreeCAD
import FreeCADGui
import os
os.environ['QT_API'] = 'pyside'
from PySide import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
 
class ColorMap(QtGui.QWidget, value):
    def __init__(self, parent=None):
        super(ColorMap, self).__init__(parent)
 ##
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.draw_colormap(value)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
          
    def draw_colormap(self, value):
        # Stess Values in MPa
        datos=value
        val_max=max(datos)
        val_min=min(datos)
        # axes
        ax = self.figure.add_axes([0.05, 0.10, 0.5, 0.8])
        cmap = mpl.cm.jet
        norm = mpl.colors.Normalize(vmin=val_min, vmax=val_max)
        ticks_cm = np.linspace(val_min, val_max, 5, endpoint=True)
        cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
                                           norm=norm,
                                           ticks=ticks_cm,
                                           orientation='vertical')
        label_cm = 'Von Misses Stress [MPa]'
        cb1.set_label(label=label_cm,weight='bold')
        cb1.ax.tick_params(labelsize=10) 
        self.canvas.draw()

