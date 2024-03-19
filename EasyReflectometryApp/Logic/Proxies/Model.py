__author__ = 'github.com/arm61'


from PySide2.QtCore import QObject, Signal, Property, Slot
from typing import Any

from easyCore import np, borg
from easyCore.Utils.io.xml import XMLSerializer
from easyCore.Utils.UndoRedo import property_stack_deco

from EasyReflectometry.sample import Layer
from EasyReflectometry.sample import Multilayer 
from EasyReflectometry.sample import RepeatingMultilayer
from EasyReflectometry.sample import SurfactantLayer
from EasyReflectometry.sample import Sample
from EasyReflectometry.experiment.model import Model
from EasyReflectometry.experiment.models import Models
from EasyReflectometry.calculators import CalculatorFactory

ITEM_LOOKUP = {'Multi-layer': Multilayer, 'Repeating Multi-layer': RepeatingMultilayer, 'Surfactant Layer': SurfactantLayer}
COLORS =["#0173B2", "#DE8F05", "#029E73", "#D55E00", "#CC78BC", "#CA9161", "#FBAFE4", "#949494", "#ECE133", "#56B4E9"]


class ModelProxy(QObject):

    modelChanged = Signal()
    modelsNameChanged = Signal()

    itemsNameChanged = Signal()
    itemsIndexChanged = Signal()
    layersIndexChanged = Signal()
    
    modelsAsXmlChanged = Signal()
    itemsAsXmlChanged = Signal()
    layersAsXmlChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self._models_as_xml = ""
        self._items_as_xml = ""
        self._layers_as_xml = ""
        self._structure = self._defaultStructure()
        self._model = Models.from_pars(self._defaultModel(structure=self._structure, interface=parent._interface))
        self._colors = [COLORS[0]]

        self._current_layers_index = 0
        self._current_items_index = 0
        self._current_model_index = 0
        self._pure_interface = CalculatorFactory()

    # # #
    # Defaults
    # # #

    def _defaultStructure(self) -> Sample:
        layers = [
            Layer.from_pars(self.parent._material_proxy._materials[0],
                            0.0,
                            0.0,
                            name='Vacuum Layer'),
            Layer.from_pars(self.parent._material_proxy._materials[1],
                            100.0,
                            3.0,
                            name='Multi-layer'),
            Layer.from_pars(self.parent._material_proxy._materials[2],
                            0.0,
                            1.2,
                            name='Si Layer'),
        ]
        items = [
            Multilayer.from_pars(layers[0], name='Superphase'),
            Multilayer.from_pars(layers[1], name='Multi-layer'),
            Multilayer.from_pars(layers[2], name='Subphase')
        ]
        structure =  Sample.from_pars(*items) 
        structure[0].layers[0].thickness.enabled = False
        structure[0].layers[0].roughness.enabled = False
        structure[-1].layers[-1].thickness.enabled = False
        return structure

    def _defaultModel(self, structure: Sample, interface=None, name="Air-D2O-Si") -> Model:
        return Model.from_pars(structure, 1, 0, 0, interface=interface, name=name)

    # # #
    # Setters and getters
    # # #


    @property
    def modelsAsObj(self):
        _models_as_obj = []
        for i, m in enumerate(self._model):
            dictionary = {'name': m.name}
            dictionary['color'] = self._colors[i]
            _models_as_obj.append(dictionary)
        return _models_as_obj

    @Property(str, notify=modelsAsXmlChanged)
    def modelColor(self):
        return self._colors[self.currentModelIndex]

    @Property(str, notify=modelsAsXmlChanged)
    def modelsAsXml(self):
        return self._models_as_xml

    def _setModelsAsXml(self):
        print('>>> _setModelsAsXml')
        self._models_as_xml = XMLSerializer().encode({"item":self.modelsAsObj}, data_only=True)
        self.modelsAsXmlChanged.emit()

    @Property(list, notify=modelsNameChanged)
    def modelList(self):
        return [i.name for i in self._model]

    @Property(list, notify=modelsNameChanged)
    def modelListAll(self):
        return ['Quick filter', 'Materials'] + [i.name for i in self._model]

    @modelList.setter
    @property_stack_deco
    def modelList(self):
        self.parent.sampleChanged.emit()

    @Property(list, notify=itemsNameChanged)
    def itemsNamesConstrain(self):
        return [i['name'] for i in self.itemsAsObj[1:] if type(i) != SurfactantLayer]

    @property
    def itemsAsObj(self):
        _items_as_obj = []
        if self.currentModelIndex >= len(self._model):
            return []
        for i in self._model[self.currentModelIndex].sample:
            dictionary = {'name': i.name}
