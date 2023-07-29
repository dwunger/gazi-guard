from PyQt5 import QtCore, QtWidgets, QtGui 

class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)  # Adjust the height as needed
        self.setStyleSheet("background-color: #BEC2C4; color: white;")

        # Color variables
        self.base_color = '#BEC2C4'
        self.title_text_color = '#000000'
        self.button_text_color = '#000000'
        self.hover_color = '#CCCCCC'
        self.pressed_color = '#888888'

        # Load "Bebas Neue" font
        font = QtGui.QFont("Bebas Neue", 9)    
        font.setFamily("Bebas Neue")
        font.setPointSize(8)
        font.setWeight(QtGui.QFont.Thin)  # Set the font weight to Thin
        font.setStretch(145)  # Set the vertical stretch to 125%


        # Set the color of the text
        text_color = QtGui.QColor(255, 0, 0)  # Red color (R, G, B)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Text, text_color)

        # Create the title label
        self.titleLabel = QtWidgets.QLabel(self)
        self.titleLabel.setText("  Gazi  Guard")
        # self.titleLabel.setStyleSheet("color: rgb(225,57,53)")        
        self.titleLabel.setStyleSheet(f"color: {self.title_text_color};")  # Set the text color directly


        self.titleLabel.setAlignment(QtCore.Qt.AlignVCenter)
        self.titleLabel.setFont(font) 
        # self.titleLabel.setPalette(palette)
        
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

        # Create the style sheet for the buttons
        buttonStyle = f"""
            QPushButton {{
                background-color: {self.base_color};
                color: {self.button_text_color};
                border: none;
                padding: 0;
                margin: 0;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.pressed_color};
            }}
        """
        
        self.titleLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        
        # Apply the style sheet to the minimize and close buttons
        self.minimizeButton.setStyleSheet(buttonStyle)
        self.closeButton.setStyleSheet(buttonStyle)

        # Create the layout for the title bar
        layout = QtWidgets.QHBoxLayout(self)

        layout.addWidget(self.titleLabel)

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
            return

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
