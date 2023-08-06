from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.data.DataRoxieParser import RoxieData
from steam_sdk.data.DataFiQuS import DataFiQuS, MultipoleRoxieGeometry, MultipoleSettings, MultipoleConductor, \
    MultipoleConductorSet


class BuilderFiQuS:
    """
        Class to generate FiQuS models
    """

    def __init__(self,
                 model_data: DataModelMagnet = None,
                 roxie_data=None,
                 flag_build: bool = True,
                 flag_plot_all: bool = False,
                 verbose: bool = True):
        """
        Object is initialized by defining FiQuS variable structure and file template.
        :param model_data: DataModelMagnet object
        :param roxie_data: RoxieData object
        :param flag_build: boolean, if set to true data objects needed for ParserFiQuS are assembled
        :param flag_plot_all: this flag gets passed to FiQuS input file for multipole only TODO: is this what we want long term
        :param verbose: if set to True, additional information is printed
        """
        # Unpack arguments
        self.verbose: bool = verbose

        if flag_build:

            # Data structure
            self.data_FiQuS = DataFiQuS(magnet={'type': model_data.GeneralParameters.magnet_type})

            # --------- general ----------
            self.data_FiQuS.general.magnet_name = model_data.GeneralParameters.magnet_name
            self.data_FiQuS.magnet.type = model_data.GeneralParameters.magnet_type
            self.data_FiQuS.run = model_data.Options_FiQuS.run

            if model_data.GeneralParameters.magnet_type == 'multipole':
                if not roxie_data:
                    raise Exception(f'Cannot build model instantly without providing RoxieData as input roxie_data')
                self.data_FiQuS_geo = MultipoleRoxieGeometry()
                self.data_FiQuS_set = MultipoleSettings()
                self.buildDataMultipole(model_data, roxie_data)
            elif model_data.GeneralParameters.magnet_type == 'CCT_straight':
                self.buildDataCCT(model_data)
            else:
                raise Exception(f'Magnet type: {model_data.GeneralParameters.magnet_type} is incompatible with FiQuS.')
                # ------------- circuit ---------
            for key, value in model_data.Circuit.dict().items():  # for keys that are present in the model data and in data FiQuS - they are the same
                self.data_FiQuS.circuit.__setattr__(key, value)

                # ------------- power_supply ---------
            for key, value in model_data.Power_Supply.dict().items():  # for keys that are present in the model data and in data FiQuS - they are the same
                self.data_FiQuS.power_supply.__setattr__(key, value)

                # ------------- quench_protection ---------
            for key, value in model_data.Quench_Protection.Energy_Extraction.dict().items():  # for keys that are present in the model data and in data FiQuS - they are the same
                self.data_FiQuS.quench_protection.energy_extraction.__setattr__(key, value)

            for key, value in model_data.Quench_Protection.Quench_Heaters.dict().items():  # for keys that are present in the model data and in data FiQuS - they are the same
                if key in self.data_FiQuS.quench_protection.quench_heaters.dict().keys():
                    self.data_FiQuS.quench_protection.quench_heaters.__setattr__(key, value)
            # set the params that are renamed in FiQuS
            self.data_FiQuS.quench_protection.quench_heaters.ids = model_data.Quench_Protection.Quench_Heaters.iQH_toHalfTurn_From
            self.data_FiQuS.quench_protection.quench_heaters.turns = model_data.Quench_Protection.Quench_Heaters.iQH_toHalfTurn_To

            for key, value in model_data.Quench_Protection.CLIQ.dict().items():  # for keys that are present in the model data and in data FiQuS - they are the same
                self.data_FiQuS.quench_protection.cliq.__setattr__(key, value)

            for key, value in model_data.Quench_Protection.FQPCs.dict().items():  # for keys that are present in the model data and in data FiQuS - they are the same
                self.data_FiQuS.quench_protection.FQPCs.__setattr__(key, value)
            # ------------- Conductors ---------
            for cond in model_data.Conductors:
                self.data_FiQuS.conductors[cond.name] = MultipoleConductor(
                    cable={'type': cond.cable.type})
                conductor = self.data_FiQuS.conductors[cond.name]
                for key, value in cond.cable.dict().items():
                    conductor.cable.__setattr__(key, value)

                print(conductor.strand['type'])
                for key, value in cond.strand.dict().items():
                    conductor.strand[key] = value

                for key, value in cond.Jc_fit.dict().items():
                    conductor.Jc_fit[key] = value



    def buildDataCCT(self, model_data):  # TODO: good idea to make them private?
        """
            Load selected conductor data from DataModelMagnet keys, check inputs, calculate and set missing variables
        """
        # --------- geometry ----------
        # windings
        for key, value in model_data.Options_FiQuS.cct.geometry.windings.dict().items():       # for keys that are present in the FiQUS Options model data (but not all keys in data FiQuS)
            self.data_FiQuS.magnet.geometry.windings.__setattr__(key, value)
        self.data_FiQuS.magnet.geometry.windings.n_turnss = model_data.CoilWindings.CCT_straight.winding_numberTurnsFormers  # additional, picked form other places in model data

        self.data_FiQuS.magnet.postproc.windings_wwns = model_data.CoilWindings.CCT_straight.winding_numRowStrands
        self.data_FiQuS.magnet.postproc.windings_whns = model_data.CoilWindings.CCT_straight.winding_numColumnStrands
        self.data_FiQuS.magnet.postproc.winding_order = model_data.CoilWindings.CCT_straight.winding_order

        # fqpls
        self.data_FiQuS.magnet.geometry.fqpls.fndpls = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.fndpls, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpls.fwhs = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.fwhs, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpls.fwws = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.fwws, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpls.n_sbs = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.n_sbs, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpls.names = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.names, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpls.r_bs = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.r_bs, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpls.r_ins = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.r_ins, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpls.thetas = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.thetas, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpls.z_ends = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.z_ends, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpls.z_starts = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.z_starts, model_data.Quench_Protection.FQPCs.enabled) if flag]

        # formers
        for key, value in model_data.Options_FiQuS.cct.geometry.formers.dict().items():       # for keys that are present in the model data (but not all keys in data FiQuS)
            self.data_FiQuS.magnet.geometry.formers.__setattr__(key, value)
        self.data_FiQuS.magnet.geometry.formers.r_ins = model_data.CoilWindings.CCT_straight.former_inner_radiuses  # additional, picked form other places in model data
        self.data_FiQuS.magnet.geometry.formers.r_outs = model_data.CoilWindings.CCT_straight.former_outer_radiuses  # additional, picked form other places in model data

        # air
        self.data_FiQuS.magnet.geometry.air = model_data.Options_FiQuS.cct.geometry.air   # for keys that are present in the model data and in data FiQuS - they are the same

        # ------------- mesh --------------
        self.data_FiQuS.magnet.mesh = model_data.Options_FiQuS.cct.mesh                # for keys that are present in the model data and in data FiQuS - they are the same

        # ------------- solve -------------
        self.data_FiQuS.magnet.solve.windings = model_data.Options_FiQuS.cct.solve.windings              # for keys that are present in the model data and in data FiQuS - they are the same
        self.data_FiQuS.magnet.solve.fqpls.mu_rs = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.mu_rs, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.solve.fqpls.currents = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.currents, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.solve.fqpls.sigmas = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.sigmas, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.solve.formers = model_data.Options_FiQuS.cct.solve.formers
        self.data_FiQuS.magnet.solve.air = model_data.Options_FiQuS.cct.solve.air
        self.data_FiQuS.magnet.solve.file_exts = model_data.Options_FiQuS.cct.solve.file_exts
        self.data_FiQuS.magnet.solve.pro_template = model_data.Options_FiQuS.cct.solve.pro_template
        self.data_FiQuS.magnet.solve.variables = model_data.Options_FiQuS.cct.solve.variables
        self.data_FiQuS.magnet.solve.volumes = model_data.Options_FiQuS.cct.solve.volumes

        # ------------- postproc ---------
        for key, value in model_data.Options_FiQuS.cct.postproc.dict().items():       # for keys that are present in the model data and in data FiQuS - they are the same
            self.data_FiQuS.magnet.postproc.__setattr__(key, value)

    def buildDataMultipole(self, model_data, roxie_data):
        """
            Load selected conductor data from DataModelMagnet keys, check inputs, calculate and set missing variables
        """

        # geom file
        self.data_FiQuS_geo.Roxie_Data = RoxieData(**roxie_data.dict())

        # set file
        self.data_FiQuS_set.Model_Data_GS.general_parameters.I_ref = \
            [model_data.Options_LEDET.field_map_files.Iref] * len(self.data_FiQuS_geo.Roxie_Data.coil.coils)
        for cond in model_data.Conductors:
            self.data_FiQuS_set.Model_Data_GS.conductors[cond.name] = MultipoleConductorSet(
                cable={'type': cond.cable.type})
            conductor = self.data_FiQuS_set.Model_Data_GS.conductors[cond.name]
            conductor.cable.bare_cable_width = cond.cable.bare_cable_width
            conductor.cable.bare_cable_height_mean = cond.cable.bare_cable_height_mean

        # --------- run ----------
        self.data_FiQuS.run = model_data.Options_FiQuS.run

        # --------- general ----------
        self.data_FiQuS.general.magnet_name = model_data.GeneralParameters.magnet_name

        # --------- geometry ----------
        self.data_FiQuS.magnet.geometry = model_data.Options_FiQuS.multipole.geometry

        # ------------- mesh --------------
        self.data_FiQuS.magnet.mesh = model_data.Options_FiQuS.multipole.mesh

        # ------------- solve -------------
        self.data_FiQuS.magnet.solve.thermal = model_data.Options_FiQuS.multipole.solve.thermal
        self.data_FiQuS.magnet.solve.thin_shells = model_data.Options_FiQuS.multipole.solve.thin_shells
        self.data_FiQuS.magnet.solve.pro_template = model_data.Options_FiQuS.multipole.solve.pro_template

        self.data_FiQuS.magnet.solve.electromagnetics.solved = model_data.Options_FiQuS.multipole.solve.electromagnetics.solved
        self.data_FiQuS.magnet.solve.electromagnetics.transient = model_data.Options_FiQuS.multipole.solve.electromagnetics.transient
        self.data_FiQuS.magnet.solve.electromagnetics.boundary_conditions.currents = \
            [model_data.Power_Supply.I_initial] * len(self.data_FiQuS_geo.Roxie_Data.coil.coils)

        # ------------- postproc ---------
        self.data_FiQuS.magnet.postproc = model_data.Options_FiQuS.multipole.postproc

