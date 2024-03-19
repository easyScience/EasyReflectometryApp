import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.XmlListModel 2.13

import easyApp.Gui.Components 1.0 as EaComponents
import easyApp.Gui.Style 1.0 as EaStyle

import Gui.Globals 1.0 as ExGlobals

EaComponents.TableView {
    id: layersTable
    defaultInfoText: qsTr("No Layers Added")

    // Table model

    model: XmlListModel {
        property int layersIndex: ExGlobals.Constants.proxy.model.currentLayersIndex + 1

        xml: ExGlobals.Constants.proxy.model.layersAsXml
        query: `/data/item[${itemsTable.currentIndex + 1}]/layers`

        XmlRole { name: "thick"; query: "thickness/value/number()" }
        XmlRole { name: "rough"; query: "roughness/value/number()" }
        XmlRole { name: "materialid"; query: "material/name/string()"}
        XmlRole { name: "thick_enabled"; query: "thickness/enabled/string()" }
        XmlRole { name: "rough_enabled"; query: "roughness/enabled/string()" }
    }

    // Table rows

    delegate: EaComponents.TableViewDelegate {
        property var layersModel: model

        EaComponents.TableViewLabel {
            id: noLabel
            width: EaStyle.Sizes.fontPixelSize * 2.3
            headerText: "No."
            text: model.index + 1
        }

        EaComponents.TableViewComboBox{
            horizontalAlignment: Text.AlignLeft
            width: EaStyle.Sizes.sideBarContentWidth - (thickLabel.width + roughLabel.width + noLabel.width + deleteRowColumn.width + 5 * EaStyle.Sizes.tableColumnSpacing)
            headerText: "Material"
            onActivated: {
                ExGlobals.Constants.proxy.model.setCurrentLayersMaterial(currentIndex)
            }
            model: ExGlobals.Constants.proxy.material.materialsName
            onModelChanged: {
                currentIndex = indexOfValue(layersModel.materialid)
            }
            Component.onCompleted: {
                currentIndex = indexOfValue(layersModel.materialid)
            }
        }

        EaComponents.TableViewTextInput {
            id: thickLabel
            horizontalAlignment: Text.AlignHCenter
            width: EaStyle.Sizes.fontPixelSize * 10.0
            headerText: "Thickness/Å"
            enabled: model.thick_enabled == "True"
            text: (isNaN(layersModel.thick)) ? '--' : layersModel.thick.toFixed(2)
            onEditingFinished: ExGlobals.Constants.proxy.model.setCurrentLayersThickness(text)
        }

        EaComponents.TableViewTextInput {
            id: roughLabel
            horizontalAlignment: Text.AlignHCenter
            width: EaStyle.Sizes.fontPixelSize * 10.0
            headerText: "Upper Roughness/Å"
            enabled: model.rough_enabled == "True"
            text: (isNaN(layersModel.rough)) ? '--' : layersModel.rough.toFixed(2)
            onEditingFinished: ExGlobals.Constants.proxy.model.setCurrentLayersRoughness(text)
        } 

        EaComponents.TableViewButton {
            id: deleteRowColumn
            headerText: "Del." //"\uf2ed"
            fontIcon: "minus-circle"
            ToolTip.text: qsTr("Remove this item")
            enabled: layersTable.model.count > 1
            onClicked: ExGlobals.Constants.proxy.model.removeLayers(layersTable.currentIndex)
        }

    }

    onCurrentIndexChanged: {
        ExGlobals.Constants.proxy.model.currentLayersIndex = layersTable.currentIndex
    }

}