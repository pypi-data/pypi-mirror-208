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


class DriverSIGMA_new:
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
        model_folder = os.path.join(self.path_folder_SIGMA, self.local_analysis_folder)
        input_file_path = os.path.join(model_folder, self.local_analysis_folder+"_SIGMA.yaml")
        # Run model
        self.MainSIGMA(input_file_path=input_file_path, model_folder=model_folder,
                       system_settings=self.system_settings)
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


