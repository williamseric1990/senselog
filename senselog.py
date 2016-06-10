import os
import msgpack
import chalk
import click
import atexit
import platform

from lib import SenselogServer


def _debug(verbose, f, arg):
    if verbose:
        f(arg)


# Finds a config file in a number of default locations in a
# Linux/Unix environment. Checks in the following places:
#  1. /etc/sensed/
#  2. .
def find_config_posix():
    if os.path.isfile('/etc/sensed/config.json'):
        return '/etc/sensed/config.json'
    elif os.path.isfile('./config.json'):
        return './config.json'
    return None


# Finds a config file in a number of default locations in a
# Windows environment. Checks in the following places:
#  1. %APPDATA%\sensed\
#  2. .
def find_config_windows():
    if os.path.isfile(os.path.join(os.getenv('APPDATA'),
                      'sensed', 'config.json')):
        return os.path.join(os.getenv('APPDATA'), 'sensed', 'config',
                            'config.json')
    elif os.path.isfile('./config.json'):
        return './config.json'
    return None


# Wrapper for the above two functions that will select
# the proper one automatically.
def find_config():
    if platform.system() == 'Windows':
        return find_config_windows()
    return find_config_posix()


def load_config(fn=None):
    f = fn or find_config()
    with open(f, 'r') as fp:
        config = json.loads(fp.read())
        return config
    return None


@click.command()
@click.option('--config', '-c', default=None,
              help='Configuration file for this instance.')
@click.option('--verbose', '-V', is_flag=True,
              help='Enable verbose output')
def senselog(config, verbose):
    if config is None:
        cfg = {
            'request_interval': 60,
            'timezone': 'America/New_York',
            'debug': False
        }
    else:
        cfg = load_config(fn=config)

        if 'debug' not in cfg:
            cfg['debug'] = False

        if 'timezone' not in cfg:
            cfg['timezone'] = 'America/New_York'

        if 'request_interval' not in cfg:
            cfg['request_interval'] = 60

    if cfg['debug']:
        verbose = True

    _debug(verbose, chalk.green, 'loaded config')

    _debug(verbose, chalk.blue, 'starting senselog server')
    server = SenselogServer(cfg)

    @atexit.register
    def close():
        chalk.blue('shutting down')
        server.shutdown()

    chalk.blue('senselog ready')

if __name__ == '__main__':
    senselog()
