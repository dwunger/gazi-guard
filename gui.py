import sys
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QProcess
from led_indicator_widget import LedIndicator
from abstract_message import AbstractMessage
import os
# import DemoAppUi
def get_int_date():
    import datetime
    current_date = datetime.datetime.now()
    return current_date.strftime("%Y-%m-%d")
run_number = get_int_date()
log_file = f"LOG_{run_number}.txt"
def logger_iter(iterable):
    with open(log_file, 'a+') as log:
        log.write('#######GUI########\n')
        log.write('iterable: \n')
        log.writelines(iterable)
        log.write('\n')
        log.write('#######GUI########\n')
def logger_str(text):
    with open(log_file, 'a+') as log:
        log.write('#######GUI########\n')
        log.write(text + "\n")
        log.write('#######GUI########\n')

class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)  # Adjust the height as needed
        self.setStyleSheet("background-color: #999999; color: white;")

        # Create the title label
        self.titleLabel = QtWidgets.QLabel(self)
        self.titleLabel.setText("  Pak Merge Tool")
        self.titleLabel.setAlignment(QtCore.Qt.AlignVCenter)
        # self.titleLabel.setAlignment(QtCore.Qt.AlignLeft)

        # Create the minimize button
        self.minimizeButton = QtWidgets.QPushButton(self)
        self.minimizeButton.setText("_")
        self.minimizeButton.setFixedSize(30, 30)
        self.minimizeButton.clicked.connect(self.onMinimizeClicked)  

        # Create the close button
        self.closeButton = QtWidgets.QPushButton(self)
        self.closeButton.setText("X")
        self.closeButton.setFixedSize(30, 30)
        self.closeButton.clicked.connect(self.onCloseClicked)  
        
        # Create a common style sheet for the buttons
        buttonStyle = """
            QPushButton {
                background-color: #999999;
                color: #FFFFFF;
                border: none;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background-color: #CCCCCC;
            }
            QPushButton:pressed {
                background-color: #888888;
            }
        """
        # self.titleLabel.setStyleSheet("background-color: transparent;")
        self.titleLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        
        # Apply the style sheet to the minimize and close buttons
        self.minimizeButton.setStyleSheet(buttonStyle)
        self.closeButton.setStyleSheet(buttonStyle)

        # Create the layout for the title bar
        layout = QtWidgets.QHBoxLayout(self)

        # layout.setStyleSheet("background-color: #999999;")
        layout.addWidget(self.titleLabel)
        # layout.addStretch()

        layout.addWidget(self.minimizeButton)
        layout.addWidget(self.closeButton)
        layout.setAlignment(QtCore.Qt.AlignRight)  
        layout.setSpacing(0)  # Set spacing between buttons to 0
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        self.startPosition = self.mapToGlobal(event.pos())

    def mouseMoveEvent(self, event):
        if self.startPosition is None:
            return  # Skip the event if startPosition is not available

        movePosition = self.mapToGlobal(event.pos())
        diff = movePosition - self.startPosition
        self.startPosition = movePosition
        self.parent().move(self.parent().pos() + diff)

    def onMinimizeClicked(self):
        # Handle minimize button click
        self.parent().showMinimized()

    def onCloseClicked(self):
        # Handle close button click
        self.parent().close()

class OptionsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.originalFlags = self.parent().windowFlags()  # Store the original window flags

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle("Options")
        self.setStyleSheet("QDialog { border: none; }")  # Remove the border using style sheet

        # Create a custom title bar
        titleBar = CustomTitleBar(self)

        # Create the 'Keep on top' toggle button
        self.keepOnTopButton = QtWidgets.QCheckBox("Keep on top", self)
        self.keepOnTopButton.toggled.connect(self.onKeepOnTopToggled)

        # Create the layout for the dialog
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.addWidget(titleBar)
        layout.addWidget(self.keepOnTopButton)
        # layout.addStretch()
        self.setLayout(layout)

        self.setStyleSheet(parent.styleSheet())  # Inherit the style from parent


    def onKeepOnTopToggled(self, checked):
        if checked:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.parent().setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | self.originalFlags)  # Restore the original window flags
        self.parent().show()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, backend_script):
        super().__init__()

        self.backend_script = backend_script
        self.backend_process = None
        self.message = AbstractMessage()  # Initialize message here
        self.pid = os.getpid()
        self.child_pid = None
        self.editor_pid = None
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Pak Tools")
        self.resize(400, 200)  # Set the initial size of the window
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

    # def createToggleLEDButton(self, toolbar):
    #     self.pushButton = QtWidgets.QPushButton("Toggle LED", self)
    #     self.pushButton.clicked.connect(self.onPressButton)
    #     toolbar.addWidget(self.pushButton)

    def createFileMenuButton(self, toolbar):
        menu = QtWidgets.QMenu(self)

        action1 = QtWidgets.QAction("Open...", self)
        # action1.triggered.connect(self.openFileDialog)
        menu.addAction(action1)

        action2 = QtWidgets.QAction("Hide", self)
        menu.addAction(action2)

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
        layout = QtWidgets.QHBoxLayout()

        # Vertically center alignment
        layout.addStretch(1)

        self.led = LedIndicator(self)
        self.led.setDisabled(True)  # Make the LED non-clickable

        layout.addWidget(self.led)

        # Add space between the LED and the text widget
        layout.addSpacing(10)

        text_widget = QtWidgets.QLabel("Mod Status")
        layout.addWidget(text_widget)

        # Vertically center alignment
        layout.addStretch(1)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
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
            self.backend_process.start("python", [self.backend_script])

    def stopBackendProcess(self):
        if self.backend_process is not None:
            self.backend_process.kill()
            self.backend_process = None
            
    @staticmethod
    def parse_stream(raw_data):

        data = raw_data.strip()  # Strip the data
        print(data)
        lines = data.split('\n')
        messages = [line.lstrip('*') for line in lines if line.startswith('*')]
        logger_iter(lines)
        logger_iter(messages)
        return messages
    
    def onListenMain(self):
        # Read the data from the stdout and stderr of the process
        raw_data = self.backend_process.readAll().data().decode()

        # print(f"Raw data: '{raw_data}'")  # Print raw data
        inbound_messages = self.parse_stream(raw_data)
        
        for inbound_message in inbound_messages:
            inbound_message_type, inbound_message = inbound_message.split(':')
            
            response = self.get_response(inbound_message_type, inbound_message)
    def get_response(self, payload_type, payload):
        #map message type and payload to a response for return value
        #start with exhaustive switching
        if payload_type == 'pid':
            self.child_pid = int(payload)
            return self.message.pid(os.getpid())
        if payload_type == 'editor_pid':
            self.editor_pid = int(payload)            
    def onExitMain(self, exit_code, exit_status):
        # Called when the backend process has finished
        print(f"Backend process finished with exit code {exit_code}")
        os.kill(self.pid, 9)
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow("main.py")
    window.show()
    window.init_main_proc()  # Start the backend process
    # window.sendMessageToBackend
    window.send_message(window.message.request('pid'))
    # window.send_message(window.message.event('initialized1'))
    # window.send_message(window.message.event('initialized2'))
    # window.send_message(window.message.event('initialized3'))
    # window.send_message(window.message.event('initialized4'))
    # window.send_message(window.message.event('initialized5'))
    # window.sendMessageToBackend(f"process:{os.getpid}")
    
    sys.exit(app.exec_())