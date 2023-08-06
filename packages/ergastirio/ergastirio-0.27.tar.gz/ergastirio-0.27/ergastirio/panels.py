import os
import PyQt5.QtWidgets as Qt# QApplication, QWidget, QMainWindow, QPushButton, QHBoxLayout
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import logging
import ergastirio.utils
import ergastirio.styles
import copy

graphics_dir = os.path.join(os.path.dirname(__file__), 'graphics')

'''
The panels defined in this module are meant to be GUIs for other classes, i.e. their events are directly connected to methods of other objects and they dont have
any relevant "internal logic"
They do not have their own logger, and they do not produce any logging event. Rather, they are "directly" connected to methods and functionalities
of the experiment object via PyQt5 signals
'''


############################################################################################################
## status_selector                                                                                        # 
############################################################################################################

class status_selector():

    def __init__(self, parent, experiment):
        # parent        = a QWidget (or QMainWindow) object that will be the parent of this gui
        # experiment    = an experiment() object, whose acquisition will be controlled by this panel

        self.parent = parent
        self.experiment  = experiment 

        ### Connect signals from model to event slots of this GUI
        #self.experiment.sig_list_ramps.connect(self.on_list_ramps_updated)
        #self.experiment.sig_single_set_acquisition.connect(self.on_single_set_acquisition_change)
        #self.experiment.sig_triggered_acquisition.connect(self.on_triggered_acquisition_change)
        #self.experiment.sig_trigger_modality.connect(self.on_trigger_modality_change)
        #self.experiment.sig_trigger_instrument.connect(self.on_trigger_instrument_change)
        #self.experiment.sig_time_interval_internal_trigger.connect(self.on_time_inteval_internal_trigger_change)
        #self.experiment.sig_time_interval_multiple_acquisitions_per_set.connect(self.on_time_interval_multiple_acquisitions_per_set_change)
        #self.experiment.sig_numb_acquisitions_per_set.connect(self.on_numb_acquisitions_per_trigger_change)
        #self.experiment.sig_make_average_set_acquisition.connect(self.on_change_make_average_set_acquisition)
        self.experiment.sig_list_instruments.connect(self.on_list_instruments_updated)
        #self.experiment.sig_trigger_instrument.connect(self.on_trigger_instrument_changed)
        #self.experiment.sig_trigger_instrument_delay.connect(self.on_trigger_delay_changed)

        #self.doing_triggered_acquisition = False    # Flag used to keep track a triggered acquisition is being performed. If this is true, some widget will not be re-enabled when self.experiment.SIG_SINGLE_SET_ACQUISITION_ENDED is sent
        #                                            # but only when self.experiment.SIG_TRIGGERED_ACQUISITION_ENDED is sent

    def create_gui(self): 
        self.create_widgets()
        self.connect_widgets_events_to_functions()

    def create_widgets(self):
        """
        - hbox                                          (QHBoxLayout)

        """

        self.vbox = Qt.QVBoxLayout()
        self.label_Info = Qt.QLabel("This panal allows to create experiment 'states', defined as list of properties of one or more instruments and their values." \
                                     "Once a state is defined, it can be quickly re-created by double clicking on it. " \
                                     "This will automatically set the values of all the properties.")
        self.label_Info.setWordWrap(True) 
        self.tableRamps = Qt.QTableWidget()
        self.tableRamps.setColumnCount(3)
        self.tableRamps.setHorizontalHeaderLabels(["Instrument","Property","Value"])
        header = self.tableRamps.horizontalHeader()
        header.setSectionResizeMode(Qt.QHeaderView.ResizeToContents)       
        #header.setSectionResizeMode(0, Qt.QHeaderView.Stretch)
        self.vbox.addWidget(self.label_Info)
        self.vbox.addWidget(self.tableRamps)

        ### Assign the layout hbox to the widget defined in self.parent
        self.parent.setLayout(self.vbox) 
        self.parent.resize(self.parent.minimumSize())

        
        return
    
    def connect_widgets_events_to_functions(self):
        ### Connect Widget Events to Event Functions
        if hasattr(self,'list_combo_ramps'):
            for index,combo_box in enumerate(self.list_combo_ramps):
                self.list_combo_ramps[index].currentIndexChanged.connect(lambda index_newvalue, index=index : self.change_combo_ChildRamp(index_newvalue, index_combobox=index))
        return self

###########################################################################################################
### Event Slots. They are normally triggered by signals from the model, and change the GUI accordingly  ###
###########################################################################################################

    def on_list_instruments_updated(self, list_instruments):
        print(list_instruments)

    def on_list_ramps_updated(self,list_ramps):
        self.list_ramps = list_ramps #store for later use
        self.tableRamps.clearContents()

        # Create a list of ramps for the comboboxes 
        combobox_items = []
        for index,ramp in enumerate(list_ramps):
            combobox_items.append(f"{str(ramp[1])} -> {str(id(ramp[2]))}")
        combobox_items.append('None')

        self.list_combo_ramps = [] #this will contain the combobox for each row of the table
