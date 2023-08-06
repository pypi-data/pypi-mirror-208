import requests
import warnings
from urllib3.exceptions import ProtocolError, MaxRetryError

from tabulate import tabulate


__all__ = ["Europa"]

class Europa:
    def __init__(self, callisto=None, org=None):
        self.callisto = callisto
        self.org = org

    def get_labels(self, properties, labelmaps):
        labels = { key: [] for res in properties['responses'] for key in res }
        
        for res in properties['responses']:
            for key in res:
                labels[key].append(res[key][0])

        for key in labels:
            llist = []
            for i in range(len(labels[key])):
                llist.append(labelmaps[i][labels[key][i]])
            labels[key] = llist
        
        return labels

    def get_image_details(self, id):
        image_url = f'{self.callisto.host}/europa/api/v2/projects/{id}'

        try:
            response = requests.get(image_url, headers=self.callisto.headers)

            if response.status_code == 200:
                image = response.json()['image']
                return image['tiles'], image['geometry'], image['status']
            else:
                print(f'Image details cannot be retrieved')
                print(f'Image meta endpoint {image_url} returned with HTTP status code : {response.status_code}')
                return None, None, None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve image details: {exc}")
            return None, None, None
            
    def get_projects(self):
        if self.org:
            get_project_url = f'{self.callisto.host}/europa/api/v2/projects?orgId={self.org}'
        else:
            get_project_url = f"{self.callisto.host}/europa/api/v2/projects?search=&status=all&isPublic=true"
        try:
            response = requests.get(get_project_url, headers=self.callisto.headers)

            if response.status_code == 200:
                projects = response.json()['results']

                return projects
            else:
                print(f'All GeoEngine projects cannot be retrieved')
                print(f'Projects endpoint {get_project_url} returned with HTTP status code : {response.status_code}\n')
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve projects: {exc}")
            return None

    def get_project_details(self, id, verbose=True):
        if self.org:
            project_details_url = f'{self.callisto.host}/europa/api/v2/projects/{id}?orgId={self.org}'
        else:
            project_details_url = f"{self.callisto.host}/europa/api/v2/projects/{id}?search=&status=all&isPublic=true"

        try:
            response = requests.get(project_details_url, headers=self.callisto.headers)
        
            if response.status_code == 200:
                project = response.json()
                
                if verbose:
                    ignorelist = ['populateCounter', 'owner', 'createdAt', 'updatedAt', 'deteledAt', 'annotators']
                    print('\Project Details:\n')
                
                    for key in project.keys():
                        if key == 'questions':
                            print(key+' : \n')
                            for qstn in project[key]:
                                print('name : {}'.format(qstn['name']))
                                print('description : {}'.format(qstn['description']))
                                print('response options : {}'.format(qstn['responseOptions']))
                                print()
                        elif key not in ignorelist:
                            print('{} : {}'.format(key, project[key]))

                    print()
                return project
            else:
                print(f'Project details cannot be retrieved')
                print(f'Project details endpoint {project_details_url} returned with HTTP status code : {response.status_code}\n')
                return None 
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve project details: {exc}")
            return None
            
    # def export_annotations(self, id):
    #     export_url = f'{self.callisto.host}/europa/api/v2/projects/{id}/export'

    #     print(f'exporting annotations for task id : {id}')

    #     response = requests.post(export_url, headers=self.callisto.headers)

    #     if response.status_code != 200:
    #         print('cannot export annotations')
    #         print(f'export endpoint {export_url} returned with HTTP status code : {response.status_code}\n')
    #         return
    #     else:
    #         print('annotations export requested')

    
    def get_project_exports(self, id):
        if self.org:
            project_exports_url = f'{self.callisto.host}/europa/api/v2/projects/{id}/datasets?orgId={self.org}'
        else:
            project_exports_url = f"{self.callisto.host}/europa/api/v2/projects/{id}/datasets?search=&status=all&isPublic=true"

        try:
            response = requests.get(project_exports_url, headers=self.callisto.headers)

            if response.status_code == 200:
                exports = response.json()['results']
                exports = {export["name"]: export for export in exports}
                
                return exports
            else:
                print(f'All exports for GeoEngine project {id} cannot be retrieved')
                print(f'Exports endpoint {project_exports_url} returned with HTTP status code : {response.status_code}\n')
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve project exports: {exc}")
            return None
        
    def get_project_export_by_id(self, project_id, export_id):
        if self.org:
            project_export_url = f'{self.callisto.host}/europa/api/v2/projects/{project_id}/datasets/{export_id}?orgId={self.org}'
        else:
            project_export_url = f"{self.callisto.host}/europa/api/v2/projects/{project_id}/datasets/{export_id}?search=&status=all&isPublic=true"

        try:
            response = requests.get(project_export_url, headers=self.callisto.headers)

            if response.status_code == 200:
                export = response.json()
                return export
            else:
                print(f'Export {export_id} for GeoEngine project {project_id} cannot be retrieved')
                print(f'Exports endpoint {project_export_url} returned with HTTP status code : {response.status_code}\n')
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve project export: {exc}")
            return None
        
    def get_questions_of_project(self, project_id):
        project_questions_url = f'{self.callisto.host}/europa/api/v2/questions?projectId={project_id}&pageSzie=1000'

        try:
            response = requests.get(project_questions_url, headers=self.callisto.headers)

            if response.status_code == 200:
                export = response.json()
                return export
            else:
                print(f'Questions for GeoEngine project {project_id} cannot be retrieved')
                print(f'Questions endpoint {project_questions_url} returned with HTTP status code : {response.status_code}\n')
                return None
        except (ConnectionRefusedError, ProtocolError, MaxRetryError) as exc:
            warnings.warn("Network issue, cannot retrieve project questions: {exc}")
            return None