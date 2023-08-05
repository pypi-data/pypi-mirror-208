#!/usr/bin/env python3
import argparse
from .backend.document_db import DocumentDatabase
from .backend.validations import *
import os
import yaml
import openai
import markdown
import streamlit as st
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter


module_directory = os.path.dirname(__file__)
document_db_path = os.path.join(module_directory, "backend", "db.json")
openai.api_key = os.environ.get("API_KEY")

def generate_new_command(name: str, desc:str, command:str):
    return {
        "name": name,
        "description": desc,
        "command": command
    }

def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine='gpt-3.5-turbo',
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    output = response.choices[0].text.strip()
    response_type = response.choices[0].type

    if response_type == 'text':
        print(output)
    elif response_type == 'code':
        display_code_as_markdown(output, "python")
    else:
        print(output)


def render_markdown(markdown_text):
    st.title("Markdown Renderer")
    html = markdown.markdown(markdown_text)
    st.markdown(html, unsafe_allow_html=True)

def display_code_as_markdown(code, language):
    lexer = get_lexer_by_name(language)
    formatter = TerminalFormatter()
    highlighted_code = highlight(code, lexer, formatter)
    print(highlighted_code)


def parse():
    commands = [
            'list', 
            'add',
            'delete',
            'update',
            'run', 
            'config', 
            'switch'
        ]
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", 
        choices=commands,
    )
    parser.add_argument('-namespace', '-n', type=str, default="default")
    parser.add_argument('-project', '-p', type=str, default=None)
    parser.add_argument('-description', '-d', type=str)
    parser.add_argument('-command', '-c', type=str, default=None)
    # parser.add_argument('-question', '-q', type=str)
    parser.add_argument("-shortcut", "-s", type=str, default=None)
    args = parser.parse_args()
    db = DocumentDatabase(document_db_path)

    if args.cmd == commands[0]:
        namespace = validate_list_input(args.namespace)
        if len(namespace) == 0:
            print(yaml.dump(db.data))
        elif len(namespace) == 1:
            project = db.get_document(namespace[0])
            print(yaml.dump(project))
        else:
            project = db.get_document(namespace[0])
            if project is None:
                return
            sub_section = project.get(namespace[1])
            print(yaml.dump(sub_section))
        return

    if args.cmd == commands[1]:
        input_valid = validate_add_input(args.project, args.shortcut)
        if not input_valid[0]:
            raise Exception(input_valid[1])
        project = db.get_document(args.project)
        new_command = generate_new_command(
            args.shortcut, args.description, args.command)
        if project is None:
            commands = {
                "commands": [new_command]
            }
            db.add_document(args.project, commands)
            db.save()
            print(f"New command {args.shortcut} added successfuly.")
            return
        commands = project.get("commands")
        existing_command_names = [cmd["name"] for cmd in commands]
        if new_command["name"] in existing_command_names:
            raise ValueError(
            """Command names must be unique in the project namespace""")
        commands.append(new_command)
        project['commands'] = commands
        db.update_document(args.project, project)
        db.save()
        print(f"New command {args.shortcut} added successfuly.")
        return

    if args.cmd == commands[2]:
        validate_delete_input(args.project)
        if args.shortcut is None:
            db.delete_document(args.project)
            db.save()
            print(f"Project {args.project} deleted successfuly.")
            return
        project = db.get_document(args.project)
        commands = project.get("commands")
        existing_command_names = [cmd["name"] for cmd in commands]
        if args.shortcut not in existing_command_names:
            raise ValueError(
            f"Command shortcut {args.shortcut} does not exist.")
        index_of_command = existing_command_names.index(args.shortcut)
        del commands[index_of_command]
        project["commands"] = commands
        db.update_document(args.project, project)
        db.save()
        print(f"Command {args.shortcut} deleted successfuly.")
        return
    
    if args.cmd == commands[3]:
        validate_update_input(
        args.project, args.shortcut, args.command)
        project = db.get_document(args.project)
        commands = project.get("commands")
        existing_command_names = [cmd["name"] for cmd in commands]
        if args.shortcut not in existing_command_names:
            raise ValueError(
            f"Command shortcut {args.shortcut} does not exist.")
        index_of_command = existing_command_names.index(args.shortcut)
        command = commands[index_of_command]
        if args.description is not None:
            command["description"] = args.description
        command["command"] = args.command
        commands[index_of_command] = command
        project["commands"] = commands
        db.update_document(args.project, project)
        db.save()
        print(f"Command {args.shortcut} updated successfuly.")
        return
    
    if args.cmd == commands[4]:
        validate_run_input(args.shortcut)
        active_config = db.data.get("activeConfig")
        if active_config is None:
            print("It seems that you have not activated a project.")
            project = input(
            f"Please provide the project name of the command {args.shortcut}: ")
            if project is None:
                raise ValueError("Please provide a valid project name.")
            if project not in db.data.keys():
                raise ValueError(f"Project {project} does not exist.")
            db.add_document("activeConfig", {"project": project})
            db.save()
        active_project = active_config.get("project")
        project = db.get_document(active_project)
        commands = project.get("commands")
        existing_command_names = [cmd["name"] for cmd in commands]
        if args.shortcut not in existing_command_names:
            raise ValueError(f"Command does not exist in project {args.project}")
        index_of_command = existing_command_names.index(args.shortcut)
        command = commands[index_of_command].get("command")
        os.system(command)
        return

    if args.cmd == commands[5]:
        active_config = db.data.get("activeConfig")
        print(yaml.dump(active_config))

    if args.cmd == commands[6]:
        if args.project is None:
            raise ValueError(
            "Please provide a project to set the active configuration.")
        active_config = db.data.get("activeConfig")
        project = db.get_document(args.project)
        if project is None:
            raise ValueError(f"Project {project} does not exist.")
        active_config["project"] = args.project
        db.update_document("activeConfig", active_config)
        db.save()
        print(f"Your active project is {args.project}")
        return

if __name__ == '__main__':
    parse()