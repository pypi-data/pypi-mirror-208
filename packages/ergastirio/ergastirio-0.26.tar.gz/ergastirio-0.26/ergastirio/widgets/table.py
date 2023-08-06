'''
This module contains several customized widgets used by Ergastirio
'''
import PyQt5.QtWidgets as Qt
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import numpy as np
import os

graphics_dir = os.path.join(os.path.dirname(__file__), '../graphics')

class Table():
    ''' Interactive table. 
    '''
    def __init__(self,  parent):
        self.parent = parent
        self._data = []
        self._data_headers = []
        self.table_widget = Qt.QTableWidget()
        #Qt.QTableWidget.__init__(self, *args)
        #self.verticalHeader().setVisible(False)
        self.refresh_continuosly = True

    def create_gui(self): 
        self.create_widgets()
        self.connect_widgets_events_to_functions()

    def create_widgets(self):
        self.vbox = Qt.QVBoxLayout()
        self.box_UpdateContinuosly = Qt.QCheckBox("Update table continuosly (might slow down measurements for large data).")
        self.box_UpdateContinuosly.setChecked(True)
        self.vbox.addWidget(self.box_UpdateContinuosly)
        self.vbox.addWidget(self.table_widget)

        ### Assign the layout hbox to the wdiget defined in self.parent
        self.parent.setLayout(self.vbox) 
        self.parent.resize(self.parent.minimumSize())

    def connect_widgets_events_to_functions(self):
        self.box_UpdateContinuosly.stateChanged.connect(self.click_box_UpdateContinuosly)

    @property
    def data_headers(self):
        return self._data_headers
    @data_headers.setter
    def data_headers(self,h):
        self._data_headers = h
        horHeaders = self._data_headers 
        self.table_widget.setColumnCount(len(self._data_headers))
        self.table_widget.setHorizontalHeaderLabels(horHeaders)
        self.table_widget.resizeColumnsToContents()

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self,d):
        self._data = d
        rows = len(self._data)
        #self.setRowCount(rows)
        #for m,row in enumerate(self._data):
        #    for n,item in enumerate(row):
        #        newitem = Qt.QTableWidgetItem(str(row[n]))
        #        self.setItem(m, n, newitem)  
        #self.data_headers = self._data_headers #We need to call this after data is added
        #self.resizeRowsToContents()
        #self.scrollToBottom()

    def display_all_data(self):
        # Refreshs the whole table by looking at the current value of data
        self.on_rows_added(Nrows = len(self._data))

    def add_signals(self,
                    signal_data_updated,
                    signal_added_new_rows,
                    signal_deleted_all_data,
                    signal_deleted_last_rows):
        signal_data_updated.connect(self.display_all_data)
        signal_added_new_rows.connect(self.on_rows_added)
        signal_deleted_all_data.connect(self.on_delete_all_data) 
        signal_deleted_last_rows.connect(self.on_last_rows_deleted)
        return

    def on_delete_all_data(self,Nrows):
        #if self._data has been emptied and if on_rows_added() is called with input = 0, it will clean up the table
        temp = self.refresh_continuosly
        self.refresh_continuosly = True
        self.on_rows_added(Nrows)
        self.refresh_continuosly = temp

    def on_last_rows_deleted(self,Nrows):
        #if the last rows of self._data have been removed and on_rows_added() is called with a negative parameters, it will effectively remove the deleted rows from the table
        temp = self.refresh_continuosly
        self.refresh_continuosly = True
        self.display_all_data()
        self.on_rows_added(-Nrows)
        self.refresh_continuosly = temp

    def on_rows_added(self,Nrows):
        if self.refresh_continuosly == False:
            return
        total_rows = len(self._data)
        self.table_widget.setRowCount(total_rows)
        if Nrows > 0:
            rows_shown = total_rows - Nrows
            for m,row in enumerate(self._data[-Nrows:]):
                for n,item in enumerate(row):
                    newitem = Qt.QTableWidgetItem(str(row[n]))
                    self.table_widget.setItem(m+rows_shown, n, newitem)  
            self.data_headers = self._data_headers #We need to call this after data is added
            self.table_widget.resizeRowsToContents()
            self.table_widget.scrollToBottom()

###################################################################################################################################################
### GUI Events Functions.###
###################################################################################################################################################

    def click_box_UpdateContinuosly(self, state):
        if state == QtCore.Qt.Checked:
            self.refresh_continuosly = True
            self.display_all_data()
        else:
            self.refresh_continuosly = False

#################################
### END GUI Events Functions ####
#################################