from os.path import isfile
from os.path import dirname

from .gbq_data import GBQDataset
from .kaggle_data import KaggleDataset
from .utils import create_dataset


version_file = '{}/version.txt'.format(dirname(__file__))

if isfile(version_file):
    with open(version_file) as version_file:
        __version__ = version_file.read().strip()

if __name__ == '__main__':
    print('Hello World')