#            dictionary['type'] = i.type
            _items_as_obj.append(dictionary)
        return _items_as_obj

    @Property(str, notify=itemsAsXmlChanged)
    def itemsAsXml(self):
        return self._items_as_xml

    def _setItemsAsXml(self):
        self._items_as_xml = XMLSerializer().encode({"item":self.itemsAsObj}, data_only=True)
        self.itemsAsXmlChanged.emit()

    @property
    def layersAsObj(self):
        _layers_as_obj = []
        for i in self._model[self.currentModelIndex].sample:
            dictionary = {'layers': [j.as_dict(skip=['interface', 'min', 'max', 'error', 'fixed', 'description', 'url']) for j in i.layers]}
            if 'repetitions' in dictionary.keys():
                dictionary['repetitions'] = i.repetitions.as_dict(skip=['interface', 'min', 'max', 'error', 'fixed', 'description', 'url'])
            _layers_as_obj.append(dictionary)
        if len(self._model[self.currentModelIndex].sample) > 0:
            _layers_as_obj[0]['layers'][0]['thickness']['value'] = np.nan
            _layers_as_obj[0]['layers'][0]['roughness']['value'] = np.nan
            _layers_as_obj[-1]['layers'][-1]['thickness']['value'] = np.nan
        return _layers_as_obj

    @Property(str, notify=layersAsXmlChanged)
    def layersAsXml(self):
        return self._layers_as_xml

    def _setLayersAsXml(self):
        self._layers_as_xml = XMLSerializer().encode({"item":self.layersAsObj}, data_only=True)
        self.layersAsXmlChanged.emit()

    @Property(int, notify=itemsIndexChanged)
    def currentItemsIndex(self):
        return self._current_items_index

    @currentItemsIndex.setter
    def currentItemsIndex(self, new_index: int):
        if self._current_items_index == new_index or new_index == -1:
            return
        self._current_items_index = new_index
        self.itemsNameChanged.emit()
        self.parent.layersSelectionChanged.emit()

    @Property(int, notify=modelChanged)
    def currentItemsRepetitions(self):
        if self.currentItemsIndex >= len(self._model[self.currentModelIndex].sample):
            return 1
        if type(self._model[self.currentModelIndex].sample[
                self.currentItemsIndex]) != RepeatingMultilayer:
            return 1
        return self._model[self.currentModelIndex].sample[self.currentItemsIndex].repetitions.raw_value

    @currentItemsRepetitions.setter
    def currentItemsRepetitions(self, new_repetitions: int):
        if type(self._model[self.currentModelIndex].sample[
                self.currentItemsIndex]) != RepeatingMultilayer:
            return
        if self._model[self.currentModelIndex].sample[
                self.
                currentItemsIndex].repetitions.raw_value == new_repetitions or new_repetitions == -1:
            return
        self._model[self.currentModelIndex].sample[self.currentItemsIndex].repetitions = new_repetitions
        self.parent.layersChanged.emit()

    @Property(str, notify=modelChanged)
    def currentItemsType(self):
        # sometimes in the process of removing an item, the model is not yet updated
        if self.currentItemsIndex >= len(self._model[self.currentModelIndex].sample):
            return ''
        return type(self._model[self.currentModelIndex].sample[self.currentItemsIndex])

    @currentItemsType.setter
    def currentItemsType(self, new_type: Any):
        if type(self._model[self.currentModelIndex].sample[self.currentItemsIndex]) == new_type or new_type == -1:
            return
        current_layers = self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers
        if type(self._model[self.currentModelIndex].sample[self.currentItemsIndex]) == SurfactantLayer:
            current_layers = Layer.from_pars(self.parent._material_proxy._materials[0], 10, 3)
        target_position = self.currentItemsIndex
        self._model[self.currentModelIndex].remove_item(self.currentItemsIndex)
        if new_type == Multilayer:
            new_instance = Multilayer.from_pars(layers=current_layers)
