import os
import click
import json
from appdirs import user_config_dir

from engine import __version__ as version

from .auth import login, logout
from .project import projects 
from .experiment import experiments


@click.group()
@click.version_option(version, message='%(version)s')
def cli():
    config_dir = user_config_dir('engine')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(os.path.join(config_dir, "config.json")):
        fout = open(os.path.join(config_dir, "config.json"), "w")
        json.dump({"host": 'https://api.granular.ai',
                    "org":  None, 
                   "email": None}, fout)
        fout.close()



cli.add_command(login)
cli.add_command(logout)
cli.add_command(projects)
cli.add_command(experiments)


if __name__ == "__main__":
    init(autoreset = True, warp = False) 
    cli()
