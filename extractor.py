from PyQt5.QtCore import QObject, pyqtSignal
import h5py
import os
import re
import numpy as np


class Extractor(QObject):

    def __init__(self, system_type, root, new_file_path, study_name):
        super(Extractor, self).__init__()

        self.root_dir = root
        self.system_type = system_type
        self.study_name = study_name
        self.h5_file_path = new_file_path

    def extract_data(self, signals, null):
        """
        Creates a new h5 file to receive the extracted data and runs the extraction functions depending on the
        specified mapping system
        """

        if os.path.isfile(self.h5_file_path):
            # Delete the old file and return a new
            os.remove(self.h5_file_path)
            h5_file = h5py.File(self.h5_file_path, 'w')
            h5_file.close()
        else:
            # Return a new file
            h5_file = h5py.File(self.h5_file_path, 'w')
            h5_file.close()

        # Extract data, depending on the system format
        if self.system_type == "carto":
            self.extract_carto_data(signals)
        elif self.system_type == "other":
            return "Other mapping system option was selected - aborted"

        return "extract_data function complete"

    def extract_carto_data(self, signals):
        """
        Extracts the data to the .h5 file from CARTO files
        """
        # Some places to keep things
        mV_gain = []
        points_info = []
        points_info_missing_data = []
        missing_data_idxs = []
        unipolar_data = np.array([])
        bipolar_data = np.array([])
        reference_data = np.array([])
        ecg_data = np.array([])
        point_coords = []
        point_coord_times = np.array([])

        # Get the files in the directory
        for root, dirs, files in os.walk(self.root_dir):

            # Total number of file to look through
            max_num_files = len(files)

            # Cycle the files in the directory
            for i, file in enumerate(files, start=1):

                # Process only those files related to the study
                if file.startswith(self.study_name) and file.endswith("ECG_Export.txt"):

                    # Variables to extract once
                    mV_gain = []

                    # Determine the tag point
                    p = re.search(r"_P(\d+)_", file)
                    if p is not None:
                        point_name = p.group(1)
                        if any(info[0] == point_name for info in points_info):
                            continue
                    else:
                        continue

                    # Open the ECG file
                    with open(self.root_dir + "/" + file) as f:
                        for ii, line in enumerate(f):
                            if ii == 1 and len(mV_gain) == 0:  # 2nd line contains mV gain
                                mV_gain = re.search(r" = (\d+\.\d+)", line).group(1)
                            elif ii == 2:  # 3rd line contains mapping and reference channels
                                uni_map_chan = re.search(r"Unipolar Mapping Channel=([0-9A-Za-z_-]+)", line).group(1)
                                bip_map_chan = re.search(r"Bipolar Mapping Channel=([0-9A-Za-z_-]+)", line).group(1)
                                ref_map_chan = re.search(r"Reference Channel=([0-9A-Za-z_-]+)", line).group(1)
                            elif ii == 3:  # 4th line contains unipolar and bipolar mapping and reference channels
                                headers = line.split()
                                uni_col_idx = next((i for i in enumerate(headers) if uni_map_chan in i[1]), [-1, -1])[0]
                                bip_col_idx = next((i for i in enumerate(headers) if bip_map_chan in i[1]), [-1, -1])[0]
                                ref_col_idx = next((i for i in enumerate(headers) if ref_map_chan in i[1]), [-1, -1])[0]
                                ecg_col_idx = next((i for i in enumerate(headers) if "I(" in i[1]), [-1, -1])[0]
                            elif ii == 4:  # 5th line contains the channel data
                                signal_data = np.loadtxt(self.root_dir + "/" + file, float, skiprows=4,
                                                         usecols=(uni_col_idx, bip_col_idx, ref_col_idx, ecg_col_idx))
                            elif ii > 4:  # Should have grabbed everything by this point
                                break

                        # Store the point info
                        points_info.append([point_name, uni_map_chan, bip_map_chan, ref_map_chan, "Lead I ECG"])
                        storage_idx = len(points_info) - 1

                        # Resize the data matrix
                        unipolar_data.resize((len(points_info), signal_data.shape[0]))
                        bipolar_data.resize((len(points_info), signal_data.shape[0]))
                        reference_data.resize((len(points_info), signal_data.shape[0]))
                        ecg_data.resize((len(points_info), signal_data.shape[0]))

                        # Add in the data
                        unipolar_data[storage_idx, :] = signal_data[:, 0]
                        bipolar_data[storage_idx, :] = signal_data[:, 1]
                        reference_data[storage_idx, :] = signal_data[:, 2]
                        ecg_data[storage_idx, :] = signal_data[:, 3]

                signals.progress.emit(100 * (i / max_num_files))

            signals.progress.emit(0)

        # Cycle the points looking for point geometry files
        for i, point in enumerate(points_info):

            # Total number of files to re-examine
            max_num_files = len(points_info)

            if "20A_" in point[1]:
                coords_file_path = self.root_dir + "/" + \
                                   self.study_name + \
                                   "_P" + point[0] + \
                                   "_MAGNETIC_20_POLE_A_CONNECTOR_Eleclectrode_Positions.txt"

                electrode = re.match(r"20A_(\d+)", point[1])[1]

            elif "20B_" in point[1]:
                coords_file_path = self.root_dir + "/" + \
                                   self.study_name + \
                                   "_P" + point[0] + \
                                   "_MAGNETIC_20_POLE_B_CONNECTOR_Eleclectrode_Positions.txt"

                electrode = re.match(r"20B_(\d+)", point[1])[1]

            elif "M" in point[1]:
                coords_file_path = self.root_dir + "/" + \
                                   self.study_name + \
                                   "_P" + point[0] + \
                                   "_NAVISTAR_CONNECTOR_Eleclectrode_Positions.txt"

                electrode = re.match(r"M(\d+)", point[1])[1]
            else:
                coords_file_path = []
                electrode = []

            if not os.path.isfile(coords_file_path):
                # Coordinate data file not found / keep track of index and continue the loop
                points_info_missing_data.append([point, ".../" + coords_file_path.split("/")[-1]])
                missing_data_idxs.append(i)
                continue

            # Open the coordinates file
            with open(coords_file_path) as f:
                start_idx_found = False
                for ii, line in enumerate(f):

                    # Get the start row of the tagging electrode's data
                    if not start_idx_found and electrode in line.split()[0]:
                        start_idx = ii
                        start_idx_found = True

                    # Get the end row
                    if start_idx_found and electrode not in line.split()[0]:
                        end_idx = ii-1
                        break

            # If the first iteration grab the timing data
            if point_coord_times.size == 0 and len(point_coords) == 0:
                raw_pt_coords = np.loadtxt(coords_file_path, float, skiprows=start_idx,
                                           usecols=(1, 2, 3, 4),
                                           max_rows=end_idx-start_idx+1)
                point_coord_times = raw_pt_coords[:, 0]
                point_coords.append(raw_pt_coords[:, 1:4])

            # Else, just append the next point's coordinates
            else:
                point_coords.append(raw_pt_coords[:, 1:4])

            signals.progress.emit(100 * (i / max_num_files))

        # Only save points with data
        good_data_idxs = list(set(range(0, unipolar_data.shape[0])) - set(missing_data_idxs))

        # Check that coordinate data matches the size of the signal data
        assert(len(good_data_idxs) == len(point_coords))

        # Save the datasets and set the mV_gain as an attribute on the signals
        with h5py.File(self.h5_file_path, 'r+') as f:
            dset_u = f.create_dataset("/unipolar", data=unipolar_data[good_data_idxs, :])
            dset_u.attrs['mV_gain'] = mV_gain
            dset_b = f.create_dataset("/bipolar", data=bipolar_data[good_data_idxs, :])
            dset_b.attrs['mV_gain'] = mV_gain
            dset_r = f.create_dataset("/reference", data=reference_data[good_data_idxs, :])
            dset_r.attrs['mV_gain'] = mV_gain
            dset_e = f.create_dataset("/ecg_leadI", data=ecg_data[good_data_idxs, :])
            dset_e.attrs['mV_gain'] = mV_gain
            f.create_dataset("/point_coordinate_times", data=point_coord_times)
            f.create_dataset("/point_coordinates", data=np.dstack(point_coords))

        # Write missing data info to text file if there is any
        if len(points_info_missing_data) > 0:
            missing_data_txt_file = os.getcwd() + "/case_files" + "/" + self.study_name + "_missing_data.txt"
            with open(missing_data_txt_file, 'w+') as f_txt:
                f_txt.write("***SIGNALXTOR MISSING DATA INFORMATION***\n\n"
                            "Study: " + self.study_name + "\n\n")
                f_txt.write("[Point, Unipolar, Bipolar, Reference, ECG lead, Missing file]\n\n")
                f_txt.write("\n\n".join(str(missing_point) for missing_point in points_info_missing_data))

            # Emit signal with missing data info
            signals.missing_files_path.emit(missing_data_txt_file)

        # Reset progress bar on leaving
        signals.progress.emit(0)

