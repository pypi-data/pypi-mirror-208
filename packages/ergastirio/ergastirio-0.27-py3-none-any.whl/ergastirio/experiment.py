import ergastirio.experiment_initializer
import PyQt5.QtCore as QtCore
import logging
import numpy as np
import datetime
import ergastirio.utils
import os
import json
import abstract_instrument_interface
## We follow as much as possible the model-view-controller paradigm. The class experiment() defines a model. The model emits signals (defined as QtCore.pyqtSignal object) 
# to let the different parts of the GUI know what is happening

class experiment(QtCore.QObject):
    """
    ......
    ...

    Attributes
    ----------
    Data
        instance of ergastirio.classes.EnhancedList
    verbose
        Defined as a @property. Can be set.
    
    name_logger
        Defined as a @property. Can be set.

    config_file
        Defined as a @property. Can be set. Changing its value will automatically load the new experiment settings.
    
    time_interval_internal_trigger
        Defined as a @property. Can be set.
    
    time_interval_multiple_acquisitions_per_set
        Defined as a @property. Can be set.
    
    numb_acquisitions_per_set
        Defined as a @property. Can be set.

    trigger_modality
        Defined as a @property. Can be set.

    make_average_set_acquisitions
        Defined as a @property. Can be set.

    settings = {
        "General_Settings": {   
                    "time_interval_internal_trigger": 0.2,              #in s. Refresh time of internal trigger (when used)
                    "numb_acquisitions_per_set": 1,                     #Every time that a trigger is "fired" (either by internal trigger, or by external trigger, or by clicking on 'take single acqusitions') 
                    "time_interval_multiple_acquisitions_per_set": 0.2, #the software takes a number of acquisitions, equal to numb_acquisitions_per_set, and separated in time by time_interval_multiple_acquisitions_per_set
                    "average_acquisition": 0,                           #When this is set to true, after taking a number of acquisitions (numb_acquisitions_per_set), it averages them and replace them by the average
                    "trigger_delay": 0,
                    "trigger_modality": 'internal',                     # can be either 'internal' or 'external'
                    "make_average_set_acquisitions": 0,                              #0 -> No Average, 1 -> Make Average
                    "trigger_instrument" : ''
                    }
                }

    data_headers

    single_set_acquisition 
    
    continuous_acquisition

    -------


    Methods 
    -------
    set_trigger_modality(modality)

    set_average_set_acquisition(status)

    read_current_data_from_all_instruments()

    store_current_data_from_all_instruments()

    [TO FINISH]

    """

    ## SIGNALS THAT WILL BE USED TO COMMUNICATE WITH THE GUI
    #                                                                           | Triggered when ...                                        | Sends as parameter    
    #                                                         #                 -----------------------------------------------------------------------------------------------------------------------         
    sig_single_set_acquisition = QtCore.pyqtSignal(int)                        #|                                                           |     
    sig_triggered_acquisition = QtCore.pyqtSignal(int)                         #|                                                           |  
    sig_trigger_modality = QtCore.pyqtSignal(str) 
    sig_trigger_instrument = QtCore.pyqtSignal(int)
    sig_trigger_instrument_delay = QtCore.pyqtSignal(float) 
    sig_list_instruments = QtCore.pyqtSignal(list) 
    sig_list_ramps = QtCore.pyqtSignal(list)                                   #|                                                           | List of all ramps defined in all instruments. The format is [ [id_instrument, fullname_instrument, ramp_object, index_ramp_child], [...] ... ] 
    sig_time_interval_internal_trigger = QtCore.pyqtSignal(float) 
    sig_time_interval_multiple_acquisitions_per_set = QtCore.pyqtSignal(float) 
    sig_numb_acquisitions_per_set = QtCore.pyqtSignal(int) 
    sig_make_average_set_acquisition = QtCore.pyqtSignal(int) 
    sig_data_updated = QtCore.pyqtSignal(int)                                  #| A generic data update has happened                        |
    sig_data_updated_added_new_rows = QtCore.pyqtSignal(int)                   #| A certain number of rows has been appended to the data    | Number of appended rows
    sig_data_updated_deleted_all_data = QtCore.pyqtSignal(int)                 #| All data has been deleted                                 |
    sig_data_updated_deleted_last_rows = QtCore.pyqtSignal(int)                #| A certain number of rows has been deleted from the data   | Number of deleted rows 
    
    
    
    ##
    # Identifier codes used for view-model communication. Other general-purpose codes are specified in abstract_instrument_interface
    SIG_SINGLE_SET_ACQUISITION_STARTED = 1
    SIG_SINGLE_SET_ACQUISITION_ENDED = 2
    SIG_TRIGGERED_ACQUISITION_STARTED = 1
    SIG_TRIGGERED_ACQUISITION_ENDED = 2
    SIG_TRIGGERED_MODALITY_INTERNAL = 'internal'
    SIG_TRIGGERED_MODALITY_EXTERNAL = 'external'
    SIG_AVERAGE_SET_ACQUISITION_ON = 1
    SIG_AVERAGE_SET_ACQUISITION_OFF = 2
    SIG_DATA_UPDATED_NEW_ROWS = 1
    SIG_DATA_UPDATED_DELETED_ALL_DATA = 2
    SIG_DATA_UPDATED_DELETED_LAST_ROWS = 3

    _verbose = True #Keep track of whether this instance of the interface should produce logs or not
    _name_logger = ''
    _config_file = ''

    def __init__(self, app, name_logger=__package__):
        # app           = The pyqt5 QApplication() object
        # name_logger   = The name of the logger used for this particular experiment. If none is specified, the name of the package (i.e. ergastirio) is used as logger name

        QtCore.QObject.__init__(self)
        self.app = app

        self.name_logger = name_logger #Setting this property will also create the logger,set output style, connect the logger output to the logging textarea and store the logger object in self.logger (see @name_logger.setter) 
        
        
        self.load_default_settings() ### Load default values of settings (might be overwritten by settings passed by user later)

        self.data_headers =[]   #List of strings, will contain the label of each 'column" of acquired data, based on the instruments connected, in the format "dev#i_dataname#j"
                                #where #i runs from 0 to the number of instruments minus 1, and dataname#j is the name of the jth data created by the i-th instrument.
                                #the data created by each instrument are specified by the keys of the 'output' dictionary defined in the interface of each instrument

        self.single_set_acquisition = False     #Boolean variable, true while performing a single-set acquisition
        self.triggered_acquisition = False      #Boolean variable, true when performing continuous acquisition (i.e. when internal trigger is used)

        return

    def load_default_settings(self):
        folder_default_file = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(folder_default_file,'default_settings.json')
        self.logger.info(f"Loading default settings...")
        try:
            with open(config_file) as jsonfile:
                self.settings = json.load(jsonfile)
        except Exception as e:
            self.logger.error(f"An error occurred while loading default settings from  {config_file}. Fix the error and restart this application\n: {e}")

    def initiate(self, config_file, func_logger_handler_adder = None, **kwargs):
        if ('virtual' in kwargs.keys()) and (kwargs['virtual'] == True):
            self.logger.info(f"Initializing the experiment with virtual instruments (when available)...")
            self.virtual_modality = True 
        else:    
            self.virtual_modality = False
        self.func_logger_handler_adder = func_logger_handler_adder
        self.func_logger_handler_adder(logger=logging.getLogger(self.name_logger)) #Having this here is kind of ugly because it partially breaks the model-view philosophy; on the other hand it allows catching the logs immediately
        self.config_file = config_file 
        self.load_settings()
        self.logger.info(f"Initializing the experiment...")
        return ergastirio.experiment_initializer.set_up_experiment(self)

    def load_settings(self):
        self.logger.info(f"Loading the content of {self.config_file}")
        try:
            with open(self.config_file) as jsonfile:
                settings = json.load(jsonfile)
                for key in settings.keys():
                    if key in self.settings.keys():
                        self.settings[key].update(settings[key])
                    else:
                        self.settings[key] = settings[key]
        except Exception as e:
            self.logger.error(f"An error occurred while loading the file {self.config_file}. Fix the error and restart this application\n: {e}")

    def save_settings(self):
        if self.config_file:
            self.logger.info(f"Storing current settings for this experiment into the file \'{self.config_file}\'...")
            #Collect settings dictionaries from all instruments
            list_settings_instruments = [instrument['interface'].settings for instrument in self.instruments]
            self.settings["Instruments_Settings"]["settings_each_instrument"] = list_settings_instruments
            try:
                with open(self.config_file, 'w') as fp:
                    json.dump(self.settings, fp, indent=4, sort_keys=True)
            except Exception as e:
                self.logger.error(f"An error occurred while saving settings in the file {self.config_file}: {e}")
        return

    def fire_all_signals(self):
        """
        Fire all signals, communicating the current value of several parameters. This function is typically called from the GUI of the experiment after the GUI has been partially
        initiallized. By making the experiment object fire all its parameters, the GUI can properly populate all of its field
        """
        self.sig_time_interval_internal_trigger.emit(self.settings["General_Settings"]['time_interval_internal_trigger'])
        self.sig_time_interval_multiple_acquisitions_per_set.emit(self.settings["General_Settings"]['time_interval_multiple_acquisitions_per_set'])
        self.sig_numb_acquisitions_per_set.emit(self.settings["General_Settings"]['numb_acquisitions_per_set'])
        self.sig_make_average_set_acquisition.emit(self.settings["General_Settings"]['make_average_set_acquisitions'])
        self.sig_triggered_acquisition.emit(self.SIG_TRIGGERED_ACQUISITION_ENDED)
        self.sig_single_set_acquisition.emit(self.SIG_SINGLE_SET_ACQUISITION_ENDED)
        self.sig_trigger_modality.emit(self.settings["General_Settings"]['trigger_modality'])
        self.sig_list_instruments.emit([instrument['fullname'] for instrument in self.instruments])
        self.sig_list_ramps.emit(self.create_list_ramps())
        self.sig_trigger_instrument.emit(self.settings["Instruments_Settings"]['trigger_instrument'])
        self.sig_trigger_instrument_delay.emit(self.settings["Instruments_Settings"]['trigger_delay'])

    def create_list_ramps(self):
        list_ramps = []
        for index, instrument in enumerate(self.instruments):
            if hasattr(instrument['interface'],'ramp') and isinstance(instrument['interface'].ramp, abstract_instrument_interface.ramp):
                list_ramps.append([index,instrument['fullname'],instrument['interface'].ramp])

        #Does another for loop to check if the ramps have children; if so, stores the index of the child ramp as 4th element of each list (-1 otherwise)
        for index, ramp in enumerate(list_ramps):
            list_ramps[index].append(-1)
            ramp_object = ramp[2]
            if hasattr(ramp_object,'child_ramp') and isinstance(ramp_object.child_ramp, abstract_instrument_interface.ramp):
                for index_possible_child,ramp_possible_child in enumerate(list_ramps):
                    if ramp_possible_child[2] == ramp_object.child_ramp:
                        list_ramps[index][3] = index_possible_child
                        break
        return list_ramps

    @property
    def verbose(self):
        return self._verbose
    @verbose.setter
    def verbose(self,verbose): #When the verbose property is changed, we also update accordingly the level of the logger object
        self._verbose = verbose
        if verbose: loglevel = logging.INFO
        else: loglevel = logging.CRITICAL
        self.logger.setLevel(level=loglevel)

    @property
    def name_logger(self):
        return self._name_logger
    @name_logger.setter
    def name_logger(self,name): #Create logger, and set default output style.
        self._name_logger = name
        self.logger = logging.getLogger(self._name_logger)
        self.verbose = self._verbose #This will automatically set the logger verbosity too
        if not self.logger.handlers:
            formatter = logging.Formatter(f"[{self.name_logger}]: %(message)s")
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        self.logger.propagate = False

    @property
    def config_file(self):
        return self._config_file
    @config_file.setter
    def config_file(self,config_file): #Setup a new config file, and then call the function ergastirio.experiment_initializer.load_config_and_setup_exp to initialize the experiment
        self.logger.info(f"Setting the config file to {config_file}...")
        self._config_file = config_file

    @property
    def time_interval_internal_trigger(self):
        return self.settings["General_Settings"]['time_interval_internal_trigger']
    @time_interval_internal_trigger.setter
    def time_interval_internal_trigger(self,r):
        try: 
            r = float(r)
            if r < 0.001:
                self.logger.error(f"The time interval of the internal trigger must be positive and >= 1ms.")
            else:
                if not self.settings["General_Settings"]['time_interval_internal_trigger'] == r:
                    self.settings["General_Settings"]['time_interval_internal_trigger'] = r
                    self.logger.info(f"The time interval of the internal trigger is now {r} s.")
        except ValueError:
            self.logger.error(f"The time interval of the internal trigger must be a valid number.")
        self.sig_time_interval_internal_trigger.emit(self.settings["General_Settings"]['time_interval_internal_trigger'])
        return self.settings["General_Settings"]['time_interval_internal_trigger']

    @property 
    def time_interval_multiple_acquisitions_per_set(self):
        return self.settings["General_Settings"]['time_interval_multiple_acquisitions_per_set']
    @time_interval_multiple_acquisitions_per_set.setter
    def time_interval_multiple_acquisitions_per_set(self,r):
        try: 
            r = float(r)
            if r < 0.001:
                self.logger.error(f"The time interval between multiple acquisitons must be positive and >= 1ms.")
            else:
                if not self.settings["General_Settings"]['time_interval_multiple_acquisitions_per_set'] == r:
                    self.settings["General_Settings"]['time_interval_multiple_acquisitions_per_set'] = r
                    self.logger.info(f"The time interval between multiple acquisitons is now {r} s.")
        except ValueError:
            self.logger.error(f"The time interval between multiple acquisitons must be a valid number.")
        self.sig_time_interval_multiple_acquisitions_per_set.emit(self.settings["General_Settings"]['time_interval_multiple_acquisitions_per_set'])
        return self.settings["General_Settings"]['time_interval_multiple_acquisitions_per_set']

    @property
    def numb_acquisitions_per_set(self):
        return self.settings["General_Settings"]['numb_acquisitions_per_set']
    @numb_acquisitions_per_set.setter
    def numb_acquisitions_per_set(self,n):
        try: 
            n = int(n)
            if n < 1:
                self.logger.error(f"The number of acquisitions per set must be a positive integer.")
            else:
                if not self.settings["General_Settings"]['numb_acquisitions_per_set'] == n:
                    self.settings["General_Settings"]['numb_acquisitions_per_set'] = n
                    self.logger.info(f"The number of acquisitions per set is now {n}.")
        except ValueError:
            self.logger.error(f"The number of acquisitions per set must be a positive integer.")
        self.sig_numb_acquisitions_per_set.emit(self.settings["General_Settings"]['numb_acquisitions_per_set'])
        return 

    @property
    def trigger_modality(self):
        return self.settings["General_Settings"]['trigger_modality']
    @trigger_modality.setter
    def trigger_modality(self,modality):
        if not (modality in ['internal','external']):
            self.logger.error(f"Trigger modality must be either 'internal' or 'external'.")
            self.reset_all_triggers() #Make sure to remove any trigger from all instruments
            return
        self.settings["General_Settings"]['trigger_modality'] = modality
        self.sig_trigger_modality.emit(modality)
        self.logger.info(f"Trigger modality set to {modality}.")

    @property
    def make_average_set_acquisitions(self):
        return bool(self.settings["General_Settings"]['make_average_set_acquisitions'])
    @make_average_set_acquisitions.setter
    def make_average_set_acquisitions(self,modality):
        if not (modality in [True, False]):
            self.logger.error(f"make_average_set_acquisitions must be either True or False.")
            return
        self.settings["General_Settings"]['make_average_set_acquisitions'] = modality
        self.sig_make_average_set_acquisition.emit(modality)
        self.logger.info(f"make_average_set_acquisitions set to {modality}.")

    def read_current_data_from_all_instruments(self,timestamp):
        '''
        Look into all the instruments interfaces (defined via the key 'interface' in each dictionary of the list exp.instruments) 
        and it extracts data from each instrument. From each instrument, the data to exctract is contained in the dictionary exp.instruments[i]['interface'].output
        '''
        current_data = []
        self.logger.info(f"Reading data from all instruments...")
        for instrument in self.instruments:
            instruments_data = instrument['interface'].read_current_output()
            instrument['interface'].receive_trigger(timestamp=timestamp)
            for data in instruments_data.values():
                current_data.append(data)  
        return current_data

    def store_current_data_from_all_instruments(self):
        '''
        '''
        now = datetime.datetime.now()
        time_string=now.strftime("%Y-%m-%d %H:%M:%S.%f")
        timestamp = datetime.datetime.timestamp(now)

        current_data = self.read_current_data_from_all_instruments(timestamp=timestamp) #Read the current data from all instruments
        acq_numb = len(self.data) + 1 #Calculate the number of rows of self.data, add 1 for the new row
        self.logger.info(f"[{time_string}] Acquisition #{acq_numb}")# {current_data}")
        current_data.insert(0, time_string)
        current_data.insert(0, timestamp )
        
        if ('post_processed_data' in self.settings['Instruments_Settings'].keys()):
            variables = {self.data_headers[i]: current_data[i] for i in range(len(current_data))}  #Create a dictionary with the values of the data that we just acquired
            for post_processed_data_name,post_processed_data_formula in self.settings['Instruments_Settings']['post_processed_data'].items():
                PostProcessedData = ergastirio.utils.evaluate_formula(post_processed_data_formula,variables)
                current_data.append(PostProcessedData)
        self.data.append(current_data)
        self.data_std.append([0]*(len(current_data)-2)) #Add a row of zeros to the standard deviations. The -2 is to avoid the columns corresponding to time and timestamp
        self.sig_data_updated_added_new_rows.emit(1)

    def start_single_set_acquisitions(self):
        self.single_set_acquisition = True
        self.sig_single_set_acquisition.emit(self.SIG_SINGLE_SET_ACQUISITION_STARTED)
        self.logger.info(f"Starting acquisition set...")
        self._single_set_of_acquisitions(counter=self.settings["General_Settings"]['numb_acquisitions_per_set'], time_interval=self.settings["General_Settings"]['time_interval_multiple_acquisitions_per_set'])

    def stop_single_set_acquisitions(self):
        self.single_set_acquisition = False
        self.sig_single_set_acquisition.emit(self.SIG_SINGLE_SET_ACQUISITION_ENDED)
        self.logger.info(f"Acquisition set stopped by user.")

    def _single_set_of_acquisitions(self,counter,time_interval):
        ''' Takes a single set of acquisitions. The number of acquisitions is  specified by the input counter, and they are separated by 
            a time interval specified by time_interval (in seconds).

            This function calls the function take_single_acquisition() and then calls itself after a time specified by self.settings['General_Settings']['time_interval_multiple_acquisitions_per_set'], 
            and with counter = counter -1. It also checks that self.single_set_acquisition = True, which can be used to interrupt the single set of measurements
            Normally, this function is called by another function with the input argument counter = self.settings['General_Settings']['numb_acquisitions_per_set']
        '''
        self.take_single_set_acquisition()
        if (counter > 1 and self.single_set_acquisition==True): 
            #if there are more acquisitions to be taken (counter>1) and if the measurment was not interrupted (self.single_set_acquisition==True), call the function again
            QtCore.QTimer.singleShot(int(time_interval*1e3), lambda: self._single_set_of_acquisitions(counter=counter-1,time_interval=time_interval))
        else:
            self.sig_single_set_acquisition.emit(self.SIG_SINGLE_SET_ACQUISITION_ENDED)
            self.single_set_acquisition=False
            self.logger.info(f"Acquisition set ended.")
            if self.settings["General_Settings"]['make_average_set_acquisitions'] and self.settings["General_Settings"]['numb_acquisitions_per_set']>1:
                self.logger.info(f"Averaging the last {self.settings['General_Settings']['numb_acquisitions_per_set']} acquisitions...")
                self.make_average_last_acquisitions(N=self.settings['General_Settings']['numb_acquisitions_per_set'])

    def take_single_set_acquisition(self):
        self.store_current_data_from_all_instruments()

    def make_average_last_acquisitions(self,N):
        '''
        Take the last N elements of self.data (where typically N = self.settings['General_Settings']['numb_acquisitions_per_set']) and replace them with their average (column-wise)
        It also populates the standard deviations (TO DO)
        '''
        rows_to_average = self.data[-N:]    #Get the last N rows
        timestamp = rows_to_average[0][0]   #Extract timestap and time of the first row to be averaged
        time = rows_to_average[0][1]
        rows_to_average2 = [elem[2:] for elem in rows_to_average] #Remove first two columns, which is timestamp and time
