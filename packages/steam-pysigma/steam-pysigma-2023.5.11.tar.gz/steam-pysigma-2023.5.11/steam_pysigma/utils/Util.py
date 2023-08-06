import logging
import pandas as pd
import ruamel.yaml
from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)


class FilesAndFolders:
    @staticmethod
    def read_data_from_yaml(full_file_path, data_class):
        with open(full_file_path, 'r') as stream:
            yaml = ruamel.yaml.YAML(typ='safe', pure=True)
            yaml_str = yaml.load(stream)
        return data_class(**yaml_str)

def displayWaitAndClose(waitTimeBeforeMessage: float, waitTimeAfterMessage: float = 0, flag_show_text: bool = True):
    """

        **Function useful in Pycharm tests; it allows closing plots after some time that they are displayed **

        Wait a certain time, display a message, and wait a certain time

        :param waitTimeBeforeMessage: Time to wait before the message [s]
        :type waitTimeBeforeMessage: float
        :param waitTimeAfterMessage: Time to wait after the message [s]
        :type waitTimeAfterMessage: float
        :return:


    """


    # Show plots in Pycharm, wait a certain time, alert time is up, and close the window
    plt.ion()
    plt.tight_layout()
    plt.show()
    plt.draw()
    plt.pause(waitTimeBeforeMessage)
    if flag_show_text == True:
        plt.title('Figure will close in {} seconds...'.format(waitTimeAfterMessage))
    plt.pause(waitTimeAfterMessage)

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