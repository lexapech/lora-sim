# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow,QFileDialog, QTableWidgetItem
from PySide6.QtCore import QStringListModel, Qt,Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from QCustomItemDelegate import CustomItemDelegate, CustomItem

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_mainwindow import Ui_MainWindow
import json

from main2 import WorkerThread
from networkDevice.networkDevice import LoraDevice
from IHaveProperties import IHaveProperties
from simulation import SimulationState

log=None

class MainWindow(QMainWindow):
    file_loaded = Signal(dict)
    def __init__(self, parent=None):
        global log 
        log = self.printLogs
        super(MainWindow, self).__init__(parent=parent)
        self.ui = Ui_MainWindow()
        self.workerThread = WorkerThread()
        self.workerThread.logger.message.connect(self.printLogs)
       
        self.selected = None

        self.ui.setupUi(self)
        self.file_loaded.connect(self.workerThread.load_simulation)
        self.workerThread.simulation.deviceListChanged.connect(self.ui.listView.updateDeviceList)
        self.workerThread.simulation.deviceListChanged.connect(self.ui.graphicsView.updateDeviceList)
        self.workerThread.simulation.deviceListChanged.connect(self.updatePropertiesTableList)
        self.ui.treeView.data_changed_signal.connect(self.workerThread.update_property)
        self.ui.listView.clicked.connect(self.on_listview_selection_changed)
        self.ui.listView.create_device.connect(self.workerThread.simulation.create_empty_device)
        self.ui.listView.delete_device.connect(self.workerThread.simulation.delete_device)
        self.ui.graphicsView.selectionChanged.connect(self.on_workspace_selection)
        self.ui.listView.data_changed.connect(self.workerThread.simulation.update_device_list)

        self.ui.pushButton_3.clicked.connect(self.workerThread.simulation.start)
        self.ui.pushButton_2.clicked.connect(self.workerThread.simulation.pause)
        self.ui.pushButton.clicked.connect(self.workerThread.simulation.stop)
        self.workerThread.simulation.state_changed.connect(self.update_buttons)

        self.ui.action.triggered.connect(self.workerThread.reset)
        self.ui.action_2.triggered.connect(self.open_file)
        self.ui.action_4.triggered.connect(self.save_file)

    def open_file(self):
        filters = ["JSON files (*.json)"]  # define your own filter here
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open File', 'simulation.json',";;".join(filters))
        if fileName:
            file = open(fileName,"r")
            self.file_loaded.emit(json.loads(file.read())) 
            file.close()
            log(f"Project loaded from file {fileName}")  # or do something else with the filename
        
    def save_file(self):
        filters = ["JSON files (*.json)"]  # define your own filter here
        fileName, _ = QFileDialog.getSaveFileName(self, 'Save File', 'simulation',";;".join(filters))
        if fileName:
            file = open(fileName,"w")
            file.write(json.dumps( self.workerThread.simulation.to_json()))
            file.close()
            log(f"Project saved to file {fileName}")   # or do something else with the filename
        

    def show(self):
        super(MainWindow, self).show()
        self.workerThread.start()

    def update_buttons(self,state):
        if state == SimulationState.STARTED:
            self.ui.pushButton_3.setDown(True)
            self.ui.pushButton_2.setDown(False)
            self.ui.pushButton.setDown(False)
        elif state == SimulationState.PAUSED:
            self.ui.pushButton_3.setDown(False)
            self.ui.pushButton_2.setDown(True)
            self.ui.pushButton.setDown(False)
        elif state == SimulationState.STOPPED:
            self.ui.pushButton_3.setDown(False)
            self.ui.pushButton_2.setDown(False)
            self.ui.pushButton.setDown(False)


    def printLogs(self,*message: object):
        for o in message:
            self.ui.textEdit.append(str(o))

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
    widget.workerThread.stop()
    sys.exit(ret)


