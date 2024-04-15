from PySide6 import QtWidgets, QtGui, QtCore,QtSvg
from PySide6.QtCore import QPointF,QRectF,Qt,Signal
import sys, math
from networkDevice.networkDevice import LoraDevice

class WorkspaceWidget(QtWidgets.QWidget):
    selectionChanged = Signal(LoraDevice)

    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.viewCenter = QtCore.QPointF(0,0)
        self.zoom = 1
        self.devices=[]
        self.selected = None
        self.moved=False

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

            for d in self.devices:
                if (self.toScene(QPointF(event.pos())) - QPointF(d.position.x,d.position.y)).manhattanLength() < 20:
                    self.selectionChanged.emit(d)
                    self.dragging = False
                    return
            self.moved=False
            self.dragging = True   # Start dragging
            self.drag_start = QtCore.QPointF(event.pos())
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.moved=True
            newpos = QtCore.QPointF(event.pos())
            self.viewCenter -= newpos- self.drag_start# Update position of the point
            self.drag_start = newpos
            self.update()   # Redraw widget to reflect changes
        
    
    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False  # Stop dragging
            if not self.moved:
                self.selectionChanged.emit(None)

    def wheelEvent(self,event):
        delta = event.angleDelta().y()/120
        pos = self.toScene(QtCore.QPointF(self.mapFromGlobal(QtGui.QCursor.pos())))
        self.viewCenter -= (self.viewCenter - pos)*0.1*math.copysign(1,delta)
        self.zoom *= (1+delta*0.05)
        self.update()

    def updateDeviceList(self, devices: list[LoraDevice]):
        self.devices = devices
        self.update()

    def setSelected(self,device):
        self.selected = device
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        renderer = QtSvg.QSvgRenderer("resources/base-station-icon.svg")
        renderer2 = QtSvg.QSvgRenderer("resources/base-station-icon-green.svg")
        for d in self.devices:     
            pos = self.toScreen(QPointF(d.position.x,d.position.y))

            if self.selected is not None and d == self.selected:
                renderer2.render(painter,QRectF(pos - QPointF(10,10),pos + QPointF(10,10)))
            else:
                renderer.render(painter,QRectF(pos - QPointF(10,10),pos + QPointF(10,10)))
            

        pen = QtGui.QPen(Qt.black, 1, Qt.DotLine)
        painter.setPen(pen)

        for x in range(0, self.width(), 20):
            painter.drawLine(self.toScreen((x, -self.height())),self.toScreen((x, self.height())))
            painter.drawLine(self.toScreen((-x, -self.height())),self.toScreen((-x, self.height())))

        for y in range(0, self.height(), 20):
            painter.drawLine(self.toScreen((-self.width(), y)),self.toScreen((self.width(), y)))
            painter.drawLine(self.toScreen((-self.width(), -y)),self.toScreen((self.width(), -y)))
                
        # Draw axes
        pen = QtGui.QPen(Qt.black, 1, Qt.DashLine)
        painter.setPen(pen)

        painter.drawLine(self.toScreen((-self.width(), 0)),self.toScreen((self.width(), 0)))
        painter.drawLine(self.toScreen((0, -self.height())),self.toScreen((0, self.height())))
        
        painter.end()