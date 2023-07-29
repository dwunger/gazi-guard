from PyQt5 import QtCore, QtWidgets

class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)  # Adjust the height as needed
        self.setStyleSheet("background-color: #999999; color: white;")

        # Create the title label
        self.titleLabel = QtWidgets.QLabel(self)
        self.titleLabel.setText("  Gazi Guard")
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