from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QFileDialog
from enum import Enum
from util.Property import Property
from util.path import Path


class CustomItem(QtGui.QStandardItem):
    def __init__(self,data):
        
        if isinstance(data,Property):
            val = data.get()
            if isinstance(val,list):
                super(CustomItem,self).__init__(str(""))
            else:
                super(CustomItem,self).__init__(str(val))
            self._data=data   
        else:     
            super(CustomItem,self).__init__(str(data))
            self._data=data
            
        

    def data(self,role=QtCore.Qt.UserRole+1):
        if role == 1000:
            return self._data
        return super().data(role)
    def setData(self,value,role=QtCore.Qt.UserRole+1):
        if role == 1000:
            if isinstance(self._data,Property):
                self._data.set(value)
            else:
                self._data=value
            super().setData(str(value),QtCore.Qt.DisplayRole)
        else:
            super().setData(value,role)


class CustomItemDelegate(QtWidgets.QStyledItemDelegate):        

    def __init__(self, parent=None):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        
        data = index.model().data(index,1000)
        if isinstance(data,Property):
            data = data.get()
        if isinstance(data,Enum) or isinstance(data,bool):  # If this is a ComboBox column (0-indexed)
            combo = QtWidgets.QComboBox(parent)
            if type(data) == bool:
                combo.addItems(["False","True"]) 
            else:
                combo.addItems([x.name for x in type(data)])  
            return combo
        elif isinstance(data, Path):
            filters = ["Python scripts (*.py)"]  # define your own filter here
            fileName, _ = QFileDialog.getOpenFileName(None, 'Open File', 'routing.py',";;".join(filters))
            editor = super().createEditor(parent, option, index)
            editor.setText(fileName)
            return editor
        else:
            return super().createEditor(parent, option, index)
    
    def setEditorData(self, editor, index):
        data = index.model().data(index,1000)
        if isinstance(data,Property):
            data = data.get()
        if isinstance(data,Enum):
            combo_index = list(type(data)).index(data)
            if combo_index != -1:
                editor.setCurrentIndex(combo_index)
        elif isinstance(data, Path):
            pass
        else:
            super().setEditorData(editor, index)
    
    def setModelData(self, editor, model, index):
        if isinstance(editor, QtWidgets.QComboBox):  # If this is a ComboBox cell
            value = editor.currentIndex()
            data = model.data(index,1000)
            if isinstance(data,Property):
                data = data.get()
            if type(data) == bool:
                model.setData(index,value != 0, 1000)
            else:
                model.setData(index, list(type(data))[value], 1000)
        else:  # If this is a normal cell
            value = editor.text()
            model.setData(index,str(value), 1000)
            #super().setModelData(editor, model, index)