#
        self.tableRamps.setRowCount(len(list_ramps)) 
        for index,ramp in enumerate(list_ramps):
            item0 = Qt.QTableWidgetItem(str(ramp[1]))
            item1 = Qt.QTableWidgetItem(str(id(ramp[2])))
            self.tableRamps.setItem(index,0,item0)
            self.tableRamps.setItem(index,1,item1)
            combo_ramps = Qt.QComboBox()
            combo_ramps.addItems(combobox_items)
            self.tableRamps.setCellWidget(index,2,combo_ramps)
            self.list_combo_ramps.append(combo_ramps)
            
            #If the ramp corresponding to this row has child, we set the combobox to the corresponding child
            if ramp[3] == -1:
                combo_ramps.setCurrentIndex(len(combobox_items)-1) # This will initialize the combobox to 'None'
            else:
                combo_ramps.setCurrentIndex(ramp[3])

        #populating the table with combobox will create new widgets, thus we need to call again connect_widgets_events_to_functions
        self.connect_widgets_events_to_functions()


#######################
### END Event Slots ###
#######################

###################################################################################################################################################
### GUI Events Functions. They are triggered by direct interaction with the GUI, and they call methods of the experiment (i.e. the model) object.###
###################################################################################################################################################

#    def change_combo_ChildRamp(self,index_newvalue,index_combobox):
#        child_ramp_index = index_newvalue
#        index_row = index_combobox
#        if child_ramp_index ==  len(self.list_ramps): # This means that the value of the combobox is 'None'
#            self.experiment.disconnect_ramp_from_child(self.list_ramps[index_row][0])
#        else:
#            self.experiment.connect_ramp_to_child(self.list_ramps[index_row][0],self.list_ramps[child_ramp_index][0])
#        return


#################################
### END GUI Events Functions ####
#################################

############################################################################################################
## END status_selector                                                                                     # 
############################################################################################################


############################################################################################################
## ramp_connection                                                                                         # 
############################################################################################################

class ramp_connection():

    def __init__(self, parent, experiment):
        # parent        = a QWidget (or QMainWindow) object that will be the parent of this gui
        # experiment    = an experiment() object, whose acquisition will be controlled by this panel

        self.parent = parent
        self.experiment  = experiment 

        ### Connect signals from model to event slots of this GUI
        self.experiment.sig_list_ramps.connect(self.on_list_ramps_updated)
        #self.experiment.sig_single_set_acquisition.connect(self.on_single_set_acquisition_change)
        #self.experiment.sig_triggered_acquisition.connect(self.on_triggered_acquisition_change)
        #self.experiment.sig_trigger_modality.connect(self.on_trigger_modality_change)
        #self.experiment.sig_trigger_instrument.connect(self.on_trigger_instrument_change)
        #self.experiment.sig_time_interval_internal_trigger.connect(self.on_time_inteval_internal_trigger_change)
        #self.experiment.sig_time_interval_multiple_acquisitions_per_set.connect(self.on_time_interval_multiple_acquisitions_per_set_change)
        #self.experiment.sig_numb_acquisitions_per_set.connect(self.on_numb_acquisitions_per_trigger_change)
        #self.experiment.sig_make_average_set_acquisition.connect(self.on_change_make_average_set_acquisition)
        #self.experiment.sig_list_instruments.connect(self.on_list_instruments_updated)
        #self.experiment.sig_trigger_instrument.connect(self.on_trigger_instrument_changed)
        #self.experiment.sig_trigger_instrument_delay.connect(self.on_trigger_delay_changed)

        #self.doing_triggered_acquisition = False    # Flag used to keep track a triggered acquisition is being performed. If this is true, some widget will not be re-enabled when self.experiment.SIG_SINGLE_SET_ACQUISITION_ENDED is sent
        #                                            # but only when self.experiment.SIG_TRIGGERED_ACQUISITION_ENDED is sent

    def create_gui(self): 
        self.create_widgets()
        self.connect_widgets_events_to_functions()

    def create_widgets(self):
        """
        - hbox                                          (QHBoxLayout)

        """

        self.vbox = Qt.QVBoxLayout()
        self.label_Info = Qt.QLabel("This panal allows to connect a (parent) ramp to (child) ramp." \
                                     "The trigger event of the parent ramp becomes the start of the child ramp. " \
                                     "This can be used to sweep multiple parameters. Typically, the instrument of the child ramp " \
                                     "(or grandchild ramp, in case of multiple connections) would be set as 'instrument trigger' for the acquisition system.\n" \
                                     "\n<b>Important<b/>: the code does not do many sanity checks, and it will not complain about incestuous situations, where a ramp is set " \
                                     "as both a parent and a child of another ramp. This will generate unpredictable situations. Don't be incestuous.")
        self.label_Info.setWordWrap(True) 
        self.tableRamps = Qt.QTableWidget()
        self.tableRamps.setColumnCount(3)
        self.tableRamps.setHorizontalHeaderLabels(["Parent Instrument","Parent Ramp ID","Select child ramp:"])
        header = self.tableRamps.horizontalHeader()
        header.setSectionResizeMode(Qt.QHeaderView.ResizeToContents)       
        #header.setSectionResizeMode(0, Qt.QHeaderView.Stretch)
        self.vbox.addWidget(self.label_Info)
        self.vbox.addWidget(self.tableRamps)

        ### Assign the layout hbox to the wdiget defined in self.parent
        self.parent.setLayout(self.vbox) 
        self.parent.resize(self.parent.minimumSize())

        
        return
    
    def connect_widgets_events_to_functions(self):
        ### Connect Widget Events to Event Functions
        if hasattr(self,'list_combo_ramps'):
            for index,combo_box in enumerate(self.list_combo_ramps):
                self.list_combo_ramps[index].currentIndexChanged.connect(lambda index_newvalue, index=index : self.change_combo_ChildRamp(index_newvalue, index_combobox=index))
        return self

