// This file is modified from Nokia's template that comes with the
// tool psa (which is part of PySide)

import QtQuick 1.1
import com.meego 1.0

Page {
    id: mainPage
    tools: commonTools
    Label {
        id: status
        anchors.centerIn: parent
        text: writeread.welcomemsg()
        visible: true
    }
    Button{
        id: log_in
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: status.bottom
        anchors.topMargin: 10
        text: qsTr("Log in!")
        onClicked: status.text = writeread.log_in()
    }
    Button{
        id: log_out
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: log_in.bottom
        anchors.topMargin: 10
        text: qsTr("Log out!")
        onClicked: status.text = writeread.log_out()
    }
}
