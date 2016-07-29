import os
import json
import chalk
import click
import atexit
import platform
import socketserver

from lib.SensedClient import SensedClient


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
              help='Configuration file for this instance')
@click.option('--hosts', '-h', default=[],
              help='Host/port pairs to query. (host:port,host:post,...)')
@click.option('--interval', '-i', default=60,
              help='Request interval in seconds')
@click.option('--verbose', '-V', is_flag=True,
              help='Enable verbose output')
def senselog(config, hosts, interval, verbose):
    if config is None:
        if not hosts == []:
            hosts = [tuple(h.split(':')) for h in hosts.split(',')]
        cfg = {
            'debug': False,
            'hosts': [],
            'port': 3000,
            'interval': 60
        }
    else:
        cfg = load_config(fn=config)

        if 'debug' not in cfg:
            cfg['debug'] = False

        if 'hosts' not in cfg:
            cfg['hosts'] = []

        if 'interval' not in cfg:
            cfg['interval'] = 60

        cfg['hosts'] = [tuple(h) for h in cfg['hosts']]

    if cfg['debug']:
        verbose = True

    _debug(verbose, chalk.green, 'loaded config')

    _debug(verbose, chalk.blue, 'starting senselog server')
    client = SensedClient(cfg)

    @atexit.register
    def close():
        chalk.blue('shutting down')

    chalk.blue(':: senselog ready')

    client.run_meta()
    client.run_forever()

if __name__ == '__main__':
    senselog()
