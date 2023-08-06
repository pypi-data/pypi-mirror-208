import os
import click
import json
import getpass

from colorama import init
from colorama import Fore, Style

from engine.connections import Callisto
from engine.libs.inquirer import text


@click.command()
@click.option('--host', required=False, type=str, 
                default='https://api.granular.ai', 
                help='Platform root address')
@click.option('--relogin', required=False, is_flag=True)
def login(host, relogin):
    """Login on GeoEngine platform

    Examples:

    \b
    $ engine login 
    """
    if host:
        if "https://" not in host:
            host = "https://" + host

    callisto = Callisto()
    if not relogin and callisto.user:
        print (Fore.GREEN + callisto.user['email'] + Style.RESET_ALL + 
              " already logged in.")
        print ("Use " + Fore.YELLOW + "engine login --relogin" +  
                Style.RESET_ALL + " to login from a different account.")
    else:
        email = text(message="Email")
        password = getpass.getpass()

        callisto = Callisto(email=email, password=password, host=host)
        if callisto.user:
            print (Fore.GREEN + callisto.user['email'] + Style.RESET_ALL + 
                   " successfully logged on " + Fore.CYAN + callisto.host + 
                   Style.RESET_ALL)
 
@click.command()
def logout():
    """Logout from GeoEngine platform

    Examples:

    \b
    $ engine logout 
    """
    callisto = Callisto()
    if callisto.user:
        callisto.logout()
        if not callisto.user:
            click.echo("Logged out.")
    else:
        click.echo("Not signed in.")