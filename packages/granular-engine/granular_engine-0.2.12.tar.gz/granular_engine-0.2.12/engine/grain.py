import os
import warnings
import ctypes
import yaml
import threading
import time
from datetime import datetime

from engine.connections import Callisto, Europa, Dione


__all__ = ["Engine"]

class Engine():
    def __init__(self, yaml_file=None, **kwargs):
        if yaml_file:
            fp = open(yaml_file, 'r')
            meta = dict(yaml.safe_load(fp.read()))
        else:
            meta = kwargs
        assert "org" in meta, "Please provide organization slug"
        assert "projectId" in meta, "No GeoEngine projectId passed"
        assert "exportId" in meta, f"No exportId for GeoEngine project {meta['projectId']} passed"

        self.callisto = Callisto()
        self.org_id = self.callisto.get_org_id_from_slug(org_slug=meta['org'])
        self.europa = Europa(self.callisto, self.org_id)
        project = self.europa.get_project_details(id=meta['projectId'], verbose=False)
        if 'projectName' in meta:
            if project['name'] != meta['projectName']:
                warnings.warn(f"{meta['projectName']} is either wrong or has been updated to {project['name']} on GeoEngine!")

        export = self.europa.get_project_export_by_id(project_id=meta['projectId'],
                                                       export_id=meta['exportId'])
        if 'exportName' in meta:
            if export['name'] != meta['exportName']:
                warnings.warn(f"{project['name']}'s export {meta['exportName']} is either wrong or has been updated to {export['name']} on GeoEngine!")

        assert "bucketPath" in project, "No bucketPath in the project"

        self.meta = meta

        if 'logsDir' not in meta:
            meta['logsDir'] = 'logs'
        elif meta['logsDir'] == '':
            meta['logsDir'] = 'logs'
        if 'weightsDir' not in meta:
            meta['weightsDir'] = 'weights'
        elif meta['weightsDir'] == '':
            meta['weightsDir'] = 'weights'

        if not os.path.exists(meta['logsDir']):
            os.makedirs(meta['logsDir'])
        if not os.path.exists(meta['weightsDir']):
            os.makedirs(meta['weightsDir'])

        proper_meta = {}
        proper = ['metaInfo', 'description', 'tags', 
                  'exportId', 'projectId', 'gitUrl', 
                  'framework', 'params', 'inputs',
                  'outputs', 'readme']
        for k in meta.keys():
            if k in proper:
                proper_meta[k] = meta[k] or ''

         # Register the experiment on dione
        self.dione = Dione(self.callisto, self.org_id)
        experiment = self.dione.create_experiment(proper_meta)
        if experiment:
            self.experiment = experiment
        else:
            raise ValueError('Cannot create experiment on GeoEngine!') 

        meta['experimentUrl'] = f"{project['bucketPath']}/experiments/{self.experiment['name']}_{self.experiment['id']}"
        self.experiment['experimentUrl'] = meta['experimentUrl']

        experiment = self.dione.update_experiment(self.experiment)
        if experiment:
            self.experiment = experiment
        else:
            raise ValueError(f"Cannot update this experiment on GeoEngine!")

        self._exit_flag = False

        self._heartbeat_thread = threading.Thread(target=self._heartbeat)
        self._heartbeat_thread.daemon = True 
        self._heartbeat_thread.start()
    
    def _heartbeat(self):
        while True:
            if self._exit_flag:
                return
  
            _ = self.dione.send_heartbeat(self.experiment["id"])

            # TODO: experiment status can be used to stop an experiment from UI side by ckecking the status

            time.sleep(5)

    def log(self, step, best=False, checkpoint_path=None, **kwargs):
        artifact = {"experimentId": self.experiment['id'],
                    "metadata": kwargs,
                    "step": step}
        if checkpoint_path:
            dst_state_path = f"{self.meta['experimentUrl']}/weights/"
            os.system(f"gsutil rsync {checkpoint_path} {dst_state_path} 2> /dev/null")
            artifact["metadata"]["checkpoint"] = f"{dst_state_path}{checkpoint_path.split('/')[-1]}"
            
            if best:
                self.experiment["bestModel"] = artifact["metadata"]["checkpoint"]
                experiment = self.dione.update_experiment(self.experiment)
                if experiment:
                    self.experiment = experiment

        # Register the artifact on dione 
        artifact = self.dione.create_artifact(artifact)

    def done(self):
        self.experiment["status"] = "success"
        experiment = self.dione.update_experiment(self.experiment)
        if experiment:
            self.experiment = experiment

        self._exit_flag = True