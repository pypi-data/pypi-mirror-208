import json
import requests 
import warnings
from urllib3.exceptions import ProtocolError, MaxRetryError

from tabulate import tabulate 


__all__ = ["Dione"]

class Dione:
    def __init__(self, callisto=None, org=None):
        self.callisto = callisto
        self.org = org

    def create_experiment(self, experiment):
        assert self.org, "No org slug passed"
        assert "projectId" in experiment, "No projectId given"
        assert experiment["projectId"], "No projectId given"
        assert "exportId" in experiment, "No exportId given"
        assert experiment["exportId"], "No exportId given"

        url = f'{self.callisto.host}/dione/api/v1/experiments?orgId={self.org}'
        try:
            response = requests.post(url=url, data=json.dumps(experiment), 
                                    headers=self.callisto.headers)

            if response.status_code == 200:
                experiment = response.json()['experiment']
                return experiment
            else:
                print (response.json())
                print ("Failed to create experiment")
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve experiments: {exc}")
            return None
    
    def update_experiment(self, experiment):
        assert self.org, "No org slug passed"
        assert isinstance(experiment, dict), "Experiment should be dictionary"
        assert experiment["id"], "No experiment id given"

        url = f"{self.callisto.host}/dione/api/v1/experiments/{experiment['id']}?orgId={self.org}"
        try:
            response = requests.put(url=url, data=json.dumps(experiment), 
                                 headers=self.callisto.headers)

            if response.status_code == 200:
                experiment = response.json()['experiment']
                return experiment
            else:
                print (response.json())
                print (f"Failed to update experiment {experiment['name']}")
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve experiment: {exc}")
            None

    def get_experiments(self, projectId):
        assert self.org, "No org slug passed"
        assert projectId, "No projectId given"

        get_experiment_url = f'{self.callisto.host}/dione/api/v1/experiments?orgId={self.org}&projectId={projectId}&perPage=1000'
        try:
            response = requests.get(get_experiment_url, headers=self.callisto.headers)

            if response.status_code == 200:
                experiments = response.json()['results']

                return experiments
            else:
                print(f'All experiments for GeoEngine project {projectId} cannot be retrieved')
                print(f'Experiments endpoint {get_experiment_url} returned with HTTP status code : {response.status_code}\n')

                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve experiments: {exc}")
            return None 
        
    def get_experiment_by_name(self, projectId, experiment_name):
        assert self.org, "No org slug passed"
        assert projectId, "No projectId given"
        assert experiment_name, "No experiment name given"

        get_experiment_url = f'{self.callisto.host}/dione/api/v1/experiments?orgId={self.org}&projectId={projectId}&experiment_name={experiment_name}'
        try:
            response = requests.get(get_experiment_url, headers=self.callisto.headers)

            if response.status_code == 200:
                experiment = response.json()['results'][0]
                return experiment
            else:
                print(f'Experiment {experiment_name} for GeoEngine project {projectId} cannot be retrieved')
                print(f'Experiments endpoint {get_experiment_url} returned with HTTP status code : {response.status_code}\n')
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve experiment: {exc}")
            None

    def create_artifact(self, artifact):
        assert self.org, "No org slug passed"
        assert artifact, "No artifact passed"

        url = f'{self.callisto.host}/dione/api/v1/artifacts?orgId={self.org}'
        try:
            response = requests.post(url=url, data=json.dumps(artifact), 
                                    headers=self.callisto.headers)

            if response.status_code == 200:
                artifact_id = response.json()["artifact"]["id"]
                return artifact_id
            else:
                print ("Failed to create artifact")
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot create artifact: {exc}")
            return None
        
    def send_heartbeat(self, experimentId):
        url = f'{self.callisto.host}/dione/api/v1/experiments/{experimentId}?orgId={self.org}'

        try:
            response = requests.patch(url=url, data={}, headers=self.callisto.headers)

            if response.status_code == 200:
                experiment_status = response.json()["experiment"]["status"]
                return experiment_status
            else:
                print ("Failed to send heartbeat")
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot send heartbeat: {exc}")
            return None