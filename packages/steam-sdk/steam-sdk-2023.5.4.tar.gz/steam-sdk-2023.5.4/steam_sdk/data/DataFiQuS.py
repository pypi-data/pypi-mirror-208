from pydantic import BaseModel
from typing import (Dict, List, Union, Literal)

from steam_sdk.data.DataConductor import ConstantJc, Bottura, CUDI3, Bordini, BSCCO_2212_LBNL, CUDI1, Summers, Round, \
    Rectangular, Rutherford, Mono, Ribbon
from steam_sdk.data.DataRoxieParser import RoxieData
from steam_sdk.data.DataModelMagnet import RunFiQuS
from steam_sdk.data.DataModelMagnet import MeshCCT
from steam_sdk.data.DataModelMagnet import Air_g
from steam_sdk.data.DataModelMagnet import MultipoleGeometry
from steam_sdk.data.DataModelMagnet import MultipoleMesh
from steam_sdk.data.DataModelMagnet import MultipoleSolve
from steam_sdk.data.DataModelMagnet import MultipolePostProc


class QuenchHeaters(BaseModel):
    """
        Level 2: Class for FiQuS input (.yaml)
    """
    N_strips: int = None
    t_trigger: List[float] = None
    U0: List[float] = None
    C: List[float] = None
    R_warm: List[float] = None
    w: List[float] = None
    h: List[float] = None
    s_ins: List[float] = None
    type_ins: List[str] = None
    s_ins_He: List[float] = None
    type_ins_He: List[str] = None
    l: List[float] = None
    l_copper: List[float] = None
    l_stainless_steel: List[float] = None
    ids: List[int] = None
    turns: List[int] = None
    turns_sides: List[str] = None


class Cliq(BaseModel):
    """
        Level 2: Class for FiQuS input (.yaml)
    """
    t_trigger: float = None
    current_direction: List[int] = None
    sym_factor: int = None
    N_units: int = None
    U0: float = None
    C: float = None
    R: float = None
    L: float = None
    I0: float = None


class FQPCs(BaseModel):
    """
        Level 2: Class for FiQuS input (.yaml)
    """
    enabled: List[bool] = None  # list specifying which fqpc is enabled
    names: List[str] = None  # name to use in gmsh and getdp
    fndpls: List[int] = None  # fqpc number of divisions per length
    fwws: List[float] = None  # fqpc wire widths (assuming rectangular) for theta = 0 this is x dimension
    fwhs: List[float] = None  # fqpc wire heights (assuming rectangular) for theta = 0 this is y dimension
    r_ins: List[
        float] = None  # radiuses for inner diameter for fqpc (radial (or x direction for theta=0) for placing the fqpc
    r_bs: List[float] = None  # radiuses for bending the fqpc by 180 degrees
    n_sbs: List[int] = None  # number of 'bending segmetns' for the 180 degrees turn
    thetas: List[float] = None  # rotation in deg from x+ axis towards y+ axis about z axis.
    z_starts: List[
        str] = None  # which air boundary to start at. These is string with either: z_min or z_max key from the Air region.
    z_ends: List[float] = None  # z coordinate of loop end
    currents: List[float] = None  # current in the wire
    sigmas: List[float] = None  # electrical conductivity
    mu_rs: List[float] = None  # relative permeability
    th_conns_def: List[List] = None


class Circuit(BaseModel):
    """
        Level 1: Class for FiQuS input (.yaml)
    """
    R_circuit: float = None
    L_circuit: float = None
    R_parallel: float = None


class EnergyExtraction(BaseModel):
    """
        Level 1: Class for FiQuS input (.yaml)
    """
    t_trigger: float = None
    R_EE: float = None
    power_R_EE: float = None
    L: float = None
    C: float = None


class PowerSupply(BaseModel):
    """
        Level 1: Class for FiQuS input (.yaml)
    """
    I_initial: float = None
    t_off: float = None
    t_control_LUT: List[float] = None
    I_control_LUT: List[float] = None
    R_crowbar: float = None
    Ud_crowbar: float = None


