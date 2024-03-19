__author__ = 'github.com/arm61'

import json

from PySide2.QtCore import QObject, Signal, Property, Slot

from easyCore import np

#from EasyReflectometry.experiment.model import Model
#from EasyReflectometry.sample import Sample
#from EasyReflectometry.calculators import CalculatorFactory

class SimulationProxy(QObject):

    simulationParametersChanged = Signal()
    simulationParametersAsObjChanged = Signal()
    simulationParametersAsXmlChanged = Signal()

    calculatedDataChanged = Signal()

    backgroundChanged = Signal()
    resolutionChanged = Signal()
    qRangeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self._background_as_obj = self._defaultBackground()
        self._resolution_as_obj = self._defaultResolution()
        self._q_range_as_obj = self._defaultQRange()
        self._experiment_parameters = None
        self._plot_rq4 = False
        self._y_main_axis_title = 'R(q)'

        # # #
        # Connections
        # # #
        self.simulationParametersChanged.connect(self._onSimulationParametersChanged)
        self.backgroundChanged.connect(self._onSimulationParametersChanged)
        self.resolutionChanged.connect(self._onSimulationParametersChanged)
        self.qRangeChanged.connect(self._onSimulationParametersChanged)

        self.calculatedDataChanged.connect(self._onCalculatedDataChanged)
        self.calculatedDataChanged.connect(self._setExperimentalData)
        self.parent._data_proxy.experimentChanged.connect(self._setExperimentalData)

    # # #
    # Defaults
    # # #

    def _defaultBackground(self):
        return {'bkg': 0e0}

    def _defaultResolution(Self):
        return {'res': 0.0}

    def _defaultQRange(self):
        return {'x_min': 0.001, 'x_max': 0.3, 'x_step': 0.002}

    # # #
    # Setters and getters
    # # #

    @Property(bool, notify=simulationParametersChanged)
    def plotRQ4(self):
        return self._plot_rq4

    @Property(str, notify=calculatedDataChanged)
    def yMainAxisTitle(self):
        return self._y_main_axis_title

    @Slot()
    def setPlotRQ4(self):
        self._plot_rq4 = not self._plot_rq4
        if self._plot_rq4:
            self._y_main_axis_title += 'q⁴'
        else:
            self._y_main_axis_title = 'R(q)'
        self.calculatedDataChanged.emit()

    @Property('QVariant', notify=backgroundChanged)
    def backgroundAsObj(self):
        return self._background_as_obj

    @backgroundAsObj.setter
    def backgroundAsObj(self, json_str):
        value = json.loads(json_str)
        if self._background_as_obj == value:
            return None
        self._background_as_obj = value
        self.parent._model_proxy._model.background = float(
            self._background_as_obj['bkg'])
        self.simulationParametersChanged.emit()
        self.parent.sampleChanged.emit()

    @Property('QVariant', notify=resolutionChanged)
    def resolutionAsObj(self):
        return self._resolution_as_obj

    @resolutionAsObj.setter
    def resolutionAsObj(self, json_str):
        value = json.loads(json_str)
        if self._resolution_as_obj == value:
            return
        self._resolution_as_obj = value
        self.parent._model_proxy._model.resolution = float(
            self._resolution_as_obj['res'])
        self.simulationParametersChanged.emit()
        self.parent.sampleChanged.emit()

    @Property('QVariant', notify=qRangeChanged)
    def qRangeAsObj(self):
        return self._q_range_as_obj

    @qRangeAsObj.setter
    def qRangeAsObj(self, json_str):
        value = json.loads(json_str)
        if self._q_range_as_obj == value:
            return
        self._q_range_as_obj = value
        self.simulationParametersChanged.emit()
        self.parent.sampleChanged.emit()

    # # #
    # Actions
    # # #

    def _setExperimentalData(self):
        if len(self.parent._data_proxy._data) > 0:
            x = self.parent._data_proxy._data[self.parent._data_proxy.currentDataIndex].x
            if self._plot_rq4:
                y = self.parent._data_proxy._data[self.parent._data_proxy.currentDataIndex].y * x ** 4
                ye = self.parent._data_proxy._data[self.parent._data_proxy.currentDataIndex].ye * x ** 4
            else: 
                y = self.parent._data_proxy._data[self.parent._data_proxy.currentDataIndex].y
                ye = self.parent._data_proxy._data[self.parent._data_proxy.currentDataIndex].ye
            self.parent._plotting_1d_proxy.setMeasuredData(x, y, ye)
            self._experiment_parameters = self._experimentDataParameters(
                self.parent._data_proxy._data[self.parent._data_proxy.currentDataIndex])
            self.qRangeAsObj = json.dumps(self._experiment_parameters[0])
            self.backgroundAsObj = json.dumps(self._experiment_parameters[1])

            self.parent._data_proxy.experimentDataAsXmlChanged.emit()
            # self.parent._project_proxy.projectInfoAsJson[
            #     'experiments'] = self.parent._data_proxy.experiments[0]['name']
            # self.parent._project_proxy.projectInfoChanged.emit()

    def _onCalculatedDataChanged(self):
        print('>>> _onCalculatedDataChanged')
        self._updateCalculatedData()

    def _onSimulationParametersChanged(self):
        print('>>> _onSimulationParametersChanged')
        self.calculatedDataChanged.emit()

    # # #
    # Calculations
    # # #

    def _updateCalculatedData(self):
        print('>>> _updateCalculatedData')
        # if not self.experimentLoaded:# and not self.experimentSkipped:
        #     return

        #  THIS IS WHERE WE WOULD LOOK UP CURRENT EXP INDEX
        # sim = self.parent._data_proxy._data.experiments[0]

        # elif self.experimentSkipped:
        x_min = float(self._q_range_as_obj['x_min'])
        x_max = float(self._q_range_as_obj['x_max'])
        x_step = float(self._q_range_as_obj['x_step'])
        x = np.arange(x_min, x_max + x_step, x_step)

        if self._plot_rq4:
            self.parent._plotting_1d_proxy.setPureData(x, self.parent._model_proxy.getPureModelReflectometry(x) * x ** 4)
        else:
            self.parent._plotting_1d_proxy.setPureData(x, self.parent._model_proxy.getPureModelReflectometry(x))
        sld_profile = self.parent._model_proxy._pure.interface.sld_profile(self.parent._model_proxy._pure.uid)
        self.parent._plotting_1d_proxy.setSampleSldData(*sld_profile)
        
        to_use = self.parent._model_proxy._model[self.parent._model_proxy.currentModelIndex]
        if self.parent._data_proxy.experimentLoaded:
            exp = self.parent._data_proxy._data.experiments[self.parent._data_proxy.currentDataIndex]
            x = exp.x
            to_use = self.parent._data_proxy._data[self.parent._data_proxy.currentDataIndex].model

        y = self.parent._interface.fit_func(x, to_use.uid)
        if self._plot_rq4:
            y *= (x ** 4)
        sld_profile = self.parent._interface.sld_profile(to_use.uid)

        self.parent._plotting_1d_proxy.setCalculatedData(x, y)
        bkg = np.empty(x.size)
        bkg.fill(to_use.background.raw_value)
        self.parent._plotting_1d_proxy.setBackgroundData(x, bkg)
        scale = np.empty(x.size)
        scale.fill(to_use.scale.raw_value)
        self.parent._plotting_1d_proxy.setScaleData(x, scale)
        self.parent._plotting_1d_proxy.setAnalysisSldData(*sld_profile)

    def resetSimulation(self):
        self._background_as_obj = self._defaultBackground()
        self._resolution_as_obj = self._defaultResolution()
        self._q_range_as_obj = self._defaultQRange()
        self._experiment_parameters = None

    # # #
    # Static methods
    # # #

    @staticmethod
    def _experimentDataParameters(data):
        x_min = data.x[0]
        x_max = data.x[-1]
        x_step = (x_max - x_min) / (len(data.x) - 1)
        bkg = np.min(data.y)
        q_range_parameters = {
            "x_min": x_min,
            "x_max": x_max,
            "x_step": x_step,
        }
        bkg_parameters = {'bkg': bkg}
        return q_range_parameters, bkg_parameters
