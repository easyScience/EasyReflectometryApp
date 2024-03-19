import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Dialogs 1.3 as Dialogs1
import QtQuick.XmlListModel 2.13

import easyApp.Gui.Style 1.0 as EaStyle
import easyApp.Gui.Elements 1.0 as EaElements
import easyApp.Gui.Components 1.0 as EaComponents

import Gui.Globals 1.0 as ExGlobals
import Gui.Pages.Sample.Layers 1.0 as ExLayers

EaElements.GroupBox {
//    id: repeatingMultilayerGroup
    title: qsTr(ExGlobals.Constants.proxy.model.currentItemsName + " editor")
    enabled: (itemsTable.model.count > 0) ? true : false //When a layer is selected
    collapsible: false
    last: true
    Row {
        spacing: EaStyle.Sizes.fontPixelSize * 0.5

        // This integer defines how many repetitions of the layer structure should be
        // used.
        EaComponents.TableViewLabel{
            horizontalAlignment: Text.AlignRight
            width: labelWidth() * 2.1
            ToolTip.text: qsTr("To create some repeating multilayer structure")
            text: qsTr("Number of repetitions:")
        }
        EaElements.SpinBox {
            id: repsSpinBox
            editable: true
            from: 1
            to: 9999
            value: layerRepetionsSpinBoxValue 
            onValueChanged: {
                ExGlobals.Constants.proxy.model.currentItemsRepetitions = value
            }
        }
    }

    ExLayers.MultilayerTable{
        id: layersTable
    }

    ExLayers.MultilayerRow{
    }
}