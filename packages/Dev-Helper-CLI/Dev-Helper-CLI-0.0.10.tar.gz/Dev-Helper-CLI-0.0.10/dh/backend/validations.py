import re

def validate_list_input(namespace:str) -> list:
    if namespace == "default":
        return []
    if "." not in namespace:
        return [namespace]
    if re.match(r'^[a-z]+\.[a-z]+$', namespace) is not None:
        return namespace.split(".")
    return []

def validate_add_input(project:str, name:str):
    if not project.islower() and not project.isalpha(): 
        return False, """Project names must be lowercase 
        and only include alphabetical characters.""",
    if len(project) > 8:
        return False, """Project names can't exceed 8 
        characters in length."""
    if not name.islower() and not name.isalpha():
        return False, """Shortcut command names must be 
        lowercase and only include alphabetical characters."""
    return True, "Valid inputs."

def validate_delete_input(project:str):
    if project is None:
        raise ValueError("Provide a project name to delete.")
    return True

def validate_update_input(project:str, name:str, command:str):
    if project is None and name is None and command is None:
        raise ValueError(
        "Please provide the project and shortcut to update")
    return True

def validate_run_input(name:str):
    if name is None:
        raise ValueError(
        "Please provide a shortcut name.")
    return