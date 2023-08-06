import sys
import ntpath
import os
import pathlib
import shutil
import importlib
import importlib.util
import pandas as pd
import pickle
import csv
import re
from copy import deepcopy
from pathlib import Path
from typing import Union

from steam_sdk.plotters.PlotterMap2d import export_B_field_txt_to_map2d_SIGMA
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.builders.BuilderModel import BuilderModel
from steam_sdk.data.DataAnalysis import DataAnalysis, ModifyModel, ModifyModelMultipleVariables, ParametricSweep, LoadCircuitParameters, WriteStimulusFile
from steam_sdk.drivers.DriverFiQuS import DriverFiQuS
from steam_sdk.drivers.DriverLEDET import DriverLEDET
from steam_sdk.drivers.DriverPSPICE import DriverPSPICE
from steam_sdk.drivers.DriverPyBBQ import DriverPyBBQ
from steam_sdk.drivers.DriverSIGMA import DriverSIGMA
from steam_sdk.drivers.DriverXYCE import DriverXYCE
from steam_sdk.parsers.ParserYAML import dict_to_yaml, yaml_to_data
from steam_sdk.parsims.ParsimConductor import ParsimConductor
from steam_sdk.parsims.ParsimEventCircuit import ParsimEventCircuit
from steam_sdk.parsims.ParsimEventMagnet import ParsimEventMagnet
from steam_sdk.utils import parse_str_to_list
from steam_sdk.postprocs.PostprocsMetrics import PostprocsMetrics
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from steam_sdk.utils.parse_str_to_list import parse_str_to_list
from steam_sdk.utils.rgetattr import rgetattr
from steam_sdk.utils.sgetattr import rsetattr
from steam_sdk.utils.rhasattr import rhasattr
from steam_sdk.viewers.Viewer import Viewer
from steam_sdk.parsers.ParserPSPICE import writeStimuliFromInterpolation
from steam_sdk.plotters.PlotterMap2d import generate_report_from_map2d


class AnalysisSTEAM:
    """
        Class to run analysis based on STEAM_SDK
    """

    def __init__(self,
                 file_name_analysis: str = None,
                 file_path_list_models: str = '',
                 relative_path_settings: str = '',
                 verbose: bool = False):
        """
        Analysis based on STEAM_SDK
        :param file_name_analysis: full path to analysis.yaml input file  # object containing the information read from the analysis input file
        :param relative_path_settings: relative path to settings.xxx.yaml file
        :param verbose: if true, more information is printed to the console
        """

        # Initialize
        self.settings = DataSettings()  # object containing the settings acquired during initialization
        self.library_path = None
        self.output_path = None
        self.temp_path = None
        if file_path_list_models:
            with open(file_path_list_models, 'rb') as input_dict:
                self.list_models = pickle.load(input_dict)
        else:
            self.list_models = {}  # this dictionary will be populated with BuilderModel objects and their names

        self.list_sims = []  # this list will be populated with integers indicating simulations to run
        self.list_viewers = {}  # this dictionary will be populated with Viewer objects and their names
        self.list_metrics = {}  # this dictionary will be populated with calculated metrics
        self.verbose = verbose
        self.summary = None  # float representing the overall outcome of a simulation for parsims

        if isinstance(file_name_analysis, str) or isinstance(file_name_analysis, pathlib.PurePath):
            self.data_analysis = yaml_to_data(file_name_analysis, DataAnalysis)  # Load yaml keys into DataAnalysis dataclass
            # Read working folders and set them up
            self._set_up_working_folders()
            # Read analysis settings
            self._load_and_write_settings(relative_path_settings)
        elif file_name_analysis is None:
            self.data_analysis = DataAnalysis()
            if verbose: print('Empty AnalysisSTEAM() object generated.')


    def setAttribute(self, dataclassSTEAM, attribute: str, value):
        try:
            setattr(dataclassSTEAM, attribute, value)
        except:
            setattr(getattr(self, dataclassSTEAM), attribute, value)

    def getAttribute(self, dataclassSTEAM, attribute):
        try:
            return getattr(dataclassSTEAM, attribute)
        except:
            return getattr(getattr(self, dataclassSTEAM), attribute)

    def _set_up_working_folders(self):
        """
            ** Read working folders and set them up **
            This method performs the following tasks:
             - Check all folder paths are defined. If not, raise an exception.
             - Check if model library folder is present. If not, raise an exception.
             - Check if output folder is present. If not, make it.
             - Check if temporary folder is present. If so, delete it.
        """

        # Raise exceptions if folders are not defined.
        if self.data_analysis.WorkingFolders.library_path == 'gitlab':
            import steam_models
            steam_models_path = steam_models.__path__[0]
            self.data_analysis.WorkingFolders.library_path = steam_models_path
        elif self.data_analysis.WorkingFolders.library_path in ['same_as_analysis_yaml']:
            self.data_analysis.WorkingFolders.library_path = '.' + os.sep + self.data_analysis.GeneralParameters.model.name + os.sep + 'input'
        elif self.data_analysis.WorkingFolders.library_path in ['steam_models_in_same_folder']:
            self.data_analysis.WorkingFolders.library_path = '..' + os.sep + 'steam_models' + os.sep + 'input'
        if not self.data_analysis.WorkingFolders.library_path:
            raise Exception('Model library path must be defined. Key to provide: WorkingFolders.library_path')
        if not self.data_analysis.WorkingFolders.output_path:
            raise Exception('Output folder path must be defined. Key to provide: WorkingFolders.output_path')
        if not self.data_analysis.WorkingFolders.temp_path:
            raise Exception('Temporary folder path must be defined. Key to provide: WorkingFolders.temp_path')

        # Resolve all paths and re-assign them to the self variables
        if self.data_analysis.WorkingFolders.library_path == 'same_as_analysis_yaml_use_model_name':
            self.library_path = 'same_as_analysis_yaml_use_model_name'
        else:
            self.library_path = Path(self.data_analysis.WorkingFolders.library_path).resolve()
        self.output_path = Path(self.data_analysis.WorkingFolders.output_path).resolve()
        self.temp_path = Path(self.data_analysis.WorkingFolders.temp_path).resolve()

        if self.verbose:
            print('Model library path:    {}'.format(self.library_path))
            print('Output folder path:    {}'.format(self.output_path))
            print('Temporary folder path: {}'.format(self.temp_path))

        # Check if model library folder is present. If not, raise an exception.
        if self.library_path != 'same_as_analysis_yaml_use_model_name':
            if not os.path.isdir(self.library_path):
                raise Exception(f'Model library path refers to a not-existing folder: {self.library_path}. Key to change: WorkingFolders.library_path')

        # Check if output folder is present. If not, make it.
        make_folder_if_not_existing(self.output_path, verbose=self.verbose)

        # Check if temporary folder is present. If so, delete it.
        if os.path.isdir(self.temp_path):
            shutil.rmtree(self.temp_path)
            if self.verbose: print('Folder {} already existed. It was removed.'.format(self.temp_path))

    def _load_and_write_settings(self, relative_path_settings: str):
        """
            ** Read analysis settings **
            They will be read either form a local settings file (if flag_permanent_settings=False)
            or from the keys in the input analysis file (if flag_permanent_settings=True)
            :param relative_path_settings: only used if flag_permanent_settings=False and allows to specify folder containing settings.user_name.yaml
            :rtype: nothing, saves temporary settings.user_name.yaml on disk
        """

        verbose = self.verbose
        user_name = os.getlogin()
        settings_file = f"settings.{user_name}.yaml"

        if self.data_analysis.GeneralParameters.flag_permanent_settings:
            # Read settings from analysis input file (yaml file)
            if verbose:
                print('flag_permanent_settings is set to True')
            settings_dict = self.data_analysis.PermanentSettings.__dict__
        else:
            # Read settings from local settings file (yaml file)
            full_path_file_settings = os.path.join(Path(relative_path_settings).resolve(), settings_file)
            if verbose:
                print('flag_permanent_settings is set to False')
                print('user_name:               {}'.format(user_name))
                print('relative_path_settings:  {}'.format(relative_path_settings))
                print('full_path_file_settings: {}'.format(full_path_file_settings))
            if not os.path.isfile(full_path_file_settings):
                raise Exception(
                    'Local setting file {} not found. This file must be provided when flag_permanent_settings is set to False.'.format(
                        full_path_file_settings))
            settings_dict = yaml_to_data(full_path_file_settings)

        # Assign the keys read either from permanent-settings or local-settings
        for name, _ in self.settings.__dict__.items():
            if name in settings_dict:
                value = settings_dict[name]
                self.setAttribute(self.settings, name, value)
                if value:
                    if verbose: print('{} : {}. Added.'.format(name, value))
            else:
                if verbose: print('{}: not found in the settings. Skipped.'.format(name))

        # Dump read keys to temporary settings file locally
        path_temp_file_settings = Path(os.path.join('', settings_file)).resolve()
        dict_to_yaml(settings_dict, path_temp_file_settings)
        if verbose: print('File {} was saved locally.'.format(path_temp_file_settings))

    def store_model_objects(self, path_output_file: str):
        """
        ** Stores the dictionary of BuilderModel objects in a pickle file at the specified path **
        This can be helpful to load the list of models instead of generating it at every iteration of a co-simulation.
        :param path_output_file: string to the file to write
        :return: None
        """
        # Make sure the target folder exists
        make_folder_if_not_existing(os.path.dirname(path_output_file), verbose=self.verbose)

        # Store the objects as pickle file
        with open(path_output_file, 'wb') as output:
            pickle.dump(self.list_models, output, pickle.HIGHEST_PROTOCOL)

        if self.verbose: print(f'File {path_output_file} saved.')

    def write_analysis_file(self, path_output_file: str):
        """
        ** Write the analysis data in the target file **
        This can be helpful to keep track of the final state of the DataAnalysis object before running it, especially if it was modified programmatically.
        :param path_output_file: string to the file to write
        :return: None
        """

        # Make sure the target folder exists
        make_folder_if_not_existing(os.path.dirname(path_output_file), verbose=self.verbose)

        # Write the STEAM analysis data to a yaml file
        dict_to_yaml({**self.data_analysis.dict()}, path_output_file,
                     list_exceptions=['AnalysisStepSequence', 'variables_to_change'])
        if self.verbose: print(f'File {path_output_file} saved.')

    def run_analysis(self, verbose: bool = None):
        """
            ** Run the analysis **
        """

        # Unpack and assign default values
        step_definitions = self.data_analysis.AnalysisStepDefinition
        if not verbose:
            verbose = self.verbose

        # Print the selected analysis steps
        if verbose:
            print('Defined analysis steps (not in sequential order):')
            for def_step in step_definitions:
                print(f'{def_step}')

        # Print analysis sequence
        if verbose: print('Defined sequence of analysis steps:')
        for s, seq_step in enumerate(self.data_analysis.AnalysisStepSequence):
            if verbose: print('Step {}/{}: {}'.format(s + 1, len(self.data_analysis.AnalysisStepSequence), seq_step))

        # Run analysis (and re-print analysis steps)
        if verbose: print('Analysis started.')
        for s, seq_step in enumerate(self.data_analysis.AnalysisStepSequence):
            if verbose: print('Step {}/{}: {}'.format(s + 1, len(self.data_analysis.AnalysisStepSequence), seq_step))
            step = step_definitions[seq_step]  # this is the object containing the information about the current step
            if step.type == 'MakeModel':
                self.step_make_model(step, verbose=verbose)
            elif step.type == 'ModifyModel': #
                self.step_modify_model(step, verbose=verbose)
            elif step.type == 'ModifyModelMultipleVariables':  #
                self.step_modify_model_multiple_variables(step, verbose=verbose)
            elif step.type == 'RunSimulation':
                self.step_run_simulation(step, verbose=verbose)
            elif step.type == 'PostProcess':
                self.step_postprocess(step, verbose=verbose)
            elif step.type == 'SetUpFolder':
                self.step_setup_folder(step, verbose=verbose)
            elif step.type == 'AddAuxiliaryFile':
                self.add_auxiliary_file(step, verbose=verbose)
            elif step.type == 'CopyFile':
                self.copy_file_to_target(step, verbose=verbose)
            elif step.type == 'RunCustomPyFunction':
                self.run_custom_py_function(step, verbose=verbose)
            elif step.type == 'RunViewer':
                self.run_viewer(step, verbose=verbose) # Add elif plot_map2d,  two paths save plot to folder png
            elif step.type == 'CalculateMetrics':
                self.calculate_metrics(step, verbose=verbose)
            elif step.type == 'LoadCircuitParameters':
                self.load_circuit_parameters(step, verbose=verbose)
            elif step.type == 'WriteStimulusFile':
                self.write_stimuli_from_interpolation(step, verbose=verbose)
            elif step.type == 'ParsimEvent':
                self.run_parsim_event(step, verbose=verbose)
            elif step.type == 'ParametricSweep':
                self.run_parsim_sweep(step, verbose=verbose)
            elif step.type == 'ParsimConductor':
                self.run_parsim_conductor(step, verbose=verbose)
            else:
                raise Exception('Unknown type of analysis step: {}'.format(step.type))

    def step_make_model(self, step, verbose: bool = False):
        if verbose:
            print('Making model object named {}'.format(str(step.model_name)))
        ## Assuming the steam-models directory structure if 'steam-models' or model_library found at the end of library path.
        # Else assuming library path directs straight to the model
        if (str(self.library_path).endswith('steam_models')) or (str(self.library_path).endswith('steam-models')) or (
                str(self.library_path).endswith('model_library')):
            file_model_data = os.path.join(self.library_path, step.case_model + 's', step.file_model_data, 'input',
                                           'modelData_' + step.file_model_data + '.yaml')
        elif isinstance(self.library_path, str):
            if self.library_path == 'same_as_analysis_yaml_use_model_name':
                file_model_data = '.' + os.sep + step.file_model_data + os.sep + 'input' + os.sep + 'modelData_' + step.file_model_data + '.yaml'
                file_model_data = Path(file_model_data).resolve()
            else:
                file_model_data = os.path.join(self.library_path, 'modelData_' + step.file_model_data + '.yaml')

        case_model = step.case_model
        software = step.software  # remember this is a list, not a string
        verbose_of_step = step.verbose
        flag_build = step.flag_build
        flag_dump_all = step.flag_dump_all
        flag_plot_all = step.flag_plot_all
        flag_json = step.flag_json
        output_folder = self.output_path
        relative_path_settings = ''

        # Build the model
        BM = BuilderModel(file_model_data=file_model_data, case_model=case_model, software=software,
                          verbose=verbose_of_step, flag_build=flag_build, flag_dump_all=flag_dump_all,
                          flag_plot_all=flag_plot_all, flag_json=flag_json, output_path=output_folder,
                          relative_path_settings=relative_path_settings)

        # Build simulation file
        if step.simulation_number is not None:
            if 'FiQuS' in step.software:
                self.setup_sim_FiQuS(simulation_name=step.simulation_name, sim_number=step.simulation_number,
                                     magnet_type=BM.model_data.GeneralParameters.magnet_type)
                # note above magnet_type is specified only for the step_make_model to make setup_sim_FiQuS copy additional files needed for the multipole magnet
            if 'LEDET' in step.software:
                flag_yaml = True  # Hard-coded for the moment
                self.setup_sim_LEDET(simulation_name=step.simulation_name, sim_number=step.simulation_number,
                                     flag_yaml=flag_yaml, flag_json=flag_json)
            if 'PyBBQ' in step.software:
                self.setup_sim_PyBBQ(simulation_name=step.simulation_name, sim_number=step.simulation_number)
            if 'PSPICE' in step.software:
                self.setup_sim_PSPICE(simulation_name=step.simulation_name, sim_number=step.simulation_number)
            if 'XYCE' in step.software:
                self.setup_sim_XYCE(simulation_name=step.simulation_name, sim_number=step.simulation_number)

        # Add the reference to the model in the dictionary
        self.list_models[step.model_name] = BM

    def step_modify_model(self, step, verbose: bool = False):
        if verbose:
            print('Modifying model object named {}'.format(str(step.model_name)))

        # Check inputs
        if step.model_name not in self.list_models:
            raise Exception('Name of the model to modify ({}) does not correspond to any of the defined models.'.format(
                step.model_name))
        len_variable_value = len(step.variable_value)
        len_simulation_numbers = len(step.simulation_numbers)
        len_new_model_name = len(step.new_model_name)
        if len_new_model_name > 0 and not len_new_model_name == len_variable_value:
            raise Exception(
                'The length of new_model_name and variable_value must be the same, but they are {} and {} instead.'.format(
                    len_new_model_name, len_variable_value))
        if len_simulation_numbers > 0 and not len_simulation_numbers == len_variable_value:
            raise Exception(
                'The length of simulation_numbers and variable_value must be the same, but they are {} and {} instead.'.format(
                    len_simulation_numbers, len_variable_value))

        # Change the value of the selected variable
        for v, value in enumerate(step.variable_value):
            BM = self.list_models[step.model_name]  # original BuilderModel object
            case_model = BM.case_model  # model case (magnet, conductor, circuit)

            if 'Conductors[' in step.variable_to_change:  # Special case when the variable to change is the Conductors key
                if verbose:
                    idx_conductor = int(step.variable_to_change.split('Conductors[')[1].split(']')[0])
                    conductor_variable_to_change = step.variable_to_change.split('].')[1]
                    print(
                        'Variable {} is treated as a Conductors key. Conductor index: #{}. Conductor variable to change: {}.'.format(
                            step.variable_to_change, idx_conductor, conductor_variable_to_change))

                    old_value = self.get_attribute_model(case_model, BM, conductor_variable_to_change, idx_conductor)
                    print('Variable {} changed from {} to {}.'.format(conductor_variable_to_change, old_value, value))

                if len_new_model_name > 0:  # Make a new copy of the BuilderModel object, and change it
                    self.list_models[step.new_model_name[v]] = deepcopy(BM)
                    BM = self.list_models[step.new_model_name[v]]

                    if case_model == 'conductor':
                        rsetattr(BM.conductor_data.Conductors[idx_conductor], conductor_variable_to_change, value)
                    else:
                        rsetattr(BM.model_data.Conductors[idx_conductor], conductor_variable_to_change, value)

                    if verbose:
                        print('Model {} copied to model {}.'.format(step.model_name, step.new_model_name[v]))
                else:  # Change the original BuilderModel object

                    if case_model == 'conductor':
                        rsetattr(BM.conductor_data.Conductors[idx_conductor], conductor_variable_to_change, value)
                    else:
                        rsetattr(BM.model_data.Conductors[idx_conductor], conductor_variable_to_change, value)

            else:  # Standard case when the variable to change is not the Conductors key
                if verbose:
                    old_value = self.get_attribute_model(case_model, BM, step.variable_to_change)
                    print('Variable {} changed from {} to {}.'.format(step.variable_to_change, old_value, value))

                if len_new_model_name > 0:  # Make a new copy of the BuilderModel object, and change it
                    self.list_models[step.new_model_name[v]] = deepcopy(BM)
                    BM = self.list_models[step.new_model_name[v]]
                    self.set_attribute_model(case_model, BM, step.variable_to_change, value)
                    if verbose:
                        print('Model {} copied to model {}.'.format(step.model_name, step.new_model_name[v]))

                else:  # Change the original BuilderModel object
                    self.set_attribute_model(case_model, BM, step.variable_to_change, value)

            # Special case: If the sub-keys of "Source" are changed, a resetting of the input paths is triggered
            if step.variable_to_change.startswith('Sources.'):
                BM.set_input_paths()

            # Build simulation file
            if len_simulation_numbers > 0:
                simulation_number = step.simulation_numbers[v]
                if 'FiQuS' in step.software:
                    BM.buildFiQuS(simulation_name=f'{step.simulation_name}')
                    self.setup_sim_FiQuS(simulation_name=step.simulation_name, sim_number=simulation_number,
                                         magnet_type=BM.model_data.GeneralParameters.magnet_type if not step.variable_to_change.startswith(
                                             'Options_FiQuS.') else None)
                if 'LEDET' in step.software:
                    flag_json = BM.flag_json
                    flag_yaml = True  # Hard-coded for the moment
                    BM.buildLEDET()
                    self.setup_sim_LEDET(simulation_name=step.simulation_name, sim_number=simulation_number,
                                         flag_yaml=flag_yaml, flag_json=flag_json)
                if 'SIGMA' in step.software:
                    make_folder_if_not_existing(os.path.join(self.settings.local_SIGMA_folder, f"{step.simulation_name}_{simulation_number}") )#ADDED
                    BM.buildSIGMA(f"{step.simulation_name}_{simulation_number}", self.library_path)
                    self.setup_sim_SIGMA(simulation_name=step.simulation_name, sim_number=simulation_number)
                if 'PyBBQ' in step.software:
                    BM.buildPyBBQ()
                    self.setup_sim_PyBBQ(simulation_name=step.simulation_name, sim_number=simulation_number)
                if 'PSPICE' in step.software:
                    BM.buildPSPICE()
                    self.setup_sim_PSPICE(simulation_name=step.simulation_name, sim_number=simulation_number)
                if 'XYCE' in step.software:
                    BM.buildXYCE()
                    self.setup_sim_XYCE(simulation_name=step.simulation_name, sim_number=simulation_number)


    def get_attribute_model(self, case_model: str, builder_model: BuilderModel, name_variable: str,
                            idx_conductor: int = None):
        """
        Helper function used to get an attribute from a key of the model data.
        Depending on the model type (circuit, magnet, conductor), the data structure to access is different.
        Also, there is a special case when the variable to read is a sub-key of the Conductors key. In such a case, an additional parameter idx_conductor must be defined (see below).
        :param case_model: Model type
        :param builder_model: BuilderModel object to access
        :param name_variable: Name of the variable to read
        :param idx_conductor: When defined, a sub-key form the Conductors key is read. The index of the conductor to read is defined by idx_conductor
        :return: Value of the variable to get
        """

        if case_model == 'magnet':
            if idx_conductor is None:  # Standard case when the variable to change is not the Conductors key
                value = rgetattr(builder_model.model_data, name_variable)
            else:
                value = rgetattr(builder_model.model_data.Conductors[idx_conductor], name_variable)
        elif case_model == 'conductor':
            if idx_conductor is None:  # Standard case when the variable to change is not the Conductors key
                value = rgetattr(builder_model.conductor_data, name_variable)
            else:
                value = rgetattr(builder_model.conductor_data.Conductors[idx_conductor], name_variable)
        elif case_model == 'circuit':
            value = rgetattr(builder_model.circuit_data, name_variable)
        else:
            raise Exception(f'Model type not supported: case_model={case_model}')
        return value

    def set_attribute_model(self, case_model: str, builder_model: BuilderModel, name_variable: str,
                            value_variable: Union[int, float, str], idx_conductor: int = None):
        """
        Helper function used to set a key of the model data to a certain value.
        Depending on the model type (circuit, magnet, conductor), the data structure to access is different.
        Also, there is a special case when the variable to change is a sub-key of the Conductors key. In such a case, an additional parameter idx_conductor must be defined (see below).
        :param case_model: Model type
        :param builder_model: BuilderModel object to access
        :param name_variable: Name of the variable to change
        :param value_variable: New value of the variable of the variable
        :param idx_conductor: When defined, a sub-key form the Conductors key is read. The index of the conductor to read is defined by idx_conductor
        :return: Value of the variable to get
        """

        if case_model == 'magnet':
            if idx_conductor is None:  # Standard case when the variable to change is not the Conductors key
                rsetattr(builder_model.model_data, name_variable, value_variable)
            else:
                rsetattr(builder_model.model_data.Conductors[idx_conductor], name_variable, value_variable)
        elif case_model == 'conductor':
            if idx_conductor is None:  # Standard case when the variable to change is not the Conductors key
                rsetattr(builder_model.conductor_data, name_variable, value_variable)
            else:
                rsetattr(builder_model.conductor_data.Conductors[idx_conductor], name_variable, value_variable)
        elif case_model == 'circuit':
            rsetattr(builder_model.circuit_data, name_variable, value_variable)
        else:
            raise Exception(f'Model type not supported: case_model={case_model}')

    def step_modify_model_multiple_variables(self, step, verbose: bool = False):
        if verbose:
            print('Modifying model object named {}'.format(str(step.model_name)))

        # Check inputs
        if step.model_name not in self.list_models:
            raise Exception(f'Name of the model to modify ({step.model_name}) does not correspond to any of the defined models.'.format(step.model_name))
        len_variables_to_change = len(step.variables_to_change)
        len_variables_value = len(step.variables_value)
        if not len_variables_to_change == len_variables_value:
            raise Exception('The length of variables_to_change and variables_value must be the same, but they are {} and {} instead.'.format(len_variables_to_change, len_variables_value))

        # Loop through the list of variables to change
        for v, variable_to_change in enumerate(step.variables_to_change):
            # For each variable to change, make an instance of an ModifyModel step and call the step_modify_model() method
            next_step = ModifyModel(type='ModifyModel')
            next_step.model_name = step.model_name
            next_step.variable_to_change = variable_to_change
            next_step.variable_value = step.variables_value[v]
            if v + 1 == len_variables_to_change:
                # If this is the last variable to change, import new_model_name and simulation_numbers from the step
                next_step.new_model_name = step.new_model_name
                next_step.simulation_numbers = step.simulation_numbers
            else:
                # else, set new_model_name and simulation_numbers to empty lists to avoid making models/simulations for intermediate changes
                next_step.new_model_name = []
                next_step.simulation_numbers = []
            next_step.simulation_name = step.simulation_name
            next_step.software = step.software
            self.step_modify_model(next_step, verbose=verbose)
        if verbose:
            print('All variables of step {} were changed.'.format(step))

    def step_run_simulation(self, step, verbose: bool = False):
        software = step.software
        simulation_name = step.simulation_name
        simFileType = step.simFileType
        sim_numbers = step.simulation_numbers
        if simulation_name == 'from_last_parametric_list':
            sim_numbers = list(self.input_parsim_sweep_df.simulation_number.to_numpy())
            sim_names = list(self.input_parsim_sweep_df.simulation_name.to_numpy())
        elif simulation_name == 'from_SetUpFolder_step':
            sim_numbers = list(self.input_parsim_sweep_df.simulation_number.to_numpy())
            for step_data in self.data_analysis.AnalysisStepDefinition.values():
                if step_data.type == 'SetUpFolder':
                    sim_name = step_data.simulation_name
            sim_names = len(sim_numbers) * [sim_name]
        else:
            sim_names = [simulation_name] * len(sim_numbers)
        for sim_name, sim_number in zip(sim_names, sim_numbers):
            if verbose:
                print('Running simulation of model {} #{} using {}.'.format(simulation_name, sim_number, software))
            # Run simulation
            self.run_sim(software, sim_name, sim_number, simFileType, verbose)

    def step_postprocess(self, step, verbose: bool = False):
        if verbose: print('postprocessing')
        if step.software and 'SIGMA' in step.software:
            for sim_num in step.simulation_numbers:
                # Check if files exist
                path_result_txt_Bx = os.path.join(self.settings.local_SIGMA_folder, f"{step.simulation_name}_{sim_num}","output", "mf.Bx.txt")
                path_result_txt_By = os.path.join(self.settings.local_SIGMA_folder, f"{step.simulation_name}_{sim_num}","output", "mf.By.txt")
                path_new_file = os.path.join(self.settings.local_SIGMA_folder, f"{step.simulation_name}_{sim_num}","output", "B_field_map2d.map2d")
                path_reference_roxie = os.path.join(self.settings.local_SIGMA_folder, f"{step.simulation_name}_{sim_num}", "sources", f"{step.simulation_name}_{sim_num}_ROXIE_REFERENCE.map2d")
                if not os.path.exists(path_result_txt_Bx):
                    raise Warning("No Bx file is found, please check that simulation ran successfully.")
                elif not os.path.exists(path_result_txt_By):
                    raise Warning("No By file is found, please check that simulation ran successfully.")
                elif not os.path.exists(path_reference_roxie):
                    print(path_reference_roxie)
                    raise Warning("No Roxie reference file is found, please check model_data.yaml in options_sigma that key map2d is specified.")
                else:
                    try:
                        export_B_field_txt_to_map2d_SIGMA(path_reference_roxie, path_result_txt_Bx, path_result_txt_By,
                                                    path_new_file)
                    except:
                        print("Can't generate map2d output. This can only be done for stationary studies and with the same coordinate in output files and roxie reference")
                    try:
                        generate_report_from_map2d(os.path.join(self.settings.local_SIGMA_folder, f"{step.simulation_name}_{sim_num}", "output"), path_reference_roxie, "Roxie Data", path_new_file, "SIGMA DATA", "coil", save=True)
                    except:
                        print("Can't generate report from map2d. This can only be done for stationary studies")
        else:
            print('Not implemented yet.')

    def step_setup_folder(self, step, verbose: bool = False):
        """
        Set up simulation working folder.
        The function applies a different logic for each simulation software.
        """
        list_software = step.software
        simulation_name = step.simulation_name

        for software in list_software:
            if verbose:
                print('Set up folder of model {} for {}.'.format(simulation_name, software))

            if 'FiQuS' in software:
                # make top level output folder
                make_folder_if_not_existing(self.settings.local_FiQuS_folder, verbose=verbose)

                # make simulation name folder inside top level folder
                make_folder_if_not_existing(os.path.join(self.settings.local_FiQuS_folder, step.simulation_name))

            elif 'LEDET' in software:
                local_LEDET_folder = Path(self.settings.local_LEDET_folder)
                # Make magnet input folder and its subfolders
                make_folder_if_not_existing(Path(local_LEDET_folder / simulation_name / 'Input').resolve(),
                                            verbose=verbose)
                make_folder_if_not_existing(
                    Path(local_LEDET_folder / simulation_name / 'Input' / 'Control current input').resolve(),
                    verbose=verbose)
                make_folder_if_not_existing(
                    Path(local_LEDET_folder / simulation_name / 'Input' / 'Initialize variables').resolve(),
                    verbose=verbose)
                make_folder_if_not_existing(
                    Path(local_LEDET_folder / simulation_name / 'Input' / 'InitializationFiles').resolve(),
                    verbose=verbose)

                # Copy csv files from the output folder
                list_csv_files = [entry for entry in os.listdir(self.output_path) if
                                  (simulation_name in entry) and ('.csv' in entry)]
                for csv_file in list_csv_files:
                    file_to_copy = os.path.join(self.output_path, csv_file)
                    file_copied = os.path.join(Path(local_LEDET_folder / simulation_name / 'Input').resolve(), csv_file)
                    shutil.copyfile(file_to_copy, file_copied)
                    if verbose: print(f'Csv file {file_to_copy} copied to {file_copied}.')

                # Make magnet field-map folder
                field_maps_folder = Path(local_LEDET_folder / '..' / 'Field maps' / simulation_name).resolve()
                make_folder_if_not_existing(field_maps_folder, verbose=verbose)

                # Copy field-map files from the output folder
                list_field_maps = [entry for entry in os.listdir(self.output_path) if
                                   (simulation_name in entry) and ('.map2d' in entry)]
                for field_map in list_field_maps:
                    file_to_copy = os.path.join(self.output_path, field_map)
                    file_copied = os.path.join(field_maps_folder, field_map)
                    shutil.copyfile(file_to_copy, file_copied)
                    if verbose: print(f'Field map file {file_to_copy} copied to {file_copied}.')

            elif 'PSPICE' in software:
                local_PSPICE_folder = Path(self.settings.local_PSPICE_folder)
                local_model_folder = Path(local_PSPICE_folder / simulation_name).resolve()
                # Make magnet input folder
                make_folder_if_not_existing(local_model_folder, verbose=verbose)

                # Copy lib files from the output folder
                list_lib_files = [entry for entry in os.listdir(self.output_path) if
                                  (simulation_name in entry) and ('.lib' in entry)]
                for lib_file in list_lib_files:
                    file_to_copy = os.path.join(self.output_path, lib_file)
                    file_copied = os.path.join(local_model_folder, lib_file)
                    shutil.copyfile(file_to_copy, file_copied)
                    if verbose: print('Lib file {} copied to {}.'.format(file_to_copy, file_copied))

                # Copy stl files from the output folder
                list_stl_files = [entry for entry in os.listdir(self.output_path) if
                                  (simulation_name in entry) and ('.stl' in entry)]
                for stl_file in list_stl_files:
                    file_to_copy = os.path.join(self.output_path, stl_file)
                    file_copied = os.path.join(local_model_folder, stl_file)
                    shutil.copyfile(file_to_copy, file_copied)
                    if verbose: print('Stl file {} copied to {}.'.format(file_to_copy, file_copied))

            elif 'SIGMA' in software:
                # make top level output folder
               # make_folder_if_not_existing(self.settings.local_SIGMA_folder, verbose=verbose)

                # make simulation name folder inside top level folder
                make_folder_if_not_existing(os.path.join(self.settings.local_SIGMA_folder, step.simulation_name))

            elif 'XYCE' in software:
                local_XYCE_folder = Path(self.settings.local_XYCE_folder)
                local_model_folder = str(Path(local_XYCE_folder / simulation_name).resolve())
                # Make circuit input folder
                make_folder_if_not_existing(local_model_folder, verbose=verbose)

                # Copy lib files from the output folder
                list_lib_files = [entry for entry in os.listdir(self.output_path) if
                                  (simulation_name in entry) and ('.lib' in entry)]
                for lib_file in list_lib_files:
                    file_to_copy = os.path.join(self.output_path, lib_file)
                    file_copied = os.path.join(local_model_folder, lib_file)
                    shutil.copyfile(file_to_copy, file_copied)
                    if verbose: print('Lib file {} copied to {}.'.format(file_to_copy, file_copied))

                # Copy stl files from the output folder
                stl_path = os.path.join(self.output_path, 'Stimulus')
                list_stl_files = [entry for entry in os.listdir(stl_path) if
                                  (simulation_name in entry) and ('.csv' in entry)]
                stl_path_new = os.path.join(local_model_folder, 'Stimulus')
                if os.path.exists(stl_path_new):
                    shutil.rmtree(stl_path_new)
                os.mkdir(stl_path_new)

                for stl_file in list_stl_files:
                    file_to_copy = os.path.join(self.output_path, stl_file)
                    file_copied = os.path.join(stl_path_new, stl_file)
                    shutil.copyfile(file_to_copy, file_copied)
                    if verbose: print('Stl file {} copied to {}.'.format(file_to_copy, file_copied))

            else:
                raise Exception(f'Software {software} not supported for automated folder setup.')

    def add_auxiliary_file(self, step, verbose: bool = False):
        """
        Copy the desired auxiliary file to the output folder
        """
        # Unpack
        full_path_aux_file = Path(step.full_path_aux_file).resolve()
        new_file_name = step.new_file_name
        output_path = self.output_path

        # If no new name is provided, use the old file name
        if new_file_name == None:
            new_file_name = ntpath.basename(full_path_aux_file)

        # Copy auxiliary file to the output folder
        full_path_output_file = os.path.join(output_path, new_file_name)
        make_folder_if_not_existing(os.path.dirname(full_path_output_file))  # in case the output folder does not exist, make it
        shutil.copyfile(full_path_aux_file, full_path_output_file)
        if verbose: print(f'File {full_path_aux_file} was copied to {full_path_output_file}.')

        # Build simulation file
        len_simulation_numbers = len(step.simulation_numbers)
        if len_simulation_numbers > 0:
            for simulation_number in step.simulation_numbers:
                if 'FiQuS' in step.software:
                    self.setup_sim_FiQuS(simulation_name=step.simulation_name, sim_number=simulation_number)
                if 'LEDET' in step.software:
                    flag_yaml = True  # Hard-coded for the moment
                    flag_json = False  # Hard-coded for the moment
                    self.setup_sim_LEDET(simulation_name=step.simulation_name, sim_number=simulation_number, flag_yaml=flag_yaml, flag_json=flag_json)
                if 'PyBBQ' in step.software:
                    self.setup_sim_PyBBQ(simulation_name=step.simulation_name, sim_number=simulation_number)
                if 'PSPICE' in step.software:
                    self.setup_sim_PSPICE(simulation_name=step.simulation_name, sim_number=simulation_number)
                if 'PSPICE' in step.software:
                    self.setup_sim_XYCE(simulation_name=step.simulation_name, sim_number=simulation_number)

    def copy_file_to_target(self, step, verbose: bool = False):
        """
            Copy one file from a location to another (the destination folder can be different from the analysis output folder)
        """
        # Unpack
        full_path_file_to_copy = Path(step.full_path_file_to_copy).resolve()
        full_path_file_target = Path(step.full_path_file_target).resolve()

        # Make sure the target folder exists
        make_folder_if_not_existing(os.path.dirname(full_path_file_target), verbose=verbose)

        # Copy file
        shutil.copyfile(full_path_file_to_copy, full_path_file_target)
        if verbose: print(f'File {full_path_file_to_copy} was copied to {full_path_file_target}.')

    def run_custom_py_function(self, step, verbose: bool = False):
        """
            Run a custom Python function with given arguments
        """
        # If the step is not enabled, the function will not be run
        if not step.flag_enable:
            if verbose: print(f'flag_enable set to False. Custom function {step.function_name} will not be run.')
            return

        # Unpack variables
        function_name = step.function_name
        function_arguments = step.function_arguments
        if step.path_module:
            # Import the custom function from a specified location different from the default location
            # This Python magic comes from: https://stackoverflow.com/questions/67631/how-do-i-import-a-module-given-the-full-path
            path_module = os.path.join(Path(step.path_module).resolve())
            custom_module = importlib.util.spec_from_file_location('custom_module',
                                                                   os.path.join(path_module, function_name + '.py'))
            custom_function_to_load = importlib.util.module_from_spec(custom_module)
            sys.modules['custom_module'] = custom_function_to_load
            custom_module.loader.exec_module(custom_function_to_load)
            custom_function = getattr(custom_function_to_load, function_name)
        else:
            # Import the custom function from the default location
            path_module = f'steam_sdk.analyses.custom_analyses.{function_name}.{function_name}'
            custom_module = importlib.import_module(path_module)
            custom_function = getattr(custom_module, function_name)

        # Run custom function with the given argument
        if verbose: print(
            f'Custom function {function_name} from module {path_module} will be run with arguments: {function_arguments}.')
        output = custom_function(function_arguments)
        return output

    def run_viewer(self, step, verbose: bool = False):
        """
            Make a steam_sdk.viewers.Viewer.Viewer() object and run its analysis
        """

        # Unpack variables
        # Unpack variables
        viewer_name = step.viewer_name

        if verbose: print(f'Making Viewer object named {viewer_name}.')

        # Make a steam_sdk.viewers.Viewer.Viewer() object and run its analysis
        V = Viewer(file_name_transients=step.file_name_transients,
                   list_events=step.list_events,
                   flag_analyze=step.flag_analyze,
                   flag_display=step.flag_display,
                   flag_save_figures=step.flag_save_figures,
                   path_output_html_report=step.path_output_html_report,
                   path_output_pdf_report=step.path_output_pdf_report,
                   figure_types=step.figure_types,
                   verbose=step.verbose)

        # Add the reference to the Viewer object in the dictionary
        self.list_viewers[viewer_name] = V

    def calculate_metrics(self, step, verbose: bool = False):
        """
        Calculate metrics (usually to compare two or more measured and/or simulated signals)
        :param step: STEAM analysis step of type CalculateMetrics, which has attributes:
        - viewer_name: the name of the Viewer object containing the data to analyze
        - metrics_to_calculate: list that defines the type of calculation to perform for each metric.
        - variables_to_analyze: list
        :param verbose:
        :return:
        """
        """
            
            The metrics to calculate are indicated in the list metrics_to_calculate, which defines the type of calculation of each metric.

        """
        if verbose: print(f'Calculate metrics.')

        # Unpack variables
        viewer_name = step.viewer_name
        metrics_name = step.metrics_name
        metrics_to_calculate = step.metrics_to_calculate
        variables_to_analyze = step.variables_to_analyze
        # Note: Avoid unpacking "list_viewers = self.list_viewers" since the variable usually has large size

        # Check input
        if not viewer_name in self.list_viewers:
            raise Exception(
                f'The selected Viewer object named {viewer_name} is not present in the current Viewer list: {self.list_viewers}. Add an analysis step of type RunViewer to define a Viewer object.')
        # if len(metrics_to_calculate) != len(variables_to_analyze):
        #     raise Exception(f'The lengths of the lists metrics_to_calculate and variables_to_analyze must match, but are {len(metrics_to_calculate)} and {len(variables_to_analyze)} instead.')

        # If the Analysis object contains a metrics set with the selected metrics_name, retrieve it: the new metrics entries will be appended to it
        if metrics_name in self.list_metrics:
            current_list_output_metrics = self.list_metrics[metrics_name]
        else:
            # If not, make a new metrics set
            current_list_output_metrics = {}

        # Loop through all events listed in the selected Viewer object
        for event_id in self.list_viewers[viewer_name].list_events:
            event_label = self.list_viewers[viewer_name].dict_events['Event label'][event_id - 1]
            if verbose: print(f'Event #{event_id}: "{event_label}".')
            current_list_output_metrics[event_label] = {}

            # For each selected pair of variables to analyze, calculate metrics
            for pair_var in variables_to_analyze:
                var_to_analyze = pair_var[0]
                var_reference = pair_var[1]

                # Check that the selected signal to analyze and its reference signal (if they are defined) exist in the current event
                if len(var_to_analyze) > 0:
                    if var_to_analyze in self.list_viewers[viewer_name].dict_data[event_label]:
                        if 'x_sim' in self.list_viewers[viewer_name].dict_data[event_label][
                            var_to_analyze]:  # usually the variable to analyze is a simulated signal
                            x_var_to_analyze = self.list_viewers[viewer_name].dict_data[event_label][var_to_analyze][
                                'x_sim']
                            y_var_to_analyze = self.list_viewers[viewer_name].dict_data[event_label][var_to_analyze][
                                'y_sim']
                        elif 'x_meas' in self.list_viewers[viewer_name].dict_data[event_label][
                            var_to_analyze]:  # but a measured signal is also supported
                            x_var_to_analyze = self.list_viewers[viewer_name].dict_data[event_label][var_to_analyze][
                                'x_meas']
                            y_var_to_analyze = self.list_viewers[viewer_name].dict_data[event_label][var_to_analyze][
                                'y_meas']
                        else:
                            print(
                                f'WARNING: Viewer {viewer_name}: Event "{event_label}": Signal label "{var_to_analyze}" not found. Signal skipped.')
                            continue
                    else:
                        print(
                            f'WARNING: Viewer "{viewer_name}": Event "{event_label}": Signal label "{var_to_analyze}" not found. Signal skipped.')
                        continue
                else:
                    raise Exception(
                        f'Viewer "{viewer_name}": Event "{event_label}": The first value of each pair in variables_to_analyze cannot be left empty, but {pair_var} was found.')

                if len(var_reference) > 0:  # if the string is empty, skip this check (it is possible to run the metrics calculation on one variable only)
                    if var_reference in self.list_viewers[viewer_name].dict_data[event_label]:
                        if 'x_meas' in self.list_viewers[viewer_name].dict_data[event_label][
                            var_reference]:  # usually the variable to analyze is a measured signal
                            x_var_reference = self.list_viewers[viewer_name].dict_data[event_label][var_reference][
                                'x_meas']
                            y_var_reference = self.list_viewers[viewer_name].dict_data[event_label][var_reference][
                                'y_meas']
                        elif 'x_sim' in self.list_viewers[viewer_name].dict_data[event_label][
                            var_reference]:  # but a simulated signal is also supported
                            x_var_reference = self.list_viewers[viewer_name].dict_data[event_label][var_reference][
                                'x_sim']
                            y_var_reference = self.list_viewers[viewer_name].dict_data[event_label][var_reference][
                                'y_sim']
                        else:
                            print(
                                f'WARNING: Viewer "{viewer_name}": Event "{event_label}": Signal label "{var_reference}" not found. Signal skipped.')
                            continue
                    else:
                        print(
                            f'WARNING: Viewer "{viewer_name}": Event "{event_label}": Signal label "{var_reference}" not found. Signal skipped.')
                        continue
                else:  # It is possible to run the metrics calculation on one variable only, without a reference signal
                    x_var_reference = None
                    y_var_reference = None

                # Perform the metrics calculation
                if verbose: print(
                    f'Viewer "{viewer_name}": Event "{event_label}": Metrics calculated using signals "{var_to_analyze}" and "{var_reference}".')

                # Calculate the metrics
                # output_metric = PostprocsMetrics(
                #     metrics_to_calculate=metrics_to_calculate,
                #     x_value=x_var_to_analyze,
                #     y_value=y_var_to_analyze,
                #     x_ref=x_var_reference,
                #     y_ref=y_var_reference,
                #     flag_run=True)
                output_metric = PostprocsMetrics(metrics_to_do=metrics_to_calculate,
                                                 var_to_interpolate=y_var_to_analyze,
                                                 var_to_interpolate_ref=y_var_reference, time_vector=x_var_to_analyze,
                                                 time_vector_ref=x_var_reference)
                current_list_output_metrics[event_label][var_to_analyze] = output_metric.metrics_result

        # Add the reference to the Viewer object in the dictionary
        self.list_metrics[metrics_name] = current_list_output_metrics

        return current_list_output_metrics

    def load_circuit_parameters(self, step, verbose: bool = False):
        """
        Load global circuit parameters from a .csv file into an existing BuilderModel circuit model
        :param step: STEAM analysis step of type LoadCircuitParameters, which has attributes:
        - model_name: BuilderModel object to edit - THIS MUST BE OF TYPE CIRCUIT
        - path_file_circuit_parameters: the name of the .csv file containing the circuit parameters
        - selected_circuit_name: name of the circuit name whose parameters will be loaded
        :param verbose: display additional logging info
        :return:
        """
        if verbose: print(f'Load circuit parameters.')

        # Unpack variables
        model_name = step.model_name
        path_file_circuit_parameters = step.path_file_circuit_parameters
        selected_circuit_name = step.selected_circuit_name

        BM = self.list_models[model_name]

        # Call function to load the parameters into the object
        BM.load_circuit_parameters_from_csv(input_file_name=path_file_circuit_parameters, selected_circuit_name=selected_circuit_name)

        # Update the BuilderModel object
        self.list_models[model_name] = BM

        return

    def setup_sim_FiQuS(self, simulation_name, sim_number, magnet_type=None):
        """
        Set up a FiQuS simulation by copying the last file generated by BuilderModel to the output folder and to the
        local FiQuS working folder.
        The original file is then deleted.
        """

        # Add simulation number to the list
        self.list_sims.append(sim_number)

        # Make simulation folder
        local_model_folder = os.path.join(self.settings.local_FiQuS_folder, f'{simulation_name}_{str(sim_number)}')
        make_folder_if_not_existing(local_model_folder)

        # Copy simulation file
        file_name_temp = os.path.join(self.output_path, f'{simulation_name}')
        yaml_temp = os.path.join(file_name_temp + '_FiQuS.yaml')
        file_name_local = os.path.join(local_model_folder, f'{simulation_name}')
        yaml_local = os.path.join(file_name_local + '.yaml')
        shutil.copyfile(yaml_temp, yaml_local)

        if magnet_type == 'multipole':
            geo_temp = os.path.join(file_name_temp + '_FiQuS.geom')
            set_temp = os.path.join(file_name_temp + '_FiQuS.set')
            geo_local = os.path.join(file_name_local + '.geom')
            set_local = os.path.join(file_name_local + '.set')
            shutil.copyfile(geo_temp, geo_local)
            shutil.copyfile(set_temp, set_local)

        if self.verbose: print('Simulation files {} generated.'.format(file_name_temp))
        if self.verbose: print('Simulation files {} copied.'.format(file_name_local))

    def setup_sim_LEDET(self, simulation_name, sim_number, flag_yaml=True, flag_json=False):
        """
        Set up a LEDET simulation by copying the last file generated by BuilderModel to the output folder and to the
        local LEDET working folder. The original file is then deleted.
        If flag_yaml=True, the model is set up to be run using a yaml input file.
        If flag_json=True, the model is set up to be run using a json input file.
        """

        # Unpack
        output_folder = self.output_path
        local_LEDET_folder = self.settings.local_LEDET_folder

        # Add simulation number to the list
        self.list_sims.append(sim_number)

        # Copy simulation file
        list_suffix = ['.xlsx']
        if flag_yaml == True:
            list_suffix.append('.yaml')
        if flag_json == True:
            list_suffix.append('.json')

        for suffix in list_suffix:
            file_name_temp = os.path.join(output_folder, simulation_name + suffix)
            file_name_output = os.path.join(output_folder, simulation_name + '_' + str(sim_number) + suffix)
            file_name_local = os.path.join(local_LEDET_folder, simulation_name, 'Input',
                                           simulation_name + '_' + str(sim_number) + suffix)

            shutil.copyfile(file_name_temp, file_name_output)
            if self.verbose: print('Simulation file {} generated.'.format(file_name_output))

            shutil.copyfile(file_name_temp, file_name_local)
            if self.verbose: print('Simulation file {} copied.'.format(file_name_local))

            # os.remove(file_name_temp)
            # print('Temporary file {} deleted.'.format(file_name_temp))

    def setup_sim_SIGMA(self, simulation_name, sim_number, magnet_type=None):
        """
        Set up a SIGMA simulation by copying the last file generated by BuilderModel to the output folder and to the
        local SIGMA working folder.
        The original file is then deleted.
        """

        # Add simulation number to the list
        self.list_sims.append(sim_number)

        # Make simulation folder
        local_model_folder = os.path.join(self.settings.local_SIGMA_folder, f'{simulation_name}_{str(sim_number)}')
        make_folder_if_not_existing(local_model_folder)
        sources_folder = os.path.join(local_model_folder, 'sources')
        make_folder_if_not_existing(sources_folder)
        input_folder = os.path.join(local_model_folder, 'input')
        make_folder_if_not_existing(input_folder)
        output_folder = os.path.join(local_model_folder, 'output')
        make_folder_if_not_existing(output_folder)
        # Copy all simulation file
        files = os.listdir(self.output_path)
        # Copy all files ending with csv, map2d or bhdata to sources

        string_simulation = f"{simulation_name}_{sim_number}"

        suffixes_sources = ['.map2d', '.csv']  # List of suffixes to filter files
        suffixes_input = ['.geom', '.set', '.yaml']  # List of suffixes to filter files


        # Iterate over files in the source directory
        for fname in files:
            if any(fname.endswith(suffix) for suffix in
                   suffixes_sources) and string_simulation in fname:  # Check if the file has any of the desired suffixes
                source_path = os.path.join(self.output_path, fname)
                destination_path = os.path.join(sources_folder, fname)
                shutil.copy2(source_path, destination_path)  # Copy

            if any(fname.endswith(suffix) for suffix in
                   suffixes_input) and string_simulation in fname:  # Check if the file has any of the desired suffixes
                source_path = os.path.join(self.output_path, fname)
                destination_path = os.path.join(input_folder, fname)
                shutil.copy2(source_path, destination_path)  # Copy
            if fname.endswith('roxie.bhdata'):
                source_path = os.path.join(self.output_path, fname)
                destination_path = os.path.join(sources_folder, fname)
                shutil.copy2(source_path, destination_path)  # Copy

        # if self.verbose: print('Simulation files {} generated.'.format(file_name_temp))
        # if self.verbose: print('Simulation files {} copied.'.format(file_name_local))

    def setup_sim_PSPICE(self, simulation_name, sim_number):
        """
        Set up a PSPICE simulation by copying the last file generated by BuilderModel to the output folder and to the
        local PSPICE working folder.
        The simulation netlist and auxiliary files are copied in a new numbered subfoldered.
        The original file is then deleted.
        """

        # Unpack
        output_folder = self.output_path
        local_PSPICE_folder = Path(self.settings.local_PSPICE_folder)

        # Add simulation number to the list
        self.list_sims.append(sim_number)

        # Make simulation folder
        local_model_folder = os.path.join(local_PSPICE_folder, simulation_name, str(sim_number))
        make_folder_if_not_existing(local_model_folder)

        # Copy simulation file
        file_name_temp = os.path.join(output_folder, simulation_name + '.cir')
        file_name_local = os.path.join(local_model_folder, simulation_name + '.cir')
        if self.verbose: print('Simulation file {} generated.'.format(file_name_temp))

        shutil.copyfile(file_name_temp, file_name_local)
        if self.verbose: print('Simulation file {} copied.'.format(file_name_local))

        # os.remove(file_name_temp)
        # print('Temporary file {} deleted.'.format(file_name_temp))

        # Copy lib files from the output folder
        list_lib_files = [entry for entry in os.listdir(output_folder) if
                          (simulation_name in entry) and ('.lib' in entry)]
        for lib_file in list_lib_files:
            file_to_copy = os.path.join(output_folder, lib_file)
            file_copied = os.path.join(local_model_folder, lib_file)
            shutil.copyfile(file_to_copy, file_copied)
            if self.verbose: print('Lib file {} copied to {}.'.format(file_to_copy, file_copied))

        # Copy stl files from the output folder
        list_stl_files = [entry for entry in os.listdir(output_folder) if
                          (simulation_name in entry) and ('.stl' in entry)]
        for stl_file in list_stl_files:
            file_to_copy = os.path.join(output_folder, stl_file)
            file_copied = os.path.join(local_model_folder, stl_file)
            shutil.copyfile(file_to_copy, file_copied)
            if self.verbose: print('Stl file {} copied to {}.'.format(file_to_copy, file_copied))

        # # Copy Conf.cir file from the output folder
        # list_cir_files = [entry for entry in os.listdir(output_folder) if ("Conf" in entry) and ('.cir' in entry)]
        # for cir_file in list_cir_files:
        #     file_to_copy = os.path.join(output_folder, cir_file)
        #     file_copied = os.path.join(local_model_folder, cir_file)
        #     shutil.copyfile(file_to_copy, file_copied)
        #     if self.verbose: print('Cir file {} copied to {}.'.format(file_to_copy, file_copied))

        # Special case: Copy coil_resistances.stl file from the output folder
        file_coil_resistances_to_copy = os.path.join(output_folder, 'coil_resistances.stl')
        file_coil_resistances_copied = os.path.join(local_model_folder, 'coil_resistances.stl')
        if os.path.isfile(file_coil_resistances_to_copy):
            shutil.copyfile(file_coil_resistances_to_copy, file_coil_resistances_copied)
            if self.verbose: print(
                'Stl file {} copied to {}.'.format(file_coil_resistances_to_copy, file_coil_resistances_copied))

    def setup_sim_XYCE(self, simulation_name, sim_number):
        """
        Set up a PSPICE simulation by copying the last file generated by BuilderModel to the output folder and to the
        local PSPICE working folder.
        The simulation netlist and auxiliary files are copied in a new numbered subfoldered.
        The original file is then deleted.
        """

        # Unpack
        output_folder = self.output_path
        local_XYCE_folder = Path(self.settings.local_XYCE_folder)

        # Add simulation number to the list
        self.list_sims.append(sim_number)

        # Make simulation folder
        local_model_folder = os.path.join(local_XYCE_folder, simulation_name, str(sim_number))
        make_folder_if_not_existing(local_model_folder)

        # Copy simulation file
        file_name_temp = os.path.join(output_folder, simulation_name + '.cir')
        file_name_local = os.path.join(local_model_folder, simulation_name + '.cir')
        if self.verbose: print('Simulation file {} generated.'.format(file_name_temp))

        self.copy_XYCE_cir(file_name_temp, file_name_local)
        if self.verbose: print('Simulation file {} copied.'.format(file_name_local))

        # os.remove(file_name_temp)
        # print('Temporary file {} deleted.'.format(file_name_temp))

        local_XYCE_folder = Path(self.settings.local_XYCE_folder)
        local_model_folder = str(Path(local_XYCE_folder / simulation_name / str(sim_number)).resolve())
        # Make circuit input folder
        make_folder_if_not_existing(local_model_folder, verbose=self.verbose)

        # Copy lib files from the output folder
        list_lib_files = [entry for entry in os.listdir(self.output_path) if
                          (simulation_name in entry) and ('.lib' in entry)]
        for lib_file in list_lib_files:
            file_to_copy = os.path.join(self.output_path, lib_file)
            file_copied = os.path.join(local_model_folder, lib_file)
            shutil.copyfile(file_to_copy, file_copied)
            if self.verbose: print('Lib file {} copied to {}.'.format(file_to_copy, file_copied))

        # Copy csv files from the output folder
        csv_path = os.path.join(self.output_path, 'Stimulus')
        if os.path.exists(csv_path):
            csv_path_new = os.path.join(local_model_folder, 'Stimulus')
            if os.path.exists(csv_path_new):
                shutil.rmtree(csv_path_new)
            os.mkdir(csv_path_new)

            list_csv_files = [entry for entry in os.listdir(csv_path) if (simulation_name in entry) and ('.csv' in entry)]
            for csv_file in list_csv_files:
                file_to_copy = os.path.join(csv_path,
                                            csv_file)  # self.output_path was first argument; changed it to stl_path
                file_copied = os.path.join(csv_path_new, csv_file)
                shutil.copyfile(file_to_copy, file_copied)
                if self.verbose: print('Csv file {} copied to {}.'.format(file_to_copy, file_copied))

        # Special case: Copy coil_resistances.csv file from the output folder
        file_coil_resistances_to_copy = os.path.join(output_folder, 'coil_resistances.csv')
        file_coil_resistances_copied = os.path.join(local_model_folder, 'coil_resistances.csv')
        if os.path.isfile(file_coil_resistances_to_copy):
            shutil.copyfile(file_coil_resistances_to_copy, file_coil_resistances_copied)
            if self.verbose: print(
                'Csv file {} copied to {}.'.format(file_coil_resistances_to_copy, file_coil_resistances_copied))

    def copy_XYCE_cir(self, file_name_temp, file_name_local):
        '''
            Function that copies the XYCE circuit file from 'file_name_temp' to 'file_name_local' and changes the
            respective output path for the csd
        :param file_name_temp: Original circuit file
        :param file_name_local: Final circuit file
        :return:
        '''

        with open(file_name_temp) as f:
            contents = f.readlines()
        for k in range(len(contents)):
            if contents[k].casefold().startswith('.print'):
                if 'csd' in contents[k]:
                    type_output = 'csd'
                elif 'csv' in contents[k]:
                    type_output = 'csv'
                elif 'txt' in contents[k]:
                    type_output = 'txt'
                else:
                    raise Exception("Don't understand output type.")
                print_line = contents[k].split('FILE=')
                print_line[-1] = f'FILE={file_name_local[:-4]}.{type_output} \n'
                contents[k] = ''.join(print_line)
                break

        contents = ''.join(contents)
        new_file = open(file_name_local, 'w')
        new_file.write(contents)
        new_file.close()

    def setup_sim_PyBBQ(self, simulation_name, sim_number):
        """
        Set up a PyBBQ simulation by copying the last file generated by BuilderModel to the output folder and to the
        local PyBBQ working folder.
        The original file is then deleted.
        """

        # Unpack
        output_folder = self.output_path
        local_PyBBQ_folder = Path(self.settings.local_PyBBQ_folder)

        # Add simulation number to the list
        self.list_sims.append(sim_number)

        # Make simulation folder
        local_model_folder = os.path.join(local_PyBBQ_folder, simulation_name, str(sim_number))
        make_folder_if_not_existing(local_model_folder)

        # Copy simulation file
        file_name_temp = os.path.join(output_folder, simulation_name + '.yaml')
        file_name_local = os.path.join(local_model_folder, simulation_name + '.yaml')
        if self.verbose: print('Simulation file {} generated.'.format(file_name_temp))

        shutil.copyfile(file_name_temp, file_name_local)
        if self.verbose: print('Simulation file {} copied.'.format(file_name_local))

        # os.remove(file_name_temp)
        # print('Temporary file {} deleted.'.format(file_name_temp))


    def run_sim(self, software: str, simulation_name: str, sim_number: int, simFileType: str = None,
                verbose: bool = False):
        """
        Run selected simulation.
        The function applies a different logic for each simulation software.
        """
        if software == 'FiQuS':
            local_analysis_folder = simulation_name + '_' + str(sim_number)
            dFiQuS = DriverFiQuS(FiQuS_path=self.settings.FiQuS_path,
                                 path_folder_FiQuS=self.settings.local_FiQuS_folder,
                                 path_folder_FiQuS_input=os.path.join(self.settings.local_FiQuS_folder,
                                                                      local_analysis_folder), verbose=verbose,
                                 GetDP_path=self.settings.GetDP_path)
            self.summary = dFiQuS.run_FiQuS(sim_file_name=simulation_name, output_directory=local_analysis_folder)
        elif software == 'LEDET':
            dLEDET = DriverLEDET(path_exe=self.settings.LEDET_path, path_folder_LEDET=self.settings.local_LEDET_folder,
                                 verbose=verbose)
            dLEDET.run_LEDET(simulation_name, str(sim_number), simFileType=simFileType)
        elif software == 'PyBBQ':
            local_model_folder_input = os.path.join(self.settings.local_PyBBQ_folder, simulation_name, str(sim_number))
            relative_folder_output = os.path.join(simulation_name, str(sim_number))
            dPyBBQ = DriverPyBBQ(path_exe=self.settings.PyBBQ_path, path_folder_PyBBQ=self.settings.local_PyBBQ_folder,
                                 path_folder_PyBBQ_input=local_model_folder_input, verbose=verbose)
            dPyBBQ.run_PyBBQ(simulation_name, outputDirectory=relative_folder_output)
        elif software == 'PSPICE':
            local_model_folder = Path(
                Path(self.settings.local_PSPICE_folder) / simulation_name / str(sim_number)).resolve()
            dPSPICE = DriverPSPICE(path_exe=self.settings.PSPICE_path, path_folder_PSPICE=local_model_folder,
                                   verbose=verbose)
            dPSPICE.run_PSPICE(simulation_name, suffix='')
        elif software == 'XYCE':
            local_model_folder = Path(
                Path(self.settings.local_XYCE_folder) / simulation_name / str(sim_number)).resolve()
            dXYCE = DriverXYCE(path_exe=self.settings.XYCE_path, path_folder_XYCE=local_model_folder, verbose=verbose)
            dXYCE.run_XYCE(simulation_name, suffix='')
        elif software == 'SIGMA':
            local_analysis_folder = simulation_name + '_' + str(sim_number)
            ds = DriverSIGMA(path_folder_SIGMA=self.settings.local_SIGMA_folder,
                             path_folder_SIGMA_input=os.path.join(self.settings.local_SIGMA_folder,
                                                                      local_analysis_folder), local_analysis_folder=local_analysis_folder, system_settings=self.settings, verbose=verbose)
            ds.run_SIGMA(simulation_name)
        else:
            raise Exception(f'Software {software} not supported for automated running.')


    def write_stimuli_from_interpolation(self, step, verbose: bool = False):
        '''
        Function to write a resistance stimuli for n apertures of a magnet for any current level. Resistance will be interpolated
        from pre-calculated values (see InterpolateResistance for closer explanation). Stimuli is then written in a .stl file for PSPICE

        :param current_level: list, all current level that shall be used for interpolation (each magnet has 1 current level)
        :param n_total_magnets: int, Number of total magnets in the circuit (A stimuli will be written for each, non-quenching = 0)
        :param n_apertures: int, Number of apertures per magnet. A stimuli will be written for each aperture for each magnet
        :param magnets: list, magnet numbers for which the stimuli shall be written
        :param tShift: list, time shift that needs to be applied to each stimuli
        (e.g. if magnet 1 quenches at 0.05s, magnet 2 at 1s etc.), so that the stimuli are applied at the correct time in the simulation
        :param Outputfile: str, name of the stimuli-file
        :param path_resources: str, path to the file with pre-calculated values
        :param InterpolationType: str, either Linear or Spline, type of interpolation
        :param type_stl: str, how to write the stimuli file (either 'a' (append) or 'w' (write))
        :param sparseTimeStepping: int, every x-th time value only a stimuli point is written (to reduce size of stimuli)
        :return:
        '''
        # Unpack inputs
        current_level = step.current_level
        n_total_magnets = step.n_total_magnets
        n_apertures = step.n_apertures
        magnets = step.magnets
        tShift = step.t_offset
        Outputfile = step.output_file
        path_resources = step.path_interpolation_file
        InterpolationType = step.interpolation_type
        type_stl = step.type_file_writing
        sparseTimeStepping = step.n_sampling
        magnet_type = step.magnet_types
        # Set default values for selected missing inputs
        if not InterpolationType:
            InterpolationType = 'Linear'
        if not type_stl:
            type_stl = 'w'
        if not sparseTimeStepping:
            sparseTimeStepping = 1  # Note: This will ovrewrite the default value of 100 used in the writeStimuliFromInterpolation_general() function

        # Call coil-resistance interpolation function
        writeStimuliFromInterpolation(current_level, n_total_magnets, n_apertures, magnets, tShift, Outputfile,
                                              path_resources, InterpolationType, type_stl, sparseTimeStepping,
                                              magnet_type)

        if verbose:
            print(f'Output stimulus file {Outputfile} written.')

    def run_parsim_event(self, step, verbose: bool = False):
        '''
        Function to generate steps based on list of events from external file

        :param step:
        :param verbose: if true displays more information
        :return:
        '''
        input_file = step.input_file
        simulation_numbers = step.simulation_numbers
        model_name = step.model_name
        case_model = step.case_model
        simulation_name = step.simulation_name
        software = step.software
        t_PC_off = step.t_PC_off
        rel_quench_heater_trip_threshold = step.rel_quench_heater_trip_threshold #
        current_polarities_CLIQ = step.current_polarities_CLIQ
        dict_QH_circuits_to_QH_strips = step.dict_QH_circuits_to_QH_strips
        path_output_viewer_csv = step.path_output_viewer_csv
        path_output_event_csv = step.path_output_event_csv
        default_keys = step.default_keys

        # Check inputs
        if not path_output_viewer_csv:
            path_output_viewer_csv = []
            if verbose: print(f'Key "path_output_viewer_csv" was not defined in the STEAM analysis file: no output viewer files will be generated.')
        if type(path_output_viewer_csv) == str:
            path_output_viewer_csv = [path_output_viewer_csv]  # Make sure this variable is always a list
        if path_output_viewer_csv and (len(path_output_viewer_csv) != len(software)):
            raise Exception(f'The length of path_output_viewer_csv ({len(path_output_viewer_csv)}) differs from the length of software({len(software)}). This is not allowed.')
        if path_output_viewer_csv and default_keys == {}:
            raise Exception(f'When key "path_output_viewer_csv" is defined in the STEAM analysis file, key "default_keys" must also be defined.')

        # Paths to output file
        if not path_output_event_csv:
            raise Exception('File path path_output_event_csv must be defined for an analysis step of type ParsimEvent.')

        # Read input file and run the ParsimEvent analysis
        if case_model == 'magnet':
            pem = ParsimEventMagnet(ref_model=self.list_models[model_name], verbose=verbose)
            pem.read_from_input(path_input_file=input_file, flag_append=False, rel_quench_heater_trip_threshold=rel_quench_heater_trip_threshold)
            pem.write_event_file(simulation_name=simulation_name, simulation_numbers=simulation_numbers,
                                 t_PC_off=t_PC_off, path_outputfile_event_csv=path_output_event_csv,
                                 current_polarities_CLIQ=current_polarities_CLIQ,
                                 dict_QH_circuits_to_QH_strips=dict_QH_circuits_to_QH_strips)

            # start parsim sweep step with newly created event file
            parsim_sweep_step = ParametricSweep(type='ParametricSweep', input_sweep_file=path_output_event_csv,
                                                model_name=model_name, case_model=case_model, software=software, verbose=verbose)
            self.run_parsim_sweep(parsim_sweep_step, verbose=verbose)

            # TODO: merge list and dict into self.data_analysis
            # TODO: add flag_show_parsim_output ?
            # TODO: add flag to write yaml analysis with all steps
            # TODO: parse Conductor Data - but what are the names in Quenchdict? (Parsim Sweep can handly conductor changes)

            # Write a .csv file that can be used to run a STEAM Viewer analysis
            for current_software, current_path_viewer_csv in zip(software, path_output_viewer_csv):
                pem.set_up_viewer(current_path_viewer_csv, default_keys, simulation_numbers, simulation_name, current_software)
                if verbose: print(f'File {current_path_viewer_csv} written. It can be used to run a STEAM Viewer analysis.')
        elif case_model == 'circuit':
            # Read input file and run the ParsimEvent analysis
            pec = ParsimEventCircuit(ref_model=self.list_models[model_name], verbose=verbose)
            pec.read_from_input(path_input_file=input_file, flag_append=False)
            pec.write_event_file(simulation_name=simulation_name, simulation_numbers=simulation_numbers,
                                 path_outputfile_event_csv=path_output_event_csv)

            quenching_magnet_list = []  # required for families where multiple magnets can quench like RB

            for event_number in range(len(pec.list_events)):  # reading through each row of the event file
                # get circuit specific information
                circuit_name = pec.list_events[event_number].GeneralParameters.name
                circuit_family_name = self.__get_circuit_family_name(circuit_name)
                magnet_name = self.__get_magnet_name(circuit_name)
                circuit_type = self.__get_circuit_type(circuit_name)
                number_of_magnets = self.__get_number_of_magnets(circuit_name)
                number_of_apertures = self.__get_number_of_apertures(circuit_name)
                current_level = pec.list_events[event_number].PoweredCircuits[circuit_name].current_at_discharge
                magnets_list = self.__get_magnets_list(number_of_magnets)
                t_PC_off = pec.list_events[event_number].PoweredCircuits[circuit_name].delta_t_FGC_PIC
                magnet_types = self.__get_magnet_types_list(number_of_magnets)

                # load circuit parameters step
                if circuit_family_name == "RQ":
                    circuit_name_1 = circuit_name.replace(".", "D_")
                    circuit_name_2 = circuit_name.replace(".", "F_")
                    load_circuit_parameters_step_1 = LoadCircuitParameters(type='LoadCircuitParameters', model_name=model_name, path_file_circuit_parameters=os.path.join(f"../../tests/builders/model_library/circuits/circuit_parameters/{circuit_family_name}_circuit_parameters.csv"), selected_circuit_name=circuit_name_1)
                    load_circuit_parameters_step_2 = LoadCircuitParameters(type='LoadCircuitParameters', model_name=model_name, path_file_circuit_parameters=os.path.join(f"../../tests/builders/model_library/circuits/circuit_parameters/{circuit_family_name}_circuit_parameters.csv"), selected_circuit_name=circuit_name_2)
                    position = pec.list_events[event_number].QuenchEvents[circuit_name].magnet_electrical_position
                    quenching_magnet = [self.__get_quenching_magnet_number(position, circuit_family_name)]
                    # modify model diode step used to change diodes across the quenching magnets with heating
                    modify_model_diode_step = ModifyModel(type='ModifyModel', model_name=model_name, variable_to_change=f'Netlist.x_D{quenching_magnet[0]}.value', variable_value=["RQ_Protection_Diode"], simulation_numbers=[], simulation_name=simulation_name, software=software)
                elif circuit_type == "RCBX":
                    circuit_name_1 = circuit_name.replace("X", "XH")
                    circuit_name_2 = circuit_name.replace("X", "XV")
                    load_circuit_parameters_step_1 = LoadCircuitParameters(type='LoadCircuitParameters', model_name=model_name, path_file_circuit_parameters=os.path.join(f"../../tests/builders/model_library/circuits/circuit_parameters/{circuit_family_name}_circuit_parameters.csv"), selected_circuit_name=circuit_name_1)
                    load_circuit_parameters_step_2 = LoadCircuitParameters(type='LoadCircuitParameters', model_name=model_name, path_file_circuit_parameters=os.path.join(f"../../tests/builders/model_library/circuits/circuit_parameters/{circuit_family_name}_circuit_parameters.csv"), selected_circuit_name=circuit_name_2)
                elif circuit_type in ["RCD", "RCO"]:
                    parts = circuit_name.split("-")
                    last_part = parts[-1]
                    string1 = parts[0] + "." + last_part.split(".")[1]
                    string2 = last_part
                    if circuit_type == "RCD":
                        load_circuit_parameters_step = LoadCircuitParameters(type='LoadCircuitParameters', model_name=model_name, path_file_circuit_parameters=os.path.join(f"../../tests/builders/model_library/circuits/circuit_parameters/{circuit_family_name}_circuit_parameters.csv"), selected_circuit_name=string1)
                    else:
                        load_circuit_parameters_step = LoadCircuitParameters(type='LoadCircuitParameters', model_name=model_name, path_file_circuit_parameters=os.path.join(f"../../tests/builders/model_library/circuits/circuit_parameters/{circuit_family_name}_circuit_parameters.csv"), selected_circuit_name=string2)
                else:
                    load_circuit_parameters_step = LoadCircuitParameters(type='LoadCircuitParameters', model_name=model_name, path_file_circuit_parameters=os.path.join(f"../../tests/builders/model_library/circuits/circuit_parameters/{circuit_family_name}_circuit_parameters.csv"), selected_circuit_name=circuit_name)

                # choosing stimulus output file location
                if circuit_family_name == "IPD":
                    stimulus_output_file = os.path.join(default_keys.path_output, f'{circuit_family_name}', f"{self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers[0]}", 'coil_resistances.stl')
                elif circuit_family_name == "RQ":
                    stimulus_output_file_1 = os.path.join(default_keys.path_output, f'{circuit_type}_47magnets', f'{event_number + 1}', 'coil_resistances.stl')
                    stimulus_output_file_2 = os.path.join(default_keys.path_output, f'{circuit_type}_47magnets',f'{event_number + 2}', 'coil_resistances.stl')
                elif circuit_type == "RCBX":
                    stimulus_output_file_1 = os.path.join(default_keys.path_output, 'RCBX', f'{event_number + 1}', 'coil_resistances.stl')
                    stimulus_output_file_2 = os.path.join(default_keys.path_output, 'RCBX', f'{event_number + 2}', 'coil_resistances.stl')
                elif simulation_name.startswith("IPQ"):
                    stimulus_output_file = os.path.join(default_keys.path_output, f'{simulation_name}', f'{event_number + 1}', 'coil_resistances.stl')
                elif circuit_name.startswith("RCBY"):
                    stimulus_output_file = os.path.join(default_keys.path_output, 'RCBY', f'{event_number + 1}', 'coil_resistances.stl')
                elif circuit_name.startswith(("RCBH", "RCBV")):
                    stimulus_output_file = os.path.join(default_keys.path_output, 'RCB', f"{self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers[0]}", 'coil_resistances.stl')
                else:
                    stimulus_output_file = os.path.join(default_keys.path_output, f'{circuit_type}', f"{self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_numbers[0]}", 'coil_resistances.stl')

                # making appropriate directory if it doesn't exist for the stimulus output file
                if circuit_family_name == "RQ" or circuit_type == "RCBX":
                    for file_path in [stimulus_output_file_1, stimulus_output_file_2]:
                        directory = os.path.dirname(file_path)
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                else:
                    directory = os.path.dirname(stimulus_output_file)
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                # write stimulus file step
                if circuit_family_name == "RQ":
                    write_stimuli_file_step_1 = WriteStimulusFile(type='WriteStimulusFile', output_file=stimulus_output_file_1, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=[current_level[0]], magnets=quenching_magnet, t_offset=[t_PC_off[0]], interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                    write_stimuli_file_step_2 = WriteStimulusFile(type='WriteStimulusFile', output_file=stimulus_output_file_2, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=[current_level[0]], magnets=quenching_magnet, t_offset=[t_PC_off[1]], interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                elif circuit_type == "RCBX":
                    write_stimuli_file_step_1 = WriteStimulusFile(type='WriteStimulusFile', output_file=stimulus_output_file_1, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[0]}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=[current_level[0]], magnets=magnets_list, t_offset=[t_PC_off[0]], interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                    write_stimuli_file_step_2 = WriteStimulusFile(type='WriteStimulusFile', output_file=stimulus_output_file_2, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[1]}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=[current_level[0]], magnets=magnets_list, t_offset=[t_PC_off[1]], interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                elif circuit_family_name == "RQX":
                    current_level = [current_level[0]+current_level[1], current_level[0]+current_level[2], current_level[0]+current_level[2], current_level[0]]
                    write_stimuli_file_step = WriteStimulusFile(type='WriteStimulusFile', output_file=stimulus_output_file, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[0]}.csv'), os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[1]}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=current_level, magnets=magnets_list, t_offset=[t_PC_off]*number_of_magnets, interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                elif circuit_family_name == "IPQ" and number_of_magnets == 2:
                    write_stimuli_file_step = WriteStimulusFile(type='WriteStimulusFile', output_file=stimulus_output_file, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[0]}.csv'), os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[1]}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=current_level, magnets=magnets_list, t_offset=[t_PC_off]*number_of_magnets, interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                elif circuit_family_name == "IPQ" and number_of_magnets == 1:
                    write_stimuli_file_step = WriteStimulusFile(type='WriteStimulusFile', output_file= stimulus_output_file, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=[current_level[0]], magnets=magnets_list, t_offset=[t_PC_off], interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                elif circuit_type in ["RCS", "ROD", "ROF", "RQ6", "RSD", "RSF", "RQTL9", "RQTD", "RQTF"]:
                    write_stimuli_file_step = WriteStimulusFile(type='WriteStimulusFile', output_file=stimulus_output_file, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[0]}.csv'), os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[1]}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=[current_level]*number_of_magnets, magnets=magnets_list, t_offset=[t_PC_off[0]]*number_of_magnets, interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                elif circuit_type == "RB":
                    position = pec.list_events[event_number].QuenchEvents[circuit_name].magnet_electrical_position
                    quenching_magnet = [self.__get_quenching_magnet_number(position, circuit_family_name)]
                    quenching_magnet_list.append(quenching_magnet[0])
                    quenching_magnet_list.sort()
                    # modify model diode step used to change diodes across the quenching magnets with heating
                    modify_model_diode_step = ModifyModel(type='ModifyModel', model_name=model_name, variable_to_change=f'Netlist.x_D{quenching_magnet[0]}.value', variable_value=["RB_Protection_Diode"], simulation_numbers=[], simulation_name=simulation_name, software=software)
                    write_stimuli_file_step = WriteStimulusFile(type='WriteStimulusFile', output_file=stimulus_output_file, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=[current_level]*(event_number + 1), magnets=quenching_magnet_list, t_offset=[t_PC_off]*(event_number + 1), interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                elif circuit_type == "RCD":
                    write_stimuli_file_step = WriteStimulusFile(type='WriteStimulusFile', output_file= stimulus_output_file, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[0]}.csv'), os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[1]}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=[current_level[1]]*number_of_magnets, magnets=magnets_list, t_offset=[t_PC_off[0]]*number_of_magnets, interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                elif circuit_type == "RCO":
                    write_stimuli_file_step = WriteStimulusFile(type='WriteStimulusFile', output_file= stimulus_output_file, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[0]}.csv'), os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name[1]}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=[current_level[0]]*number_of_magnets, magnets=magnets_list, t_offset=[t_PC_off[0]]*number_of_magnets, interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)
                else:
                    write_stimuli_file_step = WriteStimulusFile(type='WriteStimulusFile', output_file= stimulus_output_file, path_interpolation_file=[os.path.join(f'../../tests/builders/model_library/circuits/coil_resistances_to_interpolate/interpolation_resistance_{magnet_name}.csv')], n_total_magnets=number_of_magnets, n_apertures=number_of_apertures, current_level=[abs(current_level)], magnets=magnets_list, t_offset=[t_PC_off], interpolation_type='Linear', type_file_writing='w', n_sampling=1, magnet_types=magnet_types)

                # parsim sweep step with newly created event file
                if circuit_family_name == "RQ" or circuit_type == "RCBX":
                    output_files = self.__split_csv(path_output_event_csv)
                    parsim_sweep_step_1 = ParametricSweep(type='ParametricSweep', input_sweep_file=output_files[0],
                                                        model_name=model_name, case_model=case_model, software=software, verbose=verbose)
                    parsim_sweep_step_2 = ParametricSweep(type='ParametricSweep', input_sweep_file=output_files[1],
                                                        model_name=model_name, case_model=case_model, software=software, verbose=verbose)
                else:
                    parsim_sweep_step = ParametricSweep(type='ParametricSweep', input_sweep_file=path_output_event_csv,
                                                        model_name=model_name, case_model=case_model, software=software, verbose=verbose)

                # run all the steps together
                if circuit_family_name == "RQ":
                    self.load_circuit_parameters(load_circuit_parameters_step_1, verbose=verbose)
                    self.write_stimuli_from_interpolation(write_stimuli_file_step_1, verbose=verbose)
                    self.step_modify_model(modify_model_diode_step, verbose=verbose)
                    self.run_parsim_sweep(parsim_sweep_step_1, verbose=verbose)
                    self.load_circuit_parameters(load_circuit_parameters_step_2, verbose=verbose)
                    self.write_stimuli_from_interpolation(write_stimuli_file_step_2, verbose=verbose)
                    self.step_modify_model(modify_model_diode_step, verbose=verbose)
                    self.run_parsim_sweep(parsim_sweep_step_2, verbose=verbose)
                elif circuit_type == "RCBX":
                    self.load_circuit_parameters(load_circuit_parameters_step_1, verbose=verbose)
                    self.write_stimuli_from_interpolation(write_stimuli_file_step_1, verbose=verbose)
                    self.run_parsim_sweep(parsim_sweep_step_1, verbose=verbose)
                    self.load_circuit_parameters(load_circuit_parameters_step_2, verbose=verbose)
                    self.write_stimuli_from_interpolation(write_stimuli_file_step_2, verbose=verbose)
                    self.run_parsim_sweep(parsim_sweep_step_2, verbose=verbose)
                elif circuit_type == "RB":
                    self.step_modify_model(modify_model_diode_step, verbose=verbose)  # diode is changed for each row of the event file
                    if event_number == len(pec.list_events)-1:  # the simulation runs correctly only at the end
                        self.load_circuit_parameters(load_circuit_parameters_step, verbose=verbose)
                        self.write_stimuli_from_interpolation(write_stimuli_file_step, verbose=verbose)
                        self.run_parsim_sweep(parsim_sweep_step, verbose=verbose)
                else:
                    self.load_circuit_parameters(load_circuit_parameters_step, verbose=verbose)
                    self.write_stimuli_from_interpolation(write_stimuli_file_step, verbose=verbose)
                    self.run_parsim_sweep(parsim_sweep_step, verbose=verbose)

            # Write a .csv file that can be used to run a STEAM Viewer analysis #TODO consider adding set_up_viewer() method
            # for current_software, current_path_viewer_csv in zip(software, path_output_viewer_csv):
            #     pec.set_up_viewer(current_path_viewer_csv, default_keys, simulation_numbers, simulation_name, current_software)
            #     if verbose: print(f'File {current_path_viewer_csv} written. It can be used to run a STEAM Viewer analysis.')
        else:
            raise Exception(f'case_model {case_model} not supported by ParsimEvent.')

        if verbose:
            print(f'ParsimEvent called using input file {input_file}.')

    def run_parsim_conductor(self, step, verbose):
        '''
        Function to generate steps to change the conductor data of a magnet using a csv database

        :param step: instance of ParsimConductor step
        :param verbose: if true displays more information
        '''
        # Unpack inputs
        model_name = step.model_name
        case_model = step.case_model
        magnet_name = step.magnet_name
        software = step.software
        groups_to_coils = step.groups_to_coils
        length_to_coil = step.length_to_coil
        if not length_to_coil: length_to_coil = {}  # optimize coillen
        simulation_number = step.simulation_number
        input_file = step.input_file
        path_output_sweeper_csv = step.path_output_sweeper_csv
        strand_critical_current_measurements = step.strand_critical_current_measurements

        # check if crucial variables are not None
        if not path_output_sweeper_csv:
            raise Exception('File path path_output_event_csv must be defined for an analysis step of type ParsimEvent.')
        if not input_file:
            raise Exception('File path path_output_event_csv must be defined for an analysis step of type ParsimEvent.')

        # check if all groups are defined in the group dictionaries
        highest_group_index = max([max(values) for values in groups_to_coils.values()])
        expected_group_numbers = list(range(1, highest_group_index + 1))
        all_group_numbers_in_dict = [num for sublist in groups_to_coils.values() for num in sublist]
        if sorted(all_group_numbers_in_dict) != expected_group_numbers:
            raise Exception(f'Invalid groups_to_coils entry in step definition. \nSorted groups given by the user: {sorted(all_group_numbers_in_dict)}')

        # make a copy of the respective conductor for every coil and store it in the magnet model
        # NOTE: if a coil consists of 2 different conductors the user has to treat them as 2 different coils (so a coil is not always a coil but rather a subcoil with the same conductor)
        new_conductors = [None] * len(groups_to_coils)
        dict_coilname_to_conductorindex = {}
        new_conductor_to_group = [None] * len(self.list_models[model_name].model_data.CoilWindings.conductor_to_group)
        for idx, (coil_name, group_numbers) in enumerate(groups_to_coils.items()):
            # store the conductor indices of the groups that make up this coil
            conductor_indices = [self.list_models[model_name].model_data.CoilWindings.conductor_to_group[i-1] for i in group_numbers]

            # check if all the groups in the coil have the same conductor
            if len(set(conductor_indices)) != 1:
                raise Exception(f'Not every group in the coil {coil_name} has the same conductor. \n'
                                f'If a coil consists of more then one conductor it has to be treated like 2 separate coils.')
            else:
                # make a copy of the Conductor for this coil and overwrite the name
                # since all the entries in conductor_indices are the same, conductor_indices[0] can be used
                new_conductors[idx] = deepcopy(self.list_models[model_name].model_data.Conductors[conductor_indices[0]-1])
                new_conductors[idx].name = f'conductor_{coil_name}'

            # store what coilname belongs to what conductor index to later check in database
            dict_coilname_to_conductorindex[coil_name] = idx

            # change the entries in conductor_to_group with the new Conductor
            for group_number in group_numbers:
                new_conductor_to_group[group_number-1] = idx+1

        # check if all the values could be written
        if None in new_conductors or None in new_conductor_to_group:
            raise Exception(f'The given groups_to_coils did not contain all the group indices (1-{len(new_conductor_to_group)})!')

        # overwrite the information in the DataModelMagnet instance of the BuilderModel
        self.list_models[model_name].model_data.Conductors = new_conductors
        self.list_models[model_name].model_data.CoilWindings.conductor_to_group = new_conductor_to_group
        # NOTE: so far no parameters of the model_data were altered, just copies of the conductor have been made and connected to the specified groups
        del new_conductors, new_conductor_to_group


        if case_model == 'magnet':
            # create instance of ParsimConductor
            pc = ParsimConductor(verbose=verbose, model_data=self.list_models[model_name].model_data,
                                 dict_coilName_to_conductorIndex=dict_coilname_to_conductorindex,
                                 groups_to_coils=groups_to_coils, length_to_coil=length_to_coil,
                                 path_input_dir=Path(self.list_models[step.model_name].file_model_data).parent)
            # read the conductor database
            pc.read_from_input(path_input_file=input_file, magnet_name=magnet_name,
                               strand_critical_current_measurements=strand_critical_current_measurements)
            # write a sweeper csv file
            pc.write_conductor_parameter_file(path_output_file=path_output_sweeper_csv, simulation_name=model_name, # TODO simulation_name should be step variable in definition, model_name ist not step name?
                                              simulation_number=simulation_number)

            # create parsim sweep step with newly created sweeper csv file and run it
            parsim_sweep_step = ParametricSweep(type='ParametricSweep', input_sweep_file=path_output_sweeper_csv, # TODO rename teh class to ParametricSweepStep? ParsimConductor is no step class and ParametricSweep is
                                                model_name=model_name, case_model=case_model, software=software, verbose=verbose)
            self.run_parsim_sweep(parsim_sweep_step, verbose=verbose, revert=False)
        else:
            raise Exception(f'Case_model "{case_model}" not supported by ParsimConductor.')

    def run_parsim_sweep(self, step, verbose: bool = False, revert: bool = True):
        '''
        Function to generate steps based on list of models read from external file
        :param step:
        :param verbose: if true displays more information
        :param revert: if true the changes to the BM object are reverted after setting up the simulation files row by row
        '''
        # Unpack inputs
        input_sweep_file = step.input_sweep_file
        default_model_name = step.model_name
        case_model = step.case_model
        software = step.software
        verbose = step.verbose

        # read input sweeper file
        self.input_parsim_sweep_df = pd.read_csv(input_sweep_file)

        # loop through every row and run ModifyMultipleVariables step for every row (=event)
        for i, row in self.input_parsim_sweep_df.iterrows():
            # check if model_name is provided in sweeper. csv file - if not use the default one
            if 'simulation_name' in row and row['simulation_name'] in self.list_models:
                # use sweeper model_name only if model_name is existing in list_models
                model_name = row['simulation_name']
                if verbose: print(f'row {i + 1}: Using model {model_name} as specified in the input file {input_sweep_file}.')
            else:
                model_name = default_model_name
                if verbose: print(f'row {i + 1}: Using default model {default_model_name} as initial model.')

            # check if simulation number is provided and extract it from file
            try:
                # number has to be present & has to be an int (or be parsable into one) for the rest of the code to work
                simulation_number = int(row['simulation_number'])
            except:
                raise Exception(f'ERROR: no simulation_number provided in csv file {input_sweep_file}.')
            if verbose: print(f'changing these fields row # {i + 1}: {row}')

            dict_variables_to_change = dict()

            # unpack model_data
            if case_model == 'magnet':
                model_data = self.list_models[model_name].model_data
                next_simulation_name = model_data.GeneralParameters.magnet_name
            elif case_model == 'circuit':
                model_data = self.list_models[model_name].circuit_data
                next_simulation_name = model_data.GeneralParameters.circuit_name
            elif case_model == 'conductor':
                model_data = self.list_models[model_name].conductor_data
                next_simulation_name = model_data.GeneralParameters.conductor_name
            else:
                raise Exception(f'case_model {case_model} not supported by ParsimSweep.')

            # Initialize this variable, which is only used in the special case where circuit parameters are set to be changed (key "GlobalParameters.global_parameters")
            dict_circuit_param_to_change = {}

            # Iterate through the keys and values in the data dictionary & store all variables to change
            for j, (var_name, var_value) in enumerate(row.items()):
                # if value is null, skip this row
                if not pd.notnull(var_value): continue

                # Handle the change of a variable in the conductor list
                if 'Conductors[' in var_name:
                    # to check if var_name is valid (meaning it is the name of a variable in model_data)
                    try:
                        # try if eval is able to find the variable in model_data - if not: an Exception will be raised
                        eval('model_data.' + var_name)
                        dict_variables_to_change[var_name] = var_value
                    except:
                        print(f'WARNING: Sweeper skipped Column name "{var_name}" with value "{var_value}" in csv file {input_sweep_file}')

                # Handle the change of the special-case key GlobalParameters.global_parameters (dictionary of circuit global parameters)
                elif case_model == 'circuit' and var_name.startswith('GlobalParameters.global_parameters'):
                    # dict_global_parameters = deepcopy(model_data.GlobalParameters.global_parameters)  # original dictionary of circuit global parameters
                    circuit_param_to_change = var_name.split('GlobalParameters.global_parameters.')[-1]
                    # dict_global_parameters[circuit_param_to_change] = var_value
                    # dict_variables_to_change['GlobalParameters.global_parameters'] = dict_global_parameters
                    dict_circuit_param_to_change[circuit_param_to_change] = var_value

                # Check if the current variable is present in the model data structure & value in csv is not empty
                elif rhasattr(model_data, var_name):
                    # save valid new variable names and values to change them later
                    if type(var_value) == int or type(var_value) == float:
                        dict_variables_to_change[var_name] = var_value
                    elif type(var_value) == str:
                        dict_variables_to_change[var_name] = parse_str_to_list(var_value)
                    else:
                        raise Exception(f'ERROR: Datatype of Element in Column "{var_value}" Row "{j + 2}" of csv file {input_sweep_file} is invalid.')

                # print when columns have been skipped
                elif not rhasattr(model_data, var_name) and var_name != 'simulation_number':
                    print(f'WARNING: Column name "{var_name}" with value "{var_value}" in csv file {input_sweep_file} is skipped.')
            
            # Special case: If circuit parameters were set to change, add the key "GlobalParameters.global_parameters" to the dictionary of variables to change
            if len(dict_circuit_param_to_change) > 0:
                dict_global_parameters = deepcopy(model_data.GlobalParameters.global_parameters)  # original dictionary of circuit global parameters
                for key, value in dict_circuit_param_to_change.items():
                    dict_global_parameters[key] = value
                dict_variables_to_change['GlobalParameters.global_parameters'] = dict_global_parameters

            # if no variable to change is found, the simulation should run none the less, so dict_variables_to_change has to have an entry
            if not dict_variables_to_change:
                if case_model == 'magnet':
                    dict_variables_to_change['GeneralParameters.magnet_name'] = rgetattr(model_data, 'GeneralParameters.magnet_name')
                elif case_model == 'circuit':
                    dict_variables_to_change['GeneralParameters.circuit_name'] = rgetattr(model_data, 'GeneralParameters.circuit_name')
                elif case_model == 'conductor':
                    dict_variables_to_change['GeneralParameters.conductor_name'] = rgetattr(model_data, 'GeneralParameters.conductor_name')
                else:
                    raise Exception(f'case_model {case_model} not supported by ParsimSweep.')


            # copy original model to reset changes that step_modify_model_multiple_variables does
            if revert: local_model_copy = deepcopy(self.list_models[model_name])

            # make step ModifyModelMultipleVariables and alter all values found before
            next_step = ModifyModelMultipleVariables(type='ModifyModelMultipleVariables')
            next_step.model_name = model_name
            next_step.simulation_name = next_simulation_name
            next_step.variables_value = [[val] for val in dict_variables_to_change.values()]
            next_step.variables_to_change = list(dict_variables_to_change.keys())
            next_step.simulation_numbers = [simulation_number]
            next_step.software = software
            self.step_modify_model_multiple_variables(next_step, verbose=verbose)

            # reset changes to the model in self if revert flag is set
            if revert:
                self.list_models[model_name] = deepcopy(local_model_copy)
                del local_model_copy

        if verbose:
            print(f'Parsim Event called using input file {input_sweep_file}.')

    def __get_circuit_family_name(self, circuit_name: str):
        if circuit_name.startswith("RCBH") or circuit_name.startswith("RCBV"):
            return "60A"
        elif circuit_name.startswith("RD"):
            return "IPD"
        elif circuit_name.startswith("RQX"):
            return "RQX"
        elif circuit_name.startswith(("RQ4", "RQ5", "RQ6", "RQ7", "RQ8", "RQ9", "RQ10")):
            return "IPQ"
        elif circuit_name.startswith(("RQT12", "RQT13", "RQS", "RSS", "RQTL7", "RQTL8", "RQTL10", "RQTL11", "RCBX", "RQSX3", "RCS", "ROD", "ROF", "RQ6", "RSD", "RSF", "RQTL9", "RQTD", "RQTF", "RCD", "RCO")):
            return "600A"
        elif circuit_name.startswith("RQ"):
            return "RQ"
        elif circuit_name.startswith(("RCBY", "RCBC", "RCTX")):
            return "80-120A"
        elif circuit_name.startswith("RB"):
            return "RB"


    def __get_magnet_name(self, circuit_name: str):
        if circuit_name.startswith("RCBH") or circuit_name.startswith("RCBV"):
            return "MCBH"
        elif circuit_name.startswith("RD"):
            circuit_type = self.__get_circuit_type(circuit_name)
            magnet_dict = {"RD1": "MBX", "RD2": "MBRC", "RD3": "MBRS", "RD4": "MBRB"}
            return magnet_dict.get(circuit_type, "")
        elif circuit_name.startswith("RQX"):
            return ["MQXA", "MQXB"]
        elif circuit_name.startswith(("RQ4", "RQ5", "RQ6", "RQ7", "RQ8", "RQ9", "RQ10")):
            magnet_dict = {"IPQ_RQ4_2_2xRPHH_2xMQY": "MQY", "IPQ_RQ4_4_2xRPHH_4xMQY": ["MQY", "MQY"], "IPQ_RQ5_2_2xRPHGB_2xMQML": "MQML", "IPQ_RQ5_2_2xRPHH_2xMQY": "MQY", "IPQ_RQ5_4_2xRPHGB_4xMQM": ["MQM", "MQM"], "IPQ_RQ5_4_2xRPHH_4xMQY": ["MQY", "MQY"], "IPQ_RQ6_2_2xRPHGB_2xMQML": "MQML", "IPQ_RQ6_2_2xRPHGB_2xMQY": "MQY", "IPQ_RQ6_4_2xRPHGB_2xMQM_2xMQML": ["MQM", "MQML"], "IPQ_RQ7_2_2xRPHGA_2xMQM": "MQM", "IPQ_RQ7_4_2xRPHGA_4xMQM": ["MQM", "MQM"], "IPQ_RQ8_2_2xRPHGA_2xMQML": "MQML", "IPQ_RQ9_4_2xRPHGA_2xMQM_2xMQMC": ["MQM", "MQMC"], "IPQ_RQ10_2_2xRPHGA_2xMQML": "MQML"}
            return magnet_dict.get(self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name, "")
        elif circuit_name.startswith("RQ"):
            return "MQ"
        elif circuit_name.startswith("RCBY"):
            return "MCBYH"
        elif circuit_name.startswith("RCBC"):
            return "MCBCH"
        elif circuit_name.startswith("RQT12"):
            return "MQT"
        elif circuit_name.startswith("RCS"):
            return ["MCS", "MCS_quenchback"]
        elif circuit_name.startswith("RB"):
            return "MB"
        elif circuit_name.startswith("RCBX"):
            return ["MCBXH", "MCBXV"]
        elif self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name == "RCD":
            return ["MCD", "MCD_quenchback"]
        elif self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name == "RCO":
            return ["MCO", "MCO_quenchback"]

    def __get_number_of_magnets(self, circuit_name: str):
        circuit_family_name = self.__get_circuit_family_name(circuit_name)
        circuit_type = self.__get_circuit_type(circuit_name)
        if circuit_type in ["RCS", "RB"]:
            return 154
        elif circuit_type in ["RCD", "RCO"]:
            return 77
        elif circuit_family_name in ["60A", "IPD", "80-120A", "600A"]:
            return 1
        elif circuit_family_name == "RQ":
            return 47  # deal with 51 later
        elif circuit_family_name == "RQX":
            return 4
        elif circuit_family_name == "IPQ":
            return int(int(re.search(r'_(\d+)_', self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name).group(1))/2)

    def __get_number_of_apertures(self, circuit_name: str):
        circuit_family_name = self.__get_circuit_family_name(circuit_name)
        if circuit_family_name in ["IPQ", "RB"]:
            return 2
        else:
            return 1

    def __get_magnets_list(self, number_of_magnets: int):
        list = []
        for i in range(1, number_of_magnets+1):
            list.append(i)
        return list

    def __get_magnet_types_list(self, number_of_magnets: int):
        list = []
        if number_of_magnets == 4: #to be improved
            list = [1, 2, 2, 1]
        elif self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name.startswith("IPQ") and number_of_magnets == 2:
            list = [1, 2]
        elif self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name.startswith("RB"):
            for i in range(1, number_of_magnets+1):
                list.append(1)
        elif number_of_magnets in [154, 13, 8, 77, 6, 12, 11, 10, 9]:
            list = [1] + [2] * (number_of_magnets - 1)
        else:
            for i in range(1, number_of_magnets+1):
                list.append(1)
        return list

    def __get_circuit_type(self, circuit_name: str):
        if circuit_name.startswith("RCBH") or circuit_name.startswith("RCBV"):
            return "RCB"
        elif circuit_name.startswith(("RD1", "RD2", "RD3", "RD4")):
            return {"RD1": "RD1", "RD2": "RD2", "RD3": "RD3", "RD4": "RD4"}.get(circuit_name[:3], "No match found")
        elif circuit_name.startswith("RQX"):
            return "RQX"
        elif circuit_name.startswith(("RQ4", "RQ5", "RQ6", "RQ7", "RQ8", "RQ9", "RQ10")):
            return circuit_name.split(".")[0]
        elif circuit_name.startswith("RQT12"):
            return "RQT12"
        elif circuit_name.startswith("RQ"):
            return "RQ"
        elif circuit_name.startswith("RCS"):
            return "RCS"
        elif circuit_name.startswith("RB"):
            return "RB"
        elif circuit_name.startswith("RCBX"):
            return "RCBX"
        elif self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name == "RCD":
            return "RCD"
        elif self.data_analysis.AnalysisStepDefinition['runParsimEvent'].simulation_name == "RCO":
            return "RCO"

    def __get_quenching_magnet_number(self, position: str, circuit_family_name: str):
        df = pd.read_csv(os.path.join(f"../../tests/analyses/input/run_parsim_event_circuit/{circuit_family_name}_LayoutDetails.csv"))
        mask = df['Magnet'].str.split('.').str[1] == position
        result = df.loc[mask, '#Electric_circuit'].iloc[0]
        return result


    def __split_csv(self, input_file_name):
        # Create empty lists to hold the odd and even rows
        odd_rows = []
        even_rows = []

        # Open the input CSV file and read in the rows
        with open(input_file_name, 'r') as input_file:
            reader = csv.reader(input_file)

            # Save the header row
            header = next(reader)

            # Loop over the remaining rows and append them to the odd or even list
            for i, row in enumerate(reader):
                if i % 2 == 0:
                    even_rows.append(row)
                else:
                    odd_rows.append(row)

        # Write the odd and even rows to separate output files
        output_odd_file_name = 'output_odd.csv'
        with open(output_odd_file_name, 'w', newline='') as output_odd_file:
            writer_odd = csv.writer(output_odd_file)
            writer_odd.writerow(header)
            writer_odd.writerows(odd_rows)

        output_even_file_name = 'output_even.csv'
        with open(output_even_file_name, 'w', newline='') as output_even_file:
            writer_even = csv.writer(output_even_file)
            writer_even.writerow(header)
            writer_even.writerows(even_rows)

        # Return a list of the output file names
        return [output_even_file_name, output_odd_file_name]






