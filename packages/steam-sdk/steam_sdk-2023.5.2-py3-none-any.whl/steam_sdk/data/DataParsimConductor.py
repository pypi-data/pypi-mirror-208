from typing import (List, Dict)
from pydantic import BaseModel

############################
# General parameters
class GeneralParameters(BaseModel):
    magnet_name: str = None
    circuit_name: str = None  # TODO currenty unused
    state: str = None  # measured, deduced from short-samples, deduced from design  # TODO currenty unused

############################
# Magnet
class Magnet(BaseModel):
    coils: List[str] = []
    measured_inductance_versus_current: List[List[float]] = []   # TODO currenty unused

############################
# Coils
class IcMeasurement(BaseModel):
    """
        Level 1: Class for parameters of a critical current measurement to adjust Jc fit parameters
    """
    Ic: float = None
    T_ref_Ic: float = None
    B_ref_Ic: float = None
    Cu_noCu_sample: float = None


class StrandGeometry(BaseModel):
    """
        Level 2: Class for strand geometry
    """
    diameter: float = None
    bare_width: float = None
    bare_height: float = None


class ConductorSample(BaseModel):
    ID: str = None  # TODO currenty unused
    Ra: float = None
    Rc: float = None
    number_of_strands: int = None
    width: float = None
    height: float = None
    strand_twist_pitch: float = None
    filament_twist_pitch: float = None
    RRR: float = None
    Cu_noCu: float = None
    # critical current measurement attributes
    Tc0: float = None
    Bc20: float = None
    f_rho_eff: float = None
    Ic_measurements: List[IcMeasurement] = []
    strand_geometry: StrandGeometry = StrandGeometry()



class Coil(BaseModel):
    ID: str = None  # TODO currenty unused
    cable_ID: str = None  # TODO currenty unused
    # Resistance measurement attributes
    coil_resistance_room_T: float = None
    Cu_noCu_resistance_meas: float = None
    B_resistance_meas: float = None
    T_ref_coil_resistance: float = None
    T_ref_RRR_low: float = None  # TODO do i have to write this in modelData? there would be such an entry
    T_ref_RRR_high: float = None
    # list of conductor samples and weight factor
    conductorSamples: List[ConductorSample] = []
    weight_factors: List[float] = []



class DataParsimConductor(BaseModel):
    '''
        **Class for the STEAM conductor**

        This class contains the data structure of a Conductor parsim  analyzed with STEAM_SDK.

        :return: DataParsimConductor object
    '''

    GeneralParameters: GeneralParameters = GeneralParameters()
    Magnet: Magnet = Magnet()
    Coils: Dict[str, Coil] = {}  # Datastructure representing one row in the csv file
