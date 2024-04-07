# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtCore import QStringListModel
from PySide6.QtGui import QStandardItem, QStandardItemModel

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_mainwindow import Ui_MainWindow

from main2 import WorkerThread
from networkDevice.networkDevice import LoraDevice
from IHaveProperties import IHaveProperties

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.ui = Ui_MainWindow()
        self.workerThread = WorkerThread()
        self.workerThread.logger.message.connect(self.printLogs)
        self.workerThread.simulation.deviceListChanged.connect(self.updateDeviceList)
 
        self.devices=[]
        self.ui.setupUi(self)

        self.deviceListModel = QStringListModel()
        self.ui.listView.setModel(self.deviceListModel)
        self.ui.listView.clicked.connect(self.on_listview_selection_changed)

        self.propertiesTableModel = QStandardItemModel()
        self.propertiesTableModel.setHorizontalHeaderLabels(["Свойство","Значение"])
        self.propertiesTableModel.setColumnCount(2)
        self.ui.treeView.setModel(self.propertiesTableModel)

    def show(self):
        super(MainWindow, self).show()
        self.workerThread.start()

    def printLogs(self,message):
        self.ui.textEdit.append(message)

    def updateDeviceList(self, devices: list[LoraDevice]):
        self.devices = devices
        self.deviceListModel.setStringList([x.name for x in devices])

    def on_listview_selection_changed(self):
    # Get selection object from view
        selected = self.ui.listView.selectedIndexes()
            
        for index in selected:
            # Retrieve data from the model using QModelIndex
            self.updatePropertiesTable(self.devices[index.row()])

    def updatePropertiesTable(self,device):
        
        root = self.propertiesTableModel.invisibleRootItem()
        self.propertiesTableModel.removeRows(0,root.rowCount(),self.propertiesTableModel.indexFromItem(root))
        self.addPropList(root,device)
        
    def addPropList(self,root,obj):
        if isinstance(obj,IHaveProperties):
            data = obj.get_properties()
        else:
            data = obj.__dict__ 
        for text in data:  
            item = QStandardItem(str(text))
            item.setEditable(False)
           
            show_value = True
            if isinstance(data[text],IHaveProperties):
                self.addPropList(item,data[text])
                show_value = False

            elif isinstance(data[text],list):
                for idx, it in enumerate(data[text]):
                    list_item = QStandardItem(str(idx))
                    list_item.setEditable(False)
                    item.appendRow(list_item)
                    self.addPropList(list_item,it)

                show_value = False

            if show_value:
                 root.appendRow([item,QStandardItem(str(data[text]))])
            else:
                 root.appendRow(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())


