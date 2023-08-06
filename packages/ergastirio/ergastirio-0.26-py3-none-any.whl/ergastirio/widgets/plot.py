'''
This module contains several customized widgets used by Ergastirio
'''
import PyQt5.QtWidgets as Qt
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import numpy as np
import pyqtgraph as pg
import os

graphics_dir = os.path.join(os.path.dirname(__file__), '../graphics')

class PlotObject:
    ''' Interactive plot. It has built-in properties 'data' and 'data_headers', and it updates automatically the content of the plot everytime
        this properties are updated.
    '''
    _data_headers =[]
    _data = []
    _data_error = []

    def create_styles(self,colors = 'bgrcmyw',width = 1,symbol = 'o',style_labels = {"color": "#fff", "font-size": "20px"}):
        self._colors = colors
        self._width = width
        self._symbol = symbol
        self._style_labels = style_labels
        self._styles = []
        for c in self._colors:
            self._styles.append(pg.mkPen(c, width=self._width , style=QtCore.Qt.SolidLine))

    def __init__(self, parent, data_headers = None, plot_config = None):
        '''
        parent        = a QWidget (or QMainWindow) object that will be the parent for this plot
        data_headers
        plot_config   = a dictionary specifying the settings of this plot. The dictionary must contain at least two keys, 'x' and 'y'. 
                        The value of 'x' must be a single string. The value of 'y' can be either a string or a list of strings.
        '''

        self.parent = parent
        self._data_headers =[]
        self._data = []
        self._data_error = []   
        self._plot_config ={'x':'','y':[]}
        self.show_legend = True


        self.Max = 0 #Keep track of the maximum of minimum values plotted in this plot (among all possible curves). It is used for resizing purposes
        self.Min = 0

        self.MainContainer = Qt.QVBoxLayout()

        self.graphWidget = self.create_plot()
        self.controlWidget = self.create_controlPanel()

        if data_headers:
            self.data_headers = data_headers #Note: here we assume that data_headers do not already contain the "acq#" field. It will be added dynamically by counting the number of rows
        if plot_config:
            self.plot_config = plot_config


        self.MainContainer.addWidget(self.graphWidget) 
        self.MainContainer.addWidget(self.controlWidget) 
        self.MainContainer.setSpacing(0)
        #vbox.addStretch(1)
        self.parent.setLayout(self.MainContainer)
        self.create_styles()
        #self.refresh_plot()

    @property
    def plot_config(self):
        return self._plot_config    
    @plot_config.setter
    def plot_config(self,p):
        self._plot_config = p
        self.set_quantities_to_plot() #This will initialize axis and legend of the plot based on the current value of self.plot_config

    @property
    def data_headers(self):
        return self._data_headers
    @data_headers.setter
    def data_headers(self,h):
        self._data_headers = h
        self._data_headers_full = h.copy()
        self._data_headers_full.insert(0,"acq#")
        self._data_headers_full_radiobuttons_x_axis =[] # these two lists will store the radiobuttons and checkbox used to decide which quantity is plotted 
        self._data_headers_full_checkboxs_y_axis =[]    # on x and y axis. Each element of self._data_headers_full is associated to one radiobutton and one checkbox
        self.connect_widgets_to_headers()

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self,d):
        # Every time the list data is updated, store it and update the plots
        self._data = d
        self.refresh_plot()

    @property
    def data_error(self):
        return self._data_error
    @data_error.setter
    def data_error(self,d):
        self._data_error = d
        self.refresh_plot()

    ### GUI
    def create_plot(self):
        graphWidget = pg.PlotWidget()
        graphWidget.showGrid(x=True, y=True)
        #graphWidget.setMenuEnabled(False)
        return graphWidget

    def create_controlPanel(self):
        w = Qt.QWidget()
        hbox = Qt.QHBoxLayout()
        w.button_home = Qt.QPushButton("")
        w.button_home.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'home.png')))
        w.button_home.setFixedSize( 30, 30)

        w.toolButton_X = Qt.QToolButton()
        w.toolButton_X.setText('X')
        w.toolButton_X.show()
        #w.toolButton_X.setFixedSize(w.button_home.size())
        #w.toolButton_X.setSizePolicy(Qt.QSizePolicy.Preferred,Qt.QSizePolicy.Expanding)
        w.toolButton_X.setFixedSize( 30, 30)

        w.toolButton_Y = Qt.QToolButton()
        w.toolButton_Y.setText('Y')
        w.toolButton_Y.show()
        #w.toolButton_Y.setSizePolicy(Qt.QSizePolicy.Preferred,Qt.QSizePolicy.Expanding)
        w.toolButton_Y.setFixedSize( 30, 30)

        ### Connect widgets to functions
        
        ###

        hbox.addWidget(w.button_home)
        hbox.addWidget(w.toolButton_X)
        hbox.addWidget(w.toolButton_Y)

        hbox.addStretch(1)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        w.setLayout(hbox)
        return w

    def connect_widgets_to_headers(self):
        self.controlWidget.button_home.clicked.connect(self.reset_plot_view)
        self.create_menu_XY(self.controlWidget.toolButton_X,self.controlWidget.toolButton_Y)


    def create_menu_XY(self,toolButton_X,toolButton_Y):
        #code inspired by an answer to https://stackoverflow.com/questions/34731826/keep-menu-open-after-clicking-on-the-button-it-is-launched-with
        toolMenuX = Qt.QMenu()
        toolMenuY = Qt.QMenu()
        self._data_headers_full_radiobuttons_x_axis = []
        self._data_headers_full_checkboxs_y_axis = []
        #self.radio_x = []
        for data_name in self._data_headers_full:
            radiobutton = Qt.QRadioButton(data_name,toolMenuX)
            radiobutton.value = data_name
            if data_name == self.plot_config['x']:
                radiobutton.setChecked(True)
            radiobutton.toggled.connect(lambda x,object=radiobutton: self.update_plotted_data('x',object))
            checkableAction = Qt.QWidgetAction(toolMenuX)
            checkableAction.setDefaultWidget(radiobutton)
            toolMenuX.addAction(checkableAction)
            self._data_headers_full_radiobuttons_x_axis.append(radiobutton)

            checkbox = Qt.QCheckBox(data_name,toolMenuY)
            checkbox.value = data_name
            if data_name in self.plot_config['y']:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda: self.update_plotted_data('y'))
            checkableAction = Qt.QWidgetAction(toolMenuY)
            checkableAction.setDefaultWidget(checkbox)
            toolMenuY.addAction(checkableAction)
            self._data_headers_full_checkboxs_y_axis.append(checkbox)

        toolButton_X.toolMenu = toolButton_X
        toolButton_Y.toolMenu = toolButton_Y
        toolButton_X.setMenu(toolMenuX)
        toolButton_Y.setMenu(toolMenuY)
        toolButton_X.setPopupMode(Qt.QToolButton.InstantPopup)
        toolButton_X.setStyleSheet('QToolButton::menu-indicator { image: none; }')
        toolButton_Y.setPopupMode(Qt.QToolButton.InstantPopup)
        toolButton_Y.setStyleSheet('QToolButton::menu-indicator { image: none; }')
    ### END GUI

    ### GUI Events Functions
    def update_plotted_data(self, axis, object = None):
        '''
        Based on the current values of the radiobuttons and checkbox in the toolbutton menu, it updates 
        the content of self.plot_config['x'] and self.plot_config['y']
        '''
        if axis == 'x':
            if object.isChecked() == True:
                self.plot_config['x'] = object.value #(need to implement this better)
        if axis == 'y':
            self.plot_config['y'] = []
            for checkbox in self._data_headers_full_checkboxs_y_axis:
                if checkbox.isChecked() == True:
                    self.plot_config['y'].append(checkbox.value)
        self.set_quantities_to_plot()
        self.refresh_plot()

    def reset_plot_view(self):
        self.graphWidget.autoRange()
        self.graphWidget.enableAutoRange()

    ### END GUI Events Functions

    def set_quantities_to_plot(self):
        '''
        Based on the content of self.plot_config, it updates the values of self.x_index and self.y_index .
        self.x_index corresponds to the column index of the self._data matrix which will be used as x-quantity
        self.y_index is a list of indices, corresponding to the columns of the self._data matrix which will be used as y-quantities
        '''
        self.x_name = self.plot_config['x'] 
        self.x_index = self._data_headers_full.index(self.x_name) - 1 #in the self._data_headers_full list, we have added the "acq#" element at the beginning
                                                                      #thus, we substract 1 to the index to match this index with the column index in self._data
        self.y_index =[]
        self.y_names = self.plot_config['y']
        for y_name in self.plot_config['y']:
            self.y_index.append(self._data_headers_full.index(y_name) - 1) #in the self._data_headers_full list, we have added the "acq#" element at the beginning
        return

    def refresh_plot(self):
        self.graphWidget.clear()
        if len(self.y_index) == 0: #if len(self.y_index) == 0 then there are no quantities to plot on y axis. Thus, we don't do anything in this routine
            return
        if self.show_legend:
            self.graphWidget.addLegend()

        if self.x_index == -1:
            x = list(range(1,len(self._data)+1)) #if self.x_index=-1, then the data to use on x axis is the acquisition number. We build the x-data explicitly.
        else:
            x = [row[self.x_index] for row in self._data] #otherwise,  the data to use on x axis is one of the columns of self._data. We extract it.
        
        self.graphWidget.setLabel('bottom', self.x_name ,**self._style_labels)

        for i,y_index in enumerate(self.y_index):
            if y_index == -1:
                y = list(range(1,len(self._data)+1)) #if self.y_index=-1, then this specific y-data is the acquisition number. We build the ydata explicitly.
            else:
                y = [row[y_index] for row in self._data] #otherwise, this specific y-data is one of the columns of self._data. We extract it.
            index_style = (y_index+1) % len(self._styles)
            try:
                self.graphWidget.plot(x,y,  name=self.y_names[i],    pen=self._styles[index_style],    symbol=self._symbol,    symbolBrush=self._colors[index_style])
            except Exception as e:
                print(f"An error occurred while trying to plot\n: {e}")
                return
            
 
