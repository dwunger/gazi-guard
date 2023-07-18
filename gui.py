import sys
import threading
from PyQt5 import QtWidgets, QtCore

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

        self.setWindowTitle("Options")
        self.setStyleSheet(parent.styleSheet())  # Inherit the style from parent

        # Create the 'Keep on top' toggle button
        self.keepOnTopButton = QtWidgets.QCheckBox("Keep on top", self)
        self.keepOnTopButton.toggled.connect(self.onKeepOnTopToggled)

        # Create the layout for the dialog
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.keepOnTopButton)
        self.setLayout(layout)

    def onKeepOnTopToggled(self, checked):
        if checked:
            self.parent().setWindowFlags(self.parent().windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.parent().setWindowFlags(self.parent().windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.parent().show()  # The window needs to be shown again after modifying window flags

class GuiThread(threading.Thread):
    def run(self):
        # Create a new application instance
        app = QtWidgets.QApplication(sys.argv)

        # Create a main window
        window = QtWidgets.QMainWindow()
        window.setWindowTitle("Pak Tools")
        window.resize(400, 200)  # Set the initial size of the window

        # Remove the native window frame
        window.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        # Create a custom title bar
        titleBar = CustomTitleBar(window)
        window.setMenuWidget(titleBar)

        # Create a toolbar
        toolbar = QtWidgets.QToolBar(window)
        toolbar.setMovable(False)  # Disable toolbar movement
        window.addToolBar(toolbar)

        # Create a menu
        menu = QtWidgets.QMenu(window)

        # Create actions for the menu
        action1 = QtWidgets.QAction("Open...", window)
        # action1.triggered.connect(self.openFileDialog)
        menu.addAction(action1)

        action2 = QtWidgets.QAction("Hide", window)
        menu.addAction(action2)
        # Create actions for the menu
        # action3 = QtWidgets.QAction("Options...", window)
        # action3.triggered.connect(self.openOptionsDialog)
        # menu.addAction(action3)

        # Create a button in the toolbar to display the menu
        menu_button = QtWidgets.QToolButton(toolbar)
        menu_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")  # Remove the menu indicator arrow
        menu_button.setMenu(menu)
        menu_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        menu_button.setText("File")

        # Add the button to the toolbar
        toolbar.addWidget(menu_button)
        # def openOptionsDialog(self):
        #     dialog = OptionsDialog(self)
        #     dialog.exec_()

        # Display the window
        window.show()

        # Start the application event loop
        app.exec_()