from pyqtgraph import *
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
        self.graph = PlotWidget()
        self.graph.setTitle("Channel ...")
        self.graph.getAxis('left').setLabel('mV')
        self.graph.getAxis('bottom').setLabel('msec')
        self.graph.setBackground('k')
        self.graph.showGrid(x=True, y=True)

        # Signal connections
        self.make_connections()

        # Variables
        self.highlighted_point = (None, None)

    def make_connections(self):
        self.graph.scene().sigMouseClicked.connect(self.handle_mouse_click)

    def update_plot(self):
        # Clear the current data from the plot
        self.graph.clear()

        # Check if there is any data, return if not
        if self.mw.data_obj is None:
            return

        # Draw the EMG points (activations +/- subtractions)
        self.draw_EMG_points()

        # Draw the signal
        self.draw_signal()

    def draw_EMG_points(self):
        # Draw the activation points from the list
        for add_pt in self.mw.data_obj.activation_list:
            if add_pt.highlighted is True:
                self.graph.addLine(x=add_pt.point_time, y=None, pen=mkPen('b', width=5))
                self.graph.plot([add_pt.point_time], [0], symbolPen='b', symbol='o', symbolBrush='b')
            else:
                self.graph.addLine(x=add_pt.point_time, y=None, pen=mkPen('b', width=2))

        # Draw the subtraction points from the list
        for sub_pt in self.mw.data_obj.subtraction_list:
            if sub_pt.highlighted:
                self.graph.addLine(x=sub_pt.point_time, y=None, pen=mkPen('r', width=5))
                self.graph.plot([sub_pt.point_time], [0], symbolPen='r', symbol='o', symbolBrush='r')
            else:
                self.graph.addLine(x=sub_pt.point_time, y=None, pen=mkPen('r', width=2))

    def draw_signal(self):
        # Decide which signal needs to be plotted
        channel = self.mw.ui.spinBox_signals.value()
        sig_type = str(self.mw.ui.comboBox_signal_type.currentText())
        if channel > self.mw.data_obj.unipolar.shape[0]:
            channel = self.data_obj.unipolar.shape[0]
            self.ui.spinBox_signals.setValue(channel)
            self.signal_window.update_plot(self.data_obj, channel - 1, "tmp")
        signal_idx = channel - 1
        self.graph.setTitle("Channel " + str(signal_idx + 1))
        self.graph.plot(self.mw.data_obj.unipolar[signal_idx, :] * float(self.mw.data_obj.mV_gain), pen=mkPen('g', width=2))

    def handle_mouse_click(self, event):
        # Check if there is any data, return if not
        if self.mw.data_obj is None:
            return

        # Set the closest EMG point to be highlighted
        self.set_closest_EMG_point(event)

        # EMG editing off
        if self.mw.ui.radioButton_EMG_edit_off.isChecked():
            print("EMG editing off")
        # EMG editing on (editing on existing EMG interest points)
        elif self.mw.ui.radioButton_EMG_edit_on.isChecked():
            print("EMG editing on")
        # Add new EMG interest point
        elif self.mw.ui.radioButton_EMG_edit_add.isChecked():
            print("EMG editing - add")
            if self.mw.ui.radioButton_EMG_activation.isChecked():
                self.acti_EMG_point(event)
            elif self.mw.ui.radioButton_EMG_subtraction.isChecked():
                self.sub_EMG_point(event)
        # Delete nearest EMG interest point
        elif self.mw.ui.radioButton_EMG_edit_delete.isChecked():
            print("EMG editing - delete function needs to be written")

        # Redraw
        self.update_plot()

    def acti_EMG_point(self, event):
        # Get the necessary data from the mouse click
        x_time = self.graph.plotItem.vb.mapSceneToView(event.scenePos()).x()

        # Define the initial window variables around the point
        pre_x = 50
        post_x = 50
        win_shape = "exp"
        highlight_point = True

        # Create new EMGpoint instance
        newpt = EMGpoint(x_time, pre_x, post_x, win_shape, highlight_point)

        # Unhighlight the rest of the points
        self.unhighlight_all_points()

        # Add the new point to the list
        self.mw.data_obj.activation_list.append(newpt)

    def sub_EMG_point(self, event):
        # Get the necessary data from the mouse click
        x_time = self.graph.plotItem.vb.mapSceneToView(event.scenePos()).x()

        # Define the initial window variables around the point
        pre_x = 50
        post_x = 50
        win_shape = "exp"
        highlight_point = True

        # Create new EMGpoint instance
        newpt = EMGpoint(x_time, pre_x, post_x, win_shape, highlight_point)

        # Unhighlight the rest of the points
        self.unhighlight_all_points()

        # Add the new point to the list
        self.mw.data_obj.subtraction_list.append(newpt)

    def unhighlight_all_points(self):
        for pt in self.mw.data_obj.subtraction_list:
            pt.highlighted = False
        for pt in self.mw.data_obj.activation_list:
            pt.highlighted = False

    def set_closest_EMG_point(self, event):
        # Get the necessary data from the mouse click
        x_time = self.graph.plotItem.vb.mapSceneToView(event.scenePos()).x()

        # Unhighlight all of the points in the lists
        self.unhighlight_all_points()

        # Vars for the search
        closest_dist = None
        closest_type = None
        closest_idx = None
        max_click_dist = 10

        # Cycle the lists of EMG points to find the closest point to the click
        for i, pt in enumerate(self.mw.data_obj.subtraction_list):
            x_click = pt.point_time
            dist = abs(x_time - x_click)
            if dist < max_click_dist and closest_dist is None:
                closest_dist = dist
                closest_type = "Sub"
                closest_idx = i
            elif dist < max_click_dist and closest_dist is not None and dist < closest_dist:
                closest_dist = dist
                closest_type = "Sub"
                closest_idx = i

        # Cycle the lists of EMG points to find the closest point to the click
        for i, pt in enumerate(self.mw.data_obj.activation_list):
            x_click = pt.point_time
            dist = abs(x_time - x_click)
            if dist < max_click_dist and closest_dist is None:
                closest_dist = dist
                closest_type = "Add"
                closest_idx = i
            elif dist < max_click_dist and closest_dist is not None and dist < closest_dist:
                closest_dist = dist
                closest_type = "Add"
                closest_idx = i

        # Switch the highlighted property to True in the closest EMG point
        if closest_dist is not None and closest_type is not None and closest_idx is not None:
            if closest_type == "Sub":
                self.mw.data_obj.subtraction_list[closest_idx].highlighted = True
            elif closest_type == "Add":
                self.mw.data_obj.activation_list[closest_idx].highlighted = True
