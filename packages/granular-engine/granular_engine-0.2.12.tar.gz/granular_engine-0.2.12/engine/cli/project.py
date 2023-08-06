import os
import yaml
import click 
import json
import pprint
import re
from InquirerPy.base.control import Choice
from InquirerPy.utils import color_print

from yapf.yapflib.yapf_api import FormatCode

from colorama import Fore, Style

from engine.connections import Callisto, Europa, Neso
from engine.libs.inquirer import select, confirm, filepath, dirpath
from engine.libs.config import get_pyconfig_string 

from .auth import login 


@click.command()
def projects():
    """List all the project available in GeoEngine

    Examples:

    \b
    $ engine projects
    """
    callisto = Callisto()
    choose_public_private = select(
        message="Which type of projects do you want to see?",
        choices=["Open-Source", "From my organization"],
        qmark="\U0001F310",
        amark="\U0001F310"
    )
    print ()
    org = None
    if choose_public_private == "From my organization":
        if not callisto.user:
            print ("You are not logged in. Please login using " + Fore.CYAN + "engine login" + Style.RESET_ALL)
            return

        orgs = callisto.get_orgs()
        org_choices = [Choice(org, name=org["name"]) for org in orgs]
        org = select(
            message="Please select an organization",
            choices=org_choices,
            qmark="\U0001F3E2",
            amark="\U0001F3E2"
        )
        print ()

    if org:
        europa = Europa(callisto, org["id"])
    else:
        europa = Europa(callisto)
    
    projects = europa.get_projects()
    project_choices = [Choice(project, name=project["name"]) for project in projects]
    project = select(
        message="Please select a project",
        choices=project_choices,
        qmark="\U0001F4C1",
        amark="\U0001F4C1"
    )
    questions = europa.get_questions_of_project(project["id"])
    print ()

    show_detail = confirm(
        message=f"Do you want to see {project['name']} details?",
        qmark="\U0001F4C2",
        amark="\U0001F4C2"
       )

    if show_detail:
        
        if project["description"]:
            print (Fore.GREEN + "Description : " + Style.RESET_ALL, end="")
            print (Fore.GREEN + project['description'] + Style.RESET_ALL)

        if project["sensorIds"]:
            if org:
                neso = Neso(callisto, org["id"])
            else:
                neso = Neso(callisto, None)
            sensor_ids = project['sensorIds']
            sensors = neso.get_sensors()
            
            sensor_names = [sensors[sensor_id]["name"] for sensor_id in sensor_ids if sensor_id in sensors]

            if len(sensor_names):
                print (Fore.GREEN + "Sensors : " + Style.RESET_ALL, end="")
                print (Fore.GREEN + ', '.join(sensor_names) + Style.RESET_ALL)

        if project["problemTypes"]:
            print (Fore.GREEN + "Problem Type : " + Style.RESET_ALL, end="")
            print (Fore.GREEN + ', '.join(project['problemTypes']) + Style.RESET_ALL)
        
        if project["bibtex"]:
            print (Fore.MAGENTA + project['bibtex'] + Style.RESET_ALL)

    print ()

    show_exports = confirm(
        message=f"Do you want to see {project['name']} exports?",
        qmark="\U0001F6A7",
        amark="\U0001F6A7"
       )
    print ()

    if show_exports:
        if org:
            europa = Europa(callisto, org['id'])
        else:
            europa = Europa(callisto)
        exports = europa.get_project_exports(project["id"])

        export_choices = []
        for _, export in exports.items():
            if export['status'] == 'completed':
                choice = f"{export['name']} has "
                formats = export['formats']
                if len(formats) > 2:
                    choice += f"{', '.join(formats[:-1])}, and {str(formats[-1])} formats"
                elif len(formats) == 2:
                    choice += f"{' and '.join(formats)} fromats"
                elif len(formats) == 1:
                    choice += f"{formats[0]} format" 
                if export['designated']:
                    choice += f" and is a deisgnated export of {project['name']}"
                choice += "."
                export_choices.append(Choice(export, name=choice))

        export = select(
            message="Please select an export",
            choices=export_choices,
            qmark="\U0001F6A7",
            amark="\U0001F6A7"
            )
        print ()

        text = [("#B5B7B4", "Do you want to generate a geolibs experiment configuration for ")]
        if org:
            text += [("#3AB222", org['name']), ("#F7F7F7", "'s ")]
        text += [("#B4195D", project['name']),
                ("#B5B7B4", " with "),
                ("#B29822", export['name']),
                ("#B5B7B4", " export?")]
        color_print(text)
        
        if not callisto.user:
            print ()
            print ("You are not logged in. Engine library requires your organization information to generate experiment configuration file.")
            print ("Please login using " + Fore.CYAN + "engine login" + Style.RESET_ALL)
            return

        want_config = confirm(message="", qmark="\U0001F913", amark="\U0001F913")
        print ()

        if want_config:
            project_org = None
            orgs = callisto.get_orgs()
            for org in orgs:
                if project["orgId"] == org["id"]:
                    project_org = org
                    break
            if not project_org:
                click.echo("Please visit https://engine.granular.ai to clone the project.")
            else:
                question_choices = [Choice(question, name=question["name"]) for question in questions]
                question = select(
                            message="Please select a question",
                            choices=question_choices,
                            qmark="\U00002753",
                            amark="\U00002753"
                        )
                print ()

                vector_folder_name = export["metadataUrl"].split('/')[-2]
                config_url = None
                if question['problemType'] == 'imageClassification':
                    config_url = filepath(
                            message="This is a image classification task please go to https://github.com/open-mmlab/mmpretrain/tree/main/configs and find a suitable config file and paste its URL here: ",
                            qmark="\U0001F517",
                            amark="\U0001F517"
                            )
                    dataset_type = f"dataset_type = 'EngineCSV'\n"
                    vector_dir_path = f"vector_dir_path = 'vectors/{vector_folder_name}/CSV'\n"

                elif question['problemType'] == 'objectDetection':
                    config_url = filepath(
                            message="This is an object detection task please go to https://github.com/open-mmlab/mmyolo/tree/main/configs or https://github.com/open-mmlab/mmdetection/tree/main/configs and find a suitable config file and paste its URL here: ",
                            qmark="\U0001F517",
                            amark="\U0001F517"
                            )
                    dataset_type = f"dataset_type = 'EngineCocoExt'\n"
                    vector_dir_path = f"vector_dir_path = 'vectyors/{vector_folder_name}/COCO/'\n"
                    
                elif question['problemType'] == 'segmentation':
                    config_url = filepath(
                            message="This is an object detection task please go to https://github.com/open-mmlab/mmsegmentation/tree/main/configs and find a suitable config file and paste its URL here: ",
                            qmark="\U0001F517",
                            amark="\U0001F517"
                            )
                    dataset_type = f"dataset_type = 'EngineCocoExt'\n"
                    vector_dir_path = f"vector_dir_path = 'vectors/{vector_folder_name}/COCO/'\n"
                else:
                    print ("This problem type is not supported by geolibs. Please write custom config files.")
                    return 
                
                print ()

                if not config_url:
                    print ("No model config url passed.")
                    return
                
                config = {
                        "description": project["description"].replace('\n', ' ')[:100],
                        "org": project_org["slug"],
                        "exportName": export["name"],
                        "exportId": export["id"],
                        "projectName": project["name"],
                        "projectId": project["id"],
                        "tags": project["tags"]
                        }
                if question["name"]:
                    config["tags"].append(question["name"])
                if question["problemType"]:
                    config["tags"].append(question["problemType"])
                if question["questionType"]:
                    config["tags"].append(question["questionType"])
                if question["spatialScope"]:
                    config["tags"].append(question["spatialScope"])
                if question["temporalScope"]:
                    config["tags"].append(question["temporalScope"])
                if question["responseFormat"]:
                    config["tags"].append(question["responseFormat"])
                if question["tags"]:
                    config["tags"] += question["tags"]
                
                cfg_string = get_pyconfig_string(config_url)
                if question['problemType'] == 'segmentation':
                    cfg_string = cfg_string.replace('LoadAnnotations', 'LoadMasks')
                cfg_string = cfg_string.replace("'LoadImageFromFile'", "'LoadBandsFromFile', to_float32 = True")

                cfg_string = re.sub(r"num_classes=.*,\n", '', cfg_string)
                cfg_string = cfg_string.replace("head=dict(\n", "head=dict(\n\tnum_classes,\n")

                pp = pprint.PrettyPrinter(indent=4, width=100, compact=True)
                cfg_string = f"engine = {pp.pformat(config)}\n\n" + cfg_string + '\n\n'
                cfg_string = f"num_classes = {len(question['responseOptions'])}\n\n" + cfg_string
                cfg_string = f"class_title = '{question['name']}'\n" + cfg_string
                
                found = re.search("dataset_type.*\n", cfg_string)
                
                data_path = f"data_path='data/{project['name'].replace(' ', '_')}/'\n"
                raster_dir_path = f"raster_dir_path='rasters/raw/'\n"
                
                data_info = dataset_type + data_path + raster_dir_path + vector_dir_path + '\n'
                cfg_string = cfg_string.replace(found.group(0), data_info)

                cfg_string += "custom_hooks=[dict(type='EngineLoggerHook', " + \
                                            "init_kwargs=engine, by_epoch=True, " + \
                                            "interval=100)]"
                
                

                file_name = '_'.join(config_url.split('/')[-1].split('_')[:-1])

                save_path = dirpath(
                    message="Please enter location to save the experiment configuration file",
                    qmark="\U0001F4E9",
                    amark="\U0001F4E9"
                    )
                
                if save_path != '' and not os.path.exists(save_path):
                    print (f"{save_path} is not a valid directory.")
                    return
                        
                if '.py' not in save_path:
                    save_path = os.path.join(save_path, f"{file_name}.py")
                
                yapf_style = dict(
                    based_on_style='pep8',
                    blank_line_before_nested_class_or_def=True,
                    split_before_expression_after_opening_paren=True,
                    indent_dictionary_value=True)
                cfg_string, _ = FormatCode(cfg_string, style_config=yapf_style, verify=True)
                with open(save_path, 'w') as fout:
                    fout.write(cfg_string)
                    print ("Saved to " + Fore.GREEN + save_path + Style.RESET_ALL)

                print ()

                print ("You can use the config file using geolibs.")
                print (Fore.GREEN + f"python tools/train.py {save_path}" + Style.RESET_ALL)
                print ("\n")

        print ("You can download the dataset using following command. Please make sure it is inside data folder.")
        project_name = project['name'].replace(' ', '_')
        print (Fore.MAGENTA + f"mkdir data data/{project_name}")
        print (f"mkdir data/{project_name}/rasters data/{project_name}/vectors")
        print (f"gsutil -m cp -n -r {project['bucketPath']}/rasters/raw data/{project_name}/rasters/")
        print (f"gsutil -m cp -n -r {export['metadataUrl'].replace('metadata/json', '')} data/{project_name}/vectors/" + Style.RESET_ALL)
        print ()


    return