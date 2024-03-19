__author__ = 'github.com/arm61'

from PySide2.QtCore import QObject, Signal, Property

from EasyReflectometry.calculators import CalculatorFactory

from .Proxies.Calculator import CalculatorProxy
from .Proxies.Data import DataProxy
from .Proxies.Fitter import FitterProxy
from .Proxies.Material import MaterialProxy
from .Proxies.Minimizer import MinimizerProxy
from .Proxies.Project import ProjectProxy
from .Proxies.Model import ModelProxy
from .Proxies.Parameter import ParameterProxy
from .Proxies.Plotting1d import Plotting1dProxy
from .Proxies.Simulation import SimulationProxy
from .Proxies.State import StateProxy
from .Proxies.UndoRedo import UndoRedoProxy


class PyQmlProxy(QObject):
    # SIGNALS
    dummySignal = Signal()
    sampleChanged = Signal()
    layersSelectionChanged = Signal()
    layersChanged = Signal()
    itemsChanged = Signal()
    layersMaterialsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._interface = CalculatorFactory()

        # Proxies
        self._project_proxy = ProjectProxy(self)
        self._material_proxy = MaterialProxy(self)
        self._model_proxy = ModelProxy(self)
        self._data_proxy = DataProxy(self)
        self._simulation_proxy = SimulationProxy(self)
        self._calculator_proxy = CalculatorProxy(self)
        self._parameter_proxy = ParameterProxy(self)
        self._fitter_proxy = FitterProxy(self)
        self._minimizer_proxy = MinimizerProxy(self)
        self._plotting_1d_proxy = Plotting1dProxy(self)
        self._state_proxy = StateProxy(self)
        self._undoredo_proxy = UndoRedoProxy(self)

        # Sample Connections
        self.layersMaterialsChanged.connect(self._model_proxy._onLayersChanged)
        self.layersSelectionChanged.connect(self._model_proxy._onLayersChanged)


        self.layersChanged.connect(self._model_proxy._onLayersChanged)
        self.layersChanged.connect(self._parameter_proxy._onParametersChanged)
        self.layersChanged.connect(self._simulation_proxy._onCalculatedDataChanged)


        self._material_proxy.materialsChanged.connect(self._parameter_proxy._onParametersChanged)
        self._model_proxy.itemsNameChanged.connect(self._parameter_proxy._onParametersChanged)
        self.itemsChanged.connect(self._model_proxy._onItemsChanged)

        self._material_proxy._setMaterialsAsXml()
        self._model_proxy._onLayersChanged()
        self._model_proxy._onItemsChanged()
        self._simulation_proxy._onSimulationParametersChanged()

        self.sampleChanged.connect(self._material_proxy._setMaterialsAsXml)
        self.sampleChanged.connect(self._model_proxy._onLayersChanged)
        self.sampleChanged.connect(self._model_proxy._onItemsChanged)

        self.sampleChanged.connect(self._parameter_proxy._onParametersChanged)
        self.layersChanged.connect(self._fitter_proxy._onSampleChanged)
        self.sampleChanged.connect(self._simulation_proxy._onCalculatedDataChanged) # calls _updateCalculatedData
        self.sampleChanged.connect(self._undoredo_proxy.undoRedoChanged)

        # Screen recorder
        recorder = None
        try:
            from EasyReflectometryApp.Logic.ScreenRecorder import ScreenRecorder
            recorder = ScreenRecorder()
        except (ImportError, ModuleNotFoundError):
            print('Screen recording disabled')
        self._screen_recorder = recorder

    @Property('QVariant', notify=dummySignal)
    def state(self):
        return self._state_proxy

    @Property('QVariant', notify=dummySignal)
    def project(self):
        return self._project_proxy

    @Property('QVariant', notify=dummySignal)
    def simulation(self):
        return self._simulation_proxy

    @Property('QVariant', notify=dummySignal)
    def material(self):
        return self._material_proxy

    @Property('QVariant', notify=dummySignal)
    def model(self):
        return self._model_proxy

    @Property('QVariant', notify=dummySignal)
    def calculator(self):
        return self._calculator_proxy

    @Property('QVariant', notify=dummySignal)
    def parameter(self):
        return self._parameter_proxy

    @Property('QVariant', notify=dummySignal)
    def data(self):
        return self._data_proxy

    @Property('QVariant', notify=dummySignal)
    def fitter(self):
        return self._fitter_proxy

    @Property('QVariant', notify=dummySignal)
    def fitting(self):
        return self._fitter_proxy

    @Property('QVariant', notify=dummySignal)
    def minimizer(self):
        return self._minimizer_proxy

    @Property('QVariant', notify=dummySignal)
    def plotting1d(self):
        return self._plotting_1d_proxy

    @Property('QVariant', notify=dummySignal)
    def undoredo(self):
        return self._undoredo_proxy

    # # #
    # Screen recorder
    # # #

    @Property('QVariant', notify=dummySignal)
    def screenRecorder(self):
        return self._screen_recorder
