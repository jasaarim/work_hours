// This file is modified from Nokia's template that comes with the
// tool psa (which is part of PySide)

import QtQuick 1.1
import com.meego 1.0

PageStackWindow {
    id: appWindow

    initialPage: mainPage
    MainPage{id: mainPage}

    ToolBarLayout {
        id: commonTools
        visible: true
        ToolIcon { platformIconId: "toolbar-view-menu";
             anchors.right: parent===undefined ? undefined : parent.right
             onClicked: (myMenu.status == DialogStatus.Closed) ? myMenu.open() : myMenu.close()
        }
    }
    Menu {
        id: myMenu
        visualParent: pageStack

        ListView {
            id: projectList
            width: 400
            height: 400
            anchors.centerIn: parent
            model: ProjectListModel
            delegate: Component {
                Rectangle {
                    width: projectList.width
                    height: 380/6
                    color: ((index % 2 == 0)?"#222":"#111")
                    scale: delegateMouseArea.containsMouse ? 1.5 : 1
                    Behavior on scale {
                        NumberAnimation { easing.type: Easing.InOutBack }
                    }
                    Text {
                        id: title
                        text: model.project.name
                        color: "white"
                        font.bold: true
                        font.pointSize: 16
                        anchors.centerIn: parent
                        verticalAlignment: Text.AlignVCenter
                    }
                    MouseArea {
                        id: delegateMouseArea
                        hoverEnabled: true
                        anchors.fill: parent
                        onClicked: {
                            myMenu.close()
                            // FIXME: The text doesn't seem to change
			    mainPage.status.text = writeread.set_project(model.project)
                        }
                    }
                }
            }
        }
    }
}
