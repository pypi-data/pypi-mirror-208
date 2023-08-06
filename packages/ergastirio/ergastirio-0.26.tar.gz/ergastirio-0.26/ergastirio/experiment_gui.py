import PyQt5.QtWidgets as Qt# QApplication, QWidget, QMainWindow, QPushButton, QHBoxLayout
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import logging
import ergastirio.panels
import ergastirio.widgets
import ergastirio.utils
import ergastirio.styles
from importlib.metadata import version  

class experiment_gui():
    def __init__(self, exp, parent):
        self.exp = exp
        self.app = self.exp.app
        self.parent = parent 
        self.logger = self.exp.logger

        self.set_up_experiment_gui()
        self.exp.fire_all_signals() #ask the experiment to "fire" all of its signals, in order to communicate to different parts of the GUI the current values of several parameters

    def set_up_experiment_gui(self):
        self.container_connectramps = self.parent.advanced_panels['connect_ramps']['container']
        self.container_statusselector = self.parent.advanced_panels['status_selector']['container']
        
        self.container_tabledata = self.parent.basic_panels['tabledata']['container']
        self.container_plots = self.parent.basic_panels['plots']['scrollarea']
        self.container_instruments = self.parent.basic_panels['instruments']['container']

        self.create_gui_table_data()
        self.create_gui_plots()
    
        if not self.create_gui_instruments(): #Create GUIs for all loaded instruments 
            return False

        self.create_gui_connectramps()
        self.create_gui_statusselector()
        
        self.link_data_to_gui()

        #if 'DefaultView' in exp.config.keys():
        #    QtCore.QTimer.singleShot(1, lambda : exp.mainwindow.set_view(exp.config['DefaultView']))

        return True

    def create_gui_connectramps(self):
        self.connectramps_panel_box = Qt.QGroupBox()
        layout = Qt.QVBoxLayout()
        self.connectramps_panel = ergastirio.panels.ramp_connection( parent = self.connectramps_panel_box ,
                                                                    experiment = self.exp)
        layout.addWidget(self.connectramps_panel_box)
        self.container_connectramps.setLayout(layout)
        self.connectramps_panel.create_gui()
        
    def create_gui_statusselector(self):
        self.statusselector_panel_box = Qt.QGroupBox()
        layout = Qt.QVBoxLayout()
        self.statusselector_panel = ergastirio.panels.status_selector( parent = self.statusselector_panel_box,
                                                                    experiment = self.exp)
        layout.addWidget(self.statusselector_panel_box)
        self.container_statusselector.setLayout(layout)
        self.statusselector_panel.create_gui()

    def create_gui_instruments(self):
        '''
        Create GUIs for all loaded instruments, and for the acquisition control panel

        container
            QWidget which will contain the GUIs
        '''

        #if ('Alignment_Instruments_Window' in self.exp.config.keys())  and self.exp.config['Alignment_Instruments_Window']=='H':
        #    box = Qt.QHBoxLayout()
        #else: 
        box = Qt.QVBoxLayout()

        self.logger.info(f"Creating GUI for all loaded instruments...")
    
        for i,instrument in enumerate(self.exp.instruments):
            self.exp.instruments[i]['frame'] = Qt.QGroupBox() # Qt.QWidget()
            self.exp.instruments[i]['frame'].setObjectName(self.exp.instruments[i]['name']+'_frame')
            string = "QGroupBox#"+ self.exp.instruments[i]['frame'].objectName()
            self.exp.instruments[i]['frame'].setStyleSheet(string + ergastirio.styles.instrument_box + string + ergastirio.styles.instrument_boxtitle) #This line changes the style of ONLY this QWdiget

            self.exp.instruments[i]['frame'].setTitle(f"{self.exp.instruments[i]['name']} ({self.exp.instruments[i]['type']} v{version(self.exp.instruments[i]['type'])})")
        
            self.exp.instruments[i]['gui'] = self.exp.instruments[i]['device_module'].gui(interface = self.exp.instruments[i]['interface'],parent=self.exp.instruments[i]['frame'])

            self.exp.instruments[i]['frame'].resize(self.exp.instruments[i]['frame'].sizeHint())
            box.addWidget(self.exp.instruments[i]['frame'] )
        box.addStretch(1)

        self.container_instruments.setLayout(box) #This line makes sure that all widgest defined so far are assigned to the widget defined in container
        self.container_instruments.resize(self.container_instruments.sizeHint())
        return True

    def create_gui_plots(self):
        '''
        Create GUIs for all plots.
        Note: we keep two separated list, self.plots and self.exp.plots
        self.plots[plotindex] contains all the GUI objects for the plot identified by index = plotindex
        self.exp.plots[plotindex] contains all the non-GUI objects for the plot identified by index = plotindex

        '''
        self.logger.info(f"Creating GUI for all plots...")

        mdi = Qt.QMdiArea() #Create an mdi area which will contain the plots
        self.plots =[]
        for plotindex, plot in enumerate(self.exp.plots):
            self.plots.append(dict())
            #For each plot we define a QMdiSubWindow, which will contain a QScrollArea, which will contain a QWidget
            # The QWidget will be used as a container for the actual plot
            self.plots[plotindex]['subwindow'] = Qt.QMdiSubWindow() 
            self.plots[plotindex]['subwindow'].setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.plots[plotindex]['subwindow'].setWindowTitle(self.exp.plots[plotindex]['name'])
            self.plots[plotindex]['scrollarea'] = Qt.QScrollArea()
            self.plots[plotindex]['subwindow'].setWidget(self.plots[plotindex]['scrollarea'])
            self.plots[plotindex]['widget'] = Qt.QWidget()
            self.plots[plotindex]['scrollarea'].setWidget(self.plots[plotindex]['widget'])
            self.plots[plotindex]['scrollarea'].setWidgetResizable(True)
            mdi.addSubWindow(self.plots[plotindex]['subwindow'])
            self.plots[plotindex]['plotobject'] = ergastirio.widgets.PlotObject(parent = self.plots[plotindex]['widget'],
                                                                               data_headers = self.exp.data_headers,
                                                                               plot_config = self.exp.plots[plotindex])
            self.plots[plotindex]['widget'].show()
    
        self.container_plots.mdi = mdi
        self.container_plots.setWidget(mdi)
        self.container_plots.mdi.tileSubWindows()
        return True

    def create_gui_table_data(self):
        '''
        Create GUIs for data acquisition, table, data management

        container
            QWidget which will contain the GUIs
        '''  

        layout = Qt.QVBoxLayout()
        layout_row1 = Qt.QHBoxLayout()
        layout_row2 = Qt.QHBoxLayout()

        ## CREATE ACQUISITION CONTROL PANEL
        self.logger.info(f"Creating GUI for acquisition control panel...")
        self.control_panel_container = Qt.QGroupBox() 
        self.control_panel_container.setObjectName('acquisition_panel')
        string = 'QGroupBox#acquisition_panel'
        self.control_panel_container.setStyleSheet(string + ergastirio.styles.acquisitionpanel_box + '\nQGroupBox' + ergastirio.styles.acquisitionpanel_boxtitle ) #This line changes the style of ONLY this QWdiget
        self.control_panel_container.setTitle(f"Acquisition Panel")
        self.control_panel = ergastirio.panels.acquisition_control( parent = self.control_panel_container,
                                                                    experiment = self.exp)
        self.control_panel.create_gui()
        ####

        ## CREATE DATA MANAGEMENT PANEL
        self.data_management_panel_container = Qt.QGroupBox()
        self.data_management_panel = ergastirio.panels.data_management( parent = self.data_management_panel_container,
                                                                        experiment = self.exp)
        self.data_management_panel.create_gui()
        ####

        ### CREATE TABLE TO SHOW DATA
        self.logger.info(f"Creating GUI for table...")
        self.tabledata_container = Qt.QGroupBox() 
        self.tabledata = ergastirio.widgets.Table(parent = self.tabledata_container)
        self.tabledata.data_headers = self.exp.data_headers
        self.tabledata.data = self.exp.data
        self.tabledata.create_gui()
        ###
    
        layout_row1.addWidget(self.control_panel_container)
        layout_row1.addWidget(self.data_management_panel_container)
        layout_row1.addStretch(1)
        layout_row2.addWidget(self.tabledata_container,stretch=3)
        layout.addLayout(layout_row1)
        layout.addLayout(layout_row2)
        self.container_tabledata.setLayout(layout)
 
        return True

    def link_data_to_gui(self):
        '''
        The data collected in the experiment is stored in self.exp.data, which is an instance of the EnhancedList class.
        This is a 'dynamic' list, wich allows 'linked objects'. Whenever any data stored in an EnhancedList object is changed, any linked
        object is notified, and a copy of the currently stored date is sent to the object.
        This is used as an elegant way to keep the table data and plots always syncronized with the stored data.
        To link an object, we use the method add_syncronized_objects defined in the EnhancedList class

        data.add_syncronized_objects([ InstanceOfTargetObject,  TargetClassProperty])

        Every time that the content of data is changed (e.g. a row is added to acquired data), the object data is also copied into
        the propery InstanceOfTargetObject.TargetClassProperty
        '''
        #self.exp.data.add_syncronized_objects([ self.tabledata,  ergastirio.widgets.Table.data])
        self.tabledata.add_signals(
                                    signal_data_updated = self.exp.sig_data_updated,
                                    signal_added_new_rows = self.exp.sig_data_updated_added_new_rows,
                                    signal_deleted_all_data = self.exp.sig_data_updated_deleted_all_data,
                                    signal_deleted_last_rows = self.exp.sig_data_updated_deleted_last_rows)
        for plot in self.plots:
            self.exp.data.add_syncronized_objects([  plot['plotobject'],  ergastirio.widgets.PlotObject.data])
            self.exp.data_std.add_syncronized_objects([  plot['plotobject'],  ergastirio.widgets.PlotObject.data_error])
