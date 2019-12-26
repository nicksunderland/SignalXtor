from PyQt5.QtWidgets import QDialog
import os
os.system("pyuic5 UI_files/ui_default_signal_settings_dialog.ui > UI_files/ui_default_signal_settings_dialog.py")
from UI_files.ui_default_signal_settings_dialog import Ui_Dialog


class DefaultSettingsDialog(QDialog):

    def __init__(self, parent):
        super(DefaultSettingsDialog, self).__init__()

        # Setup the main window GUI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Access to parent main window GUI
        self.mw = parent

        # Set the GUI with the current parameters
        self.populate_GUI_with_current_defaults()

        # Make the button connections
        self.make_connections()

    def make_connections(self):
        # Dialog:Dialog GUI buttons / signals
        self.ui.pushButton_done.clicked.connect(self.update_default_signal_settings)
        self.ui.radioButton_win_shape_tukey.toggled.connect(self.handle_win_shape_radio_buttons)
        self.ui.radioButton_win_shape_square.toggled.connect(self.handle_win_shape_radio_buttons)
        self.ui.radioButton_win_shape_log.toggled.connect(self.handle_win_shape_radio_buttons)

    def populate_GUI_with_current_defaults(self):
        # Set values from (current) defaults
        self.ui.spinBox_pre_window_msec.setValue(self.mw.data_obj.filter_settings.pre_pt_win)
        self.ui.spinBox_post_window_msec.setValue(self.mw.data_obj.filter_settings.post_pt_win)
        if self.mw.data_obj.filter_settings.win_shape == "tukey":
            self.ui.radioButton_win_shape_tukey.setChecked(True)
            self.ui.doubleSpinBox_tukey_param.setEnabled(True)
            self.ui.doubleSpinBox_tukey_param.setValue(self.mw.data_obj.filter_settings.tukey_param)
        elif self.mw.data_obj.filter_settings.win_shape == "square":
            self.ui.radioButton_win_shape_square.setChecked(True)
            self.ui.doubleSpinBox_tukey_param.setEnabled(False)
        elif self.mw.data_obj.filter_settings.win_shape == "log":
            self.ui.radioButton_win_shape_log.setChecked(True)
            self.ui.doubleSpinBox_tukey_param.setEnabled(False)

    def update_default_signal_settings(self):
        # Update the default settings in Mainwindow's data_obj if it exists
        if self.mw.data_obj.study_file_path is None:
            self.deleteLater()
            return
        else:
            self.mw.data_obj.filter_settings.pre_pt_win = self.ui.spinBox_pre_window_msec.value()
            self.mw.data_obj.filter_settings.post_pt_win = self.ui.spinBox_post_window_msec.value()
            if self.ui.radioButton_win_shape_tukey.isChecked():
                self.mw.data_obj.filter_settings.win_shape = "tukey"
                self.mw.data_obj.filter_settings.tukey_param = self.ui.doubleSpinBox_tukey_param.value()
            elif self.ui.radioButton_win_shape_square.isChecked():
                self.mw.data_obj.filter_settings.win_shape = "square"
            elif self.ui.radioButton_win_shape_log.isChecked():
                self.mw.data_obj.filter_settings.win_shape = "log"

        # Close / delete later
        self.deleteLater()

    def handle_win_shape_radio_buttons(self):
        if self.ui.radioButton_win_shape_tukey.isChecked():
            self.ui.doubleSpinBox_tukey_param.setEnabled(True)
        else:
            self.ui.doubleSpinBox_tukey_param.setEnabled(False)