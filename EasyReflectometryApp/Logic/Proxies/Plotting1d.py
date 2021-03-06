__author__ = 'github.com/andrewsazonov'

import numpy as np

from PySide2.QtCore import QObject, Qt, QPointF, Signal, Slot, Property
from PySide2.QtGui import QImage, QBrush
from PySide2.QtQml import QJSValue
from PySide2.QtCharts import QtCharts


class Plotting1dProxy(QObject):
    """
    A proxy class to interact between the QML plot and Python datasets.
    """

    dummySignal = Signal()

    # Lib
    currentLibChanged = Signal()

    # Ranges
    experimentPlotRangesObjChanged = Signal()
    analysisPlotRangesObjChanged = Signal()
    sampleSldPlotRangesObjChanged = Signal()
    analysisSldPlotRangesObjChanged = Signal()

    # Data containers
    bokehMeasuredDataObjChanged = Signal()
    bokehCalculatedDataObjChanged = Signal()
    bokehPureDataObjChanged = Signal()
    bokehBackgroundDataObjChanged = Signal()
    bokehSampleSldDataObjChanged = Signal()
    bokehAnalysisSldDataObjChanged = Signal()

    qtchartsMeasuredDataObjChanged = Signal()
    qtchartsCalculatedDataObjChanged = Signal()
    qtchartsBackgroundDataObjChanged = Signal()

    # Misc
    sldXDataReversedChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Lib
        self._libs = ['bokeh']#, 'qtcharts']
        self._current_lib = 'bokeh'
        self.currentLibChanged.connect(self.onCurrentLibChanged)

        # Ranges
        self._measured_min_x = 999999
        self._measured_max_x = -999999
        self._measured_min_y = 999999
        self._measured_max_y = -999999

        self._calculated_min_x = 999999
        self._calculated_max_x = -999999
        self._calculated_min_y = 999999
        self._calculated_max_y = -999999

        self._pure_min_x = 999999
        self._pure_max_x = -999999
        self._pure_min_y = 999999
        self._pure_max_y = -999999

        self._sample_sld_min_x = 999999
        self._sample_sld_max_x = -999999
        self._sample_sld_min_y = 999999
        self._sample_sld_max_y = -999999

        self._analysis_sld_min_x = 999999
        self._analysis_sld_max_x = -999999
        self._analysis_sld_min_y = 999999
        self._analysis_sld_max_y = -999999

        self._y_axis_range_extension = 0.1

        # Data containers
        self._measured_xarray = np.empty(0)
        self._measured_yarray = np.empty(0)
        self._measured_syarray = np.empty(0)
        self._measured_yarray_upper = np.empty(0)
        self._measured_yarray_lower = np.empty(0)

        self._calculated_xarray = np.empty(0)
        self._calculated_yarray = np.empty(0)

        self._pure_xarray = np.empty(0)
        self._pure_yarray = np.empty(0)

        self._sample_sld_xarray = np.empty(0)
        self._sample_sld_yarray = np.empty(0)

        self._analysis_sld_xarray = np.empty(0)
        self._analysis_sld_yarray = np.empty(0)

        self._background_xarray = np.empty(0)
        self._background_yarray = np.empty(0)

        # Ranges for GUI
        self._experiment_plot_ranges_obj = {}
        self._analysis_plot_ranges_obj = {}
        self._sample_sld_plot_ranges_obj = {}
        self._analysis_sld_plot_ranges_obj = {}

        # Data containers for GUI
        self._bokeh_measured_data_obj = {}
        self._bokeh_calculated_data_obj = {}
        self._bokeh_pure_data_obj = {}
        self._bokeh_background_data_obj = {}
        self._bokeh_sample_sld_data_obj = {}
        self._bokeh_analysis_sld_data_obj = {}

        self._qtcharts_measured_data_obj = {}
        self._qtcharts_calculated_data_obj = {}
        self._qtcharts_background_data_obj = {}

        # Misc
        self._sld_x_data_reversed = False

    def clearFrontendState(self):

        # Ranges for GUI
        self._experiment_plot_ranges_obj = {}
        self._analysis_plot_ranges_obj = {}
        self._sample_sld_plot_ranges_obj = {}
        self._analysis_sld_plot_ranges_obj = {}

        # Data containers for GUI
        self._bokeh_measured_data_obj = {}
        self._bokeh_calculated_data_obj = {}
        self._bokeh_pure_data_obj = {}
        self._bokeh_background_data_obj = {}
        self._bokeh_sample_sld_data_obj = {}
        self._bokeh_analysis_sld_data_obj = {}

        self._qtcharts_measured_data_obj = {}
        self._qtcharts_calculated_data_obj = {}
        self._qtcharts_background_data_obj = {}

        # Ranges
        self.experimentPlotRangesObjChanged.emit()
        self.analysisPlotRangesObjChanged.emit()
        self.sampleSldPlotRangesObjChanged.emit()
        self.analysisSldPlotRangesObjChanged.emit()

        # Data containers
        self.bokehMeasuredDataObjChanged.emit()
        self.bokehCalculatedDataObjChanged.emit()
        self.bokehPureDataObjChanged.emit()
        self.bokehBackgroundDataObjChanged.emit()
        self.bokehSampleSldDataObjChanged.emit()
        self.bokehAnalysisSldDataObjChanged.emit()

        self.qtchartsMeasuredDataObjChanged.emit()
        self.qtchartsCalculatedDataObjChanged.emit()
        self.qtchartsBackgroundDataObjChanged.emit()

    # Public: QML frontend

    # Libs for GUI
    @Property('QVariant', notify=dummySignal)
    def libs(self):
        return self._libs

    @Property(str, notify=currentLibChanged)
    def currentLib(self):
        return self._current_lib

    @currentLib.setter
    def currentLib(self, lib):
        if self._current_lib == lib:
            return
        self._current_lib = lib
        self.currentLibChanged.emit()

    # Ranges for GUI
    @Property('QVariant', notify=experimentPlotRangesObjChanged)
    def experimentPlotRangesObj(self):
        return self._experiment_plot_ranges_obj

    @Property('QVariant', notify=analysisPlotRangesObjChanged)
    def analysisPlotRangesObj(self):
        return self._analysis_plot_ranges_obj

    @Property('QVariant', notify=sampleSldPlotRangesObjChanged)
    def sampleSldPlotRangesObj(self):
        return self._sample_sld_plot_ranges_obj

    @Property('QVariant', notify=analysisSldPlotRangesObjChanged)
    def analysisSldPlotRangesObj(self):
        return self._analysis_sld_plot_ranges_obj

    # Data containers for GUI
    @Property('QVariant', notify=bokehMeasuredDataObjChanged)
    def bokehMeasuredDataObj(self):
        return self._bokeh_measured_data_obj

    @Property('QVariant', notify=bokehCalculatedDataObjChanged)
    def bokehCalculatedDataObj(self):
        return self._bokeh_calculated_data_obj

    @Property('QVariant', notify=bokehPureDataObjChanged)
    def bokehPureDataObj(self):
        return self._bokeh_pure_data_obj

    @Property('QVariant', notify=bokehBackgroundDataObjChanged)
    def bokehBackgroundDataObj(self):
        return self._bokeh_background_data_obj

    @Property('QVariant', notify=bokehSampleSldDataObjChanged)
    def bokehSampleSldDataObj(self):
        return self._bokeh_sample_sld_data_obj

    @Property('QVariant', notify=bokehAnalysisSldDataObjChanged)
    def bokehAnalysisSldDataObj(self):
        return self._bokeh_analysis_sld_data_obj

    @Property('QVariant', notify=qtchartsMeasuredDataObjChanged)
    def qtchartsMeasuredDataObj(self):
        return self._qtcharts_measured_data_obj

    @Property('QVariant', notify=qtchartsCalculatedDataObjChanged)
    def qtchartsCalculatedDataObj(self):
        return self._qtcharts_calculated_data_obj

    @Property('QVariant', notify=qtchartsBackgroundDataObjChanged)
    def qtchartsBackgroundDataObj(self):
        return self._qtcharts_background_data_obj

    # QtCharts for GUI
    @Slot('QVariant', 'QVariant')
    def lineSeriesCustomReplace(self, line_series, points):
        if not isinstance(line_series, (QtCharts.QLineSeries, QtCharts.QScatterSeries)):
            return
        if points is None:
            return
        if isinstance(points, QJSValue):
            points = points.toVariant()
        if isinstance(points, list):
            line_series.replace(points)

    @Slot(int, str, result='QBrush')
    def verticalLine(self, size, color):
        width = size
        height = size
        textureImage = QImage(width, height, QImage.Format_ARGB32)
        # Transparent background
        for row in range(height):
            for column in range(width):
                textureImage.setPixelColor(column, row, Qt.transparent)
        # Vertical line
        for row in range(height):
            column = int(width / 2)
            textureImage.setPixelColor(column, row, color)
        brush = QBrush()
        brush.setTextureImage(textureImage)
        return brush

    # Misc
    @Property(bool, notify=sldXDataReversedChanged)
    def sldXDataReversed(self):
        return self._sld_x_data_reversed

    @Slot()
    def reverseSldXData(self):
        self._sample_sld_min_x, self._sample_sld_max_x = self._sample_sld_max_x, self._sample_sld_min_x
        self._setSampleSldPlotRanges()
        self._analysis_sld_min_x, self._analysis_sld_max_x = self._analysis_sld_max_x, self._analysis_sld_min_x
        self._setAnalysisSldPlotRanges()
        self._sld_x_data_reversed = not self._sld_x_data_reversed
        self.sldXDataReversedChanged.emit()

    # Public: Python backend

    def setMeasuredData(self, xarray, yarray, syarray=None):
        self._setMeasuredDataArrays(xarray, yarray, syarray)
        self._setMeasuredDataRanges()
        self._setExperimentPlotRanges()
        self._setAnalysisPlotRanges()
        self._setBokehMeasuredDataObj()
        if self.currentLib == 'qtcharts':
            self._setQtChartsMeasuredDataObj()

    def setCalculatedData(self, xarray, yarray):
        self._setCalculatedDataArrays(xarray, yarray)
        self._setCalculatedDataRanges()
        self._setAnalysisPlotRanges()
        self._setAnalysisSldPlotRanges()
        self._setBokehCalculatedDataObj()
        if self.currentLib == 'qtcharts':
            self._setQtChartsCalculatedDataObj()

    def setPureData(self, xarray, yarray):
        self._setPureDataArrays(xarray, yarray)
        self._setPureDataRanges()
        self._setAnalysisPlotRanges()
        self._setSampleSldPlotRanges()
        self._setBokehPureDataObj()
        # if self.currentLib == 'qtcharts':
        #     self._setQtChartsCalculatedDataObj()

    def setBackgroundData(self, xarray, yarray):
        self._setBackgroundDataArrays(xarray, yarray)
        if self._background_xarray.size:
            self._setBokehBackgroundDataObj()
            if self.currentLib == 'qtcharts':
                self._setQtChartsBackgroundDataObj()

    def setSampleSldData(self, xarray, yarray):
        self._setSampleSldDataArrays(xarray, yarray)
        self._setSampleSldDataRanges()
        self._setSampleSldPlotRanges()
        self._setBokehSampleSldDataObj()
        if self.currentLib == 'qtcharts':
            pass

    def setAnalysisSldData(self, xarray, yarray):
        self._setAnalysisSldDataArrays(xarray, yarray)
        self._setAnalysisSldDataRanges()
        self._setAnalysisSldPlotRanges()
        self._setBokehAnalysisSldDataObj()
        if self.currentLib == 'qtcharts':
            pass

    def onCurrentLibChanged(self):
        if self.currentLib == 'qtcharts':
            self._setQtChartsCalculatedDataObj()
            self._setQtChartsBackgroundDataObj()
            if self._measured_xarray.size:
                self._setQtChartsMeasuredDataObj()

    # Private: data array setters

    def _setMeasuredDataArrays(self, xarray, yarray, syarray=None):
        self._measured_xarray = xarray
        self._measured_yarray = yarray
        if syarray is not None:
            self._measured_syarray = syarray
        else:
            self._measured_syarray = np.ones_like(yarray)
        self._measured_yarray_upper = np.add(self._measured_yarray,
                                             self._measured_syarray)
        self._measured_yarray_lower = np.subtract(self._measured_yarray,
                                                  self._measured_syarray)

    def _setCalculatedDataArrays(self, xarray, yarray):
        self._calculated_xarray = xarray
        self._calculated_yarray = yarray

    def _setPureDataArrays(self, xarray, yarray):
        self._pure_xarray = xarray
        self._pure_yarray = yarray

    def _setSampleSldDataArrays(self, xarray, yarray):
        self._sample_sld_xarray = xarray
        self._sample_sld_yarray = yarray

    def _setAnalysisSldDataArrays(self, xarray, yarray):
        self._analysis_sld_xarray = xarray
        self._analysis_sld_yarray = yarray

    def _setBackgroundDataArrays(self, xarray, yarray):
        self._background_xarray = xarray
        self._background_yarray = yarray

    def _setBokehMeasuredDataObj(self):
        self._bokeh_measured_data_obj = {
            'x': Plotting1dProxy.aroundX(self._measured_xarray),
            'y': Plotting1dProxy.aroundY(self._measured_yarray),
            'sy': Plotting1dProxy.aroundY(self._measured_syarray),
            'y_upper': Plotting1dProxy.aroundY(self._measured_yarray_upper),
            'y_lower': Plotting1dProxy.aroundY(self._measured_yarray_lower)
        }
        self.bokehMeasuredDataObjChanged.emit()

    def _setBokehCalculatedDataObj(self):
        self._bokeh_calculated_data_obj = {
            'x': Plotting1dProxy.aroundX(self._calculated_xarray),
            'y': Plotting1dProxy.aroundY(self._calculated_yarray)
        }
        self.bokehCalculatedDataObjChanged.emit()

    def _setBokehPureDataObj(self):
        self._bokeh_pure_data_obj = {
            'x': Plotting1dProxy.aroundX(self._pure_xarray),
            'y': Plotting1dProxy.aroundY(self._pure_yarray)
        }
        print(self._pure_yarray)
        self.bokehPureDataObjChanged.emit()

    def _setBokehPureDataObj(self):
        self._bokeh_pure_data_obj = {
            'x': Plotting1dProxy.aroundX(self._pure_xarray),
            'y': Plotting1dProxy.aroundY(self._pure_yarray)
        }
        self.bokehPureDataObjChanged.emit()

    def _setBokehSampleSldDataObj(self):
        self._bokeh_sample_sld_data_obj = {
            'x': Plotting1dProxy.aroundX(self._sample_sld_xarray),
            'y': Plotting1dProxy.aroundY(self._sample_sld_yarray)
        }
        self.bokehSampleSldDataObjChanged.emit()
    
    def _setBokehAnalysisSldDataObj(self):
        self._bokeh_analysis_sld_data_obj = {
            'x': Plotting1dProxy.aroundX(self._analysis_sld_xarray),
            'y': Plotting1dProxy.aroundY(self._analysis_sld_yarray)
        }
        self.bokehAnalysisSldDataObjChanged.emit()

    def _setBokehBackgroundDataObj(self):
        self._bokeh_background_data_obj = {
            'x': Plotting1dProxy.aroundX(self._background_xarray),
            'y': Plotting1dProxy.aroundY(self._background_yarray)
        }
        self.bokehBackgroundDataObjChanged.emit()

    def _setQtChartsMeasuredDataObj(self):
        self._qtcharts_measured_data_obj = {
            'xy':
            Plotting1dProxy.arraysToPoints(self._measured_xarray,
                                           self._measured_yarray),
            'xy_upper':
            Plotting1dProxy.arraysToPoints(self._measured_xarray,
                                           self._measured_yarray_upper),
            'xy_lower':
            Plotting1dProxy.arraysToPoints(self._measured_xarray,
                                           self._measured_yarray_lower)
        }
        self.qtchartsMeasuredDataObjChanged.emit()

    def _setQtChartsCalculatedDataObj(self):
        self._qtcharts_calculated_data_obj = {
            'xy':
            Plotting1dProxy.arraysToPoints(self._calculated_xarray,
                                           self._calculated_yarray)
        }
        self.qtchartsCalculatedDataObjChanged.emit()

    def _setQtChartsBackgroundDataObj(self):
        self._qtcharts_background_data_obj = {
            'xy':
            Plotting1dProxy.arraysToPoints(self._background_xarray,
                                           self._background_yarray)
        }
        self.qtchartsBackgroundDataObjChanged.emit()

    # Private: range setters

    def _setMeasuredDataRanges(self):
        self._measured_min_x = Plotting1dProxy.arrayMin(self._measured_xarray)
        self._measured_max_x = Plotting1dProxy.arrayMax(self._measured_xarray)
        self._measured_min_y = Plotting1dProxy.arrayMin(self._measured_yarray_lower)
        self._measured_max_y = Plotting1dProxy.arrayMax(self._measured_yarray_upper)

    def _setCalculatedDataRanges(self):
        self._calculated_min_x = Plotting1dProxy.arrayMin(self._calculated_xarray)
        self._calculated_max_x = Plotting1dProxy.arrayMax(self._calculated_xarray)
        self._calculated_min_y = Plotting1dProxy.arrayMin(self._calculated_yarray)
        self._calculated_max_y = Plotting1dProxy.arrayMax(self._calculated_yarray)

    def _setPureDataRanges(self):
        self._pure_min_x = Plotting1dProxy.arrayMin(self._pure_xarray)
        self._pure_max_x = Plotting1dProxy.arrayMax(self._pure_xarray)
        self._pure_min_y = Plotting1dProxy.arrayMin(self._pure_yarray)
        self._pure_max_y = Plotting1dProxy.arrayMax(self._pure_yarray)

    def _setSampleSldDataRanges(self):
        self._sample_sld_min_x = Plotting1dProxy.arrayMin(self._sample_sld_xarray)
        self._sample_sld_max_x = Plotting1dProxy.arrayMax(self._sample_sld_xarray)
        if self.sldXDataReversed:
            self._sample_sld_min_x, self._sample_sld_max_x = self._sample_sld_max_x, self._sample_sld_min_x
        self._sample_sld_min_y = Plotting1dProxy.arrayMin(self._sample_sld_yarray)
        self._sample_sld_max_y = Plotting1dProxy.arrayMax(self._sample_sld_yarray)

    def _setAnalysisSldDataRanges(self):
        self._analysis_sld_min_x = Plotting1dProxy.arrayMin(self._analysis_sld_xarray)
        self._analysis_sld_max_x = Plotting1dProxy.arrayMax(self._analysis_sld_xarray)
        if self.sldXDataReversed:
            self._analysis_sld_min_x, self._analysis_sld_max_x = self._analysis_sld_max_x, self._analysis_sld_min_x
        self._analysis_sld_min_y = Plotting1dProxy.arrayMin(self._analysis_sld_yarray)
        self._analysis_sld_max_y = Plotting1dProxy.arrayMax(self._analysis_sld_yarray)

    def _yAxisMin(self, min_y, max_y):
        return min_y

    def _yAxisMax(self, max_y):
        return max_y

    def _setExperimentPlotRanges(self):
        self._experiment_plot_ranges_obj = {
            'min_x':
            Plotting1dProxy.aroundX(self._measured_min_x),
            'max_x':
            Plotting1dProxy.aroundX(self._measured_max_x),
            'min_y':
            Plotting1dProxy.aroundY(
                self._yAxisMin(self._measured_min_y, self._measured_max_y)),
            'max_y':
            Plotting1dProxy.aroundY(self._yAxisMax(self._measured_max_y))
        }
        self.experimentPlotRangesObjChanged.emit()

    def _setAnalysisPlotRanges(self):
        min_x = self._calculated_min_x
        max_x = self._calculated_max_x
        min_y = self._calculated_min_y
        max_y = self._calculated_max_y
        if self._measured_xarray.size:
            min_x = self._measured_min_x
            max_x = self._measured_max_x
            min_y = min(self._measured_min_y, self._calculated_min_y)
            max_y = max(self._measured_max_y, self._calculated_max_y)
        self._analysis_plot_ranges_obj = {
            'min_x': Plotting1dProxy.aroundX(min_x),
            'max_x': Plotting1dProxy.aroundX(max_x),
            'min_y': Plotting1dProxy.aroundY(self._yAxisMin(min_y, max_y)),
            'max_y': Plotting1dProxy.aroundY(self._yAxisMax(max_y))
        }
        self.analysisPlotRangesObjChanged.emit()

    def _setSampleSldPlotRanges(self):
        self._sample_sld_plot_ranges_obj = {
            'min_x': Plotting1dProxy.aroundX(self._sample_sld_min_x),
            'max_x': Plotting1dProxy.aroundX(self._sample_sld_max_x),
            'min_y': Plotting1dProxy.aroundY(self._sample_sld_min_y),
            'max_y': Plotting1dProxy.aroundY(self._sample_sld_max_y)
        }
        self.sampleSldPlotRangesObjChanged.emit()

    def _setAnalysisSldPlotRanges(self):
        self._analysis_sld_plot_ranges_obj = {
            'min_x': Plotting1dProxy.aroundX(self._analysis_sld_min_x),
            'max_x': Plotting1dProxy.aroundX(self._analysis_sld_max_x),
            'min_y': Plotting1dProxy.aroundY(self._analysis_sld_min_y),
            'max_y': Plotting1dProxy.aroundY(self._analysis_sld_max_y)
        }
        self.analysisSldPlotRangesObjChanged.emit()

    # Static methods

    @staticmethod
    def around(a, decimals=10):
        rounded = np.around(a, decimals=decimals)
        if isinstance(rounded, (int, float)):
            return rounded.item()
        elif isinstance(rounded, np.ndarray):
            return rounded.tolist()

    @staticmethod
    def aroundX(a):
        return Plotting1dProxy.around(a, decimals=10)

    @staticmethod
    def aroundY(a):
        return Plotting1dProxy.around(a, decimals=10)

    @staticmethod
    def aroundHkl(a):
        return Plotting1dProxy.around(a, decimals=3)

    @staticmethod
    def arrayMin(array):
        if array.size:
            return np.amin(array).item()
        return 0

    @staticmethod
    def arrayMax(array):
        if array.size:
            return np.amax(array).item()
        return 1

    @staticmethod
    def arrayMedian(array):
        if array.size:
            return np.median(array).item()
        return 0.5

    @staticmethod
    def arrayToString(array):
        string = np.array2string(array,
                                 separator=',',
                                 precision=2,
                                 suppress_small=True,
                                 max_line_width=99999,
                                 threshold=99999)
        string = string.replace(' ', '')
        return string

    @staticmethod
    def stringToFloatList(string):
        array = np.fromstring(string, separator=',', dtype=float)
        float_list = array.tolist()
        return float_list

    @staticmethod
    def arraysToPoints(xarray, yarray):
        xarray = Plotting1dProxy.aroundX(xarray)
        yarray = Plotting1dProxy.aroundY(yarray)
        return [QPointF(x, y) for x, y in zip(xarray, yarray)]
