import os
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QProcess
from abstract_message import AbstractMessage
from configs import Config
from led_indicator_widget import LedIndicator
from melder import prompt_to_restart
from options_dialog import OptionsDialog
from titlebar_widget import CustomTitleBar
from utils import resource_path

# TODO: restart main proc on settings update


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.backend_script = None
        self.backend_process = None

        self.message = AbstractMessage()  # Initialize message here
        self.pid = os.getpid()
        self.child_pid = None
        self.editor_pid = None

        # Timer for backend dead event
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(3000)  # 3000 ms
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.onBackendDead)
        self.timer.start()

        self.setupUI()
        self.init_main_proc()  # Start the backend process
        self.send_message(self.message.request('pid'))
    def setupUI(self):
        self.setWindowTitle("Pak Tools")
        self.resize(400, 150)  # Set the initial size of the window
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # Remove the native window frame

        self.createTitleBar()
        self.createToolbar()
        self.createLEDLayout()

    def createTitleBar(self):
        titleBar = CustomTitleBar(self)
        self.setMenuWidget(titleBar)

    def createToolbar(self):
        toolbar = QtWidgets.QToolBar(self)
        toolbar.setMovable(False)  # Disable toolbar movement
        self.addToolBar(toolbar)

        # self.createToggleLEDButton(toolbar)
        self.createFileMenuButton(toolbar)

    def createToggleLEDButton(self, toolbar):
        self.pushButton = QtWidgets.QPushButton("Toggle LED", self)
        self.pushButton.clicked.connect(self.onPressButton)
        toolbar.addWidget(self.pushButton)

    def createFileMenuButton(self, toolbar):
        menu = QtWidgets.QMenu(self)

        action3 = QtWidgets.QAction("Options...", self)
        action3.triggered.connect(self.openOptionsDialog)
        menu.addAction(action3)

        menu_button = QtWidgets.QToolButton(toolbar)
        menu_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")  # Remove the menu indicator arrow
        menu_button.setMenu(menu)
        menu_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        menu_button.setText("File")

        toolbar.addWidget(menu_button)

    def createLEDLayout(self):
        main_layout = QtWidgets.QHBoxLayout()

        left_layout = QtWidgets.QHBoxLayout()
        left_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.led = LedIndicator(self)
        self.led.setDisabled(True)  # Make the LED non-clickable

        left_layout.addWidget(self.led)

        self.text_widget = QtWidgets.QLabel("Mod Status: ")  # Create the text_widget attribute
        left_layout.addWidget(self.text_widget)

        main_layout.addLayout(left_layout)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def onPressButton(self):
        self.led.setChecked(not self.led.isChecked())

    def openOptionsDialog(self):
        # Temporarily remove the "Keep on top" flag
        if self.windowFlags() & QtCore.Qt.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
            self.show()

        # Create and show the dialog
        dialog = OptionsDialog(self)
        dialog.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # Set frameless window hint specifically for the dialog
        # Calculate the center position of the options dialog on the screen
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        dialog.move(center_point)

        dialog.exec_()

        # Restore the "Keep on top" flag
        if dialog.keepOnTopButton.isChecked():
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
            self.show()

    def send_message(self, message):
        if self.backend_process is not None and self.backend_process.state() == QProcess.Running:
            self.backend_process.write(message.encode() + b"\n")
            self.backend_process.waitForBytesWritten()

    def init_main_proc(self):

        if self.backend_process is None:
            self.backend_process = QProcess()
            self.backend_process.setProcessChannelMode(QProcess.MergedChannels)
            self.backend_process.readyRead.connect(self.onListenMain)
            self.backend_process.finished.connect(self.onExitMain)
            self.backend_script = 'background.exe'
            self.backend_process.start(self.backend_script)

    # def init_main_proc(self):
    #     if self.backend_process is not None:
    #         if self.backend_process.state() != QProcess.NotRunning:
    #             return

    #     if getattr(sys, 'frozen', False):
    #         # Running as an executable (compiled version)
    #         executable_path = sys.executable  # Path to the executable
    #         self.backend_script = resource_path("background.exe")
    #     else:
    #         # Running as a script
    #         executable_path = "python"
    #         self.backend_script = resource_path("background.py")

    #     self.backend_process = QProcess()
    #     self.backend_process.setProcessChannelMode(QProcess.MergedChannels)
    #     self.backend_process.readyRead.connect(self.onListenMain)
    #     self.backend_process.finished.connect(self.onExitMain)

    #     # Start the backend process
    #     self.backend_process.start(executable_path, [self.backend_script])

    def stopBackendProcess(self):
        if self.backend_process is not None:
            self.backend_process.kill()
            self.backend_process = None
    @staticmethod
    def parse_stream(raw_data):
        data = raw_data.strip()  # strip block of std::in
        print(data)
        lines = data.split('\n')
        messages = [line.lstrip('*') for line in lines if line.startswith('*')]
        messages = [message.strip() for message in messages] #strip /r from each line
        return messages
    
    def onListenMain(self):
        # Read the data from the stdout and stderr of the process
        try:
            raw_data = self.backend_process.readAll().data().decode()
        except:
            #probably a better way to deal with reloading background process
            raw_data = ""
        inbound_messages = self.parse_stream(raw_data)
        for inbound_message in inbound_messages:
            inbound_message_type, inbound_message = inbound_message.split(':')
            response = self.get_response(inbound_message_type, inbound_message)
            if response:
                self.send_message(response)
    def get_response(self, payload_type, payload):
        from logs import Logger
        logger = Logger()
        
        #map message type and payload to a response for return value
        #start with exhaustive switching
        if payload_type == 'pid':
            self.child_pid = int(payload)
            return self.message.pid(os.getpid())
        if payload_type == 'editor_pid':
            self.editor_pid = int(payload)     
        if payload_type == 'request':
            if payload == 'pid':
                return self.message.pid(os.getpid())
        if payload_type == 'set':
            if payload == 'sync':
                self.led.setChecked(True)
            elif payload == 'desync':
                self.led.setChecked(False)
            self.led.update() 
        if payload_type == 'action':
            self.text_widget.setText(f"Mod Status: {payload}")
        if payload_type == 'awake':
            if payload == 'main':
                self.timer.start()  # Restart the timer
                
    def onBackendDead(self):
        #trigger this if no backend awake message message in last five seconds
        self.led.setChecked(False)
        self.text_widget.setText(f"Background process ended. Restart app to continue")
        # pass
    def exit_all(self):
        processes_to_kill = [pid for pid in (self.editor_pid, self.child_pid, self.pid) if pid]
        for process in processes_to_kill:
            os.kill(process, 9)

    def onExitMain(self, exit_code, exit_status):
        # Called when the backend process has finished
        # os.kill(int(self.editor_pid), 9)
        os.kill(self.pid, 9)        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    # Calculate the center position of the options dialog on the screen
    bottom_right_point = QtWidgets.QDesktopWidget().availableGeometry().bottomRight()
    window.move(bottom_right_point - window.rect().bottomRight())

    window.show()
    sys.exit(app.exec_())