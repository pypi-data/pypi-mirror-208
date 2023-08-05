import os

from steam_sdk.parsers.ParserYAML import dict_to_yaml
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


class ParserSIGMA:
    """
        Class with methods to write FiQuS input files from steam sdk
    """

    def __init__(self, builder_SIGMA, verbose=True):
        """
        Initialization using a BuilderFiQuS object containing FiQuS parameter structure
        :param builder_SIGMA: BuilderFiQuS object
        :param verbose: boolean if set to true more information is printed to the screen
        """

        self.builder_SIGMA = builder_SIGMA
        self.verbose = verbose

        self.attributes = ['data_SIGMA', 'data_SIGMA_geo', 'data_SIGMA_set']
        self.file_exts = ['yaml', 'geom', 'set']

    def writeSIGMA2yaml(self, output_path: str, simulation_name=None, append_str_to_magnet_name: str = ''):
        """
        ** Writes SIGMA input files **

        :param output_path: full path to output folder.
        :param simulation_name: This is used in analysis steam to change yaml name from magnet name to simulation name
        :param append_str_to_magnet_name: additional string to add to magnet name, e.g. '_SIGMA'.
        :return:   Nothing, writes files to output folder.
        """

        make_folder_if_not_existing(output_path)  # If the output folder is not an empty string, and it does not exist, make it
        for attribute, file_ext in zip(self.attributes, self.file_exts):
            if simulation_name:
                yaml_file_name = f'{simulation_name}{append_str_to_magnet_name}.{file_ext}'
            else:
                yaml_file_name = f'{self.builder_SIGMA.data_SIGMA.general_parameters.magnet_name}{append_str_to_magnet_name}.{file_ext}'
            dict_to_yaml(getattr(self.builder_SIGMA, attribute).dict(), os.path.join(output_path, yaml_file_name), list_exceptions=[])


