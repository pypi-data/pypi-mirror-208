#!/usr/bin/env python3
import os
import shutil
import open_data_project
import argparse
import subprocess
import copy


def odp(command, project):
    command(project)

def create(project_dir):

    # Create a new project directory with the specified name
    os.mkdir(project_dir)

    od_bods_dir = f"{project_dir}/od_bods"
    os.mkdir(od_bods_dir)

    create_back_end(od_bods_dir)
    create_front_end(project_dir)

def create_back_end(back_end_dir):
    # Get the path of your package directory
    package_path = os.path.dirname(open_data_project.__file__)
    
    # Copy all files and folders from your package directory to the new project directory
    for item in os.listdir(package_path):
        item_path = os.path.join(package_path, item)
        if os.path.isfile(item_path) and item != "odp.py":
            shutil.copy(item_path, back_end_dir)
        elif os.path.isdir(item_path) and item != "__pycache__":
            shutil.copytree(item_path, os.path.join(back_end_dir, item), ignore=shutil.ignore_patterns("__pycache__"))

def create_front_end(projectdir):
    subprocess.run(["gem", "install", "jkan_odp"], cwd = f"{projectdir}", shell=True)
    subprocess.run(["jkan_odp", "new", "jkan"], cwd = f"{projectdir}", shell=True)

def run(project_main_file):
    subprocess.run(f"{project_main_file}.sh", shell=True)

def main():
    # Create a new argument parser
    parser = argparse.ArgumentParser(description='Create a new project from the package template directory')

    # Add an argument for the project name
    parser.add_argument('command', help='The name of the function to run')
    parser.add_argument('project_name', help='The name of the project to create')

    # Parse the arguments
    args = parser.parse_args()

    # Call the create_project() function with the project name argument
    if args.command == "create":
        command = copy.copy(create)
        odp(command, args.project_name)
    elif args.command == "run":
        command = copy.copy(run)
        odp(command, args.project_name)
