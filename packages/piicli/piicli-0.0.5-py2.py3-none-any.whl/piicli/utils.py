import os
import yaml


def read_yaml(path):
    if not os.path.exists(path):
        raise Exception(f"{path} not found")
    with open(path, "r") as file:
        yaml_data = yaml.safe_load(file)
        return yaml_data


def write_yaml(path, yaml_data):
    with open(path, "w") as file:
        yaml.safe_dump(yaml_data, file)