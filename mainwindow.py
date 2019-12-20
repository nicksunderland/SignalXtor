from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QFileSystemModel, QRadioButton
from PyQt5.QtCore import QRunnable, QThreadPool, QObject, pyqtSignal, pyqtSlot
import os, traceback, sys, subprocess
import re
os.system("pyuic5 UI_files/ui_mainwindow.ui > UI_files/ui_mainwindow.py")
from UI_files.ui_mainwindow import Ui_MainWindow
import signalwindow
import meshwindow
import extractor
import data


class ThreadSignals(QObject):
    """
    Defines the signals to be used by the worker thread class
    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    interim_result = pyqtSignal(object)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    missing_files_path = pyqtSignal(str)


class ThreadClass(QRunnable, QObject):
    """
    The worker thread class. Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    """

    def __init__(self, function_to_run, **kwargs):
        super(ThreadClass, self).__init__()

        # Constructor arguments
        self.func = function_to_run
        self.kwargs = kwargs
        self.signals = ThreadSignals()

        # Add things into the kwargs from the thread class as needed
        self.kwargs['signals'] = self.signals

    @pyqtSlot()
    def run(self):
        # Try the function with the kwargs and handle the output
        try:
            func_return_value = self.func(**self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(func_return_value)
        finally:
            self.signals.finished.emit()


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Setup the main window GUI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Setup the signal plotting window
        self.signal_window = signalwindow.SignalWindow()
        self.ui.verticalLayout_graph_holder.addWidget(self.signal_window.graph)

        # Setup the mesh plotting window
        self.mesh_window = meshwindow.MeshWindow()
        self.ui.vispy_layout.addWidget(self.mesh_window.canvas.native)

        # Init other variables
        self.tree_view_model = QFileSystemModel()
        self.tree_view_model.setNameFilters(["*.h5"])
        self.studies_list = []
        self.import_case_filepath = ""
        self.data_obj = None
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        # Make the button connections
        self.make_button_connections()

        # Search for existing extracted cases
        self.find_saved_cases()

        # Tmp UI settings
        self.ui.lineEdit_directory.setText(os.getcwd() + "/example_data/CartoStudy2")
        self.dir_changed()

    def make_button_connections(self):
        self.ui.toolButton_directory.clicked.connect(self.find_directory)
        self.ui.lineEdit_directory.textChanged.connect(self.dir_changed)
        self.ui.pushButton_close.clicked.connect(self.close)
        self.ui.pushButton_extract_data.clicked.connect(self.extract_data_button_pushed)
        self.ui.pushButton_import_study.clicked.connect(self.import_study_button_pushed)
        self.ui.pushButton_delete_study.clicked.connect(self.delete_study_button_pushed)
        self.ui.treeView_casesDir.clicked.connect(self.set_import_case_filepath)
        self.ui.spinBox_signals.valueChanged.connect(self.update_signal_window)

    def find_saved_cases(self):
        # Set the treeView for the case_files directory
        self.tree_view_model.setRootPath(os.getcwd() + "/case_files")
        self.ui.treeView_casesDir.setModel(self.tree_view_model)
        self.ui.treeView_casesDir.setRootIndex(self.tree_view_model.index(os.getcwd() + "/case_files"))

    def find_directory(self):
        # Load a directory search dialog and get directory path
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.ui.lineEdit_directory.setText(dir_path)

    def dir_changed(self):
        # Reset the counters and containers
        self.studies_list.clear()
        for i in reversed(range(self.ui.scrollArea_Vlayout.count())):
            self.ui.scrollArea_Vlayout.itemAt(i).widget().deleteLater()

        # Create new thread and pass in the function and kwargs
        kwargs = {"files_dir": self.ui.lineEdit_directory.text()}
        worker_thread = ThreadClass(self.handle_dir_change, **kwargs)
        worker_thread.signals.result.connect(self.print_output)
        worker_thread.signals.interim_result.connect(self.update_studies_list)
        worker_thread.signals.progress.connect(self.update_progress_bar)

        # Execute
        self.threadpool.start(worker_thread)

    def handle_dir_change(self, signals, files_dir):
        # Local copy of the found studies
        studies_list = []

        # Cycle the files in the directory
        for root, dirs, files in os.walk(files_dir):

            max_num_files = len(files)

            for i, name in enumerate(files):

                # Search for the study names
                try:
                    study = re.search(r".+_P\d+_", name)[0].split(r"_P")[0]
                except (TypeError, AttributeError):
                    continue

                # If study not already present, add it to the list
                if study not in studies_list:
                    studies_list.append(study)  # Append locally
                    signals.interim_result.emit(study)  # Emit result to main GUI thread too

                signals.progress.emit(round(100 * (i / max_num_files)))

        signals.progress.emit(0)

        return "handle dir change function complete"

    def extract_data_button_pushed(self):
        # Make sure there is are studies to extract from
        if len(self.studies_list) == 0:
            QMessageBox.information(self, "Error", "There don't seem to be any studies to extract from")
            return

        # Get the selected study name from the radio button check boxes
        for i in range(self.ui.scrollArea_Vlayout.count()):
            if self.ui.scrollArea_Vlayout.itemAt(i).widget().isChecked():
                study_name = self.ui.scrollArea_Vlayout.itemAt(i).widget().text()
        try:
            study_name
        except NameError:
            QMessageBox.information(self, "Error", "Something went wrong. \nNo checked study found. \nMake sure a "
                                                   "study is selected")
            return

        # The proposed new file path
        new_file_path = os.getcwd() + "/case_files" + "/" + study_name + ".h5"

        # First check if it already exists / ok to overwrite it
        if os.path.isfile(new_file_path):
            msgbox = QMessageBox.warning(None, "Warning", "Project: \n\n" + new_file_path.split("/case_files/")[1] +
                                                          "\n\n...already exists. "
                                                          "\n\nDo you want to overwrite it?",
                                         QMessageBox.Yes | QMessageBox.No)
            # Check if want to overwrite file
            if msgbox == QMessageBox.No:
                return

        # Create an extractor object
        if self.ui.radioButton_carto.isChecked():
            e = extractor.Extractor("carto", self.ui.lineEdit_directory.text(), new_file_path, study_name)
        elif self.ui.radioButton_other.isChecked():
            QMessageBox.information(self, "Error", "No other option currently")
            return

        # Create a new thread and pass the extractor function in, no variables needed (went into the __init__)
        kwargs = {"null": None}
        worker_thread = ThreadClass(e.extract_data, **kwargs)
        worker_thread.signals.missing_files_path.connect(self.handle_missing_data)
        worker_thread.signals.progress.connect(self.update_progress_bar)     # daisy chain the signals ---^
        worker_thread.signals.result.connect(self.print_output)

        # Execute
        self.threadpool.start(worker_thread)

    def handle_missing_data(self, missing_data_file):
        msgbox = QMessageBox.warning(None, "Warning", "Some data files not found. \n\n"
                                                      "Do you want to view the missing data information?",
                                     QMessageBox.Yes | QMessageBox.No)
        if msgbox == QMessageBox.Yes:
            # Open the .txt file with the default OS programme
            subprocess.run(['open', missing_data_file], check=True)
        else:
            return

    def print_output(self, s):
        self.ui.progressBar.setValue(0)
        print("Thread return: " + str(s))

    def update_progress_bar(self, percent_done):
        self.ui.progressBar.setValue(percent_done)

    def update_studies_list(self, study_name):
        if study_name not in self.studies_list:
            self.studies_list.append(study_name)
            radio = QRadioButton()
            radio.setText(study_name)
            self.ui.scrollArea_Vlayout.insertWidget(len(self.studies_list) - 1, radio)

    def set_import_case_filepath(self, index):
        self.import_case_filepath = self.sender().model().filePath(index)

    def import_study_button_pushed(self):
        if os.path.isfile(self.import_case_filepath):
            if self.data_obj is not None:
                msgbox = QMessageBox.warning(None, "Warning", "Study: \n" + self.data_obj.study_file_path +
                                             "\n...will be closed.\nDo you want to save changes?",
                                             QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel)
                if msgbox == QMessageBox.Save:
                    self.data_obj.resave_data()
                elif msgbox == QMessageBox.Cancel:
                    return

            self.data_obj = data.Data(self.import_case_filepath)
            self.update_signal_window()
            self.update_mesh_window()
        else:
            QMessageBox.information(self, "Error", "Import study file path not set.\nMake sure a study is selected.")
            return

    def delete_study_button_pushed(self):
        if os.path.isfile(self.import_case_filepath):
            msgbox = QMessageBox.warning(None, "Confirm delete", "Deleting file:\n" + self.import_case_filepath +
                                         "\nSure?",
                                         QMessageBox.Yes | QMessageBox.No)
            if msgbox == QMessageBox.Yes:
                # Remove the data file
                os.remove(self.import_case_filepath)
                # Also look for any missing data information .txt files and delete too
                missing_data_file_info_path = self.import_case_filepath.split(".h5")[0] + "_missing_data.txt"
                if os.path.isfile(missing_data_file_info_path):
                    os.remove(missing_data_file_info_path)

            elif msgbox == QMessageBox.No:
                return

    def update_signal_window(self):
        if self.data_obj is None:
            return
        else:
            channel = self.ui.spinBox_signals.value()
            if channel > self.data_obj.unipolar.shape[0]:
                channel = self.data_obj.unipolar.shape[0]
                self.ui.spinBox_signals.setValue(channel)
            self.signal_window.update_plot(self.data_obj, channel - 1, "tmp")

    def update_mesh_window(self):
        if self.data_obj is None:
            return
        else:
            self.mesh_window.update_plot()
