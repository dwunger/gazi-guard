import os
from PyQt5 import QtCore, QtWidgets
from configs import Config
from melder import prompt_to_restart
from titlebar_widget import CustomTitleBar

class OptionsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.config = Config()  # Initialize config

        self.setupUI()
        self.initSettingsFields()
        self.initApplyButton()

    def setupUI(self):
        self.setMinimumWidth(500)
        self.setWindowTitle("Options")
        self.setStyleSheet("QDialog { border: none; }")  # Remove the border using style sheet

        # Set window flags to make it frameless and always on top
        self.originalFlags = self.parent().windowFlags()
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)

        # Create a custom title bar
        titleBar = CustomTitleBar(self)


        # Create the 'Keep on top' toggle button
        # self.keepOnTopButton = QtWidgets.QCheckBox("Keep on top", self)
        # self.keepOnTopButton.toggled.connect(self.onKeepOnTopToggled)

        # Create the main layout for the dialog
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 2)  # Remove margins
        self.layout.addWidget(titleBar)
        # self.layout.addWidget(self.keepOnTopButton)

    def initSettingsFields(self):
        # Generate form fields for each setting
        tooltips = {
            # Tooltips for each setting...
        }

        for setting in self.config.properties:
            if setting == 'copy_to':
                continue

            # Create QLabel for each setting (if it's not a checkbox)
            if setting not in ['deep_scan', 'overwrite_default', 'hide_unpacked_content', 'use_meld', 'backup_enabled',
                'notifications', 'always_on_top']:
                label = QtWidgets.QLabel(setting.replace('_', ' ').title(), self)
                label.setAlignment(QtCore.Qt.AlignLeft)
                self.layout.addWidget(label)

            # Create the appropriate field widget based on the setting type
            if setting in ['deep_scan', 'use_meld', 'backup_enabled', 'hide_unpacked_content', 'overwrite_default',
                           'notifications', 'always_on_top']:
                field = QtWidgets.QCheckBox(setting.replace('_', ' ').title(), self)
                field.setChecked(getattr(self.config, setting))
            elif setting in ['source_pak_0', 'source_pak_1', 'mod_pak']:
                field = QtWidgets.QComboBox()
                field.addItems([file for file in os.listdir(self.config.target_workspace) if file.endswith(".pak")])
                field.setCurrentText(os.path.basename(getattr(self.config, setting)))
            else:
                field = QtWidgets.QLineEdit(self)
                field.setText(str(getattr(self.config, setting)))

            field.setToolTip(tooltips.get(setting, ""))  # Set tooltip
            setattr(self, f'{setting}_field', field)

            # Create a horizontal layout for each field and add it to the main layout
            horz_layout = QtWidgets.QHBoxLayout()
            horz_layout.addSpacing(10)
            horz_layout.addWidget(field)
            self.layout.addLayout(horz_layout)

    def initApplyButton(self):
        # Add an 'Apply' button to the form to update settings values
        self.apply_button = QtWidgets.QPushButton("Apply", self)
        self.apply_button.setFixedWidth(100)  # Set a fixed width of 100 pixels
        self.apply_button.clicked.connect(self.updateSettings)

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

    def updateSettings(self):
        response = prompt_to_restart()
        print(response)
        if response == False:
            return

        # Update settings values when 'Apply' button is clicked
        for setting in self.config.properties:
            field = getattr(self, f'{setting}_field')
            if setting in ['deep_scan', 'use_meld', 'backup_enabled', 'hide_unpacked_content', 'overwrite_default', 'notifications', 'always_on_top']:
                setattr(self.config, setting, field.isChecked())
            elif isinstance(field, QtWidgets.QLineEdit):
                setattr(self.config, setting, field.text())
            elif isinstance(field, QtWidgets.QComboBox):
                if setting != 'mod_pak':
                    setattr(self.config, setting, field.currentText())
                else:
                    setattr(self.config, setting, os.path.join(self.config.target_workspace, field.currentText()))

        # # Save updated settings to the config.ini file
        # with open(self.config.config_path, 'w') as configfile:
        #     self.config.config_parser.write(configfile)

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