class QuenchProtection(BaseModel):
    """
        Level 1: Class for FiQuS Multipole
    """
    energy_extraction: EnergyExtraction = EnergyExtraction()
    quench_heaters: QuenchHeaters = QuenchHeaters()
    cliq: Cliq = Cliq()
    FQPCs: FQPCs = FQPCs()


class MultipoleMonoSet(BaseModel):
    """
        Rutherford cable type for settings (.set)
    """
    type: Literal['Mono']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None


class MultipoleRibbonSet(BaseModel):
    """
        Rutherford cable type for settings (.set)
    """
    type: Literal['Ribbon']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None


class MultipoleRutherfordSet(BaseModel):
    """
        Rutherford cable type for settings (.set)
    """
    type: Literal['Rutherford']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None


class MultipoleConductorSet(BaseModel):
    """
        Class for conductor type for settings (.set)
    """
    cable: Union[MultipoleRutherfordSet, MultipoleRibbonSet, MultipoleMonoSet] = {'type': 'Rutherford'}


class MultipoleConductor(BaseModel):
    """
        Class for conductor type for FiQuS input (.yaml)
    """
    version: str = None
    case: str = None
    state: str = None
    cable: Union[Rutherford, Ribbon, Mono] = {'type': 'Rutherford'}
    strand: Union[Round, Rectangular] = {'type': 'Round'}  # TODO: Tape, WIC
    Jc_fit: Union[ConstantJc, Bottura, CUDI1, CUDI3, Summers, Bordini, BSCCO_2212_LBNL] = {
        'type': 'CUDI1'}  # TODO: CUDI other numbers? , Roxie?


class MultipoleRoxieGeometry(BaseModel):
    """
        Class for FiQuS multipole Roxie data (.geom)
    """
    Roxie_Data: RoxieData = RoxieData()


class MultipoleGeneralSetting(BaseModel):
    """
        Class for general information on the case study
    """
    I_ref: List[float] = None


class MultipoleModelDataSetting(BaseModel):
    """
        Class for model data for settings (.set)
    """
    general_parameters: MultipoleGeneralSetting = MultipoleGeneralSetting()
    conductors: Dict[str, MultipoleConductorSet] = {}


#######################################################################################################################


class MultipoleSettings(BaseModel):
    """
        Class for FiQuS multipole settings (.set)
    """
    Model_Data_GS: MultipoleModelDataSetting = MultipoleModelDataSetting()


# Modified classes with respect to Options_FiQuS.multipole

############################


# Modified classes with respect to Options_FiQuS.cct
class CCTWinding_G(BaseModel):  # Geometry related windings _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    names: List[str] = None  # name to use in gmsh and getdp
    r_wms: List[float] = None  # radius of the middle of the winding
    n_turnss: List[float] = None  # number of turns
    ndpts: List[int] = None  # number of divisions of turn, i.e. number of hexagonal elements for each turn
    ndpt_ins: List[int] = None  # number of divisions of terminals ins
    ndpt_outs: List[int] = None  # number of divisions of terminals outs
    lps: List[float] = None  # layer pitch
    alphas: List[float] = None  # tilt angle
    wwws: List[float] = None  # winding wire widths (assuming rectangular)
    wwhs: List[float] = None  # winding wire heights (assuming rectangular)


class CCTFormerG(BaseModel):  # Geometry related formers _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    names: List[str] = None  # name to use in gmsh and getdp
    r_ins: List[float] = None  # inner radius
    r_outs: List[float] = None  # outer radius
    z_mins: List[float] = None  # extend of former  in negative z direction
    z_maxs: List[float] = None  # extend of former in positive z direction


