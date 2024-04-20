from PySide6.QtWidgets import QListView,QMenu
from PySide6.QtGui import QContextMenuEvent, QAction
from networkDevice.networkDevice import LoraDevice
from PySide6.QtCore import QStringListModel, Qt,QEvent, Signal

class DeviceListWidget(QListView):
    create_device = Signal()
    delete_device = Signal(LoraDevice)
    data_changed = Signal()
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.devices=[]
        self.deviceListModel = QStringListModel()
        self.setModel(self.deviceListModel)
        self.installEventFilter(self)
        self.deviceListModel.dataChanged.connect(self.list_data_changed)
    
    def list_data_changed(self,e):
        
        device = self.devices[e.row()]
        device.name = self.deviceListModel.itemData(e)[0]
        self.data_changed.emit()

    def updateDeviceList(self, devices: list[LoraDevice]):
        self.devices = devices
        self.deviceListModel.setStringList([x.name for x in devices])

    def eventFilter(self,source,event):
        if event.type() == QEvent.ContextMenu:
            menu = QMenu(self)
            if source.indexAt(event.pos()).row() == -1:
                menu.addAction('Добавить')
                if menu.exec_(event.globalPos()):
                    self.create_device.emit()
            else:
                menu.addAction('Удалить')
                if menu.exec_(event.globalPos()):
                    self.delete_device.emit(self.devices[source.indexAt(event.pos()).row()])
            
            return True
        return super().eventFilter(source,event)
