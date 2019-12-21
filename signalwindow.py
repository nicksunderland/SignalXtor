import pyqtgraph
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np


class SignalWindow(QObject):
    """
    The class dealing with the signal display window that's embedded in the mainwindow GUI
    """

    def __init__(self):
        super(SignalWindow, self).__init__()
        self.graph = pyqtgraph.PlotWidget()
        self.graph.setTitle("Channel ...")
        self.graph.getAxis('left').setLabel('mV')
        self.graph.getAxis('bottom').setLabel('msec')
        self.graph.setBackground('k')
        self.graph.showGrid(x=True, y=True)

        self.graph.scene().sigMouseClicked.connect(self.on_mouse_clicked)

    def update_plot(self, data_obj, signal_idx, signal_type):
        self.graph.clear()
        self.graph.setTitle("Channel " + str(signal_idx + 1))
        self.graph.plot(data_obj.unipolar[signal_idx, :] * float(data_obj.mV_gain), pen=pyqtgraph.mkPen('g', width=2))

    def on_mouse_clicked(self, event):
        self.graph.plotItem.addLine(x=1, y=None, pen=pyqtgraph.mkPen('r', width=2))
