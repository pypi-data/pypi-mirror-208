from pydantic import BaseModel
from typing import (List, Union, Literal, Dict)
from steam_sdk.data.DataSettings import DataSettings


############################
# General parameters
class Model(BaseModel):
    """
        Level 2: Class for information on the model
    """
    name: str = None
    version: str = None
    case: str = None
    state: str = None


class General(BaseModel):
    """
        Level 1: Class for general information on the case study
    """
    analysis_name: str = None
    flag_permanent_settings: bool = None
    model: Model = Model()

class StrandCriticalCurrentMeasurement(BaseModel):
    """
        Level 1: Class for essential parameters for a critical current measurement to adjust Jc fit parameters
    """
    column_name_I_critical: str = None
    reference_mag_field: float = None
    reference_temperature: float = None
    column_name_CuNoCu_short_sample: str = None
    coil_names: List[str] = []



############################
# Working folders
class WorkingFolders(BaseModel):
    """
        Level 1: Class for information on the working folders
    """
    library_path: str = None  #
    output_path: str = None  # it would be nice if model_name and software could be read as parameters from other keys (anchors)
    temp_path: str = None


############################
# Analysis step definition
class MakeModel(BaseModel):
    """
        Level 2: Analysis step to generate a model using BuilderModel
    """
    type: Literal['MakeModel']
    model_name: str = None
    file_model_data: str = None  # it would be nice if it could be read as parameters from other keys (anchors)
    case_model: str = None
    software: List[str] = []
    simulation_name: str = None
    simulation_number: int = None
    flag_build: bool = True
    flag_dump_all: bool = False
    verbose: bool = True
    flag_plot_all: bool = False
    flag_json: bool = False


class ModifyModel(BaseModel):
    """
        Level 2: Analysis step to modify an existing BuilderModel object by changing one variable
    """
    type: Literal['ModifyModel']
    model_name: str = None
    variable_to_change: str = None
    variable_value: list = []
    new_model_name: List[str] = []  # if not empty, new copies of the model object will be built
    simulation_numbers: List[int] = []  # if not empty, simulation files will be built
    simulation_name: str = None
    software: List[str] = []


class ModifyModelMultipleVariables(BaseModel):
    """
        Level 2: Analysis step to modify an existing BuilderModel object by changing a list of variables
    """
    type: Literal['ModifyModelMultipleVariables']
    model_name: str = None
    variables_to_change: List[str] = []
    variables_value: List[list] = [[]]
    new_model_name: List[str] = []  # if not empty, new copies of the model object will be built
    simulation_numbers: List[int] = []  # if not empty, simulation files will be built
    simulation_name: str = None
    software: List[str] = []


class SetUpFolder(BaseModel):
    """
        Level 2: Analysis step to set up the folder structure for the required simulation software
    """
    type: Literal['SetUpFolder']
    simulation_name: str = None
    software: List[str] = []


class AddAuxiliaryFile(BaseModel):
    """
        Level 2: Analysis step to add/change an auxiliary file
    """
    type: Literal['AddAuxiliaryFile']
    software: str = None
    simulation_name: str = None
    simulation_numbers: List[int] = []  # if not empty, simulation files will be built
    full_path_aux_file: str = None
    new_file_name: str = None  # if empty, file is not renamed


class CopyFile(BaseModel):
    """
        Level 2: Analysis step to copy one file from a location to another
    """
    type: Literal['CopyFile']
    full_path_file_to_copy: str = None
    full_path_file_target: str = None


class RunSimulation(BaseModel):
    """
        Level 2: Analysis step to run a simulation file
    """
    type: Literal['RunSimulation']
    software: str = None
    simulation_name: str = None
    simulation_numbers: List[int] = []
    simFileType: str = None


class PostProcess(BaseModel):
    """
        Level 2: Analysis step to run a simulation file
    """
    type: Literal['PostProcess']
    software: str = None
    simulation_name: str = None
    simulation_numbers: List[int] = []

class RunCustomPyFunction(BaseModel):
    """
        Level 2: Analysis step to run a custom Python function
    """
    type: Literal['RunCustomPyFunction']
    flag_enable: bool = None
    function_name: str = None
    function_arguments: Dict = {}
    path_module: str = None  # optional


class RunViewer(BaseModel):
    """
        Level 2: Analysis step to make a steam_sdk.viewers.Viewer.Viewer() object and run its analysis
    """
    type: Literal['RunViewer']
    viewer_name: str = None
    file_name_transients: str = None
    list_events: List[int] = []
    flag_analyze: bool = None
    flag_display: bool = None
    flag_save_figures: bool = None
    path_output_html_report: str = None
    path_output_pdf_report: str = None
    figure_types: Union[List[str], str] = []
    verbose: bool = None