#            self._model[self.currentModelIndex].add_item(ITEM_LOOKUP[new_type].from_pars(current_layers,
#                                                             new_type))
        elif new_type == RepeatingMultilayer:
            new_instance = RepeatingMultilayer.from_pars(
                layers=current_layers,
                repetitions=1
            )
#            self._model[self.currentModelIndex].add_item(ITEM_LOOKUP[new_type].from_pars(current_layers, 1,
#                                                             new_type))
        elif new_type == SurfactantLayer:
            new_instance = SurfactantLayer.from_pars(
                tail_layer_molecular_formula='C32D64',
                tail_layer_thickness=16,
                tail_layer_solvent=self.parent._material_proxy._materials[0],
                tail_layer_solvent_fraction=0.0,
                tail_layer_area_per_molecule=48.0,
                tail_layer_roughness=3.0,
                head_layer_molecular_formula='C10H18NO8P',
                head_layer_thickness=10,
                head_layer_solvent=self.parent._material_proxy._materials[0],
                head_layer_solvent_fraction=0.2,
                head_layer_area_per_molecule=48.0,
                head_layer_roughness=3.0,                
                )
        else:
            raise ValueError(f"Unknown type {new_type}")
        self._model[self.currentModelIndex].add_item(new_instance)

        self.parent._parameter_proxy._setParametersAsObj()
        if target_position != len(self._model[self.currentModelIndex].sample) - 1:
            new_items_list = []
            self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
            self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
            self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
            for i, item in enumerate(self._model[self.currentModelIndex].sample):
                if i == target_position:
                    new_items_list.append(
                        self._model[self.currentModelIndex].sample[len(self._model[self.currentModelIndex].sample) - 1])
                elif i == len(self._model[self.currentModelIndex].sample) - 1:
                    new_items_list.append(self._model[self.currentModelIndex].sample[target_position])
                else:
                    new_items_list.append(item)
            while len(self._model[self.currentModelIndex].sample) != 0:
                self._model[self.currentModelIndex].remove_item(0)
            for i in range(len(new_items_list)):
                self._model[self.currentModelIndex].add_item(new_items_list[i])
            borg.stack.enabled = True
            self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
            self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
            self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
        self.itemsNameChanged.emit()
        self.parent.layersChanged.emit()
        self.parent.itemsChanged.emit()

    @Property(int, notify=layersIndexChanged)
    def currentLayersIndex(self):
        if self._current_layers_index + 1 > len(self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers):
            self._current_layers_index = 0
        return self._current_layers_index

    @currentLayersIndex.setter
    def currentLayersIndex(self, new_index: int):
        if self._current_layers_index == new_index or new_index == -1:
            return
        self._current_layers_index = new_index

    @Property(bool, notify=modelChanged)
    def constrainApm(self):
        if hasattr(self._model[self.currentModelIndex].sample[self.currentItemsIndex], 'constrain_apm'):
            return self._model[self.currentModelIndex].sample[self.currentItemsIndex].constrain_apm
        else:
            return

    @constrainApm.setter
    def constrainApm(self, x: bool):
        if self._model[self.currentModelIndex].sample[self.currentItemsIndex].constrain_apm == x:
            return 
        self._model[self.currentModelIndex].sample[self.currentItemsIndex].constrain_apm = x
        self.parent.layersChanged.emit()

    @Property(bool, notify=modelChanged)
    def conformalRoughness(self):
        if hasattr(self._model[self.currentModelIndex].sample[self.currentItemsIndex], 'conformal_roughness'):
            return self._model[self.currentModelIndex].sample[self.currentItemsIndex].conformal_roughness
        else:
            return

    @constrainApm.setter
    def conformalRoughness(self, x: bool):
        if self._model[self.currentModelIndex].sample[self.currentItemsIndex].conformal_roughness == x:
            return 
        self._model[self.currentModelIndex].sample[self.currentItemsIndex].conformal_roughness = x
        self.parent.layersChanged.emit()

    @Property(int, notify=modelChanged)
    def currentModelIndex(self):
        return self._current_model_index

    @currentModelIndex.setter
    def currentModelIndex(self, new_index: int):
        print('>>> currentModelIndex: ', new_index)
        if self._current_model_index == new_index or new_index == -1:
            return
        print('>>> currentModelIndex new_index: ', new_index)
        if new_index >= len(self._model):
            return
        self._current_model_index = new_index
        self._onItemsChanged()
        self._onLayersChanged()
        self.modelsNameChanged.emit()

    # # #
    # Actions
    # # #

    def _onItemsChanged(self):
        print('>>> _onItemsChanged')
        if self.currentModelIndex >= len(self._model):
            return
        for i in self._model[self.currentModelIndex].sample:
            for j in i.layers:
                if type(i) == SurfactantLayer:
                    j.name = j.material.name
                else:
                    j.name = j.material.name + ' Layer'
        self._setItemsAsXml()
        self._setModelsAsXml()

    def _onLayersChanged(self):
        if self.currentModelIndex >= len(self._model):
            return
        for i in self._model[self.currentModelIndex].sample:
            for j in i.layers:
                if type(i) == SurfactantLayer:
                    j.name = j.material.name
                else:
                    j.name = j.material.name + ' Layer'
        self._setLayersAsXml()
        structure_dict = self._model[self.currentModelIndex].sample.as_dict()
        self._pure = Model.from_pars(Sample.from_dict(structure_dict), 1, 0, 0, interface=self._pure_interface)

    # # #
    # Slots
    # # #

    # # Models

    @Slot()
    def addNewModels(self):
        self._model.add_model(
            self._defaultModel(self._defaultStructure(),
                               interface=self.parent._interface, 
                               name="Air-D2O-Si"))
        try:
            self._colors.append(list(set(COLORS).difference(self._colors))[0])
        except IndexError:
            n = len(self._colors) - int(len(self._colors) / 10) * 10
            self._colors.append(self._colors[n])
        self.modelsNameChanged.emit()
        self.parent.sampleChanged.emit()

    @Slot()
    def duplicateSelectedModels(self):
        structure_dict = self._model[self.currentModelIndex].sample.as_dict()
        new_structure = Sample.from_dict(structure_dict)
        for i, ml in enumerate(new_structure):
            if isinstance(ml, SurfactantLayer):
                for j, layer in enumerate(ml.layers):
                    layer.solvent = self._model[self.currentModelIndex].sample[i].layers[j].solvent
            elif isinstance(ml, Multilayer) or isinstance(ml, RepeatingMultilayer):
                for j, layer in enumerate(ml.layers):    
                    layer.assign_material(self._model[self.currentModelIndex].sample[i].layers[j].material)
        self._model.append(
            self._defaultModel(new_structure,
                               interface=self.parent._interface,
                               name=f"{self._model[self.currentModelIndex].name} Duplicate"))
        try:
            self._colors.append(list(set(COLORS).difference(self._colors))[0])
        except IndexError:
            n = len(self._colors) - int(len(self._colors) / 10) * 10
            self._colors.append(self._colors[n])
        self.modelsNameChanged.emit()
        self.parent.sampleChanged.emit()

    @Slot()
    def moveSelectedModelsUp(self):
        """
        Move the currently selected model up.
        """
        i = self.currentModelIndex
        self._model.insert(i-1, self._model.pop(i))
        self._colors.insert(i-1, self._colors.pop(i))
        self.modelsNameChanged.emit()
        self.parent.sampleChanged.emit()

    @Slot()
    def moveSelectedModelsDown(self):
        """
        Move the currently selected model down.
        """
        i = self.currentModelIndex
        self._model.insert(i+1, self._model.pop(i))
        self._colors.insert(i+1, self._colors.pop(i))
        self.modelsNameChanged.emit()
        self.parent.sampleChanged.emit()

    @Slot(str)
    def removeModels(self, i: str):
        """
        Remove an item from the items list.
        :param i: Index of the item
        :type i: str
        """
        self._model.remove_model(int(i))
        del self._colors[int(i)]
        self.itemsNameChanged.emit() # firing _onParametersChanged

    @Slot(str)
    def setCurrentModelsName(self, name):
        """
        Sets the name of the currently selected model.
        :param sld: New name
        :type sld: str
        """
        print('>>> setCurrentModelsName: ', name)
        if self._model[self.currentModelIndex].name == name:
            return
        self._model[self.currentModelIndex].name = name
        self.modelsNameChanged.emit()
        self.parent.sampleChanged.emit()

    @Property(str, notify=modelsNameChanged)
    def currentModelsName(self):
        if self.currentModelIndex >= len(self._model):
            return ''
        return self._model[self.currentModelIndex].name


    # # Items

    @Slot()
    def addNewItems(self):
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
        try:
            self._model[self.currentModelIndex].add_item(
                Multilayer.from_pars(
                    Layer.from_pars(self.parent._material_proxy._materials[0], 10.,
                                    1.2),
                    f'Multi-layer {len(self._model[self.currentModelIndex].sample)+1}'))
        except IndexError:
            self.parent._material_proxy.addNewMaterials()
            self._model[self.currentModelIndex].add_item(
                Multilayer.from_pars(
                    Layer.from_pars(self.parent._material_proxy._materials[0], 10.,
                                    1.2),
                    f'Multi-layer {len(self._model[self.currentModelIndex].sample)+1}'))
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
        self.parent.layersChanged.emit()
        self.parent.itemsChanged.emit()

    @Slot()
    def duplicateSelectedItems(self):
        # This is a fix until deepcopy is worked out
        # Manual duplication instead of creating a copy
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
        to_dup = self._model[self.currentModelIndex].sample[self.currentItemsIndex]
        if isinstance(to_dup, RepeatingMultilayer):
            to_dup_layers = []
            for i in to_dup.layers:
                to_dup_layers.append(
                    Layer.from_pars(i.material,
                                    i.thickness.raw_value,
                                    i.roughness.raw_value,
                                    name=i.name,
                                    interface=self.parent._interface))
            dup_item = RepeatingMultilayer.from_pars(*to_dup_layers, 
                                                     to_dup.repetitions.raw_value,
                                                     name=to_dup.name)
        elif isinstance(to_dup, SurfactantLayer):
            dup_item = SurfactantLayer.from_dict(to_dup.as_dict())
            for i, layer in enumerate(dup_item.layers):
                layer.solvent = to_dup.layers[i].solvent
        elif isinstance(to_dup, Multilayer):
            to_dup_layers = []
            for i in to_dup.layers:
                to_dup_layers.append(
                    Layer.from_pars(i.material,
                                    i.thickness.raw_value,
                                    i.roughness.raw_value,
                                    name=i.name,
                                    interface=self.parent._interface))
            dup_item = Multilayer.from_pars(*to_dup_layers, name=to_dup.name)
        self._model[self.currentModelIndex].add_item(dup_item)
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
        self.parent.layersChanged.emit()
        self.parent.itemsChanged.emit()

    @Slot()
    def moveSelectedItemsUp(self):
        # if borg.stack.enabled:
        #    borg.stack.beginMacro('Loaded default item')
        borg.stack.enabled = False
        # This convoluted approach is necessary as currently the BaseCollection
        # does not allow insertion or popping. In future, this could be
        # replaced with the approach for moving items around
        old_index = self.currentItemsIndex
        new_items_list = []
        if old_index != 0:
            self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
            self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
            self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
            for i, item in enumerate(self._model[self.currentModelIndex].sample):
                if i == old_index - 1:
                    new_items_list.append(self._model[self.currentModelIndex].sample[old_index])
                elif i == old_index:
                    new_items_list.append(self._model[self.currentModelIndex].sample[old_index - 1])
                else:
                    new_items_list.append(item)
            while len(self._model[self.currentModelIndex].sample) != 0:
                self._model[self.currentModelIndex].remove_item(0)
            for i in range(len(new_items_list)):
                self._model[self.currentModelIndex].add_item(new_items_list[i])
            borg.stack.enabled = True
            self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
            self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
            self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
            self.parent.layersChanged.emit()
            self.parent.itemsChanged.emit()

    @Slot()
    def moveSelectedItemsDown(self):
        # This convoluted approach is necessary as currently the BaseCollection
        # does not allow insertion or popping. In future, this could be
        # replaced with the approach for moving items around
        old_index = self.currentItemsIndex
        new_items_list = []
        if old_index != len(self._model[self.currentModelIndex].sample):
            borg.stack.enabled = False
            self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
            self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
            self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
            for i, item in enumerate(self._model[self.currentModelIndex].sample):
                if i == old_index:
                    new_items_list.append(self._model[self.currentModelIndex].sample[old_index + 1])
                elif i == old_index + 1:
                    new_items_list.append(self._model[self.currentModelIndex].sample[old_index])
                else:
                    new_items_list.append(item)
            while len(self._model[self.currentModelIndex].sample) != 0:
                self._model[self.currentModelIndex].remove_item(0)
            for i in range(len(new_items_list)):
                self._model[self.currentModelIndex].add_item(new_items_list[i])
            borg.stack.enabled = True
            self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
            self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
            self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
            self.parent.layersChanged.emit()
            self.parent.itemsChanged.emit()

    @Slot(str)
    def removeItems(self, i: str):
        """
        Remove an item from the items list.

        :param i: Index of the item
        :type i: str
        """
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
        self._model[self.currentModelIndex].remove_item(int(i))
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
        self.parent.layersChanged.emit()
        self.parent.itemsChanged.emit()

    @Slot(str)
    def setCurrentItemsName(self, name):
        """
        Sets the name of the currently selected item.

        :param sld: New name
        :type sld: str
        """
        if self._model[self.currentModelIndex].sample[self.currentItemsIndex].name == name:
            return
        self._model[self.currentModelIndex].sample[self.currentItemsIndex].name = name
        self.itemsNameChanged.emit()

    @Property(str, notify=itemsNameChanged)
    def currentItemsName(self):
        # sometimes in the process of removing an item, the model is not yet updated
        if self.currentItemsIndex >= len(self._model[self.currentModelIndex].sample):
            return ''
        return self._model[self.currentModelIndex].sample[self.currentItemsIndex].name

    # # Layers

    @Slot()
    def addNewLayers(self):
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
        try:
            self._model[self.currentModelIndex].sample[self.currentItemsIndex].add_layer(
                Layer.from_pars(
                    self.parent._material_proxy._materials[0],
                    10.0,
                    1.2,
                    name=f'Layer {len(self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers)}'
                ))
        except IndexError:
            self.addNewItems()
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
        self.parent.layersChanged.emit()

    @Slot()
    def duplicateSelectedLayers(self):
        # This is a fix until deepcopy is worked out
        # Manual duplication instead of creating a copy
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
        to_dup = self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[
            self.currentLayersIndex]
        self._model[self.currentModelIndex].sample[self.currentItemsIndex].add_layer(
            Layer.from_pars(to_dup.material,
                            to_dup.thickness.raw_value,
                            to_dup.roughness.raw_value,
                            name=to_dup.name))
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
        self.parent.layersChanged.emit()

    @Slot()
    def moveSelectedLayersUp(self):
        old_index = self.currentLayersIndex
        new_layers_list = []
        item = self._model[self.currentModelIndex].sample[self.currentItemsIndex]
        layers = item.layers
        # This convoluted approach is necessary as currently the BaseCollection does
        # not allow insertion or popping. In future, this could be replaced with the
        # approach for moving items around
        if old_index != 0:
            borg.stack.enabled = False
            self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
            self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
            self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
            for i, l in enumerate(layers):
                if i == old_index - 1:
                    new_layers_list.append(layers[old_index])
                elif i == old_index:
                    new_layers_list.append(layers[old_index - 1])
                else:
                    new_layers_list.append(l)
            while len(layers) != 0:
                item.remove_layer(0)
            for i in range(len(new_layers_list)):
                item.add_layer(new_layers_list[i])
            borg.stack.enabled = True
            self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
            self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
            self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
            self.parent.layersChanged.emit()

    @Slot()
    def moveSelectedLayersDown(self):
        old_index = self.currentLayersIndex
        new_layers_list = []
        item = self._model[self.currentModelIndex].sample[self.currentItemsIndex]
        layers = item.layers
        # This convoluted approach is necessary as currently the BaseCollection does
        # not allow insertion or popping. In future, this could be replaced with the
        # approach for moving items around
        if old_index != len(layers):
            self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
            self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
            self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
            borg.stack.enabled = False
            for i, l in enumerate(layers):
                if i == old_index:
                    new_layers_list.append(layers[old_index + 1])
                elif i == old_index + 1:
                    new_layers_list.append(layers[old_index])
                else:
                    new_layers_list.append(l)
            while len(layers) != 0:
                item.remove_layer(0)
            for i in range(len(new_layers_list)):
                item.add_layer(new_layers_list[i])
            borg.stack.enabled = True
            self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
            self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
            self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
            self.parent.layersChanged.emit()

    @Slot(str)
    def removeLayers(self, i: str):
        """
        Remove a layer from the layers list.

        :param i: Index of the layer
        :type i: str
        """
        print(">>> Removing layer: ", i)
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = True
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = True
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = True
        self._model[self.currentModelIndex].sample[self.currentItemsIndex].remove_layer(int(i))
        self._model[self.currentModelIndex].sample[0].layers[0].thickness.enabled = False
        self._model[self.currentModelIndex].sample[0].layers[0].roughness.enabled = False
        self._model[self.currentModelIndex].sample[-1].layers[-1].thickness.enabled = False
        self.parent.layersChanged.emit()

    @Slot(str)
    def setCurrentLayersMaterial(self, current_index):
        """
        Sets the material of the currently selected layer.

        :param current_index: Material index
        :type sld: str
        """
        material = self.parent._material_proxy._materials[int(current_index)]
        if self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[
                self.currentLayersIndex].material == material:
            return
        self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[
            self.currentLayersIndex].assign_material(material)
        self.parent.layersChanged.emit()

    @Slot(float)
    def setCurrentLayersThickness(self, thickness: float):
        """
        Sets the thickness of the currently selected layer.

        :param sld: New thickness value
        """
        if self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[
                self.currentLayersIndex].thickness.raw_value == thickness:
            return
        self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[
            self.currentLayersIndex].thickness = thickness
        self.parent.layersChanged.emit()

    @Slot(float)
    def setCurrentLayersRoughness(self, roughness: float):
        """
        Sets the roughness of the currently selected layer.

        :param sld: New roughness value
        """
        layer = self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[self.currentLayersIndex]
        if layer.roughness.raw_value == roughness:
            return 
        layer.roughness = roughness
        self.parent.layersChanged.emit()

    @Slot(float)
    def setCurrentItemApm(self, apm: float):
        """
        Sets the area per molecule value for the currently selected layer.
        
        :param id: New apm value
        """
        layer = self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[self.currentLayersIndex]
        if layer.area_per_molecule.raw_value == apm:
            return
        layer.area_per_molecule = apm
        self.parent.layersChanged.emit()

    @Slot(float)
    def setCurrentLayersSolvation(self, solvation: float):
        """
        Sets the solvation of the currently selected layer.

        :param solvation: New solvation value
        """
        layer = self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[self.currentLayersIndex]
        if layer.material.fraction.raw_value == solvation:
            return
        layer.material.fraction = solvation
        self.parent.layersChanged.emit()

    @Slot(str)
    def setCurrentLayersSolvent(self, current_index):
        """
        Sets the solvent for the currently selected layer.
        
        :param current_index: Material index. 
        """
        material = self.parent._material_proxy._materials[int(current_index)]
        layer = self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[self.currentLayersIndex]
        if layer.material.material_b == material:
            return
        layer.material.material_b = material
        self.parent.layersChanged.emit()
    
    @Slot(str)
    def setCurrentLayersChemStructure(self, structure: str):
        """
        Sets the chemical structure for the currently selected layer. 
        
        :param structure: Chemical structure
        """
        if self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[self.currentLayersIndex].chemical_structure == structure:
            return 
        self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[self.currentLayersIndex].chemical_structure = structure
        self.parent.layersChanged.emit()

    @Slot(str)
    def currentSurfactantSolventRoughness(self, x):
        solvent = None
        for i, item in enumerate(self.itemsAsObj):
            if item['name'] == x:
                solvent = self._model[self.currentModelIndex].sample[i].layers[0]
        if solvent is None:
            self._model[self.currentModelIndex].sample[self.currentItemsIndex].layers[0].roughness.user_constraints['solvent_roughness'].enabled == False
        else:
            solvent.roughness.enabled = True
            self._model[self.currentModelIndex].sample[self.currentItemsIndex].constrain_solvent_roughness(solvent.roughness)
        self.parent.layersChanged.emit()

    # # #
    # Calculations
    # # #

    def getPureModelReflectometry(self, x):
        return self._pure.interface.fit_func(x, self._pure.uid)

    def getPureModelSld(self):
        return self._pure.interface.sld_profile(self._pure.uid)

    def resetModel(self):
        self._structure = self._defaultStructure()
        self._model = Models.from_pars(self._defaultModel(structure=self._structure, interface=self.parent._interface))