### TO DO: check if the list rows_to_average2 is indeed a 1D array of floats or integer
        averaged = (np.nanmean(np.array(rows_to_average2),axis=0)).tolist()
        std = (np.nanstd(np.array(rows_to_average2),axis=0)).tolist()
        averaged.insert(0, time)
        averaged.insert(0, timestamp )
        del self.data[-N:]      #Remove last N rows from data
        del self.data_std[-N:]  #Remove last N rows from data_std
        self.data.append(averaged)
        self.data_std.append(std)
        self.sig_data_updated.emit(0)

    def on_trigger_received(self):
        '''
        This function is invokeded either by the internal trigger, or by the instrument that act as a trigger. 
        Every time it is invoked, it takes a single set of acquisitions.
        '''
        self.start_single_set_acquisitions()

    def start_triggered_acquisition(self):
        if self.settings["General_Settings"]['trigger_modality'] == 'external':
            self.triggered_acquisition = True
            instrument_name = self.instruments[self.settings['Instruments_Settings']['trigger_instrument']]['fullname']
            self.logger.info(f"Triggered acquisition (external trigger) started...")
            self.logger.info(f"Waiting for trigger from {instrument_name}...")
            self.sig_triggered_acquisition.emit(self.SIG_TRIGGERED_ACQUISITION_STARTED)
        else:
            time_required_single_acquisition_set = (self.settings["General_Settings"]['numb_acquisitions_per_set']-1) * self.settings["General_Settings"]['time_interval_multiple_acquisitions_per_set']
            if self.settings["General_Settings"]['time_interval_internal_trigger'] <= time_required_single_acquisition_set:
                self.logger.error(f"Time interval of internal trigger ({self.settings['General_Settings']['time_interval_internal_trigger']} s) must be longer than the time required for a single acquisition set ({time_required_single_acquisition_set} s). Otherwise different acquisition sets would overlap in time, leading to unpredictable behaviour, and possibly the thermal death of the universe.")
                return
            self.triggered_acquisition = True
            self.sig_triggered_acquisition.emit(self.SIG_TRIGGERED_ACQUISITION_STARTED)
            self.logger.info(f"Triggered acquisition (internal trigger) started...")
            self.internal_trigger()
        return

    def stop_triggered_acquisition(self):
        self.triggered_acquisition = False
        self.sig_triggered_acquisition.emit(self.SIG_TRIGGERED_ACQUISITION_ENDED)
        self.logger.info(f"Triggered acquisition stopped.")

    def internal_trigger(self):
        '''
        Once called, this routine is executed continuosly, at time intervals set by self.settings["General_Settings"]['time_interval_internal_trigger']
        as long as (self.triggered_acquisition == True) and (self.settings["General_Settings"]['trigger_modality'] == 'internal').
        If the experiment is set in internal trigger modality and if self.triggered_acquisition == True, 
        the function self.update is called. Otherwise, none is done
        '''
        if (self.triggered_acquisition == True) and (self.settings["General_Settings"]['trigger_modality'] == 'internal'):
            self.on_trigger_received()
            QtCore.QTimer.singleShot(int(self.settings["General_Settings"]['time_interval_internal_trigger']*1e3), self.internal_trigger)  
                
    def on_external_trigger_received(self):
        '''
        This function is called by instruments if they are set as trigger and when they fire a trigger
        '''
        instrument_name = self.instruments[self.settings['Instruments_Settings']['trigger_instrument']]['fullname']
        if self.triggered_acquisition:
            if self.settings["General_Settings"]['trigger_modality'] == 'external':
                self.logger.info(f"Received trigger from an instrument...")
                self.on_trigger_received()
                #self.logger.info(f"Waiting for next trigger from {instrument_name}...")
            else:
                self.logger.info(f"Received a trigger from {instrument_name}, but experiment is not in 'external trigger' modality.")
        else:
            self.logger.info(f"Received a trigger from {instrument_name}, but experiment is not currently acquiring data.")

    def reset_all_triggers(self):
        for instrument in self.instruments: # First we remove the trigger from all instruments   
            try:
                instrument['interface'].set_trigger(None,delay=0)
            except Exception as e:
                self.logger.error(f"{e}")
        return

    def find_id_and_name_of_instrument(self,instrument):
        '''
        the input argument instrument can be either a number (indicating the position of the instrument in the list of instruments) or the full name of the instrument
        '''
        if isinstance(instrument,str):
            list_instruments = [inst['fullname'] for inst in self.instruments]
            if not (instrument in list_instruments):
                self.logger.error(f"{instrument} is not a valid instrument name")
                return False
            else:
                instrument_index = list_instruments.index(inst)
                instrument_name = instrument
        elif isinstance(instrument,int):
            if not(instrument in range(len(self.instruments))):
                self.logger.error(f"{instrument} is not a valid instrument index. Possible values are between 0 and {len(self.instruments) -1}.")
                return False
            else:
                instrument_index = instrument
                instrument_name = self.instruments[instrument]['fullname']
        else:
            self.logger.error(f"The input argument {instrument} must be either a string or an integer.")
            return False
        return instrument_index,instrument_name

    def set_trigger_instrument(self,instrument,delay=0):
        '''
        instrument can be either a number (indicating the position of the instrument in the list of instruments) or the full name of the instrument
        '''
        result = self.find_id_and_name_of_instrument(instrument)
        if not(result):
            return
        instrument_index,instrument_name = result

        try: 
            delay = float(delay)
        except ValueError:
            self.logger.error(f"The trigger delay must be a valid number.")
            return 
        if delay < 0:
            self.logger.error(f"The delay time must be positive and >= 1ms.")
            return 

        self.logger.info(f"Setting the instrument {self.instruments[instrument_index]['fullname']} as trigger, with delay = {delay} s...")
        self.reset_all_triggers()
        try:
            self.instruments[instrument_index]['interface'].set_trigger(self.on_external_trigger_received,delay=delay)
            self.settings['Instruments_Settings']['trigger_instrument'] = instrument_index
            self.settings['Instruments_Settings']['trigger_delay'] = delay
        except Exception as e:
            self.logger.error(f"An error occurred while setting {self.instruments[instrument_index]['fullname']} as trigger:\n {e}")
            return False

        self.logger.info(f"{self.instruments[instrument_index]['fullname']} was succesfully set as trigger.")
        self.sig_trigger_instrument.emit(self.settings["Instruments_Settings"]['trigger_instrument'])
        self.sig_trigger_instrument_delay.emit(self.settings['Instruments_Settings']['trigger_delay'])
        return True

    def connect_ramp_to_child(self,instrument_parent,instrument_child):
        result = self.find_id_and_name_of_instrument(instrument_parent)
        if not(result):
            return
        instrument1_index,instrument1_name = result
        result = self.find_id_and_name_of_instrument(instrument_child)
        if not(result):
            return
        instrument2_index,instrument2_name = result
        if instrument1_index == instrument2_index:
            self.logger.error(f"Cannot connect a ramp to itself.")
        else:
            self.instruments[instrument1_index]['interface'].ramp.connect_to_ramp_child(self.instruments[instrument2_index]['interface'].ramp)
            self.logger.info(f"The ramp of instrument {self.instruments[instrument1_index]['fullname']} was succesfully connected to the ramp of {self.instruments[instrument2_index]['fullname']}.")
        self.sig_list_ramps.emit(self.create_list_ramps())

    def disconnect_ramp_from_child(self,instrument_parent):
        result = self.find_id_and_name_of_instrument(instrument_parent)
        if not(result):
            return
        instrument1_index,instrument1_name = result
        self.instruments[instrument1_index]['interface'].ramp.disconnect_from_ramp_child()
        self.logger.info(f"The ramp of instrument {self.instruments[instrument1_index]['fullname']} was succesfully disconnected from its child.")
        self.sig_list_ramps.emit(self.create_list_ramps())

    def delete_current_data(self):
        self.logger.info(f"All store data was deleted.")
        self.data.clear()
        self.data_std.clear()
        self.sig_data_updated_deleted_all_data.emit(0)

    def delete_row_from_data(self,row):
        try:
            self.data.pop(row)
            self.data_std.pop(row)
            if row == -1:
                row = 'Last'
            self.logger.info(f"{row} row has been removed from data.")
            self.sig_data_updated_deleted_last_rows.emit(1)
        except:
            pass

    def save_stored_data(self,filename):
        '''
        Saves the values of all currently stored data on file. 
        The data are saved in a tabular form and delimited by a comma.
        '''
        d =','
        header = ''
        for h in self.data_headers:
            header = header + h + d 
        for h in self.data_headers: #We skip the first element of headers which corresponds to acquisition time
            header = header + (h+'_std') +  d
        if len(self.data)>0:
            A = np.concatenate((np.array(self.data), np.array(self.data_std)),axis=1)
            Nrows = A.shape[0]
        else:
            A = []
            Nrows = 0
        np.savetxt(filename, A, delimiter=d, header=header, comments="",fmt='%s')#,fmt=d.join(['%s'] + ['%e']*(A.shape[1]-1)))
        self.logger.info(f"Saved all stored data (number of rows = {Nrows}) in the file {filename}")
        return

    def close(self):
        self.save_settings()
        for instrument in self.instruments:
            try:
                instrument['interface'].close()
            except:
                pass

