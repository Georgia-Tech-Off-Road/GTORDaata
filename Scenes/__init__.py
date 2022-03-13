from DataAcquisition import data
from PyQt5 import QtWidgets
from abc import ABCMeta, abstractmethod


class DAATAScene(QtWidgets.QWidget):
    def __init__(self, **kwargs):
        super().__init__()
        __metaclass__ = ABCMeta

        self.update_period = 100  # refresh 1 time a second

    @abstractmethod
    def update_active(self):
        raise NotImplementedError

    def update_graph_frequency_passively(self):
        index_time = data.get_most_recent_index()
        if index_time > 0:
            start = data.get_value("time_internal_seconds", 0)
            end = data.get_value("time_internal_seconds", index_time)
            new_sampling_freq = index_time / (end - start)
            for graph in self.graph_objects.values():
                if graph.isVisible():
                    graph.update_graph_width(new_sampling_freq)
