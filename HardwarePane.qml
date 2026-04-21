pragma ComponentBehavior: Bound

import ".."
import "../components"
import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Quickshell.Widgets
import Caelestia.Config
import qs.components
import qs.components.containers
import qs.components.controls
import qs.components.effects
import qs.services
import qs.utils

Item {
    id: root
    anchors.fill: parent

    // Caelestia Frame
    ClippingRectangle {
        id: hardwareClippingRect

        anchors.fill: parent
        anchors.margins: Tokens.padding.normal
        anchors.leftMargin: 0
        anchors.rightMargin: Tokens.padding.normal

        radius: hardwareBorder.innerRadius
        color: "transparent"

        Loader {
            id: hardwareLoader
            anchors.fill: parent
            anchors.margins: Tokens.padding.large + Tokens.padding.normal
            anchors.leftMargin: Tokens.padding.large
            anchors.rightMargin: Tokens.padding.large
            asynchronous: true
            sourceComponent: hardwareContentComponent
        }
    }

    InnerBorder {
        id: hardwareBorder
        leftThickness: 0
        rightThickness: Tokens.padding.normal
    }

    Component {
        id: hardwareContentComponent

        StyledFlickable {
            id: hardwareFlickable
            flickableDirection: Flickable.VerticalFlick
            contentHeight: contentLayout.height

            StyledScrollBar.vertical: StyledScrollBar { flickable: hardwareFlickable }

            ColumnLayout {
                id: contentLayout
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                spacing: Tokens.spacing.normal

                // --- LOCAL DEBUG SYSTEM ---
                ListModel { id: debugModel }
                function appendLog(msg) {
                    let time = new Date().toLocaleTimeString();
                    debugModel.insert(0, { "timeStr": time, "msgStr": msg });
                    console.log("DEBUG: " + msg);
                }

                Timer {
                    interval: 2000
                    running: true
                    repeat: true
                    onTriggered: {
                        Quickshell.readFile("/tmp/lumina_stats.json", function(content) {
                            if (content) {
                                // First, just write to the log for testing!
                                contentLayout.appendLog("File content: " + content.trim());
                                
                                try {
                                    let data = JSON.parse(content.trim())

                                    // Robust assignment: Only set if value exists, otherwise fallback
                                    cpuTempLabel.text = data.cpu_temp !== undefined ? data.cpu_temp + " °C" : "-- °C"
                                    gpuTempLabel.text = data.gpu_temp !== undefined ? data.gpu_temp + " °C" : "-- °C"
                                    sysFanLabel.text = data.sys_fan !== undefined ? data.sys_fan + " RPM" : "-- RPM"
                                    gpuFanLabel.text = data.gpu_fan !== undefined ? data.gpu_fan + " %" : "-- %"

                                    // Synchronize GPU slider with the real value when it is not being pressed
                                    if (data.gpu_fan !== undefined && !gpuFanSlider.pressed) {
                                        gpuFanSlider.value = data.gpu_fan / 100.0
                                    }
                                } catch(e) {
                                    // Output the broken content so we can find the error!
                                    contentLayout.appendLog("JSON Error: " + e + " | Content: '" + content.trim() + "'");
                                }
                            } else {
                                contentLayout.appendLog("Quickshell could not read the file (Permissions?).");
                            }
                        });
                    }
                }

                // --- MAIN HEADING ---
                SettingsHeader {
                    icon: "memory"
                    title: qsTr("Hardware & Cooling")
                }

                // === SECTION 1: FANS ===
                SectionHeader {
                    title: qsTr("Fans & Profiles")
                    description: qsTr("Manual control of system cooling")
                }

                SectionContainer {
                    contentSpacing: Tokens.spacing.normal

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Tokens.spacing.small

                        // System fan
                        RowLayout {
                            Layout.fillWidth: true
                            StyledText { text: qsTr("System Fan Speed"); font.pointSize: Tokens.font.size.normal; font.weight: 500 }
                            Item { Layout.fillWidth: true }
                            StyledText { text: Math.round(sysFanSlider.value * 100) + " %"; color: Colours.palette.m3outline }
                        }
                        StyledSlider {
                            id: sysFanSlider
                            Layout.fillWidth: true
                            implicitHeight: Tokens.padding.normal * 3
                            value: 0.5
                        }

                        // GPU fan
                        RowLayout {
                            Layout.fillWidth: true
                            StyledText { text: qsTr("GPU Fan Speed"); font.pointSize: Tokens.font.size.normal; font.weight: 500 }
                            Item { Layout.fillWidth: true }
                            StyledText { text: Math.round(gpuFanSlider.value * 100) + " %"; color: Colours.palette.m3outline }
                        }
                        StyledSlider {
                            id: gpuFanSlider
                            Layout.fillWidth: true
                            implicitHeight: Tokens.padding.normal * 3
                            value: 0.5
                            // onMoved is only triggered by the user, not by code changes
                            onMoved: setGpuProcess.start(Math.round(value * 100))
                        }

                        // Separate process for setting the GPU fans, replaces Quickshell.execute
                        Process {
                            id: setGpuProcess
                            // The command is built dynamically
                            function start(speed) {
                                command = [
                                    "/home/joern/Dokumente/git/Lumina-Control/venv/bin/python",
                                    "/home/joern/Dokumente/git/Lumina-Control/lumina_bridge.py",
                                    "set_gpu",
                                    speed.toString()
                                ]
                                running = true
                            }
                            onExited: {
                                if (exitCode === 0 && stdout) {
                                    contentLayout.appendLog("GPU Fan: " + stdout.trim())
                                } else if (stderr) {
                                    contentLayout.appendLog("GPU Fan ERROR: " + stderr.trim())
                                }
                            }
                        }
                        
                        // Profile Buttons
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Tokens.spacing.normal

                            Repeater {
                                model: ["Quiet", "Normal", "Performance"]
                                delegate: StyledRect {
                                    required property string modelData

                                    Layout.fillWidth: true
                                    implicitHeight: Tokens.padding.normal * 4
                                    radius: Tokens.rounding.normal
                                    color: Colours.palette.m3secondaryContainer

                                    StateLayer {
                                        onClicked: {
                                            contentLayout.appendLog("Profile selected: " + modelData);
                                        }
                                    }

                                    StyledText {
                                        anchors.centerIn: parent
                                        text: modelData
                                        color: Colours.palette.m3onSecondaryContainer
                                        font.weight: 500
                                    }
                                }
                            }
                        }
                    }
                }

                // === SECTION 2: STATISTICS ===
                SectionHeader {
                    title: qsTr("Live Statistics")
                    description: qsTr("Current system temperatures")
                }

                SectionContainer {
                    contentSpacing: Tokens.spacing.normal

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Tokens.spacing.small

                        RowLayout {
                            Layout.fillWidth: true
                            MaterialIcon { text: "thermostat"; font.pointSize: Tokens.font.size.normal; color: Colours.palette.m3outline }
                            StyledText { text: "CPU Temperature"; font.pointSize: Tokens.font.size.normal; Layout.fillWidth: true }
                            StyledText { id: cpuTempLabel; text: "-- °C"; font.weight: 500 }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            MaterialIcon { text: "device_thermostat"; font.pointSize: Tokens.font.size.normal; color: Colours.palette.m3outline }
                            StyledText { text: "GPU Temperature"; font.pointSize: Tokens.font.size.normal; Layout.fillWidth: true }
                            StyledText { id: gpuTempLabel; text: "-- °C"; font.weight: 500 }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            MaterialIcon { text: "mode_fan"; font.pointSize: Tokens.font.size.normal; color: Colours.palette.m3outline }
                            StyledText { text: "System Fan"; font.pointSize: Tokens.font.size.normal; Layout.fillWidth: true }
                            StyledText { id: sysFanLabel; text: "-- RPM"; font.weight: 500 }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            MaterialIcon { text: "mode_fan"; font.pointSize: Tokens.font.size.normal; color: Colours.palette.m3outline }
                            StyledText { text: "GPU Fan"; font.pointSize: Tokens.font.size.normal; Layout.fillWidth: true }
                            StyledText { id: gpuFanLabel; text: "-- %"; font.weight: 500 }
                        }
                    }
                }

                // === SECTION 3: RGB ===
                SectionHeader {
                    title: qsTr("Lighting")
                    description: qsTr("RGB Control")
                }

                SectionContainer {
                    contentSpacing: Tokens.spacing.normal

                    // --- Native process for OpenRGB ---
                    Process {
                        id: openrgbProcess
                        command: [
                            "/home/joern/Dokumente/git/Lumina-Control/venv/bin/python", 
                            "/home/joern/Dokumente/git/Lumina-Control/lumina_bridge.py", 
                            "openrgb"
                        ]
                        onExited: {
                            if (exitCode === 0) {
                                contentLayout.appendLog("OpenRGB signal sent.");
                            } else {
                                contentLayout.appendLog("OpenRGB ERROR: " + stderr);
                            }
                        }
                    }

                    StyledRect {
                        Layout.fillWidth: true
                        implicitHeight: Tokens.padding.normal * 4
                        radius: Tokens.rounding.normal
                        color: Colours.palette.m3primaryContainer

                        StateLayer {
                            onClicked: {
                                contentLayout.appendLog("Starting OpenRGB via daemon...");
                                openrgbProcess.running = true;
                            }
                        }

                        RowLayout {
                            anchors.centerIn: parent
                            spacing: Tokens.spacing.small
                            MaterialIcon { text: "palette"; color: Colours.palette.m3onPrimaryContainer }
                            StyledText { text: qsTr("Start OpenRGB"); color: Colours.palette.m3onPrimaryContainer; font.weight: 500 }
                        }
                    }
                }

                // === SECTION 4: DEBUG LOG ===
                SectionHeader {
                    title: qsTr("Developer Console")
                    description: qsTr("Lumina Bridge Logs & Tests")
                }

                SectionContainer {
                    Layout.preferredHeight: 220
                    contentSpacing: Tokens.spacing.normal

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: Tokens.spacing.small

                        // --- Native process for Ping ---
                        Process {
                            id: testProcess
                            command: [
                                "/home/joern/Dokumente/git/Lumina-Control/venv/bin/python", 
                                "/home/joern/Dokumente/git/Lumina-Control/lumina_bridge.py", 
                                "test"
                            ]
                            onExited: {
                                contentLayout.appendLog("Process finished (Code " + exitCode + ")");
                                if (stdout && stdout.trim() !== "") {
                                    contentLayout.appendLog("DAEMON: " + stdout.trim());
                                }
                                if (stderr && stderr.trim() !== "") {
                                    contentLayout.appendLog("ERROR: " + stderr.trim());
                                }
                            }
                        }

                        // --- TEST BUTTON ---
                        StyledRect {
                            Layout.fillWidth: true
                            implicitHeight: Tokens.padding.normal * 4
                            radius: Tokens.rounding.normal
                            color: Colours.palette.m3secondaryContainer

                            StateLayer {
                                onClicked: {
                                    contentLayout.appendLog("Sending ping to daemon...");
                                    testProcess.running = true;
                                }
                            }

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: Tokens.spacing.small
                                MaterialIcon { text: "cable"; color: Colours.palette.m3onSecondaryContainer }
                                StyledText { text: qsTr("Test Connection"); color: Colours.palette.m3onSecondaryContainer; font.weight: 500 }
                            }
                        }

                        // --- LOG LIST ---
                        ListView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            model: debugModel
                            clip: true
                            
                            delegate: RowLayout {
                                required property string timeStr
                                required property string msgStr

                                width: parent.width
                                spacing: Tokens.spacing.smaller
                                StyledText { text: timeStr; color: Colours.palette.m3primary; font.family: "monospace"; font.pointSize: 9 }
                                StyledText { text: msgStr; color: Colours.palette.m3onSurface; font.family: "monospace"; font.pointSize: 9; Layout.fillWidth: true; wrapMode: Text.Wrap }
                            }
                        }
                    }
                }
            }
        }
    }
}