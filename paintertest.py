from PySide6 import QtWidgets, QtGui, QtCore
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle("Drawing")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.begin(self)
        
        pen = QtGui.QPen(QtGui.QColor('blue'), 3, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        rect = QtCore.QRectF(10, 20, 80, 60)
        painter.drawText(rect, "Hello PySide6!")
        
        pen.setStyle(QtCore.Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(15, 25, 70, 40)
        
        brush = QtGui.QBrush(QtGui.QColor('green'), QtCore.Qt.Dense3Pattern)
        painter.setBrush(brush)
        painter.drawRect(65, 85, 120, 70)
        
        path = QtGui.QPainterPath()
        path.moveTo(40, 10)
        path.lineTo(90, 80)
        path.cubicTo(30, 90, 50, 20, 70, 60)
        painter.drawPath(path)
        
        for x in range(0, self.width(), 20):
            for y in range(0, self.height(), 20):
                painter.drawPoint(x, y)
                
        # Draw axes
        pen = QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        
        painter.drawLine(0, self.height() // 2, self.width(), self.height() // 2) # x-axis
        painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height()) # y-axis
        

        painter.end()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow()
    window.show()

    sys.exit(app.exec())