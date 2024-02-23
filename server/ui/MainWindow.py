"""The main application window
"""

import webbrowser
from functools import partial

from PyQt6.QtCore import QObject, QSize, Qt
from PyQt6.QtGui import QCloseEvent, QFont
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QScrollArea, QSizePolicy, QSlider,
                             QSpacerItem, QSplitter, QVBoxLayout, QWidget)

import ui
from modules import config, ServerSingleton, HardwareDevice
from ui import EspSettingsDialog
from utils import LoggerClass
from PyQt6.QtCore import pyqtSlot as QSlot
from PyQt6.QtCore import pyqtSignal as QSignal

from utils.Enums import HardwareConnectionType

logger = LoggerClass.getSubLogger(__name__)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs) -> None:
        logger.debug(f"Creating {__class__.__name__}")
        super().__init__(*args, **kwargs)

        self._singleWindows: dict[str, QWidget] = {}
        self._hwRows: dict[int, QWidget] = {}

        self.setupUi()
        self.server = ServerSingleton.getInstance()
        self.server.hwManager.hwListChanged.connect(
            self._handleHwListChange)
        self._pollHwList()

    def setupUi(self) -> None:
        """Initialize the main UI."""
        # the widget and it's layout
        self.setWindowTitle("VRC-patpatpat")
        self.resize(QSize(800, 430))
        self.setMaximumWidth(2000)
        self.setMinimumWidth(600)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        self.setSizePolicy(sizePolicy)
        self.theCentralWidet = QWidget(self)
        self.selfLayout = QVBoxLayout(self.theCentralWidet)

        # the splitter for the data rows
        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.splitter.setOpaqueResize(False)
        self.splitter.setChildrenCollapsible(False)

        # the top bar horizontal layout
        self.hl_topBar = QHBoxLayout()

        # hardware row label
        self.lb_espRowHeader = QLabel(self)
        self.lb_espRowHeader.setText("Hardware:")
        self.hl_topBar.addWidget(self.lb_espRowHeader)

        # help button
        self.bt_openGithub = QPushButton(self)
        self.bt_openGithub.setMaximumWidth(60)
        self.bt_openGithub.setText("Help")
        self.bt_openGithub.clicked.connect(lambda: webbrowser.open(
            "https://github.com/lebaston100/vrc-patpatpat"
            "?tab=readme-ov-file#vrc-patpatpat"))
        self.hl_topBar.addWidget(self.bt_openGithub)

        # open log window button
        self.bt_openLogWindow = QPushButton(self)
        self.bt_openLogWindow.setMaximumWidth(60)
        self.bt_openLogWindow.setText("Log")
        self.bt_openLogWindow.clicked.connect(
            partial(self.openSingleWindow, "LogWindow"))
        self.hl_topBar.addWidget(self.bt_openLogWindow)

        # open programm settings button
        self.bt_openProgramSettings = QPushButton(self)
        self.bt_openProgramSettings.setMaximumWidth(40)
        font = QFont()
        font.setPointSize(9)
        self.bt_openProgramSettings.setFont(font)
        self.bt_openProgramSettings.setToolTip("Program Settings")
        self.bt_openProgramSettings.setText("\ud83d\udd27")
        self.bt_openProgramSettings.clicked.connect(
            partial(self.openSingleWindow, "ProgramSettingsDialog"))
        self.hl_topBar.addWidget(self.bt_openProgramSettings)

        self.selfLayout.addLayout(self.hl_topBar)

        # the esp row

        # the hardware scroll area
        self.hardwareScrollArea = self.createScrollArea()

        # the single widget inside the scroll area
        self.hardwareScrollAreaWidgetContent = QWidget(self.hardwareScrollArea)
        self.hardwareScrollAreaWidgetContent.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum))

        # the layout inside the widget that's inside the scroll area
        self.hardwareScrollAreaWidgetContentLayout = QVBoxLayout(
            self.hardwareScrollAreaWidgetContent)
        self.hardwareScrollAreaWidgetContentLayout.setContentsMargins(
            0, 0, 0, 0)

        # set the hardware scroll areas only widget to our scrollarea content widget
        self.hardwareScrollArea.setWidget(self.hardwareScrollAreaWidgetContent)
        # finally add the scroll area to our splitter
        self.splitter.addWidget(self.hardwareScrollArea)

        # contact group label
        self.lb_groupRowHeader = QLabel(self)
        self.lb_groupRowHeader.setText("Contact Groups:")
        self.lb_groupRowHeader.setMaximumHeight(25)
        self.splitter.addWidget(self.lb_groupRowHeader)

        # contact group row

        # the contact group scroll area
        self.contactGroupScrollArea = self.createScrollArea()
        # the single widget inside the scroll area
        self.contactGroupScrollAreaWidgetContent = QWidget(
            self.contactGroupScrollArea)
        self.contactGroupScrollAreaWidgetContent.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum))

        # the layout inside the widget that's inside the scroll area
        self.contactGroupScrollAreaWidgetContentLayout = QVBoxLayout(
            self.contactGroupScrollAreaWidgetContent)
        self.contactGroupScrollAreaWidgetContentLayout.setContentsMargins(
            0, 0, 0, 0)

        # TODO: add rows here
        self.testContactGroupInstance1 = ContactGroupRow(
            self.contactGroupScrollAreaWidgetContent)
        self.testContactGroupInstance2 = ContactGroupRow(
            self.contactGroupScrollAreaWidgetContent)
        self.contactGroupScrollAreaWidgetContentLayout.addWidget(
            self.testContactGroupInstance1)
        self.contactGroupScrollAreaWidgetContentLayout.addWidget(
            self.testContactGroupInstance2)

        # set hardware scroll areas only widget to our scrollarea content widget
        self.contactGroupScrollArea.setWidget(
            self.contactGroupScrollAreaWidgetContent)
        # finally add the scroll area to our splitter
        self.splitter.addWidget(self.contactGroupScrollArea)

        # add layout to central widget to mainwindow
        self.selfLayout.addWidget(self.splitter)
        self.theCentralWidet.setLayout(self.selfLayout)
        self.setCentralWidget(self.theCentralWidet)

    def createScrollArea(self) -> QScrollArea:
        scrollArea = QScrollArea(self)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setVerticalStretch(1)
        scrollArea.setSizePolicy(sizePolicy)
        scrollArea.setMinimumSize(QSize(0, 55))
        scrollArea.setFrameShape(QFrame.Shape.Box)  # -> NoFrame maybe?
        scrollArea.setWidgetResizable(True)
        scrollArea.setAlignment(Qt.AlignmentFlag.AlignLeading |
                                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        return scrollArea

    def openSingleWindow(self, windowReference: str) -> None:
        if windowReference in self._singleWindows:
            self._singleWindows[windowReference].raise_()
            self._singleWindows[windowReference].activateWindow()
        else:
            window = None
            match windowReference:
                case "LogWindow":
                    window = ui.LogWindow(LoggerClass.getRootLogger())
                case "ProgramSettingsDialog":
                    window = ui.ProgramSettingsDialog()
            if window:
                window.destroyed.connect(
                    partial(self.closedSingleWindow, windowReference))
                window.show()
                self._singleWindows[windowReference] = window
        logger.debug(self._singleWindows)

    def closedSingleWindow(self, windowReference) -> None:
        logger.debug(f"closed window {windowReference}")
        if windowReference in self._singleWindows:
            del self._singleWindows[windowReference]
        logger.debug(self._singleWindows)

    def _pollHwList(self) -> None:
        """Trigger initial device row loading after startup"""
        self._handleHwListChange(self.server.hwManager.hardwareDevices)

    def _handleHwListChange(self, devices: dict[int, HardwareDevice]) -> None:
        for id, device in devices.items():
            newRow = HardwareEspRow(device._configKey,
                                    self.hardwareScrollAreaWidgetContent)
            device.uiBatteryStateChanged.connect(newRow.lb_espBat.setNum)
            device.uiRssiStateChanged.connect(newRow.lb_espRssi.setNum)
            device.deviceConnectionChanged.connect(newRow.lb_espCon.setState)
            if id in self._hwRows.keys():
                # Row already exists, re-create
                oldRow = self._hwRows[id]
                self.hardwareScrollAreaWidgetContentLayout.replaceWidget(
                    oldRow, newRow)
                oldRow.deleteLater()
            else:
                # It's a new row, append it
                self.hardwareScrollAreaWidgetContentLayout.addWidget(newRow)
            self._hwRows[id] = newRow
        sizes = [0] * len(self.splitter.children())
        sizes[1] = self.hardwareScrollArea.sizeHint().height()
        self.splitter.setSizes(sizes)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event cleanly.

        Args:
            event (QCloseEvent  |  None]): The qt event.
        """
        logger.debug(f"closeEvent in {__class__.__name__}")

        logger.debug("Stopping server...")
        self.server.stop()

        for window in self._singleWindows.values():
            window.close()


class BaseRow(QFrame):
    """The base for hardware and group rows with an expandable row."""

    def __init__(self, parent: QWidget | None) -> None:
        # logger.debug(f"Creating {__class__.__name__}")
        super().__init__(parent)

        self.expandingWidget = None
        self.buildCommonUi()
        self.buildUi()

    def buildCommonUi(self) -> None:
        self.setEnabled(True)
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setLineWidth(1)
        self.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))

        self.selfLayout = QVBoxLayout(self)

    def buildUi(self) -> None:
        raise NotImplementedError

    def createExpandingWidget(self, instance) -> None:
        self.expandingWidget = instance
        self.selfLayout.addWidget(instance)

    def deleteExpandingWidget(self) -> None:
        if self.expandingWidget:
            self.selfLayout.removeWidget(self.expandingWidget)
            self.expandingWidget.close()
            self.expandingWidget = None


class ExpandedWidgetDataRowBase(QHBoxLayout):
    """ The base for the expanding widgets """

    def __init__(self, *args, **kwargs) -> None:
        # logger.debug(f"Creating {__class__.__name__}")
        super().__init__()

        self.buildCommonUi()
        self.buildUi()

    def buildCommonUi(self) -> None:
        self.setContentsMargins(8, 0, -1, 2)

    def buildUi(self) -> None:
        raise NotImplementedError

    def updateValue(self) -> None:
        raise NotImplementedError


class HardwareEspRow(BaseRow):
    """A independent hardware row inside the scroll area."""

    def __init__(self, configKey: str, parent: QWidget | None) -> None:
        # logger.debug(f"Creating {__class__.__name__}")
        super().__init__(parent)
        self._hwSettingsWindow: QWidget | None = None
        self._configKey = configKey

        self._updateStaticText()

    def buildUi(self) -> None:
        self.hl_espTopRow = QHBoxLayout()
        # self.hl_espTopRow.setSizeConstraint(QLayout.SetMinimumSize)

        # all size policys that we need
        sizePolicy_FixedMaximum = QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Maximum)
        sizePolicy_PreferredMaximum = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        # all fonts that we need
        font10 = QFont()
        font10.setPointSize(10)
        font11 = QFont()
        font11.setPointSize(11)

        # The connection status label (symbol)
        self.lb_espCon = ui.StatefulLabel(("\u2716", "\u2705", "\u231B"), self)
        self.lb_espCon.setSizePolicy(sizePolicy_FixedMaximum)
        self.lb_espCon.setState(2)
        self.hl_espTopRow.addWidget(self.lb_espCon)

        # The esp name, mac and ip label
        self.lb_espIdMac = ui.StaticLabel(
            "ESP ", "", "", self)
        self.lb_espIdMac.setSizePolicy(sizePolicy_PreferredMaximum)
        self.lb_espIdMac.setFont(font10)
        self.hl_espTopRow.addWidget(self.lb_espIdMac)

        # the esp wifi rssi label
        self.lb_espRssi = ui.StaticLabel("Wifi: ", "", " dbm", self)
        self.lb_espRssi.setSizePolicy(sizePolicy_PreferredMaximum)
        self.lb_espRssi.setFont(font10)
        self.hl_espTopRow.addWidget(self.lb_espRssi)

        # the esp battery level label
        self.lb_espBat = ui.StaticLabel("Battery: ", "", " V", self)
        self.lb_espBat.setSizePolicy(sizePolicy_PreferredMaximum)
        self.lb_espBat.setFont(font10)
        self.hl_espTopRow.addWidget(self.lb_espBat)

        # spacer
        self.spc_espRow_1 = QSpacerItem(
            10, 2, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.hl_espTopRow.addItem(self.spc_espRow_1)

        # the button to create/destroy the control sub-widget
        self.bt_espExpand = ui.ToggleButton(
            ("\u02C5", "\u02C4"), parent=self)
        self.bt_espExpand.setMaximumWidth(40)
        self.bt_espExpand.setFont(font11)
        self.bt_espExpand.setToolTip("Expand")
        self.bt_espExpand.toggledOn.connect(
            lambda: self.createExpandingWidget(EspMoreInfoWidget(self)))
        self.bt_espExpand.toggledOff.connect(self.deleteExpandingWidget)
        self.hl_espTopRow.addWidget(self.bt_espExpand)

        # button to open the esp settings dialog
        self.bt_openEspSettings = QPushButton(self)
        self.bt_openEspSettings.setMaximumWidth(40)
        self.bt_openEspSettings.setFont(font11)
        self.bt_openEspSettings.setToolTip("Configure")
        self.bt_openEspSettings.setText("\ud83d\udd27")
        self.bt_openEspSettings.clicked.connect(self._openHardwareSettings)
        self.hl_espTopRow.addWidget(self.bt_openEspSettings)

        self.selfLayout.addLayout(self.hl_espTopRow)

    @QSlot()
    def _openHardwareSettings(self):
        if self._hwSettingsWindow:
            self._hwSettingsWindow.raise_()
            self._hwSettingsWindow.activateWindow()
        else:
            self._hwSettingsWindow = EspSettingsDialog(self._configKey)
            self._hwSettingsWindow.destroyed.connect(
                self._closedHardwareSettings)
            self._hwSettingsWindow.show()

    def _closedHardwareSettings(self):
        self._hwSettingsWindow = None

    def _updateStaticText(self) -> None:
        id = config.get(f"{self._configKey}.id")
        name = config.get(f"{self._configKey}.name")
        mac = config.get(f"{self._configKey}.wifiMac")
        connType = config.get(f"{self._configKey}.connectionType")
        connAddr = config.get(f"{self._configKey}.lastIp") if \
            connType == HardwareConnectionType.OSC else \
            config.get(f"{self._configKey}.serialPort")
        self.lb_espIdMac.setText(f"{id} '{name}' ({mac}/{connAddr})")


class EspMoreInfoWidget(QWidget):
    def __init__(self, *args, **kwargs) -> None:
        """Initialize EspMoreInfoWidget."""
        logger.debug(f"Creating {__class__.__name__}")
        super().__init__(*args, **kwargs)

        self.buildUi()

    def buildUi(self) -> None:
        self.selfLayout = QVBoxLayout(self)
        self.setContentsMargins(-1, -1, -1, 0)
        self.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum))

        # the spacing line
        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.selfLayout.addWidget(self.line)

        # the motors label
        self.lb_motorsRow = ui.StaticLabel("Motors: ", "", "", self)
        self.selfLayout.addWidget(self.lb_motorsRow)

        # TODO: this will later be dynamic, just for testing now
        self.rows = []
        for id in range(5):
            row = HardwareMotorChannelRow(id)
            self.selfLayout.addLayout(row)
            self.rows.append(row)

        # a horizontal row for the buttons
        self.bottomButtonRow = QHBoxLayout()
        # the stop app button
        self.bt_stopAllMotors = QPushButton(self)
        self.bt_stopAllMotors.setMaximumWidth(60)
        self.bt_stopAllMotors.setText("Stop all")
        self.bottomButtonRow.addWidget(
            self.bt_stopAllMotors, 0, Qt.AlignmentFlag.AlignLeft)

        self.selfLayout.addLayout(self.bottomButtonRow)

    # handle the close event
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event cleanly.

        Args:
            event QCloseEvent): The QCloseEvent.
        """
        logger.debug(f"closeEvent in {__class__.__name__}")


