from PySide6 import QtWidgets, QtCore, QtGui
from enum import Enum

class CustomItem(QtGui.QStandardItem):
    def __init__(self,data):
        super(CustomItem,self).__init__(str(data))
        self._data=data

    def data(self,role=QtCore.Qt.UserRole):
        if role == 1000 and not isinstance(self._data,str):
            return self._data
        return super().data(role)
    def setData(self,value,role=QtCore.Qt.UserRole):
        if role == 1000 and not isinstance(self._data,str):
            self._data=value
            super().setData(str(value),QtCore.Qt.DisplayRole)
        else:
            super().setData(value,role)


class CustomItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        data = index.model().data(index,1000)
        if isinstance(data,Enum) or isinstance(data,bool):  # If this is a ComboBox column (0-indexed)
            combo = QtWidgets.QComboBox(parent)
            if type(data) == bool:
                combo.addItems(["False","True"]) 
            else:
                combo.addItems([x.name for x in type(data)])  
            return combo
        else:
            return super().createEditor(parent, option, index)
    
    def setEditorData(self, editor, index):
        data = index.model().data(index,1000)
        if isinstance(data,Enum):
            print(data)
            combo_index = list(type(data)).index(data)
            if combo_index != -1:
                editor.setCurrentIndex(combo_index)
        else:
            super().setEditorData(editor, index)
    
    def setModelData(self, editor, model, index):
        if isinstance(editor, QtWidgets.QComboBox):  # If this is a ComboBox cell
            value = editor.currentIndex()
            data = model.data(index,1000)
            print(type(data))
            if type(data) == bool:
                model.setData(index,value != 0, 1000)
            else:
                model.setData(index, list(type(data))[value], 1000)
        else:  # If this is a normal cell
            super().setModelData(editor, model, index)
    
