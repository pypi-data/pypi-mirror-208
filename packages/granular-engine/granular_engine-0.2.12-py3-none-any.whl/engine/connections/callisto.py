import os 
import json 
import requests 
import click
import keyring
import warnings
from appdirs import user_config_dir 
from urllib3.exceptions import ProtocolError, MaxRetryError

from colorama import Back, Fore, Style


__all__ = ['Callisto']

class Callisto:
    def __init__(self, email=None, password=None,
                host=None):
        self.host = host
        self.email = email 
        self.password = password
        self.user = None
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.setup()

    def read_config(self):
        try:
            config_path = os.path.join(user_config_dir('engine'), "config.json")
            fin = open(config_path, 'r')
            config_data = json.load(fin)
            fin.close()

            if not self.host:
                self.host = config_data['host']
            if not self.email:
                self.email = config_data['email']
            if not self.password:
                try:
                    self.password = config_data['password']
                except:
                    self.password = keyring.get_password("engine", self.email)
            try:
                self.headers['Cookie'] = config_data['Cookie']
            except:
                self.headers['Cookie'] = keyring.get_password("engine-cookie", self.email)
        except:
            pass

    def update_config(self):
        config_path = os.path.join(user_config_dir('engine'), "config.json")
        fout = open(config_path, 'w')
        try:
            keyring.set_password("engine", self.email, self.password)
            keyring.set_password("engine-cookie", self.email, self.headers['Cookie'])

            json.dump({'host': self.host,
                        'email': self.email, 
                        'password': self.password, 
                        'cookie': self.headers['Cookie']
                        }, fout)
        except:
            json.dump({'host': self.host,
                        'email': self.email, 
                        'password': self.password, 
                        'Cookie': self.headers['Cookie']
                        }, fout)
        fout.close()
    
    def is_token_valid(self):
        response = requests.get(f'{self.host}/callisto/api/v1/users/me', headers=self.headers)
        if response.status_code == 200:
            return True 
        return False

    def login(self):
        login_url = f'{self.host}/callisto/auth/v1/login'
        data = {"email": self.email, "password": self.password}
        if 'Cookie' in self.headers:
            del self.headers['Cookie']

        try:
            response = requests.post(login_url, headers=self.headers, data=json.dumps(data))
            if response.status_code == 200:
                resdata = response.json()
                self.user = resdata["user"]
                auth_cookie = response.cookies["callisto_auth"]
                self.headers["Cookie"] = f"callisto_auth={auth_cookie}"
                self.update_config()
            else:
                print (Fore.RED  + 'Failed to authenticate' + Style.RESET_ALL)
                print ("Authentication endpoint " + Fore.CYAN + self.host + Style.RESET_ALL +
                    " returned with HTTP status code : " + Fore.RED + str(response.status_code) +
                    Style.RESET_ALL)
                print ("Please register at " + Fore.CYAN + "https://engine.granular.ai/register" + 
                        Style.RESET_ALL + " if you haven't")
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot login: {exc}")

    def logout(self):
        logout_url = f'{self.host}/callisto/auth/v1/logout'
        try:
            response = requests.post(logout_url, headers=self.headers)
            if response.status_code == 200:
                self.user = None
                self.email = None
                self.password = None
                self.headers['Cookie'] = None 
                self.update_config()
            else:
                print (Fore.RED  + 'Failed to logout' + Style.RESET_ALL)
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot logout: {exc}")

    def setup(self):
        self.read_config()
        if self.email and self.password:
            self.login()

    def get_user(self):
        if not self.user:
            url = f"{self.host}/callisto/api/v1/users/me"
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    self.user = response.json()
                else:
                    print (Fore.RED + 'Your user details cannot be retrieved' + Style.RESET_ALL)
                    return None
            except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
                warnings.warn("Network issue, cannot retrieve user info: {exc}")
                return None
        return self.user

    def get_org_id_from_slug(self, org_slug):
        url = f"{self.host}/callisto/api/v1/organizations/{org_slug}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                resdata = response.json()
                return resdata['id']
            else:
                print ("Organization slug " + Fore.RED + org_slug + Style.RESET_ALL + " not found")
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve org info: {exc}")
            return None
            
    def get_orgs(self):
        url = f"{self.host}/callisto/api/v1/organizations"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                orgs = response.json()
                return orgs
            else:
                click.echo(Fore.RED + 'No organizations found' + Style.RESET_ALL)
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve orgs: {exc}")
            return None