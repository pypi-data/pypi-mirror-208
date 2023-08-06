'''
This module contains several function which are used to initialize a certain experiment. 
Before using the functions in this module, an experiment() object needs to be created (typically by the main.pyw file), and a config file needs to be assigned to 
the experiment. After a config file have been assigned to the experiment, the function load_config_and_setup_exp(exp) is called, where exp is the experiment() object.
'''
import PyQt5.QtWidgets as Qt# QApplication, QWidget, QMainWindow, QPushButton, QHBoxLayout
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import logging
import numpy as np
import importlib
#from importlib.metadata import version  
import json
import ergastirio.utils
 
def set_up_experiment(exp):
    '''
    This function initializes a certain experiment (passed as an input argument) based on the settings stored in the dictionary exp.settings.
    It subsequently calls several functions to load instruments, initialize storage arrays, validate user configs
    '''
        
    if not load_instruments(exp):       #Load all instruments based on the strings specified in the list exp.settings['Instruments_Settings']
        return False

    #if not load_all_ramps(exp):         #Check which instrument has a ramp object
    #    return False

    if not generate_data_headers(exp):  #Based on the loaded instruments, and on the data created by each instrument, it populates the list of strings exp.data_headers
        return False

    if not load_and_check_postprocessed_data(exp):
        return False

    generate_list_valid_data_names(exp) # Use headers, plus "acq#", to generate a list of names that can be used for plotting and post-processing

    initialize_storage_variable(exp)    #Create Storage variables

    initialize_acquisition_settings(exp)
       
    if not validate_plots_settings(exp): #check if the plots settings specified in the .json file are valid (i.e. any quantity defined in 'x' and 'y' is a valid device data
        return False
    return True

def load_instruments(exp):
    ''' 
    Loads all instruments defined in exp.settings['Instruments_Settings']['instruments'] and stores them in the list exp.instruments
    For each intruments, the respective interface object is also created, but not the gui.

    Returns true if all instruments were loaded correctly, false otherwise
    '''
    exp.logger.info(f"Loading all instruments specified in {exp.config_file}...")
    exp.instruments = []
    i=0
    for instrument in exp.settings['Instruments_Settings']['instruments'] :

        # Check if the name of instrument corresponds to an install package ## TO DO : check also that it is package supported by ergastirio
        if (importlib.util.find_spec(instrument) is None):
            exp.logger.error(f"{instrument} is not a valid python package. Fix this error and restart this application")
            return False
        device_module =  importlib.import_module(instrument+'.main')

        # Check that the main module of this instrument contains a class interface
        if not(hasattr(device_module,'interface')):
            exp.logger.error(f"{instrument} is a valid package, but it does not contain an 'interface' class.")
            return False

        fullname = f"dev{i}_{instrument}"

        try:
            exp.logger.info(f"Loading an interface for instrument {instrument}, with name : {fullname}")
            config_dict=None
            if len(exp.settings["Instruments_Settings"]["settings_each_instrument"]) > i:
                config_dict=exp.settings["Instruments_Settings"]["settings_each_instrument"][i]
                if isinstance(exp.settings["Instruments_Settings"]["settings_each_instrument"][i],dict):
                    exp.logger.info(f"Found settings for this interface in the file {exp.config_file}.")
                else:
                    config_dict = None    
            exp.instruments.append(
                                        {    
                                        'name':f"dev{i}",
                                        'fullname':fullname,
                                        'type':instrument,
                                        'device_module' : device_module,
                                        'interface_class':device_module.interface,
                                        'interface':  device_module.interface(  app=exp.app,
                                                                                name_logger=fullname,
                                                                                config_dict=config_dict,
                                                                                virtual=exp.virtual_modality) 
                                        }
                                    )
            exp.func_logger_handler_adder(logger=logging.getLogger(exp.instruments[-1]['fullname'])) #Having this here is kind of ugly because it partially breaks the model-view philosophy; on the other hand it allows catching the logs immediately
        except Exception as e:
            exp.logger.error(f"An error occurred while loading the instrument {instrument}: {e}")
            return False
        
        i = i+1
    return True

