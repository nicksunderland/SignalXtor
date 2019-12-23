import pyqtgraph
from PyQt5.QtCore import *
from data import *


class SignalWindow(QObject):
    """
    The class dealing with the signal display window that's embedded in the mainwindow GUI
    """
    def __init__(self, parent):
        super(SignalWindow, self).__init__()

        # Access to parent main window GUI
        self.mw = parent

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
        # Check if there is any data, return if not
        if self.mw.data_obj is None:
            print("No data object yet, abort...")
            return

        for addpt in self.mw.data_obj.activation_list:



        # Decide which signal needs to be plotted
        channel = self.mw.ui.spinBox_signals.value()
        sig_type = str(self.mw.ui.comboBox_signal_type.currentText())
        print("Channel = " + str(channel))
        print("Signal  = " + str(sig_type))

        if channel > self.mw.data_obj.unipolar.shape[0]:
            channel = self.data_obj.unipolar.shape[0]
            self.ui.spinBox_signals.setValue(channel)
            self.signal_window.update_plot(self.data_obj, channel - 1, "tmp")


        signal_idx = channel - 1
        self.graph.setTitle("Channel " + str(signal_idx + 1))
        self.graph.plot(self.mw.data_obj.unipolar[signal_idx, :] * float(self.mw.data_obj.mV_gain), pen=pyqtgraph.mkPen('g', width=2))

    def handle_mouse_click(self, event):
        # Check if there is any data, return if not
        if self.mw.data_obj is None:
            print("No data object yet, abort...")
            return

        # EMG editing off
        if self.mw.ui.radioButton_EMG_edit_off.isChecked():
            print("EMG editing off")
            return
        # EMG editing on (editing on existing EMG interest points)
        elif self.mw.ui.radioButton_EMG_edit_on.isChecked():
            print("EMG editing on")
        # Add new EMG interest point
        elif self.mw.ui.radioButton_EMG_edit_add.isChecked():
            print("EMG editing - add")
            self.add_EMG_point(event)
        # Delete nearest EMG interest point
        elif self.mw.ui.radioButton_EMG_edit_delete.isChecked():
            print("EMG editing - delete")

    def add_EMG_point(self, event):
        # Get the necessary data from the mouse click
        x_time = self.graph.plotItem.vb.mapSceneToView(event.scenePos()).x()

        # Define the initial window variables around the point
        pre_x = 50
        post_x = 50
        win_shape = "exp"

        # Create new EMGpoint instance and add to the list
        newpt = EMGpoint(x_time, pre_x, post_x, win_shape)
        self.mw.data_obj.activation_list.append(newpt)
