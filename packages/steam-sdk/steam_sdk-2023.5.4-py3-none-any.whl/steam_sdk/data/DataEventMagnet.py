from pydantic import BaseModel
from typing import (List, Dict)

from steam_sdk.data.DataModelMagnet import Circuit, PowerSupply, EnergyExtraction


############################
# General parameters
class General(BaseModel):
    """
        Level 1: Class for general information on the case study
    """
    name: str = None  # TODO: unused so far
    place: str = None  # TODO: unused so far
    date: str = None  # TODO: unused so far
    time: str = None  # TODO: unused so far (&correct that it is a str?)
    type: str = None  # natural quench, provoked discharge, powering cycle
    type_trigger: str = None  # TODO: unused so far! & is there a difference between type_trigger and type?
    circuit: str = None  # TODO: unused so far
    magnet: str = None  # TODO: unused so far
    conductor: str = None  # TODO: unused so far
    item: str = None  # another measured item that is not circuit, magnet, or conductor   # TODO: unused so far
    state: str = None  # occurred, predicted  # TODO: unused so far
    initial_temperature: str = None

############################
# Powering
class Powering(BaseModel):
    """
        Level 1: Class for information on the power supply and its current profile
    """
    # initial_current: str = None
    current_at_discharge: str = None  # TODO: unused so far
    max_dI_dt: str = None
    max_dI_dt2: str = None
    # custom_powering_cycle: List[List[float]] = [[]]  # optional
    PowerSupply: PowerSupply = PowerSupply()  # TODO t_off, t_control_LUT, I_control_LUT are unused because writing function directly assigns value to sweeper.csv


############################
# Quench Heaters
class QuenchHeaterCircuit(BaseModel):
    """
        Level 2: Class for information on the quench heater circuit
    """
    # N_circuits: int = None
    strip_per_circuit: List[int] = []  # TODO unused, writing function takes the argument
    t_trigger: float = None
    U0: float = None
    C: float = None
    R_warm: float = None
    R_cold: float = None  # TODO unused, writing function calculates it an only assigns it to sweeper.csv
    R_total: float = None  # TODO unused, writing function calculates it an only assigns it to sweeper.csv
    L: float = None  # TODO totally unused


############################
# CLIQ
class CLIQ(BaseModel):
    """
        Level 2: Class for information on the CLIQ protection system
    """
    t_trigger: float = None
    U0: float = None
    C: float = None
    R: float = None
    L: float = None


############################
# Quench protection
class QuenchProtection(BaseModel):
    """
        Level 1: Class for information on the quench protection system
    """
    Energy_Extraction: EnergyExtraction = EnergyExtraction()  # TODO unused so far
    Quench_Heaters: Dict[str, QuenchHeaterCircuit] = {}
    CLIQ: CLIQ = CLIQ()
    # FQPLs: FQPLs = FQPLs()


############################
# Quench
class Quench(BaseModel):
    """
        Level 1: Class for information on the quench location
    """
    t_quench: str = None
    location_coil: str = None
    location_block: str = None
    location_turn: str = None
    location_half_turn: str = None


############################
# Highest level
class DataEventMagnet(BaseModel):
    '''
    **Class for the STEAM magnet event**

    This class contains the data structure of a magnet event analyzed with STEAM_SDK.

    :param GeneralParameters: General information on the case study such as name, date, time, etc.
    :param Circuit: Electrical circuit information for the magnet.
    :param Powering: Information on the power supply and its current profile for the magnet.
    :param QuenchProtection: Information on the quench protection system, including energy extraction, quench heaters, and CLIQ.
    :param Quench: Information on the quench location, including time and location details.
    '''

    GeneralParameters: General = General()
    Circuit: Circuit = Circuit()
    Powering: Powering = Powering()
    QuenchProtection: QuenchProtection = QuenchProtection()
    Quench: Quench = Quench()  # TODO unused so far
