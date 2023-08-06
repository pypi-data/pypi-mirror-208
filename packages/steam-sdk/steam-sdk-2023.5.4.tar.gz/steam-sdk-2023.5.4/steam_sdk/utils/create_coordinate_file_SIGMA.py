import pandas as pd

def create_coordinate_file(path_map2d, coordinate_file_path):
    """
    Creates a csv file with same coordinates as the map2d.

    :param path_map2d: Map2d file to read coordinates from
    :param coordinate_file_path: Path to csv filw to be created
    :return:
    """
    df = pd.read_csv(path_map2d, delim_whitespace=True)
    df_new = pd.DataFrame()
    df_new["X-POS/MM"] = df["X-POS/MM"].apply(lambda x: x / 1000)
    df_new["Y-POS/MM"] = df["Y-POS/MM"].apply(lambda x: x / 1000)
    df_new.to_csv(coordinate_file_path, header=None, index=False)