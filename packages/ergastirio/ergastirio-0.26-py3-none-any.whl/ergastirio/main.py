import os
import PyQt5
dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
import PyQt5.QtWidgets as Qt# QApplication, QWidget, QMainWindow, QPushButton, QHBoxLayout
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import logging
import sys
import argparse
import importlib
import numpy as np
import inspect
from importlib.metadata import version  
import math

from ergastirio.experiment import experiment
from ergastirio.experiment_gui import experiment_gui
import ergastirio.widgets
import ergastirio.utils
import ergastirio.logger

## This is a quick and dirty solution to get rid of the warning "QWindowsWindow::setGeometry: Unable to set geometry ...", which is due to a bug of PyQt5 in Windows. 
def handler(msg_type, msg_log_context, msg_string):
    pass
PyQt5.QtCore.qInstallMessageHandler(handler)
##

graphics_dir = os.path.join(os.path.dirname(__file__), 'graphics')

class MainWindow(Qt.QMainWindow):
    '''
    The main window contains several menus and a QMdiArea object, 
    The QMdiArea object in turn contains subwindows where instruments, plots, data table and logs will be created
    Object creation:
        window = MainWindow()
    The QMdiArea object is saved as attribute:
        window.mdi 
    The mdi object is also the parent object which needs to be passed as parameter when creating an instance of the experiment object
    For example:
        Experiment = experiment(app,window,window.mdi,config_file)
    The mdi object contains a dictionary, window.mdi.containers whose elements represent the different subwindows.
    Specifically, window.mdi.containers = {'logging':{...},'tabledata':{...},'instruments':{...},'plots':{...} }
    The object
        window.mdi.containers[name]['container']
    is the widget that will act as container for the different part of the gui. 
    Each of this widget is a child (via setWidget() method) of a corresponding QScrollArea object, 
        window.mdi.containers[name]['scrollarea']
    In turns, the scrollarea objects are children (via setWidget() method) of corresponding QMdiSubWindow objects
        window.mdi.containers[name]['subwindow']
    '''
    _views =  {'View 1':{
                "instruments":  [ "11/20", "0", "9/20", "2/3" ],
                "plots":        [ "0", "0", "11/20", "2/3" ],
                "tabledata":    [ "0", "2/3", "2/3", "1/3" ],
                "logging":      [ "2/3", "2/3", "1/3", "1/3" ]
                }
               ,
               'View 2':{
                "instruments":  [ "2/3", "0", "1/3", "2/3" ],
                "plots":        [ "0", "0", "2/3", "2/3" ],
                "tabledata":    [ "0", "2/3", "2/3", "1/3" ],
                "logging":      [ "2/3", "2/3", "1/3", "1/3" ]
                }
               ,
               'View 3':{
                "instruments":  [ "1/2", "0", "1/2", "1/2"],
                "plots":        [ "0", "0", "1/2", "1/2" ],
                "tabledata":    [ "0", "1/2", "1/2", "1/2" ],
                "logging":      [ "1/2", "1/2", "1/2", "1/2" ]
                }
               ,
               'View 4':{
                "instruments":  [ "2/3", "0", "1/3", "1/2"],
                "plots":        [ "0", "0", "2/3", "1/2" ],
                "tabledata":    [ "0", "1/2", "2/3", "1/2" ],
                "logging":      [ "2/3", "1/2", "1/3", "1/2" ]
                }
               ,
               'View 5':{
                "instruments":  [ "2/3", "0", "1/3", "1/2"],
                "plots":        [ "0", "0", "2/3", "3/5" ],
                "tabledata":    [ "0", "3/5", "2/3", "2/5" ],
                "logging":      [ "2/3", "1/2", "1/3", "1/2" ]
                }
               }
    _default_view = 'View 4'
    #This dictionary will be used to create the subwindows of the mdi, and also to populate the "View" menu
    _mdi_basic_panels ={  'logging':{'title':'Logging'},
                    'tabledata':{'title':'Data acquisition'},
                    'instruments':{'title':'Instruments'},
                    'plots':{'title':'Plots'}
                      }
    _mdi_advanced_panels ={ 'connect_ramps':{'title':'Connect Ramps'},
                           'status_selector':{'title':'Status Selector'}
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{__package__} (v{version(__package__)})")
        self.mdi = Qt.QMdiArea()
        self.setCentralWidget(self.mdi)

        self.current_view = self._views[self._default_view]
       
        mdi_basic_panels = self._mdi_basic_panels
        mdi_advanced_panels = self._mdi_advanced_panels

        def initialize_panels(panels_dict):
        #Create the different subwindows, based on the element of the dictionary panels_dictionary
            for key,mdi_panel in panels_dict.items():
                panels_dict[key]['subwindow'] = Qt.QMdiSubWindow()
                panels_dict[key]['subwindow'].setWindowFlags(QtCore.Qt.CustomizeWindowHint)
                panels_dict[key]['subwindow'].setWindowTitle(panels_dict[key]['title'])
                panels_dict[key]['scrollarea'] = Qt.QScrollArea(self)
                panels_dict[key]['container'] = Qt.QWidget(self)
                panels_dict[key]['subwindow'].setWidget(panels_dict[key]['scrollarea'])
                panels_dict[key]['scrollarea'].setWidget(panels_dict[key]['container'])
                panels_dict[key]['scrollarea'].setWidgetResizable(True)

        initialize_panels(mdi_basic_panels)
        initialize_panels(mdi_advanced_panels)

        #Add subwindows to mdi object and make them visible
        for mdi_panel in mdi_basic_panels.values():
            self.mdi.addSubWindow(mdi_panel['subwindow'])
            mdi_panel['container'].show()

        #Add subwindows to mdi object, make it hidden and restore buttons
        for mdi_panel in mdi_advanced_panels.values():
            self.mdi.addSubWindow(mdi_panel['subwindow'])
            mdi_panel['subwindow'].setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowMinimizeButtonHint)
            mdi_panel['subwindow'].setHidden(True)

        # Create top menus
        bar = self.menuBar()
        file = bar.addMenu("File")
        file.addAction("New Experiment")

        view = bar.addMenu("View")
        for k in self._views.keys():
            view.addAction(k)
        view.triggered[Qt.QAction].connect(self.action_view)

        showhide = bar.addMenu("Show/Hide")
        for mdi_panel in mdi_basic_panels.values():
            showhide.addAction(mdi_panel['title'])
        showhide.triggered[Qt.QAction].connect(self.action_showhide)

        advanced = bar.addMenu("Advanced")
        advanced.addAction("Connect Ramps")
        advanced.addAction("Status Selector")
        advanced.triggered[Qt.QAction].connect(self.action_showhide)
        
        # Store mdi_basic_panels and mdi_advanced_panels as attributes of the window object
        self.basic_panels = mdi_basic_panels
        self.advanced_panels = mdi_advanced_panels
        self.all_panels = {**(self.basic_panels),**(self.advanced_panels)}
        self.set_view(self.current_view)

        # Create Logging area
        box = Qt.QVBoxLayout()
        self.logging_text_area = ergastirio.logger.LoggerTextArea()
        box.addWidget(self.logging_text_area)
        self.basic_panels['logging']['container'].setLayout(box)
        
        # Set properties of specific panels
        #self.basic_panels['instruments']['scrollarea'].horizontalScrollBar().setEnabled(False)
        #self.basic_panels['instruments']['scrollarea'].setAutoScroll(False)
        #self.basic_panels['instruments']['scrollarea'].setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def action_view(self, p):
        for k in self._views.keys():
            if p.text() == k:
                self.current_view = self._views[k]
                self.set_view(self._views[k])
        return

    def action_showhide(self,p):
        for mdi_panel in self.all_panels.values():
            if p.text() == mdi_panel['title']:
                mdi_panel['subwindow'].setHidden(not mdi_panel['subwindow'].isHidden())

    def resizeEvent(self, event):
        Qt.QMainWindow.resizeEvent(self, event)
        self.set_view(self.current_view)

    def close(self, experiment):
        current_view = self.get_current_view()
        experiment.settings['GUI']['View'] = current_view
        experiment.close()
        pass

    def get_current_view(self):
        geomMDI = self.mdi.geometry()
        MDI_width = geomMDI.width()
        MDI_height = geomMDI.height()
        MDI_x = geomMDI.x()
        MDI_y = geomMDI.y()
        view = dict()
        for key in self.all_panels.keys():
            view[key] = list(self.all_panels[key]['subwindow'].geometry().getRect())
            view[key][0] = view[key][0]/MDI_width
            view[key][2] = view[key][2]/MDI_width
            view[key][1] = view[key][1]/MDI_height
            view[key][3] = view[key][3]/MDI_height
        return view

    def set_view(self,view):
        geomMDI = self.mdi.geometry()
        MDI_width = geomMDI.width()
        MDI_height = geomMDI.height()
        MDI_x = geomMDI.x()
        MDI_y = geomMDI.y()
        for panel,geom in view.items():
            geom_abs = [] 
            geom_abs.append(    int(ergastirio.utils.convert_fraction_to_float(geom[0])*MDI_width)  )
            geom_abs.append(    int(ergastirio.utils.convert_fraction_to_float(geom[1])*MDI_height) )
            geom_abs.append(    int(ergastirio.utils.convert_fraction_to_float(geom[2])*MDI_width)  )
            geom_abs.append(    int(ergastirio.utils.convert_fraction_to_float(geom[3])*MDI_height) )
            self.all_panels[panel]['subwindow'].setGeometry(*geom_abs)
        self.current_view = self.get_current_view()


def main():
    parser = argparse.ArgumentParser(description = "",epilog = "")
    parser.add_argument('-e', 
                        help=f"Path of .json file contaning the configuration of this experiment",
                        action="store", dest="config", type=str, default=None)
    parser.add_argument("-s", "--decrease_verbose", help="Decrease verbosity.", action="store_true")
    parser.add_argument('-virtual', help=f"Use virtual driver for each instrument (when available).", action="store_true")
    args = parser.parse_args()
    virtual = args.virtual
    if args.config:
        config_file = os.path.abspath(args.config)
    else:
        folder_default_file = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(folder_default_file,'config_default.json')
    
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    spinner = ergastirio.widgets.QtWaitingSpinner(window)
    spinner.setInnerRadius(30)
    spinner.setLineLength(30)
    spinner.setLineWidth(10)
    spinner.setRevolutionsPerSecond(1)
    spinner.setColor(QtGui.QColor(255, 255, 255))
    spinner.start() # starts spinning

    #app.aboutToQuit.connect(window.closeEvent) 

    #Create a new experiment
    Experiment = experiment(app)
    success = Experiment.initiate(config_file=config_file, func_logger_handler_adder = window.logging_text_area.add_logger, virtual=virtual)
                                                # func_logger_handler_adder must be defined as a function that takes one argument as input. The input argument is a Logger object
                                                # func_logger_handler_adder will add any Logger passed to it an handler defined elsewhere
    window.set_view(Experiment.settings['GUI']['View'])  

    #Generate the GUI for the new experiment
    if success:
        Experiment_gui = experiment_gui(Experiment,parent=window)

    spinner.stop()
    app.aboutToQuit.connect(lambda:window.close(Experiment)) 
    
    app.exec()# Start the event loop.

if __name__ == '__main__':
    main()