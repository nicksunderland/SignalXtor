import pyqtgraph
from PyQt5.QtCore import *
from data import *


class SignalWindow(QObject):
    """
    The class dealing with the signal display window that's embedded in the mainwindow GUI
    """
    def __init__(self, parent):
        super(SignalWindow, self).__init__()

        # Access to parent main GUI
        self.main_ui = parent

        # The actual plot
        self.graph = pyqtgraph.PlotWidget()
        self.graph.setTitle("Channel ...")
        self.graph.getAxis('left').setLabel('mV')
        self.graph.getAxis('bottom').setLabel('msec')
        self.graph.setBackground('k')
        self.graph.showGrid(x=True, y=True)

        # Signal connections
        self.make_connections()

    def make_connections(self):
        self.graph.scene().sigMouseClicked.connect(self.handle_mouse_click)

    def update_plot(self):

        print("Trying to update plot")

        # Check if there is any data, return if not
        if self.main_ui.data_obj is None:
            print("data obj None")
            return

        # Decide which signal needs to be plotted
        channel = self.main_ui.ui.spinBox_signals.value()
        sig_type = str(self.main_ui.ui.comboBox_signal_type.currentText())
        print(sig_type)

        return

        if channel > self.data_obj.unipolar.shape[0]:
            channel = self.data_obj.unipolar.shape[0]
            self.ui.spinBox_signals.setValue(channel)
            self.signal_window.update_plot(self.data_obj, channel - 1, "tmp")

        self.graph.clear()
        self.graph.setTitle("Channel " + str(signal_idx + 1))
        self.graph.plot(data_obj.unipolar[signal_idx, :] * float(data_obj.mV_gain), pen=pyqtgraph.mkPen('g', width=2))

    def handle_mouse_click(self, event):
        # EMG editing off
        if self.main_ui.radioButton_EMG_edit_off.isChecked():
            print("EMG editing off")
            return
        # EMG editing on (editing on existing EMG interest points)
        elif self.main_ui.radioButton_EMG_edit_on.isChecked():
            print("EMG editing on")
        # Add new EMG interest point
        elif self.main_ui.radioButton_EMG_edit_add.isChecked():
            print("EMG editing - add")
            self.add_EMG_point(event)
        # Delete nearest EMG interest point
        elif self.main_ui.radioButton_EMG_edit_delete.isChecked():
            print("EMG editing - delete")

    def add_EMG_point(self, event):
        # Get the x and y values
        pos_y_mV = self.graph.plotItem.vb.mapSceneToView(event.scenePos()).y()
        pos_x_msec = self.graph.plotItem.vb.mapSceneToView(event.scenePos()).x()

        print("x=" + str(pos_x_msec) + " y=" + str(pos_y_mV))

        return
        #
        # # Create new EMGpoint instance
        # newpt = EMGpoint()
        #
        # def __init__(self, point_time, pre_pt_win=50, post_pt_win=50, win_shape="exp"):
        #
        # #
        # # pos = self.graph.plotItem.vb.mapSceneToView(event.scenePos())
        # print("x=" + str(pos.x()) + " y=" + str(pos.y()))
        #
        # if self.main_ui.radioButton_EMG_edit_off.isChecked():
        #     self.graph.plotItem.addLine(x=pos.x(), y=None, pen=pyqtgraph.mkPen('r', width=2))
        # elif self.main_ui.radioButton_EMG_edit_on.isChecked():
        #     self.graph.plotItem.addLine(x=pos.x(), y=None, pen=pyqtgraph.mkPen('b', width=2))
        # else:
        #     self.graph.plotItem.addLine(x=pos.x(), y=None, pen=pyqtgraph.mkPen('y', width=2))
        #
