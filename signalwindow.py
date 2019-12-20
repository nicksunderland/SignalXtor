import pyqtgraph


class SignalWindow:

    def __init__(self):
        self.graph = pyqtgraph.PlotWidget()
        self.graph.setTitle("Channel ...")
        self.graph.getAxis('left').setLabel('mV')
        self.graph.getAxis('bottom').setLabel('msec')
        self.graph.setBackground('k')
        self.graph.showGrid(x=True, y=True)

    def update_plot(self, data_obj, signal_idx, signal_type):
        self.graph.clear()
        self.graph.setTitle("Channel " + str(signal_idx + 1))
        self.graph.plot(data_obj.unipolar[signal_idx, :] * float(data_obj.mV_gain))