def generate_data_headers(exp):
    ''' 
    Generates a list of data headers for the experiment exp, based on the loaded instruments.
    For each instrument in exp.instruments, the list of output data is contained in the keys of the dictionary instrument.['interface_class'].output.
    The headers 'timestamp' and 'time' are also added at the beginning of the data headers.

    Returns True
    '''
    exp.logger.info(f"Preparing the data headers...")
    exp.data_headers =[]
    exp.data_headers.append('timestamp')
    exp.data_headers.append('time')
    for instrument in exp.instruments:
        if hasattr(instrument['interface_class'],'output'):
            for key in instrument['interface_class'].output.keys():
                exp.data_headers.append(instrument['name']+'.'+key)
        else:
            exp.logger.info(f"Instrument {instrument['fullname']} does not have an \'output\' dictionary defined. I wil assume that it does not produce data.")
    exp.logger.info(f"The following data will be acquired: {exp.data_headers}")

    return True

def load_and_check_postprocessed_data(exp):
    ''' 
    Load the post-processed data defined in exp.settings['Instruments_Settings']['post_processed_data'] (if any is defined)
    and checks that each of them represents a valid formula.
    It appends the name of each post-processed data to the list exp.data_headers.

    Returns true if all post-processed data are valid, false otherwhise.

    TO DO: check that no post-processed data has same name as another valid data.
    '''
    if ('post_processed_data' in exp.settings['Instruments_Settings'].keys()):
        exp.logger.info(f"Validating post-processed data...")
        for post_processed_data_name,post_processed_data in exp.settings['Instruments_Settings']['post_processed_data'].items():
            (msg,flag) = ergastirio.utils.check_list_is_valid_formula(post_processed_data,valid_variable_names=exp.data_headers)
            if not(flag==1):
                exp.logger.error(f"A problem occurred with the post-processed data: {msg}.")
                return False
            exp.data_headers.append(post_processed_data_name)

    return True

def generate_list_valid_data_names(exp):
    exp.valid_data_names = exp.data_headers.copy()    #The list of headers gives a list of valid data can be plotted. This assume that, for each row of data, each entry is a scalar
    exp.valid_data_names.append("acq#")               #Need to implement this better
    
def initialize_storage_variable(exp):
    ''' Initialize all arrays for data storage. '''      
    exp.data = ergastirio.classes.EnhancedList([]) #np.empty([0,len(exp.data_headers)]) 
    exp.data_std = ergastirio.classes.EnhancedList([])
    return True

def initialize_acquisition_settings(exp):
    if 'trigger_modality' in exp.settings['General_Settings'].keys():
        exp.trigger_modality = exp.settings['General_Settings']['trigger_modality']
    else:
        return
    if 'trigger_instrument' in exp.settings['Instruments_Settings'].keys():
        if 'trigger_delay' in exp.settings['Instruments_Settings'].keys():
            delay = exp.settings['Instruments_Settings']['trigger_delay']
        else:
            delay = 0
        exp.set_trigger_instrument(exp.settings['Instruments_Settings']['trigger_instrument'], delay = delay)

    
def validate_plots_settings(exp):
    '''
    Looks at the content of exp.settings['Plot_Settings']['plots'] and check that all settings specified by the user are valid. If the user specificied an empty plot,
    it uses "acq#" for x axis and the first valid data (excluding 'timestamp' and 'time') for the y axis
    '''
    exp.logger.info(f"Validating all plot settings...")
    exp.plots = []

    for plotindex, plot in enumerate(exp.settings['Plot_Settings']['plots']):
        if isinstance(plot,dict):
            if 'x' in plot.keys():
                if not plot['x'] in exp.valid_data_names:
                    exp.logger.error(f"Plot #{plotindex}: {plot['x']} is not a valid device data")
                    return False
            else:
                plot['x'] =  exp.valid_data_names[-1]
            if 'y' in plot.keys():
                if isinstance(plot['y'],str):
                    plot['y'] = [plot['y']]
                for y_data in plot['y']:
                    if not y_data in exp.valid_data_names:
                        exp.logger.error(f"Plot #{plotindex}: {y_data} is not a valid device data")
                        return False    
            else:
                plot['y'] =  [exp.valid_data_names[2]]
        else:
            exp.logger.error(f"Each plot must be defined in the .json file as a dictionary containing an 'x' and a 'y' key.")
            return False
        exp.plots.append({'name':f"plot{plotindex}",
                            'x':plot['x'],
                            'y':plot['y']})
        exp.logger.info(f"Plot #{plotindex}, x = {plot['x']}, y = {plot['y']}")
    return True

