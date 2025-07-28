from typing import Any

from configparser import ConfigParser
import os

def get_relative_path(folder_location, file_name):
    return os.path.relpath(f"{os.getcwd()}/{folder_location}/{file_name}")

def get_relative_path_of_folder(folder_path_from_content_root):
    return os.path.relpath(f"{os.getcwd()}/{folder_path_from_content_root}")

def get_absolute_path(folder_location, file_name):
    return os.path.abspath(f"{os.getcwd()}/{folder_location}/{file_name}")

def get_config():
    path_to_ini_file = get_relative_path("src/configs", "settings.ini")
    config = ConfigParser()
    config.read(path_to_ini_file)
    return config

def get_test_environment():
    env: str = get_config()["ENV"]["dev"]
    return env

def get_job_name():
    job = get_config()["JOB"]["job_1"]
    return job
