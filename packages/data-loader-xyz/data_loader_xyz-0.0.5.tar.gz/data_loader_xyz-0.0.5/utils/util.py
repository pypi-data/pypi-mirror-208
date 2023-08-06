from functools import wraps


def get_config_section(config_file_path, section, value):
    import configparser
    from configs import base_config
    config = configparser.ConfigParser()
    config.read(config_file_path)
    return base_config.project_empl + config[section][value]


def read_json_data(json_file, param):
    import json
    f = open(json_file)
    variables = json.load(f)
    return variables[param]


def read_csv_data(json_file, delimiter=','):
    import csv
    f = open(json_file)
    data = csv.reader(f, delimiter)
    return data


def read_yaml_data(yaml_file):
    import yaml
    from yaml.loader import SafeLoader

    f = open(yaml_file)
    data = yaml.load(f, Loader=SafeLoader)
    return data


def no_except(func):
    def _main(*args):
        try:
            return func(*args)
        except:
            pass

    return _main


def get_log(func):
    import logging
    import logging.config
    import os

    project_empl = os.path.abspath(os.curdir)
    project_name = project_empl.rsplit('/', 1)[1]

    log_format = '%(asctime)s;%(filename)s;%(message)s;%(name)s;%(levelname)s'

    isExist = os.path.exists("/tmp/{}/".format(project_name))
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs("/tmp/{}/".format(project_name))

    logs_file_path = "/tmp/{}/logs.log".format(project_name)

    logging.basicConfig(filename=logs_file_path, format=log_format, encoding='utf-8', level=logging.DEBUG)

    @wraps(func)
    def _main(*args):
        try:
            fonc = func(*args)
            logging.info("Execution sucess")
            return fonc
        except Exception as e:
            logging.warning("Execution error :\n{}".format(e))

    return _main
