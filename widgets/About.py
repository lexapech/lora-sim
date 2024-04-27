
from PySide6 import QtWidgets, QtGui, QtCore

class AboutWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("About")
        
        # Create a label for the application icon and text
        layout = QtWidgets.QVBoxLayout()
        
        
        textEdit = QtWidgets.QLabel()
        aboutText = "LoraSim 2024"
        textEdit.setText(aboutText)

        layout.addWidget(textEdit)
        
        self.setLayout(layout)