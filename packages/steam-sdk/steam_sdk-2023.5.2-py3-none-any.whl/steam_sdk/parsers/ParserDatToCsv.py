import pandas as pd
import os




def convert_dat_folder_to_csv(folder_path, skiprows=1):
    """
    Function that correctly converts all .dat files in a folder to csv files.

    Args:
        folder_path (str): The path to the folder containing the .dat files.
        skiprows (int, optional): The number of rows to skip when reading the dat file. Defaults to 1.
    """

    # Loop through all files in the folder with .dat extension
    for filename in os.listdir(folder_path):
        if filename.endswith(".dat"):
            # Read the file into a DataFrame
            path = os.path.join(folder_path, filename)
            df = pd.read_csv(path, sep='\t', skiprows=skiprows)

            # Save the DataFrame to a CSV file
            new_path = os.path.join(folder_path, filename.replace(".dat", ".csv"))
            df.to_csv(new_path, index=False)

# example use
folder_path = r"\\eosproject-smb\eos\project\s\steam\measurement_database\MCDXF11"
convert_dat_folder_to_csv(folder_path)

