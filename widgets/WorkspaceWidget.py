from PySide6 import QtWidgets, QtGui, QtCore
import sys, math

class WorkspaceWidget(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.viewCenter = QtCore.QPointF(0,0)
        self.zoom = 1

    def toScreen(self,point: [QtCore.QPointF,tuple[int,int]]):
        if isinstance(point,tuple):
            point = QtCore.QPointF(point[0],point[1])
        return (point - self.viewCenter)*self.zoom + QtCore.QPointF(self.width() / 2,self.height() / 2)

    def toScene(self,point: [QtCore.QPointF,tuple[int,int]]):
        if isinstance(point,tuple):
            point = QtCore.QPointF(point[0],point[1])
        return (point - QtCore.QPointF(self.width() / 2,self.height() / 2))/self.zoom + self.viewCenter

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            
            self.dragging = True   # Start dragging
            self.drag_start = QtCore.QPointF(event.pos())
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            newpos = QtCore.QPointF(event.pos())
            self.viewCenter -= newpos- self.drag_start# Update position of the point
            self.drag_start = newpos
            self.update()   # Redraw widget to reflect changes
        
    
    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False  # Stop dragging

    def wheelEvent(self,event):
        delta = event.angleDelta().y()/120
        pos = self.toScene(QtCore.QPointF(self.mapFromGlobal(QtGui.QCursor.pos())))
        self.viewCenter -= (self.viewCenter - pos)*0.1*math.copysign(1,delta)
        self.zoom *= (1+delta*0.05)
        self.update()


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        
        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        for x in range(0, self.width(), 20):
            for y in range(0, self.height(), 20):
                if x < self.width() and y < self.height():
                    painter.drawPoint(self.toScreen((x, y)))
                    painter.drawPoint(self.toScreen((-x, y)))
                    painter.drawPoint(self.toScreen((x, -y)))
                    painter.drawPoint(self.toScreen((-x, -y)))
                
        # Draw axes
        pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(self.toScreen((-self.width(), 0)),self.toScreen((self.width(), 0)))
        painter.drawLine(self.toScreen((0, -self.height())),self.toScreen((0, self.height())))
        
