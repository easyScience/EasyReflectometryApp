__author__ = 'github.com/arm61'

import os
import datetime
import json

from PySide2.QtCore import QObject, Signal, Property, Slot

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from easyCore import np
from easyApp.Logic.Utils.Utils import generalizePath

from EasyReflectometryApp.Logic.DataStore import DataSet1D
from EasyReflectometry.sample import MaterialCollection
from EasyReflectometry.experiment.models import Models


class ProjectProxy(QObject):
    dummySignal = Signal()
    projectCreatedChanged = Signal()
    projectInfoChanged = Signal()
    htmlExportingFinished = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self._project_created = False
        self._project_info = self._defaultProjectInfo()
        self.project_save_filepath = ""
        self._currentProjectPath = os.path.expanduser('~')

        self._report = ""

    # # #
    # Defaults
    # # #

    def _defaultProjectInfo(self):
        return dict(
            name="Example Project",
            # location=os.path.join(os.path.expanduser("~"), "Example Project"),
            short_description="reflectometry, 1D",
            samples="None",
            experiments="None",
            modified=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))

    # # #
    # Setters and getters
    # # #

    @Property(bool, notify=projectCreatedChanged)
    def projectCreated(self):
        return self._project_created

    @projectCreated.setter
    def projectCreated(self, created: bool):
        if self._project_created == created:
            return
        self._project_created = created
        self.projectCreatedChanged.emit()

    @Property('QVariant', notify=projectInfoChanged)
    def projectInfoAsJson(self):
        return self._project_info

    @projectInfoAsJson.setter
    def projectInfoAsJson(self, json_str):
        self._project_info = json.loads(json_str)
        self.projectInfoChanged.emit()

    @Property(str, notify=projectInfoChanged)
    def projectInfoAsCif(self):
        cif_list = []
        for key, value in self.projectInfoAsJson.items():
            if ' ' in value:
                value = f"'{value}'"
            cif_list.append(f'_{key} {value}')
        cif_str = '\n'.join(cif_list)
        return cif_str

    @Slot(str, str)
    def editProjectInfo(self, key, value):
        if key == 'location':
            self.currentProjectPath = value
            return
        else:
            if self._project_info[key] == value:
                return
            self._project_info[key] = value
        self.projectInfoChanged.emit()

    @Property(str, notify=projectInfoChanged)
    def currentProjectPath(self):
        return self._currentProjectPath

    @currentProjectPath.setter
    def currentProjectPath(self, new_path):
        if self._currentProjectPath == new_path:
            return
        self._currentProjectPath = new_path
        self.projectInfoChanged.emit()

    # # #
    # Slot
    # # #

    @Slot()
    def createProject(self):
        projectPath = self.currentProjectPath
        mainCif = os.path.join(projectPath, 'project.cif')
        samplesPath = os.path.join(projectPath, 'samples')
        experimentsPath = os.path.join(projectPath, 'experiments')
        calculationsPath = os.path.join(projectPath, 'calculations')
        if not os.path.exists(projectPath):
            os.makedirs(projectPath)
            os.makedirs(samplesPath)
            os.makedirs(experimentsPath)
            os.makedirs(calculationsPath)
            with open(mainCif, 'w') as file:
                file.write(self.projectInfoAsCif)
        else:
            print(f"ERROR: Directory {projectPath} already exists")

    @Slot()
    def saveProject(self):
        self._saveProject()
        self.parent._state_proxy.stateChanged.emit(False)

    @Slot(str)
    def loadProjectAs(self, filepath):
        self._loadProjectAs(filepath)
        self.parent._state_proxy.stateChanged.emit(False)

    @Slot()
    def loadProject(self):
        self._loadProject()
        self.parent._state_proxy.stateChanged.emit(False)

    @Property(str, notify=dummySignal)
    def projectFilePath(self):
        return self.project_save_filepath

    def _saveProject(self):
        """
        """
        projectPath = self.currentProjectPath
        project_save_filepath = os.path.join(projectPath, 'project.json')
        materials_in_model = []
        for i in self.parent._model_proxy._model:
            for j in i.sample:
                for k in j.layers:
                    materials_in_model.append(k.material)
        materials_not_in_model = []
        for i in self.parent._material_proxy._materials:
            if i not in materials_in_model:
                materials_not_in_model.append(i)
        descr = {
            'model':
                self.parent._model_proxy._model.as_dict(skip=['interface']),
            'materials_not_in_model':
                MaterialCollection(*materials_not_in_model).as_dict(skip=['interface'])
        }

        if self.parent._data_proxy._data.experiments:
            descr['experiments'] = []
            descr['experiments_models'] = []
            descr['experiments_names'] = []
            for i in self.parent._data_proxy._data.experiments:
                if self.parent._data_proxy._data.experiments[0].xe is not None:
                    descr['experiments'].append([
                        i.x, i.y, i.ye, i.xe
                    ])
                else:
                    descr['experiments'].append([i.x, i.y, i.ye])
                descr['experiments_models'].append(i.model.name)
                descr['experiments_names'].append(i.name)

        descr['experiment_skipped'] = self.parent._data_proxy._experiment_skipped
        descr['project_info'] = self._project_info

        descr['interface'] = [self.parent._interface.current_interface_name]

        descr['colors'] = self.parent._model_proxy._colors

        descr['minimizer'] = {
            'engine': self.parent._fitter_proxy.eFitter.easy_f.current_engine.name,
            'method': self.parent._minimizer_proxy._current_minimizer_method_name
        }

        content_json = json.dumps(descr, indent=4, default=self.default)
        path = generalizePath(project_save_filepath)
        self.createFile(path, content_json)

    def default(self, obj):
        if type(obj).__module__ == np.__name__:
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj.item()
        raise TypeError('Unknown type:', type(obj))

    def _loadProjectAs(self, filepath):
        """
        """
        self.project_load_filepath = filepath
        print("LoadProjectAs " + filepath)
        self.loadProject()

    def _loadProject(self):
        """
        """
        path = generalizePath(self.project_load_filepath)
        if not os.path.isfile(path):
            print("Failed to find project: '{0}'".format(path))
            return
        self.currentProjectPath = os.path.split(path)[0]
        with open(path, 'r') as xml_file:
            descr: dict = json.load(xml_file)

        interface_name = descr.get('interface', None)
        for i, inter in enumerate(interface_name):
            if inter is not None:
                old_interface_name = self.parent._interface.current_interface_name
                if old_interface_name != inter:
                    self.parent._interface.switch(inter)

        self.parent._model_proxy._colors = descr['colors']
        self.parent._model_proxy._model = Models.from_dict(descr['model'])
        self.parent._material_proxy._materials = MaterialCollection.from_pars()
        for model in self.parent._model_proxy._model:
            for structure in model.sample:
                for layer in structure.layers:
                    self.parent._material_proxy._materials.append(layer.material)
            model.interface = self.parent._interface
        mats = descr['materials_not_in_model']
        if mats['data']:
            for material in MaterialCollection.from_dict(mats):
                self.parent._material_proxy._materials.append(material)

        # experiment
        if 'experiments' in descr:
            #self.parent._data_proxy.experimentLoaded = True
            for i, e in enumerate(descr['experiments']):
                x = np.array(e[0])
                y = np.array(e[1])
                ye = np.array(e[2])
                if len(e) == 4:
                    xe = np.array(e[3])
                else:
                    xe = np.zeros_like(ye)
                name = descr['experiments_names'][i]
                model_name = descr['experiments_models'][i]
                model = None
                for i in self.parent._model_proxy._model:
                    if i.name == model_name:
                        model = i
                        break
                ds = DataSet1D(name=name, x=x, y=y, ye=ye, xe=xe,
                               model=model,
                               x_label='q (1/angstrom)',
                               y_label='Reflectivity')
                self.parent._data_proxy._data.append(ds)

            self.parent._data_proxy.experimentLoaded = True
            self.parent._data_proxy.experimentSkipped = False
            self.parent._data_proxy.experimentChanged.emit()
            self.parent._parameter_proxy._onParametersChanged()

        else:
            # delete existing experiment
            try:
                for index, data in enumerate(self.parent.data):
                    data.removeExperiment(index)
            except TypeError:
                pass
            self.parent._data_proxy.experimentLoaded = False
            if descr['experiment_skipped']:
                self.parent._data_proxy.experimentSkipped = True
                self.parent._data_proxy.experimentSkippedChanged.emit()
            else:
                self.parent._data_proxy.experimentSkipped = False

        # project info
        self.projectInfoAsJson = json.dumps(descr['project_info'])
        self.parent.sampleChanged.emit()

        new_minimizer_settings = descr.get('minimizer', None)
        if new_minimizer_settings is not None:
            new_engine = new_minimizer_settings['engine']
            new_method = new_minimizer_settings['method']
            new_engine_index = self.parent._minimizer_proxy.minimizerNames.index(new_engine)
            self.currentMinimizerIndex = new_engine_index
            try:
                new_method_index = self.parent._minimizer_proxy.minimizerMethodNames.index(new_method)
            except ValueError:
                new_method_index = self.parent._minimizer_proxy.minimizerMethodNames[0]
            self.currentMinimizerMethodIndex = new_method_index

        self.parent._undoredo_proxy.resetUndoRedoStack()

        self.projectCreated = True

    @staticmethod
    def createFile(path, content):
        if os.path.exists(path):
            print(f'File already exists {path}. Overwriting...')
            os.unlink(path)
        try:
            message = f'create file {path}'
            with open(path, "w") as file:
                file.write(content)
        except Exception as exception:
            print(message, exception)

    @Slot(str)
    def setReport(self, report):
        """
        Keep the QML generated HTML report for saving
        """
        self._report = report

    @Slot(str)
    def saveReport(self, filepath):
        """
        Save the generated report to the specified file
        Currently only html
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self._report)
            success = True
        except IOError:
            success = False
        self.htmlExportingFinished.emit(success, filepath)

    def resetProject(self):
        self._project_created = False
        self._project_info = self._defaultProjectInfo()
        self.parent._model_proxy._setModelsAsXml()
        self.projectInfoChanged.emit()

    @Slot(str, float, float)
    def savePlot(self, filename: str, figsize_x: float, figsize_y: float):
        fig = self.make_plot(filename, figsize_x, figsize_y)
        fig.savefig(filename, dpi=600)
        plt.close()
        self.htmlExportingFinished.emit(True, filename)

    @Slot(str, float, float)
    def showPlot(self, filename: str, figsize_x: float, figsize_y: float):
        fig = self.make_plot(filename, figsize_x, figsize_y)
        plt.show()

    def make_plot(self, filename: str, figsize_x: float, figsize_y: float):
        fig = plt.figure(figsize=(figsize_x / 2.54, figsize_y / 2.54), constrained_layout=True)
        gs = gridspec.GridSpec(1, 2, figure=fig)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax1.set_xlabel('$q$/Å$^{-1}$')
        if self.parent._simulation_proxy._plot_rq4:
            ax1.set_ylabel('$R(q)q^4$/Å$^{-4}$')
        else:
            ax1.set_ylabel('$R(q)$')
        ax2.set_xlabel('$z$/Å')
        ax2.set_ylabel('SLD($z$)/$10^{-6}$Å$^{-2}$')
        data = self.parent._data_proxy._data
        if len(data) != 0:
            for i, d in enumerate(data):
                model_index = self.parent._model_proxy._model.index(d.model)
                color = self.parent._model_proxy._colors[model_index]
                y = self.parent._interface.fit_func(d.x, d.model.uid)
                if self.parent._simulation_proxy._plot_rq4:
                    ax1.errorbar(d.x, (d.y * d.x ** 4) * 10 ** i, (d.ye * d.x ** 4) * 10 ** i, marker='', ls='',
                                 color=color, alpha=0.5)
                    ax1.plot(d.x, (y * d.x ** 4) * 10 ** i, ls='-', color=color, zorder=10, label=d.name)
                else:
                    ax1.errorbar(d.x, d.y * 10 ** i, d.ye * 10 ** i, marker='', ls='', color=color, alpha=0.5)
                    ax1.plot(d.x, y * 10 ** i, ls='-', color=color, zorder=10, label=d.name)
                sld_profile = self.parent._interface.sld_profile(d.model.uid)
                ax2.plot(sld_profile[0], sld_profile[1] + 10 * i, color=color, ls='-')
            ax1.set_yscale('log')
        else:
            x_min = float(self.parent._simulation_proxy._q_range_as_obj['x_min'])
            x_max = float(self.parent._simulation_proxy._q_range_as_obj['x_max'])
            x_step = float(self.parent._simulation_proxy._q_range_as_obj['x_step'])
            x = np.arange(x_min, x_max + x_step, x_step)
            model = self.parent._model_proxy._model
            for i, m in enumerate(model):
                color = self.parent._model_proxy._colors[i]
                y = self.parent._interface.fit_func(x, m.uid)
                if self.parent._simulation_proxy._plot_rq4:
                    ax1.plot(x, (y * d.x ** 4) * 10 ** i, ls='-', color=color, zorder=10, label=m.name)
                else:
                    ax1.plot(x, y * 10 ** i, ls='-', color=color, zorder=10, label=m.name)
                sld_profile = self.parent._interface.sld_profile(m.uid)
                ax2.plot(sld_profile[0], sld_profile[1] + 10 * i, color=color, ls='-')
            ax1.set_yscale('log')
        ax1.legend()
        return fig