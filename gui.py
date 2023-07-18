import sys
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QProcess
from LedIndicatorWidget import *
# import DemoAppUi



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
        self.backend_process = None  # Initialize the backend_process here

        self.setWindowTitle("Pak Tools")
        self.resize(400, 200)  # Set the initial size of the window

        # Remove the native window frame
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        # Create a custom title bar
        titleBar = CustomTitleBar(self)
        self.setMenuWidget(titleBar)

        # Create a toolbar
        toolbar = QtWidgets.QToolBar(self)
        toolbar.setMovable(False)  # Disable toolbar movement
        self.addToolBar(toolbar)

        # Create the layout for the LED
        layout = QtWidgets.QHBoxLayout()
        self.led = LedIndicator(self)
        self.led.setDisabled(True)  # Make the led non-clickable
        layout.addWidget(self.led)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.pushButton = QtWidgets.QPushButton("Toggle LED", self)
        self.pushButton.clicked.connect(self.onPressButton)
        toolbar.addWidget(self.pushButton)

        # Create a menu
        menu = QtWidgets.QMenu(self)

        # Create actions for the menu
        action1 = QtWidgets.QAction("Open...", self)
        # action1.triggered.connect(self.openFileDialog)
        menu.addAction(action1)

        action2 = QtWidgets.QAction("Hide", self)
        menu.addAction(action2)

        # Create actions for the menu
        action3 = QtWidgets.QAction("Options...", self)
        action3.triggered.connect(self.openOptionsDialog)
        menu.addAction(action3)

        # Create a button in the toolbar to display the menu
        menu_button = QtWidgets.QToolButton(toolbar)
        menu_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")  # Remove the menu indicator arrow
        menu_button.setMenu(menu)
        menu_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        menu_button.setText("File")

        # Add the button to the toolbar
        toolbar.addWidget(menu_button)
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
            
    def sendMessageToBackend(self, message):
        if self.backend_process is not None and self.backend_process.state() == QProcess.Running:
            self.backend_process.write(message.encode() + b"\n")
            self.backend_process.waitForBytesWritten()
            
    def startBackendProcess(self):
        if self.backend_process is None:
            self.backend_process = QProcess()
            self.backend_process.setProcessChannelMode(QProcess.MergedChannels)
            self.backend_process.readyRead.connect(self.onReadyRead)
            self.backend_process.finished.connect(self.onBackendFinished)
            self.backend_process.start("python", [self.backend_script])

    def stopBackendProcess(self):
        if self.backend_process is not None:
            self.backend_process.kill()
            self.backend_process = None
            
    def onReadyRead(self):
        # Read the data from the stdout and stderr of the process
        raw_data = self.backend_process.readAll().data().decode()
        data = raw_data.strip()  # Strip the data
        print(f"Raw data: '{raw_data}'")  # Print raw data
        print('**********************')
        print(f"Stripped data: '{data}'")  # Print stripped data
        
        if data == "sync":
            # Process data
            self.led.setChecked(True)
            self.led.update()  # Force the led widget to redraw itself


    def onBackendFinished(self, exit_code, exit_status):
        # Called when the backend process has finished
        print(f"Backend process finished with exit code {exit_code}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow("main.py")
    window.show()
    window.startBackendProcess()  # Start the backend process

    window.sendMessageToBackend("Initialized")
    
    sys.exit(app.exec_())