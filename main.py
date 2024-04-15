# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtCore import QStringListModel, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from QCustomItemDelegate import CustomItemDelegate, CustomItem
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
       
        self.selected = None

        self.ui.setupUi(self)
        self.workerThread.simulation.deviceListChanged.connect(self.ui.listView.updateDeviceList)
        self.workerThread.simulation.deviceListChanged.connect(self.ui.graphicsView.updateDeviceList)
        self.workerThread.simulation.deviceListChanged.connect(self.updatePropertiesTableList)
        self.ui.treeView.data_changed_signal.connect(self.workerThread.update_property)
        self.ui.listView.clicked.connect(self.on_listview_selection_changed)
        self.ui.listView.create_device.connect(self.workerThread.simulation.create_empty_device)
        self.ui.listView.delete_device.connect(self.workerThread.simulation.delete_device)
        self.ui.graphicsView.selectionChanged.connect(self.on_workspace_selection)
        self.ui.listView.data_changed.connect(self.workerThread.simulation.update_device_list)

    def show(self):
        super(MainWindow, self).show()
        self.workerThread.start()

    def printLogs(self,message):
        self.ui.textEdit.append(message)

    def on_workspace_selection(self, dev):
        self.set_selection(dev)

    def set_selection(self,dev):
        self.selected = dev
        self.ui.graphicsView.setSelected(dev)
        self.ui.treeView.updatePropertiesTable(dev)
        if dev is None:
            index=self.ui.listView.deviceListModel.index(-1,0)
        else:
            index=self.ui.listView.deviceListModel.index(self.ui.listView.devices.index(dev),0)
        self.ui.listView.setCurrentIndex(index)

    def on_listview_selection_changed(self):
    # Get selection object from view
        selected = self.ui.listView.selectedIndexes()
            
        for index in selected:
            # Retrieve data from the model using QModelIndex
            dev = self.ui.listView.devices[index.row()]
            self.set_selection(dev)
            return
        if self.selected in self.ui.listView.devices:
            self.set_selection(self.selected)
        else:
            self.set_selection(None)


    def updatePropertiesTableList(self,devices):
       
        self.on_listview_selection_changed()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.setWindowState(Qt.WindowMaximized)
    widget.show()
    ret = app.exec()
    widget.workerThread.quit()
    sys.exit(ret)


