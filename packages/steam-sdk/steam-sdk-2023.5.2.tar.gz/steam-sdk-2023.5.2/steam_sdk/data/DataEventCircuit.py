from pydantic import BaseModel
from typing import (List, Union, Literal, Dict)

from steam_sdk.data.DataModelMagnet import Circuit, PowerSupply, EnergyExtraction
from typing import List, Optional


############################
# General parameters
class General(BaseModel):
    """
        Level 1: Class for general information on the case study
    """
    name: str = None
    place: str = None
    date: str = None
    period: str = None  # for example: "HWC 2021"
    time: str = None  # TODO: correct that it is a str?
    state: str = None  # occurred, predicted
    circuit_type: str = None
    initial_temperature: str = None

############################
# Powering
class Powering(BaseModel):
    """
        Level 1: Class for information on the circuit powering
    """
    circuit_name: str = None
    circuit_type: str = None
    delta_t_FGC_PIC: List[float] = [] # time delay between PIC signal and power supply switching-off signal (FGC)
    current_at_discharge: List[float] = []
    dI_dt_at_discharge: List[float] = []
    plateau_duration: List[float] = []
    cause_FPA: str = None


############################
# Energy extraction
class EnergyExtraction(BaseModel):
    delta_t_EE_PIC: float = None  # time delay between PIC signal and energy-extraction triggering
    U_EE_max: float = None


############################
# Quench event
class QuenchEvent(BaseModel):
    """
        Level 1: Class for information on the quench event occurred in the circuit
        The name of the keys in the QuenchEvent dictionary is the name of the quenched magnet
    """
    quench_cause: str = None
    magnet_name: str = None  # for example: magnet #23 or magnet Q1
    magnet_electrical_position: int = None
    quench_order: int = None  # defining in which order multiple quenches occurred
    current_at_quench: List[float] = []
    delta_t_iQPS_PIC: float = None  # time delay between PIC signal and "initial" quench detection system (iQPS)
    delta_t_nQPS_PIC: float = None  # time delay between PIC signal and "new" quench detection system (nQPS)
    quench_location: str = None  # for example: in which aperture the quench occurred
    QDS_trigger_cause: str = None
    QDS_trigger_origin: str = None
    dU_iQPS_dt: float = None
    V_symm_max: float = None
    dV_symm_dt: float = None


############################
# Highest level
class DataEventCircuit(BaseModel):
    '''
        **Class for the STEAM magnet event**

        This class contains the data structure of a magnet event analyzed with STEAM_SDK.

        :return: DataModelCircuit object
    '''

    GeneralParameters: General = General()
    PoweredCircuits: Dict[str, Powering] = {}
    EnergyExtractionSystem: Dict[str, EnergyExtraction] = {}
    QuenchEvents: Dict[str, QuenchEvent] = {}
