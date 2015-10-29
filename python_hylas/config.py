import os
import yaml

# Get the base directory of the project, relative to the current directory.
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, 'data')

config_file = os.path.join(BASE_PATH, 'config.yaml')

settings = {}
with open(config_file, 'r') as f:
    settings['general'] = yaml.load(f)
