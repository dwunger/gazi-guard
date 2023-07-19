import os
import sys
import threading

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QProcess

from abstract_message import AbstractMessage
from configs import Config
from led_indicator_widget import LedIndicator
from melder import prompt_to_restart

# import DemoAppUi
def get_int_date():
    import datetime
    current_date = datetime.datetime.now()
    return current_date.strftime("%Y-%m-%d")
run_number = get_int_date()
log_file = f"LOG_{run_number}.log"
def logger_iter(iterable):
    with open(log_file, 'a+') as log:
        log.write('#######GUI_START_MESSAGE########\n')
        log.write('iterable: \n')
        log.writelines(iterable)
        log.write('\n')
        log.write('#######GUI_END_MESSAGE########\n')
def logger_str(text):
    with open(log_file, 'a+') as log:
        log.write('#######GUI_START_MESSAGE########\n')
        log.write(text + "\n")
        log.write('#######GUI_END_MESSAGE########\n')

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
        
        self.startPosition = None #Dealing with AttributeError: 'CustomTitleBar' object has no attribute 'startPosition'
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
            return  #Dealing with AttributeError: 'CustomTitleBar' object has no attribute 'startPosition'

        movePosition = self.mapToGlobal(event.pos())
        diff = movePosition - self.startPosition
        self.startPosition = movePosition
        self.parent().move(self.parent().pos() + diff)

    def onMinimizeClicked(self):
        # Handle minimize button click
        self.parent().showMinimized()

    def onCloseClicked(self):
        # Handle close button click
        try:
            parent = self.parent()
            parent.exit_all()
        except:
            self.parent().close()
#TODO: restart main proc on settings update
#TODO: remove unused file methods
#TODO: gracefully close editor with request and wait for confirmation
# class OptionsDialog(QtWidgets.QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)

#         self.originalFlags = self.parent().windowFlags()  # Store the original window flags

#         self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
#         self.setWindowTitle("Options")
#         self.setStyleSheet("QDialog { border: none; }")  # Remove the border using style sheet

#         # Create a custom title bar
#         titleBar = CustomTitleBar(self)

#         # Create the 'Keep on top' toggle button
#         self.keepOnTopButton = QtWidgets.QCheckBox("Keep on top", self)
#         self.keepOnTopButton.toggled.connect(self.onKeepOnTopToggled)

#         # Create the layout for the dialog
#         layout = QtWidgets.QVBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
#         layout.addWidget(titleBar)
#         layout.addWidget(self.keepOnTopButton)
#         # layout.addStretch()
#         self.setLayout(layout)

#         self.setStyleSheet(parent.styleSheet())  # Inherit the style from parent

