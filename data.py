import h5py
import numpy as np


class EMGpoint:
    """
    A class defining a particular point of interest in the EMG - e.g. a stimulation time,
    QRS activation time, or atrial activation time
    """
    def __init__(self, point_time, signal_length, default_settings, highlighted=False):
        self.point_time = point_time
        self.pre_pt_win = default_settings.pre_pt_win
        self.post_pt_win = default_settings.post_pt_win
        self.win_shape = default_settings.win_shape
        self.tukey_param = default_settings.tukey_param
        self.highlighted = highlighted
        self.signal_length = signal_length

        self.window_array_y = []
        self.window_array_x = []
        self.create_window_array()

    def create_window_array(self):
        """
        Create the weighting coefficients for the window around the EMG point
        """
        win_len = self.post_pt_win + self.pre_pt_win + 1
        self.window_array_x = np.linspace(self.point_time - self.pre_pt_win, self.point_time + self.post_pt_win, win_len, dtype=int)
        a = np.linspace(0, 1, self.pre_pt_win)
        b = 1
        c = np.linspace(1, 0, self.post_pt_win)
        self.window_array_y = np.concatenate((a, b, c), axis=None)


class FilterSettings:
    """
    A class to hold the filter settings
    """
    def __init__(self):
        self.pre_pt_win = 50
        self.post_pt_win = 50
        self.win_shape = "log"
        self.tukey_param = 1.0


class Data:
    """
    A class to hold elements of the study's data file, process those elements, and hold
    them in a form that is easily transferred to the graphics interface
    """
    def __init__(self):
        # The path to the h5 file
        self.study_file_path = None

        # Init the data objects variables
        self.points = np.array([])
        self.points_times = np.array([])
        self.unipolar = np.array([])
        self.bipolar = np.array([])
        self.reference = np.array([])
        self.ecg = np.array([])
        self.mV_gain = []
        self.vertices = np.array([])
        self.faces = np.array([])
        self.subtraction_list = []
        self.activation_list = []

        # Init a filter settings object
        self.filter_settings = FilterSettings()

    def set_h5_filepath(self, study_file_path):
        self.study_file_path = study_file_path

    def read_in_data(self):
        # Open the .h5 file and get the contents
        with h5py.File(self.study_file_path, 'r') as f:
            self.unipolar = f['unipolar'][()]
            self.bipolar = f['bipolar'][()]
            self.reference = f['reference'][()]
            self.ecg = f['ecg_leadI'][()]
            self.mV_gain = f['unipolar'].attrs['mV_gain']
            self.points = f['point_coordinates'][()]
            self.points_times = f['point_coordinate_times'][()]

    def resave_data(self):
        x = 1

    def subtraction(self):
        # Initial coefficients / weights = 1 (i.e. nothing changes)
        sub_arr = np.ones((1, self.unipolar.shape[1]))

        # Adjust the subtraction windows according to each EMG point
        for pt in self.subtraction_list:
            sub_arr[0, pt.window_array_x] = 1 - pt.window_array_y

        # Multiply the channels with the subtraction array
        self.unipolar = self.unipolar * sub_arr
