import csv
import numpy as np
import os
from typing import List

import pandas as pd

from steam_sdk.builders.BuilderModel import BuilderModel
from steam_sdk.data.DataEventCircuit import DataEventCircuit
from steam_sdk.data.DataEventCircuit import Powering, General, QuenchEvent, EnergyExtraction
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from steam_sdk.utils.rgetattr import rgetattr
from steam_sdk.utils.sgetattr import rsetattr
from steam_sdk.utils.utils_PC import calculate_t_PC_off

class ParsimEventCircuit:
    """

    """

    def __init__(self, ref_model: BuilderModel = None, verbose: bool = True):
        """
        If verbose is set to True, additional information will be displayed
        """
        # Unpack arguments
        self.verbose: bool = verbose
        self.list_events: List[DataEventCircuit] = []
        # self.dict_AnalysisStepDefinition = {}
        # self.list_AnalysisStepSequence = []
        # # save local reference model, so that empty field in EventData.csv can be populated with default ones
        self.ref_model = ref_model
        # # TODO add a dictionary of default values?

    def read_from_input(self, path_input_file: str, flag_append: bool):
        '''
        Read a list of events from an input .csv file and assign its content to a list of DataEventCircuit() objects.
        This method is used to read and set the variables that can be expressed with one or a limited amount of values.
        More complex variables are covered by dedicated methods.

        :param path_input_file: Path to the .csv file to read
        :param flag_append: If True, merge the content of the file to the current list of events. If False, overwrite it.
        :return:
        '''

        # Read the input file
        if path_input_file.endswith('.csv'):
            df_events = pd.read_csv(path_input_file)
        elif path_input_file.endswith('.xlsx'):
            df_events = pd.read_excel(path_input_file)
        else:
            raise Exception(f'The extension of the file {path_input_file} is not supported.')
        df_events = pd.DataFrame([[None if pd.isna(x) else x for x in row] for row in df_events.values], columns=df_events.columns)
        #df_events = df_events.dropna(axis=1, how='all')

        # validate dataframe - if csv file has a headline or empty rows on the top, skip row until there all columnnames have values
        skip_rows = 0
        while any(['Unnamed: ' in s for s in
                   df_events.columns]):  # pandas assigns the columname 'Unnamed: i' when no name can be found
            skip_rows += 1
            if path_input_file.endswith('.csv'):
                df_events = pd.read_csv(path_input_file, skiprows=skip_rows)
            elif path_input_file.endswith('.xlsx'):
                df_events = pd.read_excel(path_input_file, skiprows=skip_rows)

            df_events = pd.DataFrame([[None if pd.isna(x) else x for x in row] for row in df_events.values],
                                     columns=df_events.columns)
            #df_events = df_events.dropna(axis=1, how='all')

            if skip_rows == 2:  # check only for the first 2 rows
                raise Exception(
                    f"The input file {path_input_file} has an incorrect format. Some columns have no name, or one of the column names starts with 'Unnamed: '.")

        # Assign the content to a dataclass structure
        list_events = []
        parsed_columns = []  # list containing the column names that were parsed
        for index, event_info in df_events.iterrows():
            new_event = DataEventCircuit()
            circuit_type = event_info["Circuit Family"]
            circuit_name = event_info["Circuit Name"]
            rsetattr(new_event, 'GeneralParameters.circuit_type', circuit_type)

            if self.verbose:
                print(f"circuit type: {circuit_type}")
            if circuit_type in ["RCBH", "RCBV"]:
                parsed_columns += self.__read_60A(event_info, new_event)
            elif circuit_type == "RQX":
                parsed_columns += self.__read_RQX(event_info, new_event)
            elif circuit_type in ["RQ4", "RQ5", "RQ7", "RQ8", "RQ9", "RQ10"] or (circuit_name.startswith("RQ6.") and len(circuit_name) == 6):
                parsed_columns += self.__read_IPQ(event_info, new_event)
            elif circuit_type in ["RD1", "RD2", "RD3", "RD4"]:
                parsed_columns += self.__read_IPD(event_info, new_event)
            elif circuit_type in ["RCS", "ROD", "ROF", "RSD", "RSF", "RQTL9", "RQTD", "RQTF"] or (circuit_name.startswith("RQ6.") and len(circuit_name) == 8):
                parsed_columns += self.__read_600A_with_EE(event_info, new_event)
            elif circuit_type == "RCD":
                parsed_columns += self.__read_RCD(event_info, new_event)
            elif circuit_type == "RCBX":
                parsed_columns += self.__read_RCBX(event_info, new_event)
            elif circuit_type in ["RCBCH", "RCBCV", "RCBYH", "RCBYV"]:
                parsed_columns += self.__read_80_120A(event_info, new_event)
            elif circuit_type == "RQ":
                parsed_columns += self.__read_RQ(event_info, new_event)
            elif circuit_type == "RB":
                parsed_columns += self.__read_RB(event_info, new_event)
            elif circuit_type in ["RQT12", "RQT13", "RSS", "RQTL7", "RQTL8", "RQTL10", "RQTL11", "RQSX3"]: #RQS common to EE and no EE case
                parsed_columns += self.__read_600A_no_EE(event_info, new_event)
            else:
                raise Exception(f"circuit type not supported {circuit_type}")
            list_events.append(new_event)

        # print out all the names of the ignored columns
        ignored_column_names = list(set(df_events.columns) - set(parsed_columns))
        if self.verbose:
            print(f'Names of ignored columns: {ignored_column_names}')

        # Update attribute
        if flag_append:
            self.list_events += list_events
        else:
            self.list_events = list_events


    def write_event_file(self, simulation_name: str, simulation_numbers: List[int], path_outputfile_event_csv: str):
        """
        Write the event information to a CSV file, that can be used to run a ParsimSweep Step.

        Parameters:
            simulation_name (str): Simulation name.
            simulation_numbers (List[int]): List of simulation numbers.
            path_outputfile_event_csv (str): Path to the output event CSV file.

        Raises:
            Exception: If the length of input simulation numbers differs from length of events found in the input file.

        """
        # check inputs
        if simulation_name in ["RQ_47magnets", "RQ_51magnets", "RCBX"]:
            if len(simulation_numbers) != 2 * len(self.list_events):
                raise Exception(
                    f'length of input simulation numbers ({len(simulation_numbers)}) is not double of length of events found in the input file ({len(self.list_events)}) for RQ type circuit')
        elif len(simulation_numbers) != len(self.list_events):
            raise Exception(
                f'length of input simulation numbers ({len(simulation_numbers)}) differs from length of events found in the input file ({len(self.list_events)})')

        # Make target folder if it is missing
        make_folder_if_not_existing(os.path.dirname(path_outputfile_event_csv))

        # open file in writing mode
        all_rows = []
        list_paramerers = []

        # Loop trough each element of self.list_events and write parameters to csv
        for i, event in enumerate(self.list_events):
            print(i, event)
            new_row = {'simulation_name': simulation_name, 'simulation_number': simulation_numbers[i]}
            event_data = self.__write_event(event)
            event_data_counter = 0
            if isinstance(event_data, list):
                for data in event_data:
                    new_row.update(data)
                    if simulation_name in ["RQ_47magnets", "RQ_51magnets", "RCBX"] and event_data_counter % 2 != 0:
                        new_row['simulation_number'] = 2
                    all_rows.append(new_row.copy())
                    list_paramerers = list(set(list_paramerers + list(new_row.keys())))
                    event_data_counter = event_data_counter + 1
            else:
                new_row.update(event_data)
                all_rows.append(new_row)
                list_paramerers = list(set(list_paramerers + list(new_row.keys())))

        # TODO reorder the columns
        # Write file
        with open(path_outputfile_event_csv, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list_paramerers)
            writer.writeheader()
            for new_row in all_rows:
                writer.writerow(new_row)

    ### Helper functions ###
    def __read_600A_no_EE(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read 600A circuit family with no EE parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC)": 'GeneralParameters.date',
            "Time (FGC)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            "Circuit Name": 'circuit_name',
            "Circuit Family": 'circuit_type',
            'I_Q_circ': 'current_at_discharge',
            "Ramp rate": 'dI_dt_at_discharge',
            "Plateau duration": 'plateau_duration',
            "Delta_t(FGC-PIC)": 'delta_t_FGC_PIC',
            "FPA Reason": 'cause_FPA'
        }
        dict_params_QuenchEvents = {
            'I_Q_circ': 'current_at_quench',
            'Type of Quench': 'quench_cause',
            "Delta_t(QPS-PIC)": 'delta_t_iQPS_PIC',
            "dU_QPS/dt": 'dU_iQPS_dt',
            "QDS trigger origin": "QDS_trigger_origin"
        }
        # Assign General parameters
        new_event.GeneralParameters = General()
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])

        return_list = list(dict_params_Powering.keys()) + list(dict_params_QuenchEvents.keys()) + list(dict_params_GeneralParameters.keys())
        return return_list
    def __read_60A(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read 60 A family parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC)": 'GeneralParameters.date',
            "Time (FGC)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            'I_Q_circ': 'current_at_discharge',
            "Ramp rate": 'dI_dt_at_discharge',
            "Plateau duration": 'plateau_duration'
        }
        dict_params_QuenchEvents = {
            'I_Q_circ': 'current_at_quench',
            'Type of Quench': 'quench_cause'
        }

        # Assign General parameters
        new_event.GeneralParameters = General()
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])

        # if not new_event.PoweredCircuits:
        #     circuit_name = [key for key, value in dict_params.items() if value == 'new_event.neralParameters.name']
        #     raise Exception(
        #         f'No file name for the test could be found in the csv file. A column with one of the following keys should have a valid name: {circuit_name}.')

        return_list = list(dict_params_Powering.keys()) + list(dict_params_QuenchEvents.keys()) + list(dict_params_GeneralParameters.keys())
        return return_list

    def __read_RQX(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read RQX family parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC_RQX)": 'GeneralParameters.date',
            "Time (FGC_RQX)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            "Circuit Name": 'circuit_name',
            "Circuit Family": 'circuit_type',
            ('I_Q_RQX', 'I_Q_RTQX1', 'I_Q_RTQX2'): 'current_at_discharge',
            ("Ramp rate RQX", "Ramp rate RTQX1", "Ramp rate RTQX2"): 'dI_dt_at_discharge',
            ("Plateau duration RQX", "Plateau duration RTQX1", "Plateau duration RTQX2"): 'plateau_duration',
            "Delta_t(FGC_RQX-PIC)": 'delta_t_FGC_PIC',
            "FPA Reason": 'cause_FPA'
        }
        dict_params_QuenchEvents = {
            ('I_Q_RQX', 'I_Q_RTQX1', 'I_Q_RTQX2'): 'current_at_quench',
            'Type of Quench': 'quench_cause',
            "Delta_t(QPS-PIC)": 'delta_t_iQPS_PIC',
            "Quench origin": 'magnet_name',
            "dU_QPS/dt": 'dU_iQPS_dt'
        }

        # Assign General parameters
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])
            elif param in [('I_Q_RQX', 'I_Q_RTQX1', 'I_Q_RTQX2'), ("Ramp rate RQX", "Ramp rate RTQX1", "Ramp rate RTQX2"), ("Plateau duration RQX", "Plateau duration RTQX1", "Plateau duration RTQX2")]:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], [event_info[param[0]],event_info[param[1]],event_info[param[2]]])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])
            elif param in [('I_Q_RQX', 'I_Q_RTQX1', 'I_Q_RTQX2')]:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], [event_info[param[0]], event_info[param[1]], event_info[param[2]]])

        return_list = []
        merged_dict = {k: v for d in (dict_params_GeneralParameters, dict_params_Powering, dict_params_QuenchEvents) for k, v in d.items()}
        for key, value in merged_dict.items():
            if isinstance(key, tuple):
                for subkey in key:
                    return_list.append(subkey)
            else:
                return_list.append(key)

        return return_list

    def __read_IPQ(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read RQ4 family parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC_Bn)": 'GeneralParameters.date',
            "Time (FGC_Bn)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            "Circuit Name": 'circuit_name',
            "Circuit Family": 'circuit_type',
            ('I_Q_B1', 'I_Q_B2'): 'current_at_discharge',
            ("Ramp rate B1", "Ramp rate B2"): 'dI_dt_at_discharge',
            ("Plateau duration B1", "Plateau duration B2"): 'plateau_duration',
            "Delta_t(FGC-PIC)": 'delta_t_FGC_PIC',
            "FPA Reason": 'cause_FPA'
        }
        dict_params_QuenchEvents = {
            ('I_Q_B1','I_Q_B2'): 'current_at_quench',
            'Type of Quench': 'quench_cause',
            "Delta_t(QPS-PIC)": 'delta_t_iQPS_PIC',
            "Quench origin": 'magnet_name',
            ("dU_QPS_B1/dt", "dU_QPS_B2/dt"): 'dU_iQPS_dt'
        }

        # Assign General parameters
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])
            elif param in [('I_Q_B1', 'I_Q_B2'), ("Ramp rate B1", "Ramp rate B2"), ("Plateau duration B1", "Plateau duration B2")]:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], [event_info[param[0]], event_info[param[1]]])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])
            elif param in [('I_Q_B1', 'I_Q_B2'), ("dU_QPS_B1/dt", "dU_QPS_B2/dt")]:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], [event_info[param[0]], event_info[param[1]]])

        return_list = []
        merged_dict = {k: v for d in (dict_params_GeneralParameters, dict_params_Powering, dict_params_QuenchEvents) for k, v in d.items()}
        for key, value in merged_dict.items():
            if isinstance(key, tuple):
                for subkey in key:
                    return_list.append(subkey)
            else:
                return_list.append(key)

        return return_list

    def __read_IPD(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read RD1 family parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC)": 'GeneralParameters.date',
            "Time (FGC)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            "Circuit Name": 'circuit_name',
            "Circuit Family": 'circuit_type',
            'I_Q_circ': 'current_at_discharge',
            "Ramp rate": 'dI_dt_at_discharge',
            "Plateau duration": 'plateau_duration',
            "Delta_t(FGC-PIC)": 'delta_t_FGC_PIC',
            "FPA Reason": 'cause_FPA'
        }
        dict_params_QuenchEvents = {
            'I_Q_circ': 'current_at_quench',
            'Type of Quench': 'quench_cause',
            "Delta_t(QPS-PIC)": 'delta_t_iQPS_PIC',
            "dU_QPS/dt": 'dU_iQPS_dt',
            "QDS trigger origin": "QDS_trigger_origin"
        }
        # Assign General parameters
        new_event.GeneralParameters = General()
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])

        return_list = list(dict_params_Powering.keys()) + list(dict_params_QuenchEvents.keys()) + list(dict_params_GeneralParameters.keys())
        return return_list

    def __read_600A_with_EE(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read RCS family parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC)": 'GeneralParameters.date',
            "Time (FGC)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            "Circuit Name": 'circuit_name',
            "Circuit Family": 'circuit_type',
            'I_Q_circ': 'current_at_discharge',
            "Ramp rate": 'dI_dt_at_discharge',
            "Plateau duration": 'plateau_duration',
            "Delta_t(FGC-PIC)": 'delta_t_FGC_PIC',
            "FPA Reason": 'cause_FPA'
        }
        dict_params_QuenchEvents = {
            'I_Q_circ': 'current_at_quench',
            'Type of Quench': 'quench_cause',
            "Delta_t(QPS-PIC)": 'delta_t_iQPS_PIC',
            "dU_QPS/dt": 'dU_iQPS_dt',
            "QDS trigger origin": "QDS_trigger_origin"
        }
        dict_params_EnergyExtraction = {
            "Delta_t(EE-PIC)": 'delta_t_EE_PIC',
            "U_EE_max": 'U_EE_max'
        }
        # Assign General parameters
        new_event.GeneralParameters = General()
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])

        # Assign Energy Extraction event parameters
        new_event.EnergyExtractionSystem[circuit_name] = EnergyExtraction()
        for param in dict_params_EnergyExtraction:
            if param in event_info:
                rsetattr(new_event.EnergyExtractionSystem[circuit_name], dict_params_EnergyExtraction[param], event_info[param])

        return_list = list(dict_params_Powering.keys()) + list(dict_params_QuenchEvents.keys()) + list(dict_params_GeneralParameters.keys()) + list(dict_params_EnergyExtraction.keys())
        return return_list

    def __read_RCD(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read RQ4 family parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC)": 'GeneralParameters.date',
            "Time (FGC)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            "Circuit Name": 'circuit_name',
            "Circuit Family": 'circuit_type',
            ('I_Q_RCO', 'I_Q_RCD'): 'current_at_discharge',
            ("Ramp rate RCO", "Ramp rate RCD"): 'dI_dt_at_discharge',
            ("Plateau duration RCO", "Plateau duration RCD"): 'plateau_duration',
            "Delta_t(FGC-PIC)": 'delta_t_FGC_PIC',
            "FPA Reason": 'cause_FPA'
        }
        dict_params_QuenchEvents = {
            ('I_Q_RCO', 'I_Q_RCD'): 'current_at_quench',
            'Type of Quench': 'quench_cause',
            "Delta_t(QPS-PIC)": 'delta_t_iQPS_PIC',
            "Quench origin": 'magnet_name',
            ("dU_QPS/dt_RCO", "dU_QPS/dt_RCD"): 'dU_iQPS_dt',
            "QDS trigger origin": "QDS_trigger_origin"
        }
        dict_params_EnergyExtraction = {
            "Delta_t(EE_RCD-PIC)": 'delta_t_EE_PIC',
            "U_EE_RCD_max": 'U_EE_max'
        }

        # Assign General parameters
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])
            elif param in [('I_Q_RCO', 'I_Q_RCD'), ("Ramp rate RCO", "Ramp rate RCD"), ("Plateau duration RCO", "Plateau duration RCD")]:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], [event_info[param[0]], event_info[param[1]]])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])
            elif param in [('I_Q_RCO', 'I_Q_RCD'), ("dU_QPS/dt_RCO", "dU_QPS/dt_RCD")]:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param],[event_info[param[0]], event_info[param[1]]])

        # Assign Energy Extraction event parameters
        new_event.EnergyExtractionSystem[circuit_name] = EnergyExtraction()
        for param in dict_params_EnergyExtraction:
            if param in event_info:
                rsetattr(new_event.EnergyExtractionSystem[circuit_name], dict_params_EnergyExtraction[param], event_info[param])

        return_list = []
        merged_dict = {k: v for d in (dict_params_GeneralParameters, dict_params_Powering, dict_params_QuenchEvents, dict_params_EnergyExtraction) for k, v in d.items()}
        for key, value in merged_dict.items():
            if isinstance(key, tuple):
                for subkey in key:
                    return_list.append(subkey)
            else:
                return_list.append(key)

        return return_list

    def __read_RCBX(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read RCBX family parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC)": 'GeneralParameters.date',
            "Time (FGC)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            "Circuit Name": 'circuit_name',
            "Circuit Family": 'circuit_type',
            ('I_Q_H', 'I_Q_V'): 'current_at_discharge',
            ("Ramp rate H", "Ramp rate V"): 'dI_dt_at_discharge',
            ("Plateau duration H", "Plateau duration V"): 'plateau_duration',
            "Delta_t(FGC-PIC)": 'delta_t_FGC_PIC',
            "FPA Reason": 'cause_FPA'
        }
        dict_params_QuenchEvents = {
            ('I_Q_H','I_Q_V'): 'current_at_quench',
            'Type of Quench': 'quench_cause',
            "Delta_t(QPS-PIC)": 'delta_t_iQPS_PIC',
            "Quench origin": 'magnet_name',
            ("dU_QPS/dt_H", "dU_QPS/dt_V"): 'dU_iQPS_dt',
            "QDS trigger origin": "QDS_trigger_origin"

        }

        # Assign General parameters
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])
            elif param in [('I_Q_H', 'I_Q_V'), ("Ramp rate H", "Ramp rate V"), ("Plateau duration H", "Plateau duration V")]:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], [event_info[param[0]], event_info[param[1]]])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])
            elif param in [('I_Q_H', 'I_Q_V'), ("dU_QPS/dt_H", "dU_QPS/dt_V")]:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], [event_info[param[0]], event_info[param[1]]])

        return_list = []
        merged_dict = {k: v for d in (dict_params_GeneralParameters, dict_params_Powering, dict_params_QuenchEvents) for k, v in d.items()}
        for key, value in merged_dict.items():
            if isinstance(key, tuple):
                for subkey in key:
                    return_list.append(subkey)
            else:
                return_list.append(key)

        return return_list

    def __read_80_120A(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read RCBC, RCBY family parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC)": 'GeneralParameters.date',
            "Time (FGC)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            "Circuit Name": 'circuit_name',
            "Circuit Family": 'circuit_type',
            'I_Q_circ': 'current_at_discharge',
            "Ramp rate": 'dI_dt_at_discharge',
            "Plateau duration": 'plateau_duration',
            "FPA Reason": 'cause_FPA'
        }
        dict_params_QuenchEvents = {
            'I_Q_circ': 'current_at_quench',
            'Type of Quench': 'quench_cause'
        }
        # Assign General parameters
        new_event.GeneralParameters = General()
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])

        return_list = list(dict_params_Powering.keys()) + list(dict_params_QuenchEvents.keys()) + list(dict_params_GeneralParameters.keys())
        return return_list

    def __read_RQ(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read RQ family parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC)": 'GeneralParameters.date',
            "Time (FGC)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            "Circuit Name": 'circuit_name',
            "Circuit Family": 'circuit_type',
            ('I_Q_RQD', 'I_Q_RQF'): 'current_at_discharge',
            ("Ramp rate RQD", "Ramp rate RQF"): 'dI_dt_at_discharge',
            ("Plateau duration RQD", "Plateau duration RQF"): 'plateau_duration',
            "Delta_t(FGC-PIC)": 'delta_t_FGC_PIC',
            "FPA Reason": 'cause_FPA'
        }
        dict_params_QuenchEvents = {
            ('I_Q_MQD', 'I_Q_MQF'): 'current_at_quench',
            'Type of Quench': 'quench_cause',
            "Delta_t(iQPS-PIC)": 'delta_t_iQPS_PIC',
            ("Delta_t(nQPS_RQD-PIC)", "Delta_t(nQPS_RQF-PIC)"): 'delta_t_nQPS_PIC',
            "Quench origin": 'magnet_name',
            "Position": 'magnet_electrical_position',
            "Nr in Q event": 'quench_order',
            ("dU_iQPS/dt_RQD", "dU_iQPS/dt_RQF"): 'dU_iQPS_dt',
            "QDS trigger origin": "QDS_trigger_origin"
        }
        dict_params_EnergyExtraction = {
            ("Delta_t(EE_RQD-PIC)", "Delta_t(EE_RQF-PIC)"): 'delta_t_EE_PIC',
            ("U_EE_max_RQD", "U_EE_max_RQF"): 'U_EE_max'
        }

        # Assign General parameters
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])
            elif param in [('I_Q_RQD', 'I_Q_RQF'), ("Ramp rate RQD", "Ramp rate RQF"), ("Plateau duration RQD", "Plateau duration RQF")]:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], [event_info[param[0]], event_info[param[1]]])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])
            elif param in [('I_Q_MQD', 'I_Q_MQF'), ("Delta_t(nQPS_RQD-PIC)", "Delta_t(nQPS_RQF-PIC)"), ("dU_iQPS/dt_RQD", "dU_iQPS/dt_RQF")]:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], [event_info[param[0]], event_info[param[1]]])

        # Assign Energy Extraction event parameters
        new_event.EnergyExtractionSystem[circuit_name] = EnergyExtraction()
        for param in dict_params_EnergyExtraction:
            if param in event_info:
                rsetattr(new_event.EnergyExtractionSystem[circuit_name], dict_params_EnergyExtraction[param], event_info[param])
            elif param in [("Delta_t(EE_RQD-PIC)", "Delta_t(EE_RQF-PIC)"), ("U_EE_max_RQD", "U_EE_max_RQF")]:
                rsetattr(new_event.EnergyExtractionSystem[circuit_name], dict_params_EnergyExtraction[param], [event_info[param[0]], event_info[param[1]]])

        return_list = []
        merged_dict = {k: v for d in (dict_params_GeneralParameters, dict_params_Powering, dict_params_QuenchEvents, dict_params_EnergyExtraction) for k, v in d.items()}
        for key, value in merged_dict.items():
            if isinstance(key, tuple):
                for subkey in key:
                    return_list.append(subkey)
            else:
                return_list.append(key)

        return return_list

    def __read_RB(self, event_info: pd.Series, new_event: DataEventCircuit):
        '''
        Function to read RB family parameters

        :param event_info: Series of parameters
        :param new_event: DataEventCircuit object to update
        :return: new_event
        '''
        circuit_name = event_info["Circuit Name"]
        dict_params_GeneralParameters = {
            'Circuit Name': 'GeneralParameters.name',
            "Period": 'GeneralParameters.period',
            "Date (FGC)": 'GeneralParameters.date',
            "Time (FGC)": 'GeneralParameters.time',
            'Circuit Family': 'GeneralParameters.circuit_type'
        }
        dict_params_Powering = {
            "Circuit Name": 'circuit_name',
            "Circuit Family": 'circuit_type',
            'I_Q_circ': 'current_at_discharge',
            "Ramp rate": 'dI_dt_at_discharge',
            "Plateau duration": 'plateau_duration',
            "Delta_t(FGC-PIC)": 'delta_t_FGC_PIC',
            "FPA Reason": 'cause_FPA'
        }
        dict_params_QuenchEvents = {
            'I_Q_M': 'current_at_quench',
            'Type of Quench': 'quench_cause',
            "Delta_t(iQPS-PIC)": 'delta_t_iQPS_PIC',
            "Delta_t(nQPS-PIC)": 'delta_t_nQPS_PIC',
            "Quench origin": 'magnet_name',
            "dU_iQPS/dt": 'dU_iQPS_dt',
            "Position": 'magnet_electrical_position',
            "Nr in Q event": 'quench_order',
            "QDS trigger origin": "QDS_trigger_origin",
            "V_symm_max": 'V_symm_max',
            "dV_symm/dt": 'dV_symm_dt'

        }
        dict_params_EnergyExtraction = {
            ("Delta_t(EE_even-PIC)", "Delta_t(EE_odd-PIC)"): 'delta_t_EE_PIC',
            ("U_EE_max_ODD", "U_EE_max_EVEN"): 'U_EE_max'
        }

        # Assign General parameters
        for param in dict_params_GeneralParameters:
            if param in event_info:
                rsetattr(new_event, dict_params_GeneralParameters[param], event_info[param])

        # Assign powering parameters
        new_event.PoweredCircuits[circuit_name] = Powering()
        for param in dict_params_Powering:
            if param in event_info:
                rsetattr(new_event.PoweredCircuits[circuit_name], dict_params_Powering[param], event_info[param])

        # Assign quench event parameters
        new_event.QuenchEvents[circuit_name] = QuenchEvent()
        for param in dict_params_QuenchEvents:
            if param in event_info:
                rsetattr(new_event.QuenchEvents[circuit_name], dict_params_QuenchEvents[param], event_info[param])

        # Assign Energy Extraction event parameters
        new_event.EnergyExtractionSystem[circuit_name] = EnergyExtraction()
        for param in dict_params_EnergyExtraction:
            if param in event_info:
                rsetattr(new_event.EnergyExtractionSystem[circuit_name], dict_params_EnergyExtraction[param], event_info[param])
            elif param in [("Delta_t(EE_even-PIC)", "Delta_t(EE_odd-PIC)"), ("U_EE_max_ODD", "U_EE_max_EVEN")]:
                rsetattr(new_event.EnergyExtractionSystem[circuit_name], dict_params_EnergyExtraction[param], [event_info[param[0]], event_info[param[1]]])

        return_list = []
        merged_dict = {k: v for d in (dict_params_GeneralParameters, dict_params_Powering, dict_params_QuenchEvents, dict_params_EnergyExtraction) for k, v in d.items()}
        for key, value in merged_dict.items():
            if isinstance(key, tuple):
                for subkey in key:
                    return_list.append(subkey)
            else:
                return_list.append(key)

        return return_list

    def __write_event(self, event: DataEventCircuit, t_after_PC_off: float = 10.0):
        circuit_type = event.GeneralParameters.circuit_type
        circuit_name = event.GeneralParameters.name
        if circuit_type in ['RCBH', 'RCBV', "RQT12", "RQT13", "RSS", "RQTL7", "RQTL8", "RQTL10", "RQTL11", "RQSX3", "RCBYV", "RCBYH", "RCBCH", "RCBCV", "RD1", "RD2", "RD3", "RD4"]:
            event_dict = self.__write_common_circuit_family(event, t_after_PC_off=t_after_PC_off)
        elif circuit_type == "RQ":
            event_dict = self.__write_RQ(event, t_after_PC_off=t_after_PC_off)
        elif circuit_type in ["RQ4", "RQ5", "RQ7", "RQ8", "RQ9", "RQ10"] or (circuit_name.startswith("RQ6.") and len(circuit_name) == 6):
            event_dict = self.__write_IPQ(event, t_after_PC_off=t_after_PC_off)
        elif circuit_type == "RQX":
            event_dict = self.__write_RQX(event, t_after_PC_off=t_after_PC_off)
        elif circuit_type in ["RCS", "ROD", "ROF", "RSD", "RSF", "RQTL9", "RQTD", "RQTF"] or (circuit_name.startswith("RQ6.") and len(circuit_name) == 8):
            event_dict = self.__write_600A_with_EE(event, t_after_PC_off=t_after_PC_off)
        elif circuit_type == "RB":
            event_dict = self.__write_RB(event, t_after_PC_off=t_after_PC_off)
        elif circuit_type == "RCBX":
            event_dict = self.__write_RCBX(event, t_after_PC_off=t_after_PC_off)
        return event_dict

    def __write_common_circuit_family(self, event: DataEventCircuit, t_after_PC_off: float = 10.0):
        """
        Extract the information for an event of circuit type RCB.

        Parameters:
            event (DataEventCircuit): The data event object to read the data.

        Returns:
            dict: A dictionary containing the RCB information.

        """
        circuit_name = event.GeneralParameters.name
        event_dict = dict()
        t_start = 0  # hard-coded
        I_start = 0.0  # hard-coded
        dI_dt2 = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')['dI_dt2'])  # read dI/dt2 from the STEAM model
        dI_dt = event.PoweredCircuits[circuit_name].dI_dt_at_discharge
        current_at_discharge = event.PoweredCircuits[circuit_name].current_at_discharge
        t_PC_off = self.__handle_ramp_rate_cases(event, circuit_name, t_after_PC_off, t_start, I_start, dI_dt, dI_dt2, current_at_discharge, event_dict)
        event.PoweredCircuits[circuit_name].delta_t_FGC_PIC = t_PC_off

        # TODO
        # if dI/dt is 0:
        # read dI/dt and dI/st2 from the STEAM model
        # set the plateau length
        # set the I_end_1
        # set t_PC_off (time to reach I_end_1 + plateau)
        # set timing options based on t_PC_off
        # else:
        # read dI/dt2 from the STEAM model
        # set dI/dt
        # set the I_end_1
        # set t_PC_off (time to reach I_end_1)
        # set timing options based on t_PC_off

        # # populate steps in list of steps
        # dict_params_Powering = {
        #     'current_at_discharge': 'GlobalParameters.global_parameters.I_end_2',
        #     # "Circuit Family": 'circuit_family',
        #     # 'I_Q_circ': 'current_at_discharge',
        #     # "Ramp rate": 'dI_dt_at_discharge',
        #     # "Plateau duration": 'plateau_duration',
        #     # "FPA Reason": 'cause_FPA'
        # }
        # # dict_params_QuenchEvents = {
        # #     'I_Q_circ': 'current_at_quench',
        # #     'Type of Quench': 'quench_cause'
        # # }
        #
        # for old_name, new_name in dict_params_Powering.items():
        #     if rgetattr(event.PoweredCircuits[circuit_name], old_name) and not math.isnan(rgetattr(event.PoweredCircuits[circuit_name], old_name)):
        #         event_dict[new_name] = rgetattr(event.PoweredCircuits[circuit_name], old_name)
        #     if not new_name in event_dict:
        #         event_dict[new_name] = ''

        return event_dict

    def __write_RQ(self, event: DataEventCircuit, t_after_PC_off: float = 10.0):
        """
        Extract the information for an event of circuit type RQ.

        Parameters:
            event (DataEventCircuit): The data event object to read the data.

        Returns:
            list[dict]: A list of dictionaries containing the RQ information.

        """
        circuit_name = event.GeneralParameters.name
        list= []
        t_EE_list = []
        t_PC_off_list = []
        for i in range(2):
            event_dict = dict()
            t_start = 0  # hard-coded
            I_start = 0.0  # hard-coded
            dI_dt2 = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')['dI_dt2'])  # read dI/dt2 from the STEAM model
            dI_dt = event.PoweredCircuits[circuit_name].dI_dt_at_discharge[i]

            current_at_discharge = event.PoweredCircuits[circuit_name].current_at_discharge[i]
            if dI_dt == 0:
                I_end = current_at_discharge
                dI_dt = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')['dI_dt'])
                time_to_reach_I = self.__time_to_reach_I(I=I_end, dI_dt=dI_dt, dI_dt2=dI_dt2, I_start=I_start)
                t_plateau = event.PoweredCircuits[circuit_name].plateau_duration[i]
                t_PC_off = t_start + time_to_reach_I + t_plateau
                #event_dict['GlobalParameters.global_parameters.t_plateau'] = t_plateau
                event_dict['GlobalParameters.global_parameters.I_end_1'] = I_end
                event_dict['GlobalParameters.global_parameters.I_end_2'] = 0.0

            elif np.sign(dI_dt) != np.sign(current_at_discharge):
                I_end_1 = 1.2*current_at_discharge
                I_end_2 = current_at_discharge
                t_plateau = 10  # hard-coded
                t_PC_off = calculate_t_PC_off(t_start, I_start, [I_end_1, I_end_2], [-dI_dt, dI_dt], [dI_dt2, dI_dt2], [t_plateau, t_plateau], I_end_2)
                event_dict['GlobalParameters.global_parameters.I_end_1'] = I_end_1
                event_dict['GlobalParameters.global_parameters.I_end_2'] = I_end_2
                event_dict['GlobalParameters.global_parameters.dI_dt'] = -dI_dt  # setting dI_dt
                event_dict['GlobalParameters.global_parameters.dI_dt2'] = dI_dt2  # setting dI_dt2

            else:
                I_end = str(current_at_discharge) + " + 100.0"
                I_target = current_at_discharge + 100.0
                t_plateau = t_start + 2 * dI_dt / dI_dt2 + (I_target - I_start - dI_dt ** 2 / dI_dt2) / dI_dt
                t_PC_off = calculate_t_PC_off(t_start, I_start,  I_target, [dI_dt], [dI_dt2], [t_plateau], I_target - 100)
                event_dict['GlobalParameters.global_parameters.dI_dt'] = dI_dt  #setting dI_dt
                event_dict['GlobalParameters.global_parameters.I_end_1'] = I_target
                event_dict['GlobalParameters.global_parameters.I_end_2'] = 0.0

            t_PC_off_list.append(t_PC_off)
            dict_time_schedule = {
                '0.0': '0.5',
                f'{t_PC_off - 1.000}': '0.100',
                f'{t_PC_off - 0.100}': '0.010',
                f'{t_PC_off - 0.010}': '0.001',
                f'{t_PC_off - 0.001}': '0.0001',
                f'{t_PC_off + 0.020}': '0.001',
                f'{t_PC_off + 1.000}': '0.010',
                f'{t_PC_off + 3.000}': '0.500'
            }
            event_dict['GlobalParameters.global_parameters.I_start'] = I_start
            event_dict['GlobalParameters.global_parameters.t_start'] = t_start
            event_dict['GlobalParameters.global_parameters.t_plateau'] = t_plateau
            event_dict['GlobalParameters.global_parameters.t_PC_off'] = t_PC_off
            event_dict['GlobalParameters.global_parameters.t_EE'] = t_PC_off + 0.096
            event_dict['Analysis.simulation_time.time_end'] = t_PC_off + t_after_PC_off
            event_dict['Analysis.simulation_time.time_schedule'] = dict_time_schedule
            event.PoweredCircuits[circuit_name].delta_t_FGC_PIC = t_PC_off_list
            event.EnergyExtractionSystem[circuit_name].delta_t_EE_PIC = t_EE_list.append(t_PC_off + 0.096)

            list.append(event_dict)

        return list

    def __write_RCBX(self, event: DataEventCircuit, t_after_PC_off: float = 10.0):
        """
        Extract the information for an event of circuit type RCBX.

        Parameters:
            event (DataEventCircuit): The data event object to read the data.

        Returns:
            list[dict]: A list of dictionaries containing the RQ information.

        """
        circuit_name = event.GeneralParameters.name
        list= []
        t_PC_off_list = []
        for i in range(2):
            event_dict = dict()
            t_start = 0  # hard-coded
            I_start = 0.0  # hard-coded
            dI_dt2 = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')['dI_dt2'])  # read dI/dt2 from the STEAM model
            dI_dt = event.PoweredCircuits[circuit_name].dI_dt_at_discharge[i]
            current_at_discharge = event.PoweredCircuits[circuit_name].current_at_discharge[i]
            t_PC_off = self.__handle_ramp_rate_cases(event, circuit_name, t_after_PC_off, t_start, I_start, dI_dt, dI_dt2, current_at_discharge, event_dict)
            t_PC_off_list.append(t_PC_off)
            event.PoweredCircuits[circuit_name].delta_t_FGC_PIC = t_PC_off_list
            list.append(event_dict)

        return list

    def __write_RQX(self, event: DataEventCircuit, t_after_PC_off: float = 10.0):
        """
        Extract the information for an event of circuit type RQX.

        Parameters:
            event (DataEventCircuit): The data event object to read the data.

        Returns:
            list[dict]: A list of dictionaries containing the RQX information.

        """
        circuit_name = event.GeneralParameters.name
        list= []
        t_PC_off_list = []
        acceleration_list = ["dI_dt2_PC1", "dI_dt2_PC2", "dI_dt2_PC3"]
        ramp_rate_list = ["dI_dt_PC1", "dI_dt_PC2", "dI_dt_PC3"]

        #loop to calculate list of t_PC_off
        for i in range(3):
            #event_dict = dict()
            t_start = 0  # hard-coded
            I_start = 0.0  # hard-coded
            dI_dt2 = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')[acceleration_list[i]])  # read dI/dt2 from the STEAM model
            dI_dt = event.PoweredCircuits[circuit_name].dI_dt_at_discharge[i]

            current_at_discharge = event.PoweredCircuits[circuit_name].current_at_discharge[i]

            if dI_dt == 0:
                I_end = current_at_discharge
                dI_dt = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')[ramp_rate_list[i]])
                time_to_reach_I = self.__time_to_reach_I(I=I_end, dI_dt=dI_dt, dI_dt2=dI_dt2, I_start=I_start)
                t_plateau = event.PoweredCircuits[circuit_name].plateau_duration[i]
                t_PC_off = t_start + time_to_reach_I + t_plateau

            elif np.sign(dI_dt) != np.sign(current_at_discharge):
                I_end_1 = 1.2*current_at_discharge
                I_end_2 = current_at_discharge
                t_plateau = 10  # hard-coded
                t_PC_off = calculate_t_PC_off(t_start, I_start, [I_end_1, I_end_2], [-dI_dt, dI_dt], [dI_dt2, dI_dt2], [t_plateau, t_plateau], I_end_2)

            else:
                I_end = str(current_at_discharge) + " + 100.0"
                I_target = current_at_discharge + 100.0
                t_plateau = t_start + 2 * dI_dt / dI_dt2 + (I_target - I_start - dI_dt ** 2 / dI_dt2) / dI_dt
                t_PC_off = calculate_t_PC_off(t_start, I_start,  I_target, [dI_dt], [dI_dt2], [t_plateau], I_target - 100)

            t_PC_off_list.append(t_PC_off)

        t_PC_off = max(t_PC_off_list)
        dict_time_schedule = {
            '0.0': '0.5',
            f'{t_PC_off - 1.000}': '0.100',
            f'{t_PC_off - 0.100}': '0.010',
            f'{t_PC_off - 0.010}': '0.001',
            f'{t_PC_off - 0.001}': '0.0001',
            f'{t_PC_off + 0.020}': '0.001',
            f'{t_PC_off + 1.000}': '0.010',
            f'{t_PC_off + 3.000}': '0.500'
        }
        #loop to write events
        for i in range(3):
            event_dict = dict()
            dI_dt = event.PoweredCircuits[circuit_name].dI_dt_at_discharge[i]
            dI_dt2 = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')[acceleration_list[i]])
            current_at_discharge = event.PoweredCircuits[circuit_name].current_at_discharge[i]
            if t_PC_off_list[i] < t_PC_off:
                t_start = t_PC_off - t_PC_off_list[i]
            else:
                t_start = 0
            I_start = 0.0  # hard-coded
            if dI_dt == 0:
                event_dict[f'GlobalParameters.global_parameters.I_end_1_PC{i+1}'] = current_at_discharge
                event_dict[f'GlobalParameters.global_parameters.I_end_2_PC{i+1}'] = 0.0
                t_plateau = event.PoweredCircuits[circuit_name].plateau_duration[i]
            elif np.sign(dI_dt) != np.sign(current_at_discharge):
                I_end_1 = 1.2*current_at_discharge
                I_end_2 = current_at_discharge
                event_dict[f'GlobalParameters.global_parameters.I_end_1_PC{i+1}'] = I_end_1
                event_dict[f'GlobalParameters.global_parameters.I_end_2_PC{i+1}'] = I_end_2
                event_dict[f'GlobalParameters.global_parameters.dI_dt_PC{i+1}'] = -dI_dt  # setting dI_dt
                event_dict[f'GlobalParameters.global_parameters.dI_dt2_PC{i+1}'] = dI_dt2  # setting dI_dt2
                t_plateau = 10  # hard-coded
            else:
                I_target = current_at_discharge + 100.0
                event_dict[f'GlobalParameters.global_parameters.dI_dt_PC{i+1}'] = dI_dt  #setting dI_dt
                event_dict[f'GlobalParameters.global_parameters.I_end_1_PC{i+1}'] = I_target
                event_dict[f'GlobalParameters.global_parameters.I_end_2_PC{i+1}'] = 0.0
                t_plateau = t_start + 2 * dI_dt / dI_dt2 + (I_target - I_start - dI_dt ** 2 / dI_dt2) / dI_dt

            event_dict[f'GlobalParameters.global_parameters.t_PC_off_PC{i+1}'] = t_PC_off
            event_dict['Analysis.simulation_time.time_end'] = t_PC_off + t_after_PC_off
            event_dict['Analysis.simulation_time.time_schedule'] = dict_time_schedule
            event_dict[f'GlobalParameters.global_parameters.I_start_PC{i+1}'] = I_start
            event_dict[f'GlobalParameters.global_parameters.t_start_PC{i+1}'] = t_start
            event_dict[f'GlobalParameters.global_parameters.t_plateau_PC{i + 1}'] = t_plateau
            list.append(event_dict)

        event.PoweredCircuits[circuit_name].delta_t_FGC_PIC = t_PC_off
        return list

    def __write_IPQ(self, event: DataEventCircuit, t_after_PC_off: float = 10.0):
        """
        Extract the information for an event of circuit type IPQ.

        Parameters:
            event (DataEventCircuit): The data event object to read the data.

        Returns:
            list[dict]: A list of dictionaries containing the IPQ information.

        """
        circuit_name = event.GeneralParameters.name
        list= []
        t_PC_off_list = []
        acceleration_list = ["dI_dt2_PC1", "dI_dt2_PC2"]
        ramp_rate_list = ["dI_dt_PC1", "dI_dt_PC2"]

        #loop to calculate list of t_PC_off
        for i in range(2):
            #event_dict = dict()
            t_start = 0  # hard-coded
            I_start = 0.0  # hard-coded
            dI_dt2 = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')[acceleration_list[i]])  # read dI/dt2 from the STEAM model
            dI_dt = event.PoweredCircuits[circuit_name].dI_dt_at_discharge[i]

            current_at_discharge = event.PoweredCircuits[circuit_name].current_at_discharge[i]

            if dI_dt == 0:
                I_end = current_at_discharge
                dI_dt = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')[ramp_rate_list[i]])
                time_to_reach_I = self.__time_to_reach_I(I=I_end, dI_dt=dI_dt, dI_dt2=dI_dt2, I_start=I_start)
                t_plateau = event.PoweredCircuits[circuit_name].plateau_duration[i]
                t_PC_off = t_start + time_to_reach_I + t_plateau

            elif np.sign(dI_dt) != np.sign(current_at_discharge):
                I_end_1 = 1.2*current_at_discharge
                I_end_2 = current_at_discharge
                t_plateau = 10  # hard-coded
                t_PC_off = calculate_t_PC_off(t_start, I_start, [I_end_1, I_end_2], [-dI_dt, dI_dt], [dI_dt2, dI_dt2], [t_plateau, t_plateau], I_end_2)

            else:
                I_end = str(current_at_discharge) + " + 100.0"
                I_target = current_at_discharge + 100.0
                t_plateau = t_start + 2 * dI_dt / dI_dt2 + (I_target - I_start - dI_dt ** 2 / dI_dt2) / dI_dt
                t_PC_off = calculate_t_PC_off(t_start, I_start,  I_target, [dI_dt], [dI_dt2], [t_plateau], I_target - 100)

            t_PC_off_list.append(t_PC_off)

        t_PC_off = max(t_PC_off_list)
        dict_time_schedule = {
            '0.0': '0.5',
            f'{t_PC_off - 1.000}': '0.100',
            f'{t_PC_off - 0.100}': '0.010',
            f'{t_PC_off - 0.010}': '0.001',
            f'{t_PC_off - 0.001}': '0.0001',
            f'{t_PC_off + 0.020}': '0.001',
            f'{t_PC_off + 1.000}': '0.010',
            f'{t_PC_off + 3.000}': '0.500'
        }
        #loop to write events
        for i in range(2):
            event_dict = dict()
            dI_dt = event.PoweredCircuits[circuit_name].dI_dt_at_discharge[i]
            dI_dt2 = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')[acceleration_list[i]])
            current_at_discharge = event.PoweredCircuits[circuit_name].current_at_discharge[i]
            if t_PC_off_list[i] < t_PC_off:
                t_start = t_PC_off - t_PC_off_list[i]
            else:
                t_start = 0
            I_start = 0.0  # hard-coded
            if dI_dt == 0:
                event_dict[f'GlobalParameters.global_parameters.I_end_1_PC{i+1}'] = current_at_discharge
                event_dict[f'GlobalParameters.global_parameters.I_end_2_PC{i+1}'] = 0.0
                t_plateau = event.PoweredCircuits[circuit_name].plateau_duration[i]
            elif np.sign(dI_dt) != np.sign(current_at_discharge):
                I_end_1 = 1.2*current_at_discharge
                I_end_2 = current_at_discharge
                event_dict[f'GlobalParameters.global_parameters.I_end_1_PC{i+1}'] = I_end_1
                event_dict[f'GlobalParameters.global_parameters.I_end_2_PC{i+1}'] = I_end_2
                event_dict[f'GlobalParameters.global_parameters.dI_dt_PC{i+1}'] = -dI_dt  # setting dI_dt
                event_dict[f'GlobalParameters.global_parameters.dI_dt2_PC{i+1}'] = dI_dt2  # setting dI_dt2
                t_plateau = 10  # hard-coded
            else:
                I_target = current_at_discharge + 100.0
                event_dict[f'GlobalParameters.global_parameters.dI_dt_PC{i+1}'] = dI_dt  #setting dI_dt
                event_dict[f'GlobalParameters.global_parameters.I_end_1_PC{i+1}'] = I_target
                event_dict[f'GlobalParameters.global_parameters.I_end_2_PC{i+1}'] = 0.0
                t_plateau = t_start + 2 * dI_dt / dI_dt2 + (I_target - I_start - dI_dt ** 2 / dI_dt2) / dI_dt

            event_dict[f'GlobalParameters.global_parameters.t_PC_off_PC{i+1}'] = t_PC_off
            event_dict['Analysis.simulation_time.time_end'] = t_PC_off + t_after_PC_off
            event_dict['Analysis.simulation_time.time_schedule'] = dict_time_schedule
            event_dict[f'GlobalParameters.global_parameters.I_start_PC{i+1}'] = I_start
            event_dict[f'GlobalParameters.global_parameters.t_start_PC{i+1}'] = t_start
            event_dict[f'GlobalParameters.global_parameters.t_plateau_PC{i + 1}'] = t_plateau
            list.append(event_dict)

        event.PoweredCircuits[circuit_name].delta_t_FGC_PIC = t_PC_off
        return list

    def __write_600A_with_EE(self, event: DataEventCircuit, t_after_PC_off: float = 10.0):
        """
        Extract the information for an event of circuit type 600A with EE.

        Parameters:
            event (DataEventCircuit): The data event object to read the data.

        Returns:
            list[dict]: A list of dictionaries containing the RQ information.

        """
        circuit_name = event.GeneralParameters.name
        list= []
        t_EE_list = []
        t_PC_off_list = []
        event_dict = dict()
        t_start = 0  # hard-coded
        I_start = 0.0  # hard-coded
        dI_dt2 = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')['dI_dt2'])  # read dI/dt2 from the STEAM model
        dI_dt = event.PoweredCircuits[circuit_name].dI_dt_at_discharge
        current_at_discharge = event.PoweredCircuits[circuit_name].current_at_discharge
        t_PC_off = self.__handle_ramp_rate_cases(event, circuit_name, t_after_PC_off, t_start, I_start, dI_dt, dI_dt2, current_at_discharge, event_dict)
        t_PC_off_list.append(t_PC_off)
        event_dict['GlobalParameters.global_parameters.t_EE'] = t_PC_off + 0.008
        event.PoweredCircuits[circuit_name].delta_t_FGC_PIC = t_PC_off_list
        event.EnergyExtractionSystem[circuit_name].delta_t_EE_PIC = t_EE_list.append(t_PC_off + 0.008)

        list.append(event_dict)

        return list

    def __write_RB(self, event: DataEventCircuit, t_after_PC_off: float = 10.0):
        """
        Extract the information for an event of circuit type RB.

        Parameters:
            event (DataEventCircuit): The data event object to read the data.

        Returns:
            list[dict]: A list of dictionaries containing the RQ information.

        """
        circuit_name = event.GeneralParameters.name
        list= []
        event_dict = dict()
        t_start = 0  # hard-coded
        I_start = 0.0  # hard-coded
        dI_dt2 = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')['dI_dt2'])  # read dI/dt2 from the STEAM model
        dI_dt = event.PoweredCircuits[circuit_name].dI_dt_at_discharge
        current_at_discharge = event.PoweredCircuits[circuit_name].current_at_discharge
        t_PC_off = self.__handle_ramp_rate_cases(event, circuit_name, t_after_PC_off, t_start, I_start, dI_dt, dI_dt2, current_at_discharge, event_dict)
        event_dict['GlobalParameters.global_parameters.t_EE_1'] = t_PC_off + 0.005 # value to be confirmed for RB
        event_dict['GlobalParameters.global_parameters.t_EE_2'] = t_PC_off + 0.005
        event.PoweredCircuits[circuit_name].delta_t_FGC_PIC = t_PC_off
        event.EnergyExtractionSystem[circuit_name].delta_t_EE_PIC = [t_PC_off + 0.005]*2

        list.append(event_dict)

        return list

    def __handle_ramp_rate_cases(self, event: DataEventCircuit, circuit_name: str, t_after_PC_off: float, t_start: float, I_start: float, dI_dt: float, dI_dt2: float, current_at_discharge: float, event_dict: dict ):
        if dI_dt == 0:
            I_end = current_at_discharge
            dI_dt = float(rgetattr(self.ref_model.circuit_data, 'GlobalParameters.global_parameters')['dI_dt'])
            time_to_reach_I = self.__time_to_reach_I(I=I_end, dI_dt=dI_dt, dI_dt2=dI_dt2, I_start=I_start)
            t_plateau = event.PoweredCircuits[circuit_name].plateau_duration
            t_PC_off = t_start + time_to_reach_I + t_plateau
            event_dict['GlobalParameters.global_parameters.I_end_1'] = I_end
            event_dict['GlobalParameters.global_parameters.I_end_2'] = 0.0

        elif np.sign(dI_dt) != np.sign(current_at_discharge):
            I_end_1 = 1.2*current_at_discharge
            I_end_2 = current_at_discharge
            I_target = current_at_discharge + np.sign(current_at_discharge) * 100.0
            t_plateau = 10  # hard-coded
            t_PC_off = calculate_t_PC_off(t_start, I_start, [I_end_1, I_target], [-dI_dt, dI_dt], [dI_dt2, dI_dt2], [t_plateau, t_plateau], I_end_2)
            event_dict['GlobalParameters.global_parameters.I_end_1'] = I_end_1
            event_dict['GlobalParameters.global_parameters.I_end_2'] = I_end_2
            event_dict['GlobalParameters.global_parameters.dI_dt'] = -dI_dt  # setting dI_dt
            event_dict['GlobalParameters.global_parameters.dI_dt2'] = dI_dt2  # setting dI_dt2

        else:
            I_end = str(current_at_discharge) + " + 100.0"
            I_target = current_at_discharge + 100.0
            t_plateau = t_start + 2 * dI_dt / dI_dt2 + (I_target - I_start - dI_dt ** 2 / dI_dt2) / dI_dt
            t_PC_off = calculate_t_PC_off(t_start, I_start,  I_target, [dI_dt], [dI_dt2], [t_plateau], I_target - 100)
            event_dict['GlobalParameters.global_parameters.dI_dt'] = dI_dt  #setting dI_dt
            event_dict['GlobalParameters.global_parameters.I_end_1'] = I_target
            event_dict['GlobalParameters.global_parameters.I_end_2'] = 0.0

        dict_time_schedule = {
            '0.0': '0.5',
            f'{t_PC_off - 1.000}': '0.100',
            f'{t_PC_off - 0.100}': '0.010',
            f'{t_PC_off - 0.010}': '0.001',
            f'{t_PC_off - 0.001}': '0.0001',
            f'{t_PC_off + 0.020}': '0.001',
            f'{t_PC_off + 1.000}': '0.010',
            f'{t_PC_off + 3.000}': '0.500'
        }

        event_dict['GlobalParameters.global_parameters.I_start'] = I_start
        event_dict['GlobalParameters.global_parameters.t_start'] = t_start
        event_dict['GlobalParameters.global_parameters.t_plateau'] = t_plateau
        event_dict['GlobalParameters.global_parameters.t_PC_off'] = t_PC_off
        event_dict['Analysis.simulation_time.time_end'] = t_PC_off + t_after_PC_off
        event_dict['Analysis.simulation_time.time_schedule'] = dict_time_schedule

        return t_PC_off

    @staticmethod
    def __time_to_reach_I(I: float, dI_dt: float, dI_dt2: float, I_start: float):
        '''
        Calculate the time to reach a current assuming a parabolic, linear, and parabolic profile
        :return: time [s]
        '''
        t_parabolic = dI_dt / dI_dt2
        I_parabolic = 0.5 * dI_dt2 * t_parabolic**2
        t_linear = (I - I_start - 2*I_parabolic) / dI_dt
        return t_parabolic*2 + t_linear