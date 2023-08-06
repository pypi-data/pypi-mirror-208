from InquirerPy import inquirer
from InquirerPy.validator import PathValidator

def select(choices, **kwargs):
    return inquirer.select(
        choices=choices,
        message=kwargs.get("message", "Please select"),
        instruction=kwargs.get("instruction", ""),
        multiselect=kwargs.get("multiselect", False),
        qmark=kwargs.get("qmark", ""),
        amark=kwargs.get("amark", ""),
        pointer=kwargs.get("pointer", "->"),
    ).execute()

def confirm(**kwargs):
    return inquirer.confirm(
        message=kwargs.get("message", ""),
        qmark=kwargs.get("qmark", ""),
        amark=kwargs.get("amark", ""),
        ).execute()

def filepath(message, **kwargs):
    return inquirer.filepath(
        message=message,
        qmark=kwargs.get("qmark", ""),
        amark=kwargs.get("amark", ""),
    ).execute()

def dirpath(message, **kwargs):
    return inquirer.filepath(
        message=message,
        qmark=kwargs.get("qmark", ""),
        amark=kwargs.get("amark", ""),
        only_directories=True,
    ).execute()

def text(message, **kwargs):
    return inquirer.text(
        message=message,
        qmark=kwargs.get("qmark", ""),
        amark=kwargs.get("amark", ""),
        ).execute()

def secret(message, **kwargs):
    return inquirer.secret(
        message=message,
        transformer=lambda _: "[hidden]",
        qmark=kwargs.get("qmark", ""),
        amark=kwargs.get("amark", ""),
    ).execute()