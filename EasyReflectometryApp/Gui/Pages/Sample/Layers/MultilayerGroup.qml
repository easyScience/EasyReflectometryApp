import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Dialogs 1.3 as Dialogs1
import QtQuick.XmlListModel 2.13

import easyApp.Gui.Elements 1.0 as EaElements

import Gui.Globals 1.0 as ExGlobals
import Gui.Pages.Sample.Layers 1.0 as ExLayers

EaElements.GroupBox {
    // When an item in the above table is selected, this box will become enabled.
    // Allowing different parameters and layers to be defined for the item.
    id: multilayerGroup
    title: qsTr(ExGlobals.Constants.proxy.model.currentItemsName + " editor")
    enabled: (itemsTable.model.count > 0) ? true : false //When a layer is selected
    collapsible: false
    last: true

    ExLayers.MultilayerTable{
        id: layersTable
    }

    ExLayers.MultilayerRow{
    }
}