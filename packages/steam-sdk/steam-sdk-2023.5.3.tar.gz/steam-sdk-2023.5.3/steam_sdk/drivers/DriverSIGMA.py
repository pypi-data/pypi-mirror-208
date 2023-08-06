import glob
import os
import subprocess
from pathlib import Path

import pandas as pd
import yaml

from steam_sdk.builders.BuilderSIGMA import BuilderSIGMA
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.parsers.ParserCOMSOLToTxt import ParserCOMSOLToTxt
from steam_sdk.parsers.ParserRoxie import ParserRoxie


class DriverSIGMA:
    """
        Class to drive SIGMA models
    """

    def __init__(self,
                 path_folder_SIGMA,
                 path_folder_SIGMA_input, local_analysis_folder, system_settings, verbose=False):
        self.path_folder_SIGMA = path_folder_SIGMA
        self.path_folder_SIGMA_input = path_folder_SIGMA_input
        self.local_analysis_folder = local_analysis_folder
        self.system_settings = system_settings
        from steam_pysigma.MainSIGMA import MainSIGMA as MF
        self.MainSIGMA = MF

    @staticmethod
    def export_all_txt_to_concat_csv():
        """
        Export 1D plots vs time to a concatenated csv file. This file can be utilized with the Viewer.
        :return:
        """
        keyword = "all_times"
        files_to_concat = []
        for filename in os.listdir():
            if keyword in filename:
                files_to_concat.append(filename)
        df_concat = pd.DataFrame()
        for file in files_to_concat:
            df = ParserCOMSOLToTxt().loadTxtCOMSOL(file, header=["time", file.replace(".txt", "")])
            df_concat = pd.concat([df_concat, df], axis=1)
            df_concat = df_concat.loc[:, ~df_concat.columns.duplicated()]
            print(df_concat)
        df_concat = df_concat.reset_index(drop=True)
        df_concat.to_csv("SIGMA_transient_concat_output_1234567890MF.csv", index=False)

    def run_SIGMA(self, simulation_name):
        # input_file_path = os.path.join(self.path_folder_SIGMA_input, sim_file_name + '.yaml')
        model_folder = os.path.join(self.path_folder_SIGMA, self.local_analysis_folder, 'input')
        input_file_path = os.path.join(model_folder, self.local_analysis_folder+"_SIGMA.yaml")
        # Run model
        bh_curve_database = os.path.join(self.path_folder_SIGMA, self.local_analysis_folder, 'sources',
                     'roxie.bhdata')
        input_coordinates_path = os.path.join(self.path_folder_SIGMA, self.local_analysis_folder, 'sources',
                     self.local_analysis_folder + "_ROXIE_COORD.csv")
        if not Path(input_coordinates_path).exists():
            input_coordinates_path = None
        path_to_results = os.path.join(self.path_folder_SIGMA, self.local_analysis_folder, 'output')
        if not Path(path_to_results).exists():
            path_to_results = None
        print(f"Using {model_folder} as input file path")
        print(f"Using {input_file_path} yaml source path")
        print(f"Using {input_coordinates_path} as coordinate file path")
        print(f"Using {bh_curve_database} as bh file path")
        print(f"Using {path_to_results} as path to results")


        self.MainSIGMA(input_file_path=input_file_path, model_folder=model_folder,
                       system_settings=self.system_settings, bh_curve_database=bh_curve_database,
                       input_coordinates_path=input_coordinates_path,path_to_results=path_to_results)
        os.chdir(model_folder)
        batch_file_path = os.path.join(model_folder, f"{simulation_name}_Model_Compile_and_Open.bat")
        print(f'Running Comsol model via: {batch_file_path}')
        subprocess.call(batch_file_path)
        proc = subprocess.Popen([batch_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        (stdout, stderr) = proc.communicate()
        if proc.returncode != 0:
            print(stderr)
        else:
            print(stdout)