###########################################################################################################
### Event Slots. They are normally triggered by signals from the model, and change the GUI accordingly  ###
###########################################################################################################

    def on_list_ramps_updated(self,list_ramps):
        self.list_ramps = list_ramps #store for later use
        self.tableRamps.clearContents()

        # Create a list of ramps for the comboboxes 
        combobox_items = []
        for index,ramp in enumerate(list_ramps):
            combobox_items.append(f"{str(ramp[1])} -> {str(id(ramp[2]))}")
        combobox_items.append('None')

        self.list_combo_ramps = [] #this will contain the combobox for each row of the table
#
        self.tableRamps.setRowCount(len(list_ramps)) 
        for index,ramp in enumerate(list_ramps):
            item0 = Qt.QTableWidgetItem(str(ramp[1]))
            item1 = Qt.QTableWidgetItem(str(id(ramp[2])))
            self.tableRamps.setItem(index,0,item0)
            self.tableRamps.setItem(index,1,item1)
            combo_ramps = Qt.QComboBox()
            combo_ramps.addItems(combobox_items)
            self.tableRamps.setCellWidget(index,2,combo_ramps)
            self.list_combo_ramps.append(combo_ramps)
            
            #If the ramp corresponding to this row has child, we set the combobox to the corresponding child
            if ramp[3] == -1:
                combo_ramps.setCurrentIndex(len(combobox_items)-1) # This will initialize the combobox to 'None'
            else:
                combo_ramps.setCurrentIndex(ramp[3])

        #populating the table with combobox will create new widgets, thus we need to call again connect_widgets_events_to_functions
        self.connect_widgets_events_to_functions()


#######################
### END Event Slots ###
#######################

###################################################################################################################################################
### GUI Events Functions. They are triggered by direct interaction with the GUI, and they call methods of the experiment (i.e. the model) object.###
###################################################################################################################################################

    def change_combo_ChildRamp(self,index_newvalue,index_combobox):
        child_ramp_index = index_newvalue
        index_row = index_combobox
        if child_ramp_index ==  len(self.list_ramps): # This means that the value of the combobox is 'None'
            self.experiment.disconnect_ramp_from_child(self.list_ramps[index_row][0])
        else:
            self.experiment.connect_ramp_to_child(self.list_ramps[index_row][0],self.list_ramps[child_ramp_index][0])
        return


#################################
### END GUI Events Functions ####
#################################

############################################################################################################
## END ramp_connection                                                                                     # 
############################################################################################################

############################################################################################################
## acquisition_control                                                                                     # 
############################################################################################################

