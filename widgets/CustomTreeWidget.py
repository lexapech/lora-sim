from PySide6.QtWidgets import QTreeView,QMenu
from QCustomItemDelegate import CustomItemDelegate, CustomItem
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import Signal,QEvent
from IHaveProperties import IHaveProperties
from Property import Property

class CustomTreeWidget(QTreeView):
    data_changed_signal = Signal(Property)
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.propertiesTableModel = QStandardItemModel()
        self.propertiesTableModel.setHorizontalHeaderLabels(["Свойство","Значение"])
        self.propertiesTableModel.setColumnCount(2)
        delegate = CustomItemDelegate()
        self.propertiesTableModel.dataChanged.connect(self.data_changed)
        self.setModel(self.propertiesTableModel)
        self.setItemDelegate(delegate)
        self.installEventFilter(self)

    def data_changed(self,data):
        value = self.propertiesTableModel.data(data,1000)
        self.data_changed_signal.emit(value)

    def updatePropertiesTable(self,device):
        root = self.propertiesTableModel.invisibleRootItem()
        self.propertiesTableModel.removeRows(0,root.rowCount(),self.propertiesTableModel.indexFromItem(root))
        if device is None:
            return
        self.addPropList(root,device)

    def eventFilter(self,source,event):
        if event.type() == QEvent.ContextMenu:
            menu = QMenu(self)
            pos = self.viewport().mapFromGlobal(event.globalPos())
            index = source.indexAt(pos)
            index = index.siblingAtColumn(1)
            index0 = index.siblingAtColumn(0)
            parent_index = index.parent().siblingAtColumn(1)
            prop0 = self.propertiesTableModel.itemFromIndex(index0)._data
            prop = self.propertiesTableModel.itemFromIndex(index)._data
            parent_item = self.propertiesTableModel.itemFromIndex(parent_index)
            if parent_item is not None:
                parent_prop = parent_item._data
            if isinstance(prop,Property) and isinstance(prop.get(),list) and prop.add_func is not None:
                menu.addAction('Добавить')
                if menu.exec_(event.globalPos()):
                    prop.add_func()
                    self.data_changed_signal.emit(prop)
                    #self.create_device.emit()
            elif isinstance(prop,str) and isinstance(parent_prop,Property) and isinstance(parent_prop.get(),list):
                menu.addAction('Удалить')
                if menu.exec_(event.globalPos()):
                    lst = parent_prop.get()
                    lst.remove(lst[int(prop0)])
                    self.data_changed_signal.emit(parent_prop)
                    #self.delete_device.emit(self.devices[source.indexAt(event.pos()).row()])
            
            return True
        return super().eventFilter(source,event)


    def addPropList(self,root,obj):
        if isinstance(obj,IHaveProperties):
            data = obj.get_properties()
        else:
            data = obj.__dict__
        for text in data:  
            item = CustomItem(str(text))
            item.setEditable(False)
            show_value = True
            editable = True

            value = data[text]
            if isinstance(value, Property):
                value = value.get()

            if isinstance(value,IHaveProperties):
                self.addPropList(item,value)
                show_value = len(value.get_minimized()) != 0
                editable = False

            elif isinstance(value,list):
                editable = False

                for idx, it in enumerate(value):
                    list_item = CustomItem(str(idx))
                    list_item.setEditable(False)
                    val_item = CustomItem(str(""))
                    val_item.setEditable(False)
                    item.appendRow([list_item,val_item])
                    self.addPropList(list_item,it)

                #show_value = False
            elif isinstance(value,tuple):
                for idx, it in enumerate(value):
                    list_item = CustomItem(str(idx))
                    list_item.setEditable(False)
                    val_item = CustomItem(str(it))
                    val_item.setEditable(False)
                    item.appendRow([list_item,val_item])

            if show_value:
                val_item = CustomItem(data[text])
                val_item.setEditable(editable)
                root.appendRow([item,val_item])
            else:
                val_item = CustomItem("")
                val_item.setEditable(False)
                root.appendRow([item,val_item])
