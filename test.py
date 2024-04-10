from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPainter, QPen
import sys

class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        
app = QApplication(sys.argv)
window = GraphicsView()
# Add a line from (10, 10) to (200, 300)
window.scene.addLine(0,0,100,100)
window.scene.
window.show()
sys.exit(app.exec())