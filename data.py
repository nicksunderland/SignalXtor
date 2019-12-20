import h5py
import numpy as np


class Data:

    def __init__(self, study_file_path):
        # Save the path to the h5 file
        self.study_file_path = study_file_path

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

        # Read in the data from the .h5 file
        self.read_in_data()

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