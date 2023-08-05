import argparse
import os
import requests
from zipfile import ZipFile
import subprocess
import shutil
from aacommpy.nugetmanagement import download_nuget, nuget_version, update_nuget, dotnetfw


entry_points = {
    'console_scripts': [
        'nuget_download = nugetmanagement:download_nuget',
        'nuget_version = nugetmanagement:nuget_version',
        'update_nuget = nugetmanagement:update_nuget'
    ]
}
def install_template() -> None:
    msg = 'Download Python package for AAComm to this directory (y/n)? '
    user_response = input(msg)
    if user_response != 'y':
        return None
    url = 'https://github.com/jamesbond90/aacommpyDownloader/archive/refs/heads/main.zip'
    r = requests.get(url)
    with open(os.path.join(os.path.dirname(__file__), 'main.zip'), 'wb') as f:
        f.write(r.content)

    with ZipFile(os.path.join(os.path.dirname(__file__), 'main.zip'), 'r') as repo_zip:
        repo_zip.extractall(os.path.dirname(__file__))

    os.remove(os.path.join(os.path.dirname(__file__), 'main.zip'))
    return None

def download_and_install(version: str = "") -> None:
    install_template()
    # Add code to wait for the nuget.exe file to be fully downloaded
    nuget_path = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main', 'nuget.exe')
    while not os.path.exists(nuget_path):
        time.sleep(1)
    # nuget.exe is fully downloaded, proceed with download_nuget()
    if version:
        download_nuget(version)
    else:
        download_nuget()

def main() -> None:
    parser = argparse.ArgumentParser(description='Download aacommpy package.')
    parser.add_argument('command', choices=['install', 'downloadnuget', 'version', 'update', 'dotnetfw'], help='Choose a command to execute.')
    parser.add_argument('--version', help='Specify version to install/download.')
    parser.add_argument('--netfw', choices=['net40', 'net46', 'net48', 'netcoreapp3.1', 'net5.0'], default='net5.0', help='Choose the .NET framework version to use.')
    args = parser.parse_args()

    if args.command == 'install':
        if args.version:
            download_and_install(args.version)
        else:
            download_and_install()        
    # elif args.command == 'downloadnuget':
    #     if args.version:
    #         download_nuget(args.version)
    #     else:
    #         download_nuget()
    elif args.command == 'version':
        nuget_version()
    elif args.command == 'update':
        update_nuget()
    elif args.command == 'dotnetfw':
        dotnetfw(version=args.netfw)
    else:
        raise RuntimeError('Please supply a valid command for aacommpy - e.g. install.')

    return None

if __name__ == '__main__':
    main()
