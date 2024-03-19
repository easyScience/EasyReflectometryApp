__author__ = 'github.com/arm61'

from matplotlib import cm, colors

from PySide2.QtCore import QObject, Signal, Property, Slot

from easyCore import borg
from easyCore.Utils.io.xml import XMLSerializer

from EasyReflectometry.sample import Material
from EasyReflectometry.sample import MaterialCollection

COLOURMAP = cm.get_cmap('Blues', 100)
MIN_SLD = -3
MAX_SLD = 15


class MaterialProxy(QObject):

    materialsChanged = Signal()
    materialsIndexChanged = Signal()
    materialsAsXmlChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self._materials_as_xml = ""
        self._materials = self._defaultMaterials()

        self._current_materials_index = 0

        self.materialsChanged.connect(self._setMaterialsAsXml)

    # # #
    # Defaults
    # # #

    def _defaultMaterials(self) -> MaterialCollection:
        """
        Default materials for EasyReflecometry.
        
        :return: Three materials; Air, D2O and Si.
        """
        return MaterialCollection(
            Material.from_pars(0., 0., name='Air'),
            Material.from_pars(6.335, 0., name='D2O'),
            Material.from_pars(2.074, 0., name='Si')
        )

    # # #
    # Setters and getters
    # # #

    @property
    def materialsAsObj(self):
        """
        :return: A list of the materials to be converted to XML.
        """
        _materials_as_obj = []
        for i in self._materials:
            dictionary = i.as_dict(skip=['interface', 'min', 'max', 'error', 'fixed', 'description', 'url'])
            dictionary['color'] = colors.rgb2hex(
                COLOURMAP((dictionary['sld']['value'] - MIN_SLD) / (MAX_SLD - MIN_SLD)))
            _materials_as_obj.append(dictionary)
        return _materials_as_obj

    @Property(str, notify=materialsAsXmlChanged)
    def materialsAsXml(self):
        """
        :return: The list of materials as XML.
        """
        return self._materials_as_xml

    def _setMaterialsAsXml(self):
        """
        Sets the _materials_as_xml object. 
        """
        print(">>> _setMaterialsAsXml")
        self._materials_as_xml = XMLSerializer().encode({"item":self.materialsAsObj}, data_only=True)
        self.materialsAsXmlChanged.emit()

    @Property(list, notify=materialsChanged)
    def materialsName(self):
        """
        :return: A list of just the materials names
        """
        return self._materials.names

    @Property(int, notify=materialsIndexChanged)
    def currentMaterialsIndex(self):
        """
        :return: The index of the currently selected material.
        """
        return self._current_materials_index

    @currentMaterialsIndex.setter
    def currentMaterialsIndex(self, new_index: int):
        """
        Sets the _current_materials_index integer.
        """
        if self._current_materials_index == new_index or new_index == -1:
            return
        self._current_materials_index = new_index

    # # #
    # Slot
    # # #

    @Slot()
    def addNewMaterials(self):
        """
        Add a new material.
        """
        borg.stack.enabled = False
        self._materials.append(
            Material.from_pars(2.074,
                               0.000,
                               name=f'Si',
                               interface=self.parent._interface))
        borg.stack.enabled = True
        self.materialsChanged.emit()
        self.parent.layersMaterialsChanged.emit()

    @Slot()
    def duplicateSelectedMaterials(self):
        """
        Duplicate the currently selected material.
        """
        # if borg.stack.enabled:
        #    borg.stack.beginMacro('Loaded default material')
        borg.stack.enabled = False
        # This is a fix until deepcopy is worked out
        # Manual duplication instead of creating a copy
        to_dup = self._materials[self.currentMaterialsIndex]
        self._materials.append(
            Material.from_pars(to_dup.sld.raw_value,
                               to_dup.isld.raw_value,
                               name=to_dup.name,
                               interface=self.parent._interface))
        borg.stack.enabled = True
        self.materialsChanged.emit()
        self.parent.layersMaterialsChanged.emit()

    @Slot(str)
    def removeMaterials(self, i: str):
        """
        Remove a material from the materials list.

        :param i: Index of the material
        """
        del self._materials[int(i)]
        self.materialsChanged.emit()
        self.parent.layersMaterialsChanged.emit()

    @Slot()
    def moveSelectedMaterialsUp(self):
        """
        Move the currently selected material up.
        """
        i = self.currentMaterialsIndex
        self._materials.insert(i-1, self._materials.pop(i))
        self.materialsChanged.emit()
        self.parent.layersMaterialsChanged.emit()

    @Slot()
    def moveSelectedMaterialsDown(self):
        """
        Move the currently selected material down.
        """
        i = self.currentMaterialsIndex
        self._materials.insert(i+1, self._materials.pop(i))
        self.materialsChanged.emit()
        self.parent.layersMaterialsChanged.emit()

    @Slot(str)
    def setCurrentMaterialsName(self, name: str):
        """
        Sets the name of the currently selected material.

        :param sld: New material name
        """
        if self._materials[self.currentMaterialsIndex].name == name:
            return
        self._materials[self.currentMaterialsIndex].name = name
        self.materialsChanged.emit()
        self.parent.layersMaterialsChanged.emit()

    @Slot(float)
    def setCurrentMaterialsSld(self, sld: float):
        """
        Sets the SLD of the currently selected material.

        :param sld: New SLD value
        """
        if self._materials[self.currentMaterialsIndex].sld.raw_value == sld:
            return
        self._materials[self.currentMaterialsIndex].sld = sld
        self.materialsChanged.emit()
        self.parent.layersChanged.emit()

    @Slot(float)
    def setCurrentMaterialsISld(self, isld: float):
        """
        Sets the iSLD of the currently selected material.

        :param isld: New iSLD value
        """
        if self._materials[self.currentMaterialsIndex].isld.raw_value == isld:
            return
        self._materials[self.currentMaterialsIndex].isld = isld
        self.materialsChanged.emit()
        self.parent.layersChanged.emit()

    def resetMaterial(self):
        """
        Reset the materials to the default.
        """
        self._materials = self.parent._material_proxy._defaultMaterials()
        self.materialsChanged.emit()
        self.parent.layersChanged.emit()