class FQPL_g(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    names: List[str] = None  # name to use in gmsh and getdp
    fndpls: List[int] = None  # fqpl number of divisions per length
    fwws: List[float] = None  # fqpl wire widths (assuming rectangular) for theta = 0 this is x dimension
    fwhs: List[float] = None  # fqpl wire heights (assuming rectangular) for theta = 0 this is y dimension
    r_ins: List[
        float] = None  # radiuses for inner diameter for fqpl (radial (or x direction for theta=0) for placing the fqpl
    r_bs: List[float] = None  # radiuses for bending the fqpl by 180 degrees
    n_sbs: List[int] = None  # number of 'bending segmetns' for the 180 degrees turn
    thetas: List[float] = None  # rotation in deg from x+ axis towards y+ axis about z axis.
    z_starts: List[
        str] = None  # which air boundary to start at. These is string with either: z_min or z_max key from the Air region.
    z_ends: List[float] = None  # z coordinate of loop end


class CCTGeometry(BaseModel):
    """
        Level 2: Class for FiQuS CCT for FiQuS input
    """
    windings: CCTWinding_G = CCTWinding_G()
    fqpls: FQPL_g = FQPL_g()
    formers: CCTFormerG = CCTFormerG()
    air: Air_g = Air_g()


class Winding_s(BaseModel):  # Solution time used windings _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    currents: List[float] = None  # current in the wire
    sigmas: List[float] = None  # electrical conductivity
    mu_rs: List[float] = None  # relative permeability


class FQPL_s(BaseModel):  # Solution time used windings _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    currents: List[float] = None  # current in the wire
    sigmas: List[float] = None  # electrical conductivity
    mu_rs: List[float] = None  # relative permeability


class Former_s(BaseModel):  # Solution time used formers _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    sigmas: List[float] = None  # electrical conductivity
    mu_rs: List[float] = None  # relative permeability


class Air_s(BaseModel):  # Solution time used air _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    sigma: float = None  # electrical conductivity
    mu_r: float = None  # relative permeability


class SolveCCT(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    windings: Winding_s = Winding_s()  # windings solution time _inputs
    formers: Former_s = Former_s()  # former solution time _inputs
    fqpls: FQPL_s = FQPL_s()  # fqpls solution time _inputs
    air: Air_s = Air_s()  # air solution time _inputs
    pro_template: str = None  # file name of .pro template file
    variables: List[str] = None  # Name of variable to post-process by GetDP, like B for magnetic flux density
    volumes: List[str] = None  # Name of volume to post-process by GetDP, line Winding_1
    file_exts: List[str] = None  # Name of file extensions to post-process by GetDP, like .pos


class CCTPostproc(BaseModel):
    """
        Class for FiQuS CCT input file
    """
    windings_wwns: List[int] = None  # wires in width direction numbers
    windings_whns: List[int] = None  # wires in height direction numbers
    additional_outputs: List[str] = None  # Name of software specific input files to prepare, like :LEDET3D
    winding_order: List[int] = None
    fqpl_export_trim_tol: List[
        float] = None  # this multiplier times winding extend gives 'z' coordinate above(below) which hexes are exported for LEDET, length of this list must match number of fqpls
    variables: List[str] = None  # Name of variable to post-process by python Gmsh API, like B for magnetic flux density
    volumes: List[str] = None  # Name of volume to post-process by python Gmsh API, line Winding_1
    file_exts: List[str] = None  # Name of file extensions o post-process by python Gmsh API, like .pos


############################


class CCTDM(BaseModel):
    """
        Class for FiQuS CCT
    """
    type: Literal['CCT_straight']
    geometry: CCTGeometry = CCTGeometry()
    mesh: MeshCCT = MeshCCT()
    solve: SolveCCT = SolveCCT()
    postproc: CCTPostproc = CCTPostproc()


class MPDM(BaseModel):
    """
        Class for FiQuS multipole
    """
    type: Literal['multipole']
    geometry: MultipoleGeometry = MultipoleGeometry()
    mesh: MultipoleMesh = MultipoleMesh()
    solve: MultipoleSolve = MultipoleSolve()
    postproc: MultipolePostProc = MultipolePostProc()


class General(BaseModel):
    """
        Class for FiQuS general
    """
    magnet_name: str = None


class DataFiQuS(BaseModel):
    """
        Class for FiQuS
    """
    general: General = General()
    run: RunFiQuS = RunFiQuS()
    magnet: Union[MPDM, CCTDM] = {'type': 'multipole'}
    circuit: Circuit = Circuit()
    power_supply: PowerSupply = PowerSupply()
    quench_protection: QuenchProtection = QuenchProtection()
    conductors: Dict[str, MultipoleConductor] = {}
