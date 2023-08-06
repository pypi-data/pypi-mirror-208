from ast import literal_eval
from configparser import ConfigParser
import os


__version__ = '1.0.0'


def apply(cfg):
    environ = {}
    # gunicorn.ini_config would be more consistent, but e.g. bash refuses
    # to work with dots in env var names.
    iniconfig = os.environ.pop('GUNICORN_INI_CONFIG', None)
    if iniconfig:
        environ.update(parse_inifile(iniconfig))
    environ.update(os.environ)

    for key, value in environ.items():
        if not key.startswith('gunicorn.'):
            continue
        key = key.replace('gunicorn.', '', 1)
        if '__literal__' in key:
            key = key.replace('__literal__', '')
            value = literal_eval(value)
        cfg[key] = value


def parse_inifile(config_url):
    filename, section = config_url.split('#')
    config = ConfigParser()
    config.read(filename)
    return dict(config.items(section))