class HardwareMotorChannelRow(ExpandedWidgetDataRowBase):
    def __init__(self, rowId: int, *args, **kwargs) -> None:
        """Initialize HardwareMotorChannelRow."""
        logger.debug(f"Creating {__class__.__name__}")
        self.rowId = rowId
        self.sliderLocked = False
        super().__init__(*args, **kwargs)

    def buildUi(self) -> None:
        # Motor number
        self.lb_motorNum = ui.StaticLabel("Channel ", str(self.rowId))
        self.addWidget(self.lb_motorNum)

        # the pwm slider
        self.hsld_motorVal = QSlider(Qt.Orientation.Horizontal)
        self.hsld_motorVal.setMinimumSize(QSize(100, 0))
        self.hsld_motorVal.setMaximum(255)
        self.hsld_motorVal.setValue(0)
        self.hsld_motorVal.setTracking(True)
        self.addWidget(self.hsld_motorVal)

        # the pwm number
        self.lb_motorVal = ui.StaticLabel("PWM: ", "0")
        self.addWidget(self.lb_motorVal)

        # enable slider locking while mouse has it grabbed
        self.hsld_motorVal.sliderPressed.connect(self._lockSlider)
        self.hsld_motorVal.sliderReleased.connect(self._unlockSlider)

    # handle the close event
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event cleanly.

        Args:
            event QCloseEvent): The QCloseEvent.
        """
        logger.debug(f"closeEvent in {__class__.__name__}")

    def _lockSlider(self) -> None:
        logger.debug("Slider locked")
        self.sliderLocked = True

    def _unlockSlider(self) -> None:
        logger.debug("Slider unlocked")
        self.sliderLocked = False

    def updateValue(self, value: int) -> None:
        self.lb_motorVal.setNum(value)
        if not self.sliderLocked:
            self.hsld_motorVal.setValue(value)


class ContactGroupRow(BaseRow):
    """A independent contact group row inside the scroll area."""

    def __init__(self, parent: QWidget | None) -> None:
        # logger.debug(f"Creating {__class__.__name__}")
        super().__init__(parent)

    def buildUi(self) -> None:
        self.hl_groupTopRow = QHBoxLayout()

        # all fonts that we need
        font11 = QFont()
        font11.setPointSize(11)

        # the name label
        self.lb_contactGroupName = ui.StaticLabel("Name: ", "Head", "", self)
        # self.lb_contactGroupName.setScaledContents(True)
        self.hl_groupTopRow.addWidget(self.lb_contactGroupName)

        # the vrc data label
        self.lb_groupHasIncomingData = ui.StatefulLabel(
            ("VRC Data: \u274C", "VRC Data: \u2705"), self)
        self.lb_groupHasIncomingData.setState()

        self.hl_groupTopRow.addWidget(self.lb_groupHasIncomingData)

        # spacer
        self.spc_groupRow_1 = QSpacerItem(
            10, 2, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.hl_groupTopRow.addItem(self.spc_groupRow_1)

        # the group info expand button
        self.bt_groupExpand = ui.ToggleButton(
            ("\u02C5", "\u02C4"), parent=self)
        self.bt_groupExpand.setMaximumWidth(40)
        self.bt_groupExpand.setFont(font11)
        self.bt_groupExpand.setToolTip("Expand")
        self.bt_groupExpand.toggledOn.connect(
            lambda: self.createExpandingWidget(ContactGroupPointsWidget(self)))
        self.bt_groupExpand.toggledOff.connect(
            self.deleteExpandingWidget)
        self.hl_groupTopRow.addWidget(self.bt_groupExpand)

        # the open visualizer button
        self.bt_openVisualizer = QPushButton(self)
        self.bt_openVisualizer.setMaximumWidth(40)
        self.bt_openVisualizer.setFont(font11)
        self.bt_openVisualizer.setToolTip("Open visualizer")
        self.bt_openVisualizer.setText("\ud83d\udcc8")
        self.hl_groupTopRow.addWidget(self.bt_openVisualizer)

        # button to open the group settings dialog
        self.bt_openGroupSettings = QPushButton(self)
        self.bt_openGroupSettings.setMaximumWidth(40)
        self.bt_openGroupSettings.setFont(font11)
        self.bt_openGroupSettings.setToolTip("Configure")
        self.bt_openGroupSettings.setText("\ud83d\udd27")
        self.hl_groupTopRow.addWidget(self.bt_openGroupSettings)

        self.selfLayout.addLayout(self.hl_groupTopRow)


class ContactGroupPointsWidget(QWidget):
    def __init__(self, *args, **kwargs) -> None:
        """Initialize ContactGroupPointsWidget."""
        logger.debug(f"Creating {__class__.__name__}")
        super().__init__(*args, **kwargs)

        self.buildUi()

    def buildUi(self) -> None:
        self.selfLayout = QVBoxLayout(self)
        self.setContentsMargins(-1, -1, -1, 0)
        self.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum))

        # the spacing line
        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.selfLayout.addWidget(self.line)

        # the points label
        self.lb_pointsRow = QLabel(self)
        self.lb_pointsRow.setText("Points:")
        self.selfLayout.addWidget(self.lb_pointsRow)

        # TODO: this will later be dynamic, just for testing now
        self.rows = []
        for id in range(5):
            row = PointDetailsRow(id)
            self.selfLayout.addLayout(row)
            self.rows.append(row)

    # handle the close event
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event cleanly.

        Args:
            event QCloseEvent): The QCloseEvent.
        """
        logger.debug(f"closeEvent in {__class__.__name__}")


class PointDetailsRow(ExpandedWidgetDataRowBase):
    def __init__(self, rowId: int, *args, **kwargs) -> None:
        """Initialize PointDetailsRow."""
        logger.debug(f"Creating {__class__.__name__}")
        self.rowId = rowId
        super().__init__(*args, **kwargs)

    def buildUi(self) -> None:
        self.lb_groupPointName = ui.StaticLabel(
            "Name: ", str(self.rowId), parent=self.parent())
        self.addWidget(self.lb_groupPointName, 0, Qt.AlignmentFlag.AlignLeft)
        self.lb_groupPointValue = ui.StaticLabel(
            "Value: ", "0.2", parent=self.parent())
        self.addWidget(self.lb_groupPointValue, 0, Qt.AlignmentFlag.AlignLeft)
        self.addStretch(1)

    def updateValue(self, value: float) -> None:
        self.lb_groupPointValue.setFloat(value)


if __name__ == "__main__":
    print("There is no point running this file directly")
