from pathlib import Path
from typing import (Dict, List, Union, Literal)

from pydantic import BaseModel

from steam_sdk.data.DataFiQuS import MultipoleModelDataSetting
from steam_sdk.data.DataRoxieParser import RoxieData


class MultipoleRibbon(BaseModel):
    """
        Rutherford cable type
    """
    type: Literal['Ribbon']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None
    th_insulation_along_height: float = None
    th_insulation_along_width: float = None
    Rc: float = None
    Ra: float = None
    bare_cable_height_low: float = None
    bare_cable_height_high: float = None
    n_strands: int = None
    n_strands_per_layers: int = None
    n_strand_layers: int = None
    strand_twist_pitch: float = None
    width_core: float = None
    height_core: float = None
    strand_twist_pitch_angle: float = None
    f_inner_voids: float = None
    f_outer_voids: float = None


class MultipoleRutherford(BaseModel):
    """
        Rutherford cable type
    """
    type: Literal['Rutherford']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None
    th_insulation_along_height: float = None
    th_insulation_along_width: float = None
    Rc: float = None
    Ra: float = None
    bare_cable_height_low: float = None
    bare_cable_height_high: float = None
    n_strands: int = None
    n_strands_per_layers: int = None
    n_strand_layers: int = None
    strand_twist_pitch: float = None
    width_core: float = None
    height_core: float = None
    strand_twist_pitch_angle: float = None
    f_inner_voids: float = None
    f_outer_voids: float = None


class MultipoleRoxieGeometry(BaseModel):
    """
        Class for FiQuS multipole Roxie data (.geom)
    """
    Roxie_Data: RoxieData = RoxieData()

class Jc_FitSIGMA(BaseModel):
    type: str = None
    C1_CUDI1: str = None
    C2_CUDI1: str = None

class StrandSIGMA(BaseModel):
        filament_diameter: float = None
        diameter: float = None
        f_Rho_effective: float = None
        fil_twist_pitch: float = None
        RRR: float = None
        T_ref_RRR_high: float = None
        Cu_noCu_in_strand: float = None


class MultipoleSettings(BaseModel):
    """
        Class for FiQuS multipole settings (.set)
    """
    Model_Data_GS: MultipoleModelDataSetting = MultipoleModelDataSetting()


class MultipoleMono(BaseModel):
    """
        Rutherford cable type
    """
    type: Literal['Mono']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None
    th_insulation_along_height: float = None
    th_insulation_along_width: float = None
    Rc: float = None
    Ra: float = None
    bare_cable_height_low: float = None
    bare_cable_height_high: float = None
    n_strands: int = None
    n_strands_per_layers: int = None
    n_strand_layers: int = None
    strand_twist_pitch: float = None
    width_core: float = None
    height_core: float = None
    strand_twist_pitch_angle: float = None
    f_inner_voids: float = None
    f_outer_voids: float = None






class MultipoleConductor(BaseModel):
    """
        Class for conductor type
    """
    cable: Union[MultipoleRutherford, MultipoleRibbon, MultipoleMono] = {'type': 'Rutherford'}
    strand: StrandSIGMA = StrandSIGMA()
    Jc_fit: Jc_FitSIGMA = Jc_FitSIGMA()


class Sources(BaseModel):
    bh_curve_source: Path = None


class GeneralParameters(BaseModel):
    magnet_name: str = None
    T_initial: float = None
    magnetic_length: float = None


class PowerSupply(BaseModel):
    I_initial: float = None


class QuenchHeaters(BaseModel):
    N_strips: int = None
    t_trigger: List[float] = None
    U0: List[float] = None
    C: List[float] = None
    R_warm: List[float] = None
    w: List[float] = None
    h: List[float] = None
    s_ins: List[float] = None
    type_ins: List[float] = None
    s_ins_He: List[float] = None
    type_ins_He: List[float] = None
    l: List[float] = None
    l_copper: List[float] = None
    l_stainless_steel: List[float] = None
    f_cover: List[float] = None


class Cliq(BaseModel):
    t_trigger: float = None
    sym_factor: int = None
    U0: float = None
    I0: float = None
    C: float = None
    R: float = None
    L: float = None

class Circuit(BaseModel):
    R_circuit: float = None
    L_circuit: float = None
    R_parallel: float = None

class QuenchProtection(BaseModel):
    quench_heaters: QuenchHeaters = QuenchHeaters()
    cliq: Cliq = Cliq()


class TimeVectorSolutionSIGMA(BaseModel):
    time_step: List[List[float]] = None


class Simulation(BaseModel):
    generate_study: bool = None
    study_type: str = None
    make_batch_mode_executable: bool = None
    nbr_elements_mesh_width: int = None
    nbr_elements_mesh_height: int = None


class Physics(BaseModel):
    FLAG_M_pers: int = None
    FLAG_ifcc: int = None
    FLAG_iscc_crossover: int = None
    FLAG_iscc_adjw: int = None
    FLAG_iscc_adjn: int = None
    tauCC_PE: int = None


class QuenchInitialization(BaseModel):
    PARAM_time_quench: float = None
    FLAG_quench_all: int = None
    FLAG_quench_off: int = None
    num_qh_div: List[int] = None
    quench_init_heat: float = None
    quench_init_HT: List[str] = None
    quench_stop_temp: float = None


class Out2DAtPoints(BaseModel):
    coordinate_source: Path = None
    variables: List[str] = None
    time: List[List[float]] = None
    map2d: str = None


class Out1DVsTimes(BaseModel):
    variables: List[str] = None
    time: List[List[float]] = None


class Out1DVsAllTimes(BaseModel):
    variables: List[str] = None


class Postprocessing(BaseModel):
    out_2D_at_points: Out2DAtPoints = Out2DAtPoints()
    out_1D_vs_times: Out1DVsTimes = Out1DVsTimes()
    out_1D_vs_all_times: Out1DVsAllTimes = Out1DVsAllTimes()


class QuenchHeatersSIGMA(BaseModel):
    quench_heater_positions: List[int] = None
    th_coils: List[float] = None


class SIGMA(BaseModel):
    time_vector_solution: TimeVectorSolutionSIGMA = TimeVectorSolutionSIGMA()
    simulation: Simulation = Simulation()
    physics: Physics = Physics()
    quench_initialization: QuenchInitialization = QuenchInitialization()
    postprocessing: Postprocessing = Postprocessing()
    quench_heaters: QuenchHeatersSIGMA = QuenchHeatersSIGMA()


class DataSIGMA(BaseModel):
    sources: Sources = Sources()
    general_parameters: GeneralParameters = GeneralParameters()
    power_supply: PowerSupply = PowerSupply()
    quench_protection: QuenchProtection = QuenchProtection()
    options_sigma: SIGMA = SIGMA()
    circuit: Circuit = Circuit()