class acquisition_control():

    def __init__(self, parent, experiment):
        # parent        = a QWidget (or QMainWindow) object that will be the parent of this gui
        # experiment    = an experiment() object, whose acquisition will be controlled by this panel

        self.parent = parent
        self.experiment  = experiment 

        ### Connect signals from model to event slots of this GUI
        self.experiment.sig_single_set_acquisition.connect(self.on_single_set_acquisition_change)
        self.experiment.sig_triggered_acquisition.connect(self.on_triggered_acquisition_change)
        self.experiment.sig_trigger_modality.connect(self.on_trigger_modality_change)
        self.experiment.sig_trigger_instrument.connect(self.on_trigger_instrument_change)
        self.experiment.sig_time_interval_internal_trigger.connect(self.on_time_inteval_internal_trigger_change)
        self.experiment.sig_time_interval_multiple_acquisitions_per_set.connect(self.on_time_interval_multiple_acquisitions_per_set_change)
        self.experiment.sig_numb_acquisitions_per_set.connect(self.on_numb_acquisitions_per_trigger_change)
        self.experiment.sig_make_average_set_acquisition.connect(self.on_change_make_average_set_acquisition)
        self.experiment.sig_list_instruments.connect(self.on_list_instruments_updated)
        self.experiment.sig_trigger_instrument.connect(self.on_trigger_instrument_changed)
        self.experiment.sig_trigger_instrument_delay.connect(self.on_trigger_delay_changed)

        self.doing_triggered_acquisition = False    # Flag used to keep track a triggered acquisition is being performed. If this is true, some widget will not be re-enabled when self.experiment.SIG_SINGLE_SET_ACQUISITION_ENDED is sent
                                                    # but only when self.experiment.SIG_TRIGGERED_ACQUISITION_ENDED is sent

    def create_gui(self): 
        self.create_widgets()
        self.connect_widgets_events_to_functions()

    def create_widgets(self):
        """
        - hbox_acquisition_control                                          (QHBoxLayout)
            - box_trigger                                                   (QGroupBox)
                - box_trigger_hbox                                          (QVBoxLayout)
                    - StartPauseTriggeredAcquisition_hbox                   (QHBoxLayout)
                            ...widgets...
                    - InternalExternalTrigger_hbox                          (QHBoxLayout)
                        - panelInternalTrigger                              (QWidget)
                            - panelInternalTrigger_layout                   (QHBoxLayout)
                                ...widgets... 
                        - panelExternalTrigger                              (QWidget)
                            - panelExternalTrigger_layout                   (QVBoxLayout) 
                                - panelExternalTrigger_layout_row1          (QHBoxLayout)
                                    ...widgets... 
                                - panelExternalTrigger_layout_row2          (QHBoxLayout)
                                    ...widgets...
            - label_Arrow                                                   (QLabel)
            - box_acquisitionset                                            (QGroupBox)
                - box_acquisitionset_vbox                                   (QVBoxLayout)
                    - AcquisitionSet_row1                                   (QHBoxLayout)
                        ...widgets...
                    - AcquisitionSet_row2                                   (QHBoxLayout)
                        ...widgets...

        """

        hbox_acquisition_control = Qt.QHBoxLayout()
        box_trigger = Qt.QGroupBox()
        box_trigger.setTitle(f"Trigger")
        self.label_Arrow = Qt.QLabel() #This hosts the arrow image
        box_acquisitionset = Qt.QGroupBox()
        box_acquisitionset.setTitle(f"Acquisition(s)")

        #Initial setup of the three main blocks
        box_trigger.setObjectName('box_trigger')
        string = 'QGroupBox#box_trigger'
        box_trigger.setStyleSheet(string + ergastirio.styles.acquisitionpanel_box + '\nQGroupBox' + ergastirio.styles.acquisitionpanel_boxtitle ) #This line changes the style of ONLY this QWdiget
    
        pixmap = QtGui.QPixmap(os.path.join(graphics_dir,'arrow.png'))
        smaller_pixmap = pixmap.scaled(32, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        self.label_Arrow.setPixmap(smaller_pixmap)

        box_acquisitionset.setObjectName('box_acquisitionset')
        string = 'QGroupBox#box_acquisitionset'
        box_acquisitionset.setStyleSheet(string + ergastirio.styles.acquisitionpanel_box + '\nQGroupBox' + ergastirio.styles.acquisitionpanel_boxtitle ) #This line changes the style of ONLY this QWdiget

        hbox_acquisition_control.addWidget(box_trigger)
        hbox_acquisition_control.addWidget(self.label_Arrow)  
        hbox_acquisition_control.addWidget(box_acquisitionset)  
        #hbox_acquisition_control.addStretch(1)

        self.widgets_box_trigger = [] #This list will contain all widgets contained in box_trigger
        self.widgets_box_trigger_internal = []
        self.widgets_box_trigger_external = []
        self.widgets_box_acquisitionset = [] #This list will contain all widgets contained in box_acquisitionset
        self.widgets_box_acquisitionset_first_row = []

###### POPULATE box_trigger
        ### Add a horizontal box inside box_trigger
        box_trigger_hbox = Qt.QHBoxLayout()
        box_trigger.setLayout(box_trigger_hbox)

        ### Add two boxes, one horizontal to host the button and one vertical to host the two radio buttons
        StartPauseTriggeredAcquisition_hbox = Qt.QHBoxLayout()
        InternalExternalTrigger_hbox = Qt.QVBoxLayout()
        #vbox_trigger_box_vbox.setContentsMargins(0,0,0,0)
        box_trigger_hbox.addLayout(StartPauseTriggeredAcquisition_hbox)
        box_trigger_hbox.addLayout(InternalExternalTrigger_hbox)
        
        ### Populate the InternalExternalTrigger_hbox box with two widgets (in order to assign a style)
        self.panelInternalTrigger = Qt.QWidget()
        self.panelExternalTrigger = Qt.QWidget()
        InternalExternalTrigger_hbox.addWidget(self.panelInternalTrigger)
        InternalExternalTrigger_hbox.addWidget(self.panelExternalTrigger)
        
        ### Populate StartPauseTriggeredAcquisition_hbox with widgets
        StartPauseTriggeredAcquisition_hbox.setContentsMargins(0,0,0,0)
        StartPauseTriggeredAcquisition_hbox.setAlignment(QtCore.Qt.AlignCenter)
        self.button_StartPauseTriggeredAcquisition = Qt.QPushButton()
        self.button_StartPauseTriggeredAcquisition.setToolTip('Start or pause triggered data acquisition. Each time a trigger (either internal or by instrument) is received, \nit takes a single set of acquisitions.') 
        self.button_StartPauseTriggeredAcquisition.setText('Pause triggered\nacquisition')
        for w in [self.button_StartPauseTriggeredAcquisition]:
            StartPauseTriggeredAcquisition_hbox.addWidget(w)
            self.widgets_box_trigger.append(w)
        
        #panelStartPauseTriggeredAcquisition_layout.addStretch(1)

        ### Populate self.panelInternalTrigger with a hbox layout, and add widgets to the layout
        self.panelInternalTrigger.setStyleSheet("background-color: #D3D3D3;")
        panelInternalTrigger_layout = Qt.QHBoxLayout(self.panelInternalTrigger)
        panelInternalTrigger_layout.setContentsMargins(0,0,0,0)
        self.radio_TriggerInternal = Qt.QRadioButton()
        self.radio_TriggerInternal.setText("Internal")
        self.radio_TriggerInternal.setStyleSheet("QRadioButton { font: bold;}");
        self.radio_TriggerInternal.setChecked(True)
        self.radio_TriggerInternal.value= "internal"
        self.radio_TriggerInternal.setToolTip('In this modality, data from all instruments is acquired at periodic intervals of time, set by the \'refresh time\'. \nNote: user must check that each instrument is running and refreshing its own data.') 
        self.label_RefreshTime = Qt.QLabel("Time interval (s) = ")
        self.edit_RefreshTime = Qt.QLineEdit()
        self.edit_RefreshTime.setFixedWidth(50)
        
        self.edit_RefreshTime.setAlignment(QtCore.Qt.AlignRight)
        self.edit_RefreshTime.setStyleSheet("background-color: #FFFFFF;")
        for w in [self.radio_TriggerInternal,self.label_RefreshTime,self.edit_RefreshTime]:
            panelInternalTrigger_layout.addWidget(w)
            self.widgets_box_trigger.append(w)
            self.widgets_box_trigger_internal.append(w)
        panelInternalTrigger_layout.addStretch(1)

        ### Populate self.panelExternalTrigger with a vbox layout, which in turns contain two hbox layouts, and add widgets the hbox layouts
        self.panelExternalTrigger.setStyleSheet("background-color: #D3D3D3;")
        panelExternalTrigger_layout = Qt.QVBoxLayout(self.panelExternalTrigger)
        panelExternalTrigger_layout.setContentsMargins(0,0,0,0)
        panelExternalTrigger_layout_row1 = Qt.QHBoxLayout()
        panelExternalTrigger_layout_row2 = Qt.QHBoxLayout()
        panelExternalTrigger_layout.addLayout(panelExternalTrigger_layout_row1)
        panelExternalTrigger_layout.addLayout(panelExternalTrigger_layout_row2)
        self.radio_TriggerExternal = Qt.QRadioButton()
        self.radio_TriggerExternal.setText("By Instrument")
        self.radio_TriggerExternal.setStyleSheet("QRadioButton { font: bold;}");
        self.radio_TriggerExternal.value= "external"
        self.radio_TriggerExternal.setToolTip('In this modality, one instrument is designated as trigger. Whenever that instrument updates its own data, it triggers an acquisition.') 
        self.label_TriggerExternal = Qt.QLabel("=")
        self.combo_TriggerInstruments = Qt.QComboBox()
        self.combo_TriggerInstruments.resize(self.combo_TriggerInstruments.sizeHint())
        self.combo_TriggerInstruments.setStyleSheet("background-color: #FFFFFF;")
        self.label_TriggerInstrumentDelay = Qt.QLabel("[ delayed  by (s) = ")
        self.label_TriggerInstrumentDelay.setFont(QtGui.QFont('Arial', 8))
        self.edit_TriggerInstrumentDelay = Qt.QLineEdit()
        self.edit_TriggerInstrumentDelay.setStyleSheet("background-color: #FFFFFF;")
        self.edit_TriggerInstrumentDelay.setFixedWidth(50)
        self.edit_TriggerInstrumentDelay.setAlignment(QtCore.Qt.AlignRight)
        self.edit_TriggerInstrumentDelay.setFont(QtGui.QFont('Arial', 8))
        self.edit_TriggerInstrumentDelay.setFixedHeight(15)
        self.label_TriggerInstrumentDelay2 = Qt.QLabel("]")
        self.label_TriggerInstrumentDelay2.setFont(QtGui.QFont('Arial', 8))
        for w in [self.radio_TriggerExternal,self.label_TriggerExternal,self.combo_TriggerInstruments]:
            panelExternalTrigger_layout_row1.addWidget(w)
            self.widgets_box_trigger.append(w)
            self.widgets_box_trigger_external.append(w)
        panelExternalTrigger_layout_row1.addStretch(1)
        for w in [self.label_TriggerInstrumentDelay,self.edit_TriggerInstrumentDelay,self.label_TriggerInstrumentDelay2]:
            panelExternalTrigger_layout_row2.addWidget(w)
            self.widgets_box_trigger.append(w)
            self.widgets_box_trigger_external.append(w)
        panelExternalTrigger_layout_row2.addStretch(1)

        #Connect Trigger buttons
        self.buttongroup_trigger = Qt.QButtonGroup(self.parent)
        self.buttongroup_trigger.addButton(self.radio_TriggerInternal)
        self.buttongroup_trigger.addButton(self.radio_TriggerExternal)

###### POPULATE box_acquisitionset
        ### Add a vertical box inside box_acquisitionset
        box_acquisitionset_vbox = Qt.QVBoxLayout()
        box_acquisitionset_vbox.setAlignment(QtCore.Qt.AlignCenter)
        box_acquisitionset.setLayout(box_acquisitionset_vbox)

        ### Add two hbox layouts to box_acquisitionset_vbox
        AcquisitionSet_row1 =  Qt.QHBoxLayout()
        AcquisitionSet_row2 =  Qt.QHBoxLayout()
        box_acquisitionset_vbox.addLayout(AcquisitionSet_row1)
        box_acquisitionset_vbox.addLayout(AcquisitionSet_row2)

        ### Populate AcquisitionSet_row1 with widgets
        self.label_NumbAcquisitions = Qt.QLabel("Take N = ")
        self.spinbox_NumbAcquisitions = Qt.QSpinBox()
        self.spinbox_NumbAcquisitions.setRange(1, 10000)
        self.label_NumbAcquisitions2 = Qt.QLabel("acquisitions, every ")
        self.edit_AcquisitionRefreshTime = Qt.QLineEdit()
        self.edit_AcquisitionRefreshTime.setFixedWidth(30)
        self.edit_AcquisitionRefreshTime.setAlignment(QtCore.Qt.AlignRight)
        self.edit_AcquisitionRefreshTime.setStyleSheet("background-color: #FFFFFF;")
        self.label_NumbAcquisitions3 = Qt.QLabel("s,  ")
        self.box_MakeAverage = Qt.QCheckBox("and average them.")
        self.box_MakeAverage.setToolTip('When checked, the multiple acquisitions are averaged.')
        for w in [self.label_NumbAcquisitions, self.label_NumbAcquisitions, self.spinbox_NumbAcquisitions, self.label_NumbAcquisitions2, 
                  self.edit_AcquisitionRefreshTime, self.label_NumbAcquisitions3,self.box_MakeAverage]:
            AcquisitionSet_row1.addWidget(w)
            self.widgets_box_acquisitionset.append(w)
            self.widgets_box_acquisitionset_first_row .append(w)
        
        ### Populate AcquisitionSet_row2 with widgets
        self.button_SingleAcquisition = Qt.QPushButton("Take single set acquisitions")
        self.button_SingleAcquisition.setToolTip('Triggers a single set of acquisitions, with the number of acquisitions N and time interval specified here above.') 
        AcquisitionSet_row2.setAlignment(QtCore.Qt.AlignCenter)
        for w in [self.button_SingleAcquisition]:   
            AcquisitionSet_row2.addWidget(w)    
            self.widgets_box_acquisitionset.append(w)

        # Widgets for which we want to constraint the min size by using sizeHint()
        widget_list = [self.button_StartPauseTriggeredAcquisition,self.button_SingleAcquisition]
        for w in widget_list:
            w.setMinimumSize(w.sizeHint())

        # Widgets for which we want to constraint the max size by using sizeHint()
        #widget_list = [box_acquisitionset,box_trigger]
        #for w in widget_list:
        #    w.setMaximumSize(w.sizeHint())

        ### Assign the layout hbox_acquisition_control to the wdiget defined in self.parent
        self.parent.setLayout(hbox_acquisition_control) 
        self.parent.resize(self.parent.minimumSize())

        return
    
    def connect_widgets_events_to_functions(self):
        ### Connect Widget Events to Event Functions
        self.button_StartPauseTriggeredAcquisition.clicked.connect(self.click_button_StartPauseTriggeredAcquisition)
        self.radio_TriggerInternal.clicked.connect(self.click_radio_trigger)
        self.radio_TriggerExternal.clicked.connect(self.click_radio_trigger)
        self.edit_TriggerInstrumentDelay.returnPressed.connect(self.press_enter_edit_TriggerInstrumentDelay)
        self.edit_RefreshTime.returnPressed.connect(self.press_enter_edit_RefreshTime)
        self.combo_TriggerInstruments.currentIndexChanged.connect(self.change_combo_TriggerInstruments)
        self.button_SingleAcquisition.clicked.connect(self.click_button_SingleAcquisition)
        self.spinbox_NumbAcquisitions.valueChanged.connect(self.value_changed_spinbox_NumbAcquisitions)
        self.edit_AcquisitionRefreshTime.returnPressed.connect(self.press_enter_edit_AcquisitionRefreshTime)
        self.box_MakeAverage.stateChanged.connect(self.click_box_MakeAverage)
        return self

###########################################################################################################
### Event Slots. They are normally triggered by signals from the model, and change the GUI accordingly  ###
###########################################################################################################

    def on_single_set_acquisition_change(self,status):
        if self.doing_triggered_acquisition == False: #If we are doing a triggered acquisition, we dont change anything in the GUI when a single set of acquisitions is either started or ended
            if status == self.experiment.SIG_SINGLE_SET_ACQUISITION_STARTED:
                ergastirio.utils.disable_widget(self.widgets_box_trigger)
                ergastirio.utils.disable_widget(self.widgets_box_acquisitionset_first_row)
                self.button_SingleAcquisition.setText('Stop')
            if status == self.experiment.SIG_SINGLE_SET_ACQUISITION_ENDED:
                ergastirio.utils.enable_widget(self.widgets_box_trigger)
                ergastirio.utils.enable_widget(self.widgets_box_acquisitionset_first_row)
                self.button_SingleAcquisition.setText('Take single set acquisitions')

    def on_triggered_acquisition_change(self,status):
        if status == self.experiment.SIG_TRIGGERED_ACQUISITION_STARTED:
            self.doing_triggered_acquisition = True
            ergastirio.utils.enable_widget(self.widgets_box_trigger)
            ergastirio.utils.disable_widget(self.widgets_box_trigger_internal + self.widgets_box_trigger_external )
            ergastirio.utils.disable_widget(self.widgets_box_acquisitionset)
            self.button_StartPauseTriggeredAcquisition.setText('Pause triggered\nacquisition')
            pass
        if status == self.experiment.SIG_TRIGGERED_ACQUISITION_ENDED:
            self.doing_triggered_acquisition = False
            ergastirio.utils.enable_widget(self.widgets_box_trigger)
            ergastirio.utils.enable_widget(self.widgets_box_acquisitionset)
            self.button_StartPauseTriggeredAcquisition.setText('Start triggered\nacquisition')
            pass

    def on_trigger_modality_change(self,status):
        if status == self.experiment.SIG_TRIGGERED_MODALITY_INTERNAL:
            self.radio_TriggerInternal.setChecked(True)
            ergastirio.utils.enable_widget([self.edit_RefreshTime,self.label_RefreshTime])
            ergastirio.utils.disable_widget([self.combo_TriggerInstruments,self.edit_TriggerInstrumentDelay,self.label_TriggerExternal,self.label_TriggerInstrumentDelay])
        if status == self.experiment.SIG_TRIGGERED_MODALITY_EXTERNAL:
            self.radio_TriggerExternal.setChecked(True)
            ergastirio.utils.disable_widget([self.edit_RefreshTime,self.label_RefreshTime])
            ergastirio.utils.enable_widget([self.combo_TriggerInstruments,self.edit_TriggerInstrumentDelay,self.label_TriggerExternal,self.label_TriggerInstrumentDelay])

    def on_trigger_instrument_change(self,trigger_instrument):
        pass

    def on_time_inteval_internal_trigger_change(self,time_interval):
        self.edit_RefreshTime.setText(f"{time_interval}") 
        pass

    def on_time_interval_multiple_acquisitions_per_set_change(self,time_interval):
        self.edit_AcquisitionRefreshTime.setText(f"{time_interval}") 
        pass

    def on_numb_acquisitions_per_trigger_change(self,numb_acquisition):
        self.spinbox_NumbAcquisitions.setValue(numb_acquisition)
        pass

    def on_change_make_average_set_acquisition(self,status):
        self.box_MakeAverage.setChecked(status)

    def on_list_instruments_updated(self,list_instruments):
        self.combo_TriggerInstruments.blockSignals(True)
        self.combo_TriggerInstruments.clear()
        self.combo_TriggerInstruments.addItems(list_instruments) 
        self.combo_TriggerInstruments.blockSignals(False)

    def on_trigger_instrument_changed(self,instrument_index):
        self.combo_TriggerInstruments.blockSignals(True)
        self.combo_TriggerInstruments.setCurrentIndex(instrument_index)
        self.combo_TriggerInstruments.blockSignals(False)

    def on_trigger_delay_changed(self,delay):
        self.edit_TriggerInstrumentDelay.setText(f"{delay}") 

#######################
### END Event Slots ###
#######################

###################################################################################################################################################
### GUI Events Functions. They are triggered by direct interaction with the GUI, and they call methods of the experiment (i.e. the model) object.###
###################################################################################################################################################

    def click_button_StartPauseTriggeredAcquisition(self): 
        if(self.experiment.triggered_acquisition == False):
            self.press_enter_edit_AcquisitionRefreshTime()
            self.press_enter_edit_RefreshTime()
            #self.press_enter_edit_TriggerInstrumentDelay()
            self.experiment.start_triggered_acquisition()
        elif (self.experiment.triggered_acquisition == True):
            self.experiment.stop_triggered_acquisition()
        return

    def click_button_SingleAcquisition(self):
        if(self.experiment.single_set_acquisition == False):
            self.press_enter_edit_AcquisitionRefreshTime()
            self.experiment.start_single_set_acquisitions()
        elif (self.experiment.single_set_acquisition == True): #When this is true, the experiment is currently taking a single acquisition
            self.experiment.stop_single_set_acquisitions()
        return

    def press_enter_edit_RefreshTime(self):
        refresh_time_internal_trigger = self.edit_RefreshTime.text()
        self.experiment.time_interval_internal_trigger = refresh_time_internal_trigger #When doing this assignment, the setter of self.experiment.time_interval_internal_trigger will check if the input is valid, and eventually update the value
        return True
 
    def press_enter_edit_AcquisitionRefreshTime(self):
        acquisition_refresh_time = self.edit_AcquisitionRefreshTime.text()
        self.experiment.time_interval_multiple_acquisitions_per_set = acquisition_refresh_time #When doing this assignment, the setter of self.experiment.time_interval_multiple_acquisitions_per_set will check if the input is valid, and eventually update the value
        return True

    def press_enter_edit_TriggerInstrumentDelay(self):
        self.change_combo_TriggerInstruments()

    def value_changed_spinbox_NumbAcquisitions(self):
        self.experiment.numb_acquisitions_per_set = self.spinbox_NumbAcquisitions.value()

    def click_radio_trigger(self):
        if self.radio_TriggerInternal.isChecked():
            self.experiment.trigger_modality = 'internal'
            self.press_enter_edit_RefreshTime()
        if self.radio_TriggerExternal.isChecked():
            self.experiment.trigger_modality = 'external'
            self.change_combo_TriggerInstruments()
            
    def change_combo_TriggerInstruments(self):
        trigger_delay = self.edit_TriggerInstrumentDelay.text()
        self.experiment.set_trigger_instrument(self.combo_TriggerInstruments.currentIndex(),delay=trigger_delay)
        return

    def click_box_MakeAverage(self, state):
        if state == QtCore.Qt.Checked:
            status_bool = True
        else:
            status_bool = False
        self.experiment.make_average_set_acquisitions = status_bool

#################################
### END GUI Events Functions ####
#################################

############################################################################################################
## END acquisition_control                                                                                 # 
############################################################################################################




############################################################################################################
## data_management                                                                                         # 
############################################################################################################

class data_management():
    """
    Panel which contains the buttons 'Save Data','Delete all data','Delete last row'
    """
    def __init__(self, parent, experiment):
        """
        parent        = a QWidget (or QMainWindow) object that will be the parent of this gui
        experiment    = an experiment() object, whose acquisition will be controlled by this panel
        """
        self.parent = parent
        self.experiment  = experiment 

    def create_gui(self): 
        vbox1 = Qt.QVBoxLayout()

        self.button_SaveData = Qt.QPushButton("Save data")
        self.button_SaveData.setToolTip('Save all currently stored data in a .csv file.') 
        self.button_SaveData.clicked.connect(self.click_button_SaveData)
        self.button_DeleteAllData = Qt.QPushButton("Delete all data")
        self.button_DeleteAllData.setToolTip('Delete all currently stored data.') 
        self.button_DeleteAllData.clicked.connect(self.click_button_DeleteAllData)
        self.button_DeleteLastRowData = Qt.QPushButton("Delete last row")
        self.button_DeleteLastRowData.setToolTip('Delete last row of stored data.') 
        self.button_DeleteLastRowData.clicked.connect(self.click_button_DeleteLastRowData)

        vbox1.addWidget(self.button_SaveData)
        vbox1.addWidget(self.button_DeleteAllData)
        vbox1.addWidget(self.button_DeleteLastRowData)
        #vbox1.addStretch(1)

        vbox = Qt.QVBoxLayout()
        vbox.addLayout(vbox1)  
        #vbox.addStretch(1)

        self.parent.setLayout(vbox) #This line makes sure that all widgets defined so far are assigned to the widget defines in self.parent
        self.parent.resize(self.parent.minimumSize())

        return self

    ### GUI Events Functions

    def click_button_SaveData(self): 
        filename, _ = Qt.QFileDialog.getSaveFileName(self.parent, 
                        "Save File", "", "Csv Files (*.csv);;Text Files (*.txt)")
        if filename:
            self.experiment.save_stored_data(filename)
        return

    def click_button_DeleteAllData(self):
        answer = Qt.QMessageBox.question(self.parent,'', "Are you sure?", Qt.QMessageBox.Yes | Qt.QMessageBox.No, Qt.QMessageBox.No)
        if answer == Qt.QMessageBox.Yes:
            self.experiment.delete_current_data()
        return

    def click_button_DeleteLastRowData(self):
        self.experiment.delete_row_from_data(-1)
        return