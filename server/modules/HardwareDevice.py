from typing import Type
from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtCore import pyqtSignal as QSignal
from PyQt6.QtCore import pyqtSlot as QSlot

from modules.GlobalConfig import GlobalConfigSingleton, config
from modules.OscMessageTypes import DiscoveryResponseMessage, HeartbeatMessage
from utils import LoggerClass, threadAsStr

logger = LoggerClass.getSubLogger(__name__)


class HardwareDevice(QObject):
    """Represents a physical Hardware Device/ESP."""

    frontendDataChanged = QSignal()
    motorDataSent = QSignal()  # Not sure about this yet
    deviceConnectionChanged = QSignal(bool)

    def __init__(self, key: str) -> None:
        super().__init__()
        self._configKey = f"esps.{key}"
        self._isConnected = False

        # Heartbeat checker
        self._lastHeartbeat: None | HeartbeatMessage = None
        self._heartbeatTimer = QTimer()
        self._heartbeatTimer.timeout.connect(self.updateConnectionStatus)
        self._heartbeatTimer.start(10)

        self.loadSettingsFromConfig()
        self.pinStates: dict[int, int | float] = {
            i: 0 for i in range(self._numMotors)}
        hardwareCommunicationAdapterClass = \
            HardwareCommunicationAdapterFactory.build_adapter(
                self._connectionType)
        if hardwareCommunicationAdapterClass:
            self.hardwareCommunicationAdapter = \
                hardwareCommunicationAdapterClass()
        else:
            raise RuntimeError("Unknown hardware connection type.")

    def loadSettingsFromConfig(self) -> None:
        """Load settings from settings file into object."""
        self._id: int = config.get(f"{self._configKey}.id")
        self._name: str = config.get(f"{self._configKey}.name", "")
        self._connectionType: int = config.get(
            f"{self._configKey}.connectionType", "OSC")
        self._lastIp: str = config.get(f"{self._configKey}.lastIp")
        self._wifiMac: str = config.get(f"{self._configKey}.wifiMac")
        self._serialPort: str = config.get(f"{self._configKey}.serialPort", "")
        self._numMotors: int = config.get(f"{self._configKey}.numMotors", 0)

    def sendPinValues(self) -> None:
        """Create and send current self.pinStates to Hw
        """
        ...

    def processHeartbeat(self, msg: HeartbeatMessage) -> None:
        """Process an incoming heartbeat message from the comms interface.

        Args:
            msg (HeartbeatMessage): The HeartbeatMessage dataclass
        """
        ...

    def updateConnectionStatus(self) -> None:
        """Recalculate the hardware connection status."""
        ...
        # self.deviceConnectionChanged.emit(self._isConnected)

    def close(self) -> None:
        """Closes everything we own and care for
        """
        logger.debug(f"Stopping {__class__.__name__}")
        if hasattr(self, "_heartbeatTimer") and self._heartbeatTimer.isActive():
            self._heartbeatTimer.stop()


class IHardwareCommunicationAdapter():
    """The interface for a HardwareDevice to talk to the actual hardware."""

    heartbeat = QSignal(object)

    def setup(self):
        """A generic setup method to be reimplemented."""
        raise NotImplementedError

    def sendPinValues(self):
        """A generic sendPinValues method to be reimplemented."""
        raise NotImplementedError

    def receivedExtHeartbeat(self):
        """A generic receivedExtHeartbeat method to be reimplemented."""
        raise NotImplementedError

    def close(self):
        """A generic close method to be reimplemented."""
        raise NotImplementedError


class OscCommunicationAdapterImpl(IHardwareCommunicationAdapter, QObject):
    """Handle communication with a device over OSC."""

    def __init__(self, *args, **kwargs) -> None:
        ...


class SlipSerialCommunicationAdapterImpl(IHardwareCommunicationAdapter, QObject):
    """Handle communication with a device over Serial."""

    def __init__(self, *args, **kwargs) -> None:
        ...


class HardwareCommunicationAdapterFactory:
    """Factory class to build hardware communication adapters."""

    @staticmethod
    def build_adapter(adapterType) -> Type[OscCommunicationAdapterImpl] | \
            Type[SlipSerialCommunicationAdapterImpl] | None:
        """Static method to build the appropriate adapter based on the type.

        Args:
            adapterType (str): The type of adapter to build.

        Returns:
            Type[OscCommunicationAdapterImpl] | 
                Type[SlipSerialCommunicationAdapterImpl] |
                None: The built adapter or None if the type is not recognized.
        """
        match adapterType:
            case "OSC":
                return OscCommunicationAdapterImpl
            case "SlipSerial":
                return SlipSerialCommunicationAdapterImpl


if __name__ == "__main__":
    print("There is no point running this file directly")