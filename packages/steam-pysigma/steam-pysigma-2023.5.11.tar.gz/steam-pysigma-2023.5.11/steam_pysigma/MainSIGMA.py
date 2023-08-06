import os
from pathlib import Path

from steam_pysigma.comsol.BuildComsolModel import BuildComsolModel
from steam_pysigma.data import DataSIGMA as dS
import yaml
from steam_pysigma.utils import Util
import logging


class MainSIGMA:
    """
        Class to generate SIGMA models
    """

    def __init__(self, input_file_path: str = None, input_coordinates_path=None, model_folder: str = None, path_to_results=None, dm=None,
                 system_settings: dict = None, bh_curve_database: str = None, verbose: bool = False):
        """

        :param input_file_path: path to input yaml file
        :param input_coordinates_path: path to file with coordinates to evaluate B_field
        :param model_folder: Output path of java files and mph model.
        :param path_to_results: location of comsol-generated results
        :param dm: data model
        :param system_settings: settings dict
        :param bh_curve_database: bh_curve_database: path to bh curve file
        :param verbose:
        """
        self.start_folder = os.getcwd()
        self.wrk_folder = model_folder

        logger = logging.getLogger()
        if verbose:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)

        self.settings = system_settings
        # Load yaml input file
        if not dm:
            self.dm = Util.FilesAndFolders.read_data_from_yaml(input_file_path, dS.DataSIGMA)
        else:
            self.dm = dm
        base_file_name = os.path.splitext(input_file_path)[0]
        self.sdm = Util.FilesAndFolders.read_data_from_yaml(f'{base_file_name}.set', dS.MultipoleSettings)
        self.roxie_data = Util.FilesAndFolders.read_data_from_yaml(f'{base_file_name}.geom', dS.SIGMAGeometry)

        BuildComsolModel(model_data=self.dm, input_conductor_params=self.sdm, settings=self.settings,
                         output_path=self.wrk_folder, path_to_results=path_to_results,
                         input_coordinates_path=input_coordinates_path, roxie_data=self.roxie_data,
                         bh_curve_database=bh_curve_database)


if __name__ == "__main__":
    # if len(sys.argv) < 4:
    #     mp = MainFiQuS(sys.argv[1], sys.argv[2])

    magnet = 'MQXA_SIGMA'
    yaml_file = f'{magnet}.yaml'
    output_folder = r"C:\Users\jlidholm\Git-projects\steam-pysigma\steam-pysigma"
    print(os.path.join(output_folder))
    system_settings_path = (Path.joinpath(Path(__file__).parent, "../steam_pysigma/settings.SYSTEM.yaml"))
    if Path.exists(system_settings_path):
        with open(system_settings_path, 'r') as stream:
            settings = yaml.safe_load(stream)
    sim_result = MainSIGMA(input_file_path=yaml_file,
                           system_settings=settings, model_folder=os.path.join(output_folder))
