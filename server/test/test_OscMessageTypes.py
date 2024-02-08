import pytest


class TestOscMessageTypes:
    def test_init(self):
        """Test that the module imports and a  classes can be created"""
        try:
            from modules import HeartbeatMessage
            HeartbeatMessage()
        except Exception:
            assert False

        try:
            from modules import DiscoveryResponseMessage
            DiscoveryResponseMessage()
        except Exception:
            assert False

    @pytest.fixture()
    def HeartbeatMessageData(self):
        return ("/patpatpat/heartbeat", ["AA:AA:AA:AA:AA:AA", 1, 2, 3])

    @pytest.fixture()
    def validHeartbeatMessage(self, HeartbeatMessageData):
        """Yield a class-persistant HeartbeatMessage to test on"""
        from modules import HeartbeatMessage
        yield HeartbeatMessage(*HeartbeatMessageData[1])

    def test_HeartbeatMessage(self, validHeartbeatMessage, HeartbeatMessageData):
        from dataclasses import FrozenInstanceError
        from modules import HeartbeatMessage

        """Test if it can check it's own message"""
        assert HeartbeatMessage.isType(*HeartbeatMessageData)

        """Test if data is as expected"""
        m = validHeartbeatMessage
        assert m.mac == "AA:AA:AA:AA:AA:AA" \
            and m.uptime == 1 and m.vccBat == 2 and m.rssi == 3

        """Test if object is mutable"""
        with pytest.raises(FrozenInstanceError):
            m.mac = 123

    @pytest.fixture()
    def DiscoveryResponseMessageData(self):
        return ("/patpatpat/noticeme/senpai", ["AA:AA:AA:AA:AA:AA", 1])

    @pytest.fixture()
    def validDiscoveryResponseMessage(self, DiscoveryResponseMessageData):
        """Yield a class-persistant DiscoveryResponseMessage to test on"""
        from modules import DiscoveryResponseMessage
        yield DiscoveryResponseMessage(*DiscoveryResponseMessageData[1])

    def test_DiscoveryResponseMessage(self, validDiscoveryResponseMessage, DiscoveryResponseMessageData):
        from dataclasses import FrozenInstanceError
        from modules import DiscoveryResponseMessage

        """Test if it can check it's own message"""
        assert DiscoveryResponseMessage.isType(*DiscoveryResponseMessageData)

        """Test if data is as expected"""
        m = validDiscoveryResponseMessage
        assert m.mac == "AA:AA:AA:AA:AA:AA" and m.numMotors == 1

        """Test if object is mutable"""
        with pytest.raises(FrozenInstanceError):
            m.numMotors = 123
