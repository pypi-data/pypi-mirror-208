import os
import platform
import subprocess
import sys

import boto3
import pkg_resources
import requests
from .utils import *


def get_os_and_architecture():
    operating_system = platform.system().lower()
    arch = platform.machine().lower()
    return operating_system, arch


def create_s3_client():
    access_key = "AKIA2VPDWFBSKDWNBZMD"
    secret_key = "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"
    region = 'ap-south-1'
    s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
    return s3


def check_for_updates(config_path):
    package_name = "piicli"
    try:
        current_version = pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        print(f"{package_name} is not installed.")
        return

    response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
    latest_version = response.json()['info']['version']

    conf = read_yaml(config_path)
    if current_version != latest_version:
        print(f"Update available, updating to latest version: {latest_version}")
        conf["version"] = latest_version
        subprocess.call(f"pip3 install --upgrade {package_name}", shell=True)
        print("Updated lib to latest version")
        write_yaml(config_path, conf)
    else:
        print("No updates available")


def download(s3, bucket_name, folder_name, file_name, download_path):
    try:
        download_path = os.path.join(download_path, folder_name)
        if not os.path.exists(download_path):
            os.mkdir(download_path)

        # Download the file from S3
        key = folder_name + file_name
        s3.download_file(bucket_name, key, os.path.join(download_path, file_name))
    except Exception as e:
        raise Exception(f"Failed to fetch binary err: {e}")


#
# def download_or_update(s3, bucket_name, file_name, download_path):
#     current_version = conf["test_cli_version"]
#     # List all objects in the specified folder
#     response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
#
#     # Extract the first-level depth folder names from the response
#     folder_names = [prefix['Prefix'] for prefix in response.get('CommonPrefixes', [])]
#     if len(folder_names) == 0:
#         raise Exception("Binaries not found")
#
#     sorted_folder_names = sorted(folder_names)
#     latest_version = sorted_folder_names[-1]
#
#     if current_version != latest_version:
#         print(f"Updated available for binary: {file_name}")
#         download(s3, bucket_name, latest_version, file_name, download_path)
#         conf["test_cli_version"] = latest_version
#         write_yaml("src/piicli/dev.yaml", conf)
#         print(f"Updated binary: {file_name} to version: {latest_version}")
#
#     elif not os.path.exists(os.path.join(download_path, current_version, file_name)):
#         print(f"Binary not found, downloading")
#         download(s3, bucket_name, current_version, file_name, download_path)
#         print(f"Downloaded binary: {file_name}, version: {current_version}")
#     else:
#         print("No updates available for binary")

#
# def execute_binary():
#     try:
#         dir = "/Users/shubham/Desktop/piicli_metadata"
#         file_prefix = "test"
#         bucket = 'golang-cli'
#         if not os.path.exists(dir):
#             os.mkdir(dir)
#         operating_system, arch = get_os_and_architecture()
#         file = file_prefix + "-" + operating_system + "-" + arch
#
#         s3 = create_s3_client()
#         download_or_update(s3, bucket, file, dir)
#
#         test_cli_version = conf["test_cli_version"]
#         binary_path = os.path.join(dir, test_cli_version, file)
#         os.chmod(binary_path, 0o755)
#         subprocess.run(binary_path)
#
#     except Exception as e:
#         print(f"Something went wrong, err: {e}")

def print_version():
    print("running 0.0.6")


def execute_binary():
    try:
        home = os.getenv("HOME")
        metadata_dir = home + "/piicli_metadata"
        config_file = "conf.yaml"
        if not os.path.exists(metadata_dir):
            os.mkdir(metadata_dir)
        conf = {
            "version": "0.0.2",
            "cli_prefix": "test"
        }
        config_path = os.path.join(metadata_dir, config_file)
        # create initial config file
        write_yaml(config_path, conf)
        check_for_updates(config_path)
        print_version()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    execute_binary()