#TODO: create prompt at start of update method then restart background proc
class OptionsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.config = Config()  # Initialize config
        self.setMinimumWidth(500)  # Replace '500' with your desired minimum width.

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
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 2)  # Remove margins
        self.layout.addWidget(titleBar)
        self.layout.addWidget(self.keepOnTopButton)

        # Initialize and display settings fields
        self.add_settings_fields()

        # Inherit the style from parent
        self.setStyleSheet(parent.styleSheet())

    def add_settings_fields(self):
        # Generate form fields for each setting
        tooltips = {
            'target_workspace': 'Folder containing source \nmaterials: source_pak_0, source_pak_1, \nand mod_pak',
            'deep_scan': 'Compares files line-wise for \nchanges.',
            'source_pak_0': 'Name of data0.pak (source archive\n containing original scripts).',
            'source_pak_1': 'Name of data1.pak (source archive\n containing original scripts).',
            'mod_pak': 'Name of dataX.pak (mod archive containing\n mod\'s scripts).',
            'overwrite_default': 'If true: mod_pak overwrites changes to unpacked archive on new load \nof this tool. If false: unpacked \narchive overwrites changes to mod_pak on \nnew load of this tool.',
            'hide_unpacked_content': 'Set OS hidden flag to \nunpacked directory.',
            'meld_config_path': 'Path to Meld.exe as per config.ini.\n Falls back to None which scans \npath and again falls back to call \ninstaller for Meld.',
            'use_meld': 'Launch Meld editor after unpacking mod\n and source scripts.',
            'backup_enabled': 'Create backup of mod_pak (mod scripts)\n on startup.',
            'backup_count': 'Number of rolling backups for backup \nmanager to retain.',
        }

        for setting in self.config.properties:
            if setting == 'copy_to': 
                continue
            if setting not in ['deep_scan', 'overwrite_default','hide_unpacked_content', 'use_meld', 'backup_enabled']:
                # Create QLabel for each setting
                label = QtWidgets.QLabel(setting.replace('_', ' ').title(), self)
                label.setAlignment(QtCore.Qt.AlignLeft)
                self.layout.addWidget(label)

            if setting in ['deep_scan', 'use_meld', 'backup_enabled', 'hide_unpacked_content', 'overwrite_default']:
                field = QtWidgets.QCheckBox(setting.replace('_', ' ').title(), self)
                field.setChecked(getattr(self.config, setting))
            elif setting in ['source_pak_0', 'source_pak_1', 'mod_pak']:
                field = QtWidgets.QComboBox()
                field.addItems([file for file in os.listdir(self.config.target_workspace) if file.endswith(".pak")])
                field.setCurrentText(str(getattr(self.config, setting)))
            else:
                field = QtWidgets.QLineEdit(self)
                field.setText(str(getattr(self.config, setting)))

            field.setToolTip(tooltips.get(setting, ""))  # Set tooltip
            setattr(self, f'{setting}_field', field)
            horz_layout = QtWidgets.QHBoxLayout()
            horz_layout.addSpacing(10)
            horz_layout.addWidget(field)
            self.layout.addLayout(horz_layout)

            # field.setStyleSheet('''padding: 4px;
            #                     margin: 4px;
            #                     ''')

        # Add an 'Apply' button to the form to update settings values
        self.apply_button = QtWidgets.QPushButton("Apply", self)
        self.apply_button.setFixedWidth(100)  # Set a fixed width of 100 pixels
        self.apply_button.clicked.connect(self.update_settings)

        # Create a horizontal layout for the apply button
        button_layout = QtWidgets.QHBoxLayout()

        # Add the apply button to the layout
        button_layout.addWidget(self.apply_button)

        # Add spacing on the right side
        button_layout.addSpacing(10)  # Adjust the spacing value as needed

        # Create a vertical layout for the main content
        content_layout = QtWidgets.QVBoxLayout()

        # Add the button layout to the content layout
        content_layout.addLayout(button_layout)

        # Add spacing at the bottom
        content_layout.addSpacing(10)  # Adjust the spacing value as needed

        # Add the content layout to the main layout
        self.layout.addLayout(content_layout)


    def update_settings(self):
        response = prompt_to_restart()
        print(response)
        if response == False:
            return
        
        # Update settings values when 'Apply' button is clicked
        for setting in self.config.properties:
            field = getattr(self, f'{setting}_field')
            if setting in ['deep_scan', 'use_meld', 'backup_enabled', 'hide_unpacked_content', 'overwrite_default']:
                setattr(self.config, setting, field.isChecked())
            elif isinstance(field, QtWidgets.QLineEdit):
                setattr(self.config, setting, field.text())
            elif isinstance(field, QtWidgets.QComboBox):
                setattr(self.config, setting, field.currentText())

        # Save updated settings to the config.ini file
        with open(self.config.config_path, 'w') as configfile:
            self.config.config_parser.write(configfile)
        parent = self.parent()
        parent.backend_process.kill()
        parent.backend_process = None
        parent.init_main_proc()
        self.close()
        

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

    # def createToggleLEDButton(self, toolbar):
    #     self.pushButton = QtWidgets.QPushButton("Toggle LED", self)
    #     self.pushButton.clicked.connect(self.onPressButton)
    #     toolbar.addWidget(self.pushButton)

    def createFileMenuButton(self, toolbar):
        menu = QtWidgets.QMenu(self)

        # action1 = QtWidgets.QAction("Open...", self)
        # # action1.triggered.connect(self.openFileDialog)
        # menu.addAction(action1)

        # action2 = QtWidgets.QAction("Hide", self)
        # menu.addAction(action2)

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

        text_widget = QtWidgets.QLabel("Mod Repack Status")
        left_layout.addWidget(text_widget)

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
        # logger_iter(lines)
        # logger_iter(messages)
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
        if payload_type == 'set':
            if payload == 'sync':
                self.led.setChecked(True)
            elif payload == 'desync':
                self.led.setChecked(False)
            self.led.update() 
            
    def exit_all(self):
        processes_to_kill = [pid for pid in (self.editor_pid, self.child_pid, self.pid) if pid]
        for process in processes_to_kill:
            os.kill(process, 9)

    def onExitMain(self, exit_code, exit_status):
        # Called when the backend process has finished
        os.kill(self.editor_pid, 9)
        print(f"Backend process finished with exit code {exit_code}")
        # os.kill(self.pid, 9)
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow("main.py")
    window.show()
    window.init_main_proc()  # Start the backend process

    window.send_message(window.message.request('pid'))

    sys.exit(app.exec_())