class CalculateMetrics(BaseModel):
    """
        Level 2: Analysis step to calculate metrics (usually to compare two or more measured and/or simulated signals)
    """
    type: Literal['CalculateMetrics']
    viewer_name: str = None
    metrics_name: str = None
    metrics_to_calculate: List[str] = []
    variables_to_analyze: List[List[str]] = [[]]


class LoadCircuitParameters(BaseModel):
    """
        Level 2: Analysis step to load global circuit parameters from a .csv file
    """
    type: Literal['LoadCircuitParameters']
    model_name: str = None
    path_file_circuit_parameters: str = None
    selected_circuit_name: str = None


class WriteStimulusFile(BaseModel):
    """
        Level 2: Analysis step to write stimulus file from coil resistance csv file
    """
    type: Literal['WriteStimulusFile']
    output_file: str = None
    path_interpolation_file: Union[str, List[str]] = None
    n_total_magnets: int = None
    n_apertures: int = None
    current_level: List[float] = []
    magnets: List[int] = []
    t_offset: List[float] = []
    interpolation_type: str = None  # 'Linear' or 'Spline'
    type_file_writing: str = None  # 'w' or 'a'
    n_sampling: int = None
    magnet_types: List[int] = []


class DefaultParsimEventKeys(BaseModel):
    """
        Level 3: Class for default keys of ParsimEventMagnet
    """
    local_LEDET_folder: str = None
    path_config_file: str = None
    default_configs: List[str] = []
    path_tdms_files: str = None
    path_output_measurement_files: str = None
    path_output: str = None


class ParsimEvent(BaseModel):
    """
        Level 2: Analysis step to write stimulus file from coil resistance csv file
    """
    type: Literal['ParsimEvent']
    input_file: str = None
    path_output_event_csv: str = None
    path_output_viewer_csv: Union[List[str], str] = None  # This list must have the same number of elements as the software list
    simulation_numbers: List[int] = []
    model_name: str = None
    case_model: str = None
    simulation_name: str = None
    software: List[str] = []
    t_PC_off: float = None  # TODO: consider making list of floats
    rel_quench_heater_trip_threshold: float = None
    current_polarities_CLIQ: List[int] = []  # TODO: consider making list of lists
    dict_QH_circuits_to_QH_strips: Dict[str, List[int]] = {}
    default_keys: DefaultParsimEventKeys = DefaultParsimEventKeys()


class ParametricSweep(BaseModel):
    """
        Level 2: Analysis step to write stimulus file from sweep input csv file
    """
    type: Literal['ParametricSweep']
    input_sweep_file: str = None
    model_name: str = None
    case_model: str = None
    software: List[str] = []
    verbose: bool = None


class ParsimConductor(BaseModel):
    """
        Level 2: Analysis step to write stimulus file from coil csv file
    """
    type: Literal['ParsimConductor']
    model_name: str = None
    case_model: str = None
    input_file: str = None
    magnet_name: str = None
    software: List[str] = []
    simulation_number: int = None
    strand_critical_current_measurements: List[StrandCriticalCurrentMeasurement] = []
    groups_to_coils: Dict[str, List[int]] = {}
    length_to_coil: Dict[str, float] = {}
    path_output_sweeper_csv: str = None

# class AnalysisStep(BaseModel):
#     """
#         Level 1: Class for information on the analysis step
#         Objects of this class will be defined in AnalysisStepDefinition
#     """
#     step: Union[MakeModel, ModifyModel, ModifyModelMultipleVariables, SetUpFolder, ChangeAuxiliaryFile, RunSimulation, PostProcess] = {}

############################
# Highest level
class DataAnalysis(BaseModel):
    '''
        **Class for the STEAM analysis inputs**

        This class contains the data structure of an analysis performed with STEAM_SDK.

        :param N: test 1
        :type N: int
        :param n: test 2
        :type n: int

        :return: DataModelCircuit object
    '''

    GeneralParameters: General = General()
    PermanentSettings: DataSettings = DataSettings()
    WorkingFolders: WorkingFolders = WorkingFolders()
    AnalysisStepDefinition: Dict[str, Union[MakeModel, ModifyModel, ModifyModelMultipleVariables, SetUpFolder,
                                            AddAuxiliaryFile, CopyFile, RunSimulation, PostProcess, RunCustomPyFunction,
                                            RunViewer, CalculateMetrics, LoadCircuitParameters, WriteStimulusFile,
                                            ParsimEvent, ParametricSweep, ParsimConductor]] = {}
    AnalysisStepSequence: List[str] = []  # Here the analysis steps are defined, in execution order. Names must be defined in AnalysisStepDefinition. Repetitions ARE allowed.
