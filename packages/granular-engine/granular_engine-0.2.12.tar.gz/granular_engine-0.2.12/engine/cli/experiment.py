import click 

from InquirerPy.base.control import Choice
from InquirerPy.utils import color_print

from colorama import Fore, Style

from engine.connections import Callisto, Dione, Europa
from engine.libs.inquirer import select, confirm, filepath


@click.group()
@click.pass_context
def experiment(ctx):
    if ctx.invoked_subcommand is None:
        click.echo('Preparing GeoEngine project for training')

@experiment.command()
@click.option('--org', required=True, type=str, default=None,
              help='Organization to which the project belongs')
@click.option('--project', required=True, type=str, 
              help='Project for which experiments to show')
@click.option('--name', required=False, type=str, default=None,
              help='Get this experiment detail.')
def experiments(org, project, name):
    """List all the experiments available for a project in GeoEngine

    Examples:

    \b
    $ engine experiments --project=PROJECT_NAME --org=ORG_SLUG [Optional]
    """
    assert org, "Please provide an org slug!"

    callisto = Callisto()
    if org:
        org_id = callisto.get_org_id_from_slug(org_slug=org)
        if org_id:
            europa = Europa(callisto, org_id)
            dione = Dione(callisto, org_id)
        else:
            print (Fore.RED + org + Style.RESET_ALL + 
              " does not exist or you do not have access.")
            return
    
    projects = europa.get_projects()
    project_found = None
    for this_project in projects:
        if this_project['name'] == project:
            project_found = this_project
            break
    
    if not project_found:
        print (Fore.RED + project + Style.RESET_ALL + 
              " project does not exist.")
        return 
    
    experiments = dione.get_experiments(projectId=project_found["id"])
    if not name:
        print (Fore.GREEN + str(len(experiments)) + Style.RESET_ALL + 
                " experiments found.")
        experiment_choices = []
        for experiment in experiments:
            name = experiment['name']
            if experiment["bestModel"]:
                name += " [Best]"

            experiment_choices.append(Choice(experiment, name=name))

        experiment_found = select(
            message="Please select an experiment",
            choices=experiment_choices,
            qmark="\U0001F3E2",
            amark="\U0001F3E2"
        )
        print ()
        show_detail = confirm(
            message=f"Do you want to see {experiment_found['name']} details?",
            qmark="\U0001F4C2",
            amark="\U0001F4C2"
        )
    else:
        experiment_found = dione.get_experiment_by_name(projectId=project_found["id"],
                                                        experiment_name=name)
        if not experiment_found:
            print (Fore.RED + name + Style.RESET_ALL + 
              " experiment does not exist.")
            return
        else:
            show_detail = True
    
    if show_detail:
        if experiment_found["description"]:
            print (Fore.WHITE + "Description : " + Style.RESET_ALL, end="")
            print (Fore.GREEN + experiment_found['description'] + Style.RESET_ALL)

        if experiment_found["tags"]:
            print (Fore.WHITE + "Tags : " + Style.RESET_ALL, end="")
            print (Fore.GREEN + ', '.join(experiment_found["tags"]) + Style.RESET_ALL)

        if experiment_found["summary"]: 
            print ("------------------------------------------------")
            print (Fore.WHITE + "Experiment Summary" + Style.RESET_ALL)
            for k, v in experiment_found['summary'].items():
                print (Fore.WHITE + str(k) + " : " + Fore.CYAN + str(v) + Style.RESET_ALL)
            print ("------------------------------------------------")

        if experiment_found["experimentUrl"]:
            print (Fore.YELLOW + "Experiment Files Location : " + Style.RESET_ALL, end="")
            print (Fore.CYAN + experiment_found['experimentUrl'] + Style.RESET_ALL)
        
    print ()