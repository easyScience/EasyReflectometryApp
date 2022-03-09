import json
from typing import Union
from dicttoxml import dicttoxml

from matplotlib import cm, colors

from PySide2.QtCore import QObject, Signal, Property, Slot

from easyCore import borg
from easyCore.Utils.UndoRedo import property_stack_deco
from easyCore.Utils.classTools import generatePath
        

class ParameterProxy(QObject):

    parametersAsXmlChanged = Signal()
    parametersAsObjChanged = Signal()

    parametersFilterCriteriaChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self._parameters_as_obj = []
        self._parameters_as_xml = ""

        self._parameters_filter_criteria = ""

        self.parametersFilterCriteriaChanged.connect(self._onParametersFilterCriteriaChanged)


    # # #
    # Setters and getters
    # # #

    @Property('QVariant', notify=parametersAsObjChanged)
    def parametersAsObj(self):
        return self._parameters_as_obj

    def _setParametersAsObj(self):
        self._parameters_as_obj.clear()

        par_ids, par_paths = generatePath(self.parent._model_proxy._model, True)
        for par_index, par_path in enumerate(par_paths):
            par_id = par_ids[par_index]
            par = borg.map.get_item_by_key(par_id)
            if par_path[-11:] == 'repetitions' and par.raw_value == 1:
                continue

            if not par.enabled:
                continue

            if self._parameters_filter_criteria.lower() not in par_path.lower():
                continue

            label = par_path
            unit = '{:~P}'.format(par.unit)
            if par_path[-3:] == 'sld':
                label = (' ').join(par_path.split('.')[-2:])
                label = label[:-3] + 'SLD'
            elif par_path[-9:] == 'thickness':
                label = (' ').join(par_path.split('.')[-2:])
                label = label[:-9] + 'Thickness'
            elif par_path[-9:] == 'roughness':
                label = (' ').join(par_path.split('.')[-2:])
                label = label[:-9] + 'Upper Roughness'
            elif par_path[-11:] == 'repetitions':
                label = (' ').join(par_path.split('.')[-2:])
                label = label[:-11] + 'Repetitions'
            elif par_path == 'scale':
                label = 'Instrumental Scaling'
            elif par_path == 'background':
                label = 'Instrumental Background'
            elif par_path == 'resolution':
                label = 'Resolution (dq/q)'
                unit = '%'
            self._parameters_as_obj.append({
                "id":     str(par_id),
                "number": par_index + 1,
                "label":  label,
                "value":  par.raw_value,
                "unit":   unit,
                "error":  float(par.error),
                "fit":    int(not par.fixed)
            })

        self.parametersAsObjChanged.emit()

    @Property(str, notify=parametersAsXmlChanged)
    def parametersAsXml(self):
        return self._parameters_as_xml

    def _setParametersAsXml(self):
        self._parameters_as_xml = dicttoxml(self._parameters_as_obj, attr_type=False).decode()
        self.parametersAsXmlChanged.emit()

    @Slot(str)
    def setParametersFilterCriteria(self, new_criteria):
        if self._parameters_filter_criteria == new_criteria:
            return
        self._parameters_filter_criteria = new_criteria
        self.parametersFilterCriteriaChanged.emit()

    # # # 
    # Actions
    # # # 

    def _onParametersChanged(self):
        self._setParametersAsObj()
        self._setParametersAsXml()
        self.parent.stateChanged.emit(True)
    
    def _onParametersFilterCriteriaChanged(self):
        self._onParametersChanged()

    @Slot(str, 'QVariant')
    def editParameter(self, obj_id: str, new_value: Union[bool, float, str]):  # covers both parameter and descriptor
        if not obj_id:
            return

        obj = self._parameterObj(obj_id)
        if obj is None:
            return
        # print(f"\n\n+ editParameter {obj_id} of {type(new_value)} from {obj.raw_value} to {new_value}")

        if isinstance(new_value, bool):
            if obj.fixed == (not new_value):
                return

            obj.fixed = not new_value
            self._onParametersChanged()
            self.undoRedoChanged.emit()

        else:
            if obj.raw_value == new_value:
                return

            obj.value = new_value
            self.parent.parametersChanged.emit()

    def _parameterObj(self, obj_id: str):
        if not obj_id:
            return
        obj_id = int(obj_id)
        obj = borg.map.get_item_by_key(obj_id)
        return obj