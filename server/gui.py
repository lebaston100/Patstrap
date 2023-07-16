from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
from PyQt6.QtCore import Qt
from server import Server
from config import Config
import time
import sys
import logging
import pathlib

logging.basicConfig(level=logging.DEBUG)

# get local directory as path object
LOCALDIR = pathlib.Path(__file__).parent.resolve()

class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.slider_strength = None

        self.prev_patstrap_status = False
        self.prev_vrchat_status = False

        self.setWindowTitle("leb-Patstrap Server 0.1")
        with open("global.css","r") as file:
            self.setStyleSheet(file.read())

        layoutMain = QVBoxLayout()
        layoutMain.setContentsMargins(0, 0, 0, 0)

        box = QWidget()
        box.setObjectName("mainbackground")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.create_patstrap_status())
        layout.addWidget(self.create_recv_vrchat_data_status())
        layout.addWidget(self.create_settings())
        layout.addWidget(self.create_test())
        
        # create config handler
        self.config = Config(file=LOCALDIR / "patstrap.cfg")
        self.server = Server(self)

        box.setLayout(layout)
        layoutMain.addWidget(box)

        self.setLayout(layoutMain)

    def create_patstrap_status(self) -> QWidget:
        box = QWidget()
        box.setObjectName("section")
        box.setFixedHeight(85)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Patstrap connection")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title_label)

        self.status_hardware_connection = QLabel(" ⬤")
        self.status_hardware_connection.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_hardware_connection.setStyleSheet("color: #b94029; font-size: 30px;")
        layout.addWidget(self.status_hardware_connection)

        box.setLayout(layout)
        return box

    def create_recv_vrchat_data_status(self) -> QWidget:
        box = QWidget()
        box.setObjectName("section")
        box.setFixedHeight(85)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("VRChat data")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title_label)

        self.status_vrchat_connection = QLabel("  ⬤")
        self.status_vrchat_connection.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_vrchat_connection.setStyleSheet("color: #b94029; font-size: 30px;")
        layout.addWidget(self.status_vrchat_connection)

        box.setLayout(layout)
        return box

    def create_settings(self) -> QWidget:
        box = QWidget()
        box.setObjectName("section")
        box.setFixedHeight(85)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Intensity")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label)

        self.slider_strength = QSlider(Qt.Orientation.Horizontal)
        self.slider_strength.setMaximumWidth(200)
        self.slider_strength.setMinimum(0)
        self.slider_strength.setMaximum(100)
        self.slider_strength.setValue(50)
        layout.addWidget(self.slider_strength)

        box.setLayout(layout)
        return box

    def get_intensity(self) -> float:
        if self.slider_strength is None:
            return 0
        return self.slider_strength.value() / 100.0

    def create_test(self) -> QWidget:
        box = QWidget()
        box.setObjectName("section")
        box.setFixedHeight(140)

        layoutH = QHBoxLayout()
        layoutV = QVBoxLayout()
        layoutV.setContentsMargins(20, 20, 20, 20)

        self.test_left_button = QPushButton("Pat left")
        self.test_left_button.clicked.connect(self.pat_left)
        self.test_left_button.setDisabled(True)
        layoutH.addWidget(self.test_left_button)

        self.test_right_button = QPushButton("Pat right")
        self.test_right_button.clicked.connect(self.pat_right)
        self.test_right_button.setDisabled(True)
        layoutH.addWidget(self.test_right_button)

        info_label = QLabel("Test hardware")
        info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_label.setFixedHeight(40)
        layoutV.addWidget(info_label)
        layoutV.addItem(layoutH)

        box.setLayout(layoutV)
        return box

    def pat_left(self) -> None:
        logging.debug("Pat left")
        self.server.oscMotorTxData[0] = 0
        time.sleep(1)
        self.server.oscMotorTxData[0] = 255

    def pat_right(self) -> None:
        logging.debug("Pat right")
        self.server.oscMotorTxData[1] = 0
        time.sleep(1)
        self.server.oscMotorTxData[1] = 255

    def set_patstrap_status(self, status: bool) -> None:
        if self.prev_patstrap_status != status:
            self.prev_patstrap_status = status
            self.status_hardware_connection.setStyleSheet("color: #29b980; font-size: 30px;" if status else "color: #b94029; font-size: 30px;")

            self.test_right_button.setDisabled(not status)
            self.test_left_button.setDisabled(not status)

    def set_vrchat_status(self, status: bool) -> None:
        if self.prev_vrchat_status != status:
            self.prev_vrchat_status = status
            self.status_vrchat_connection.setStyleSheet("color: #29b980; font-size: 30px;" if status else "color: #b94029; font-size: 30px;")

    def closeEvent(self, _) -> None:
        self.server.shutdown()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setFixedSize(400, 425)
    window.show()
    sys.exit(app.exec())
