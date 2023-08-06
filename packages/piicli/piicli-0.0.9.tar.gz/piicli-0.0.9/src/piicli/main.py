import platform
import subprocess
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


def get_version(package_name):
    return pkg_resources.get_distribution(package_name).version


def get_file_name(prefix):
    operating_system, arch = get_os_and_architecture()
    file_name = prefix + "-" + operating_system + "-" + arch
    return file_name


def check_for_cli_updates(current_version, package_name):
    response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
    latest_version = response.json()['info']['version']

    if current_version != latest_version:
        print(f"Update available, updating to latest version: {latest_version}")
        subprocess.call(f"pip3 install --upgrade {package_name}", shell=True)
        print(f"Updated cli to latest version: {latest_version}")
    else:
        print("No updates available")


def download(s3, bucket_name, folder_name, file_name, download_path):
    try:
        download_path = os.path.join(download_path, folder_name)
        if not os.path.exists(download_path):
            os.mkdir(download_path)

        # Download the file from S3
        key = folder_name + "/" + file_name
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

def download_binary(metadata_dir, binary, version):
    s3 = create_s3_client()
    bucket = 'golang-cli'
    file = get_file_name(binary)
    if not os.path.exists(os.path.join(metadata_dir, version, file)):
        print(f"Downloading binary:{binary} for version: {version}")
        download(s3, bucket, version, file, metadata_dir)


def execute_binary(package_name, binary_name):
    home = os.getenv("HOME")
    metadata_path = home + "/piicli_metadata"
    current_version = get_version(package_name)
    file = get_file_name(binary_name)
    try:
        binary_path = os.path.join(metadata_path, current_version, file)
        os.chmod(binary_path, 0o755)
        print(f"Executing go binary for version: {current_version}")
        subprocess.run(binary_path)
    except Exception as e:
        print(f"Something went wrong, err: {e}")


def pre_execution_workflow(package_name, binary_name):
    try:
        current_version = get_version(package_name)
        home = os.getenv("HOME")
        metadata_dir = home + "/piicli_metadata"
        if not os.path.exists(metadata_dir):
            os.mkdir(metadata_dir)
        check_for_cli_updates(current_version, package_name)

        current_version = get_version(package_name)
        download_binary(metadata_dir, binary_name, current_version)

    except Exception as e:
        print(e)


def run_cli():
    try:
        package_name = "piicli"
        binary_name = "secrets"
        pre_execution_workflow(package_name, binary_name)
        print("Running main cli, version: 0.0.9")
        execute_binary(package_name, binary_name)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    run_cli()
