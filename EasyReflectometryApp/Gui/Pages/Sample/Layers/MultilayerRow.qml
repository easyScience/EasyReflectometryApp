import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.XmlListModel 2.13

import easyApp.Gui.Elements 1.0 as EaElements
import easyApp.Gui.Style 1.0 as EaStyle

import Gui.Globals 1.0 as ExGlobals

Row {
    spacing: EaStyle.Sizes.fontPixelSize

    EaElements.SideBarButton {
        width: (EaStyle.Sizes.sideBarContentWidth - (2 * (EaStyle.Sizes.tableRowHeight + EaStyle.Sizes.fontPixelSize)) - EaStyle.Sizes.fontPixelSize) / 2
        enabled: true
        fontIcon: "plus-circle"
        text: qsTr("Add layer")
        onClicked: ExGlobals.Constants.proxy.model.addNewLayers()
    }

    EaElements.SideBarButton {
        width: (EaStyle.Sizes.sideBarContentWidth - (2 * (EaStyle.Sizes.tableRowHeight + EaStyle.Sizes.fontPixelSize)) - EaStyle.Sizes.fontPixelSize) / 2
        enabled: (layersTable.model.count > 0) ? true : false //when item is selected
        fontIcon: "clone"
        text: qsTr("Duplicate layer")
        onClicked: ExGlobals.Constants.proxy.model.duplicateSelectedLayers()
    }

    EaElements.SideBarButton {
        width: EaStyle.Sizes.tableRowHeight
        enabled: (layersTable.model.count > 0 && layersTable.currentIndex != 0) ? true : false//When item is selected
        fontIcon: "arrow-up"
        ToolTip.text: qsTr("Move layer up")
        onClicked: ExGlobals.Constants.proxy.model.moveSelectedLayersUp()
    }

    EaElements.SideBarButton {
        width: EaStyle.Sizes.tableRowHeight
        enabled: (layersTable.model.count > 0 && layersTable.currentIndex + 1 != layersTable.model.count) ? true : false
        fontIcon: "arrow-down"
        ToolTip.text: qsTr("Move layer down")
        onClicked: ExGlobals.Constants.proxy.model.moveSelectedLayersDown()
    }
}