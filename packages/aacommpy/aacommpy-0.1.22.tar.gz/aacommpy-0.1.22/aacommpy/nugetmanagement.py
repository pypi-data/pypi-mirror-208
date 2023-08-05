import os
import shutil
import subprocess

def download_nuget(version: str = "", update: bool = False) -> None:
    nuget_path = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main', 'nuget.exe')
    installed = False
    for dirname in os.listdir(os.path.dirname(nuget_path)):
        if dirname.startswith('Agito.AAComm.') and os.path.isdir(os.path.join(os.path.dirname(nuget_path), dirname)):
            installed = True
            old_version = dirname.split('.')[2:]
            old_version = '.'.join(old_version)
            break
    if update and installed:
        shutil.rmtree(os.path.join(os.path.dirname(nuget_path), f'Agito.AAComm.{old_version}'))
    nuget_cmd = [nuget_path, 'install', 'Agito.AAComm', '-OutputDirectory', os.path.join(os.path.dirname(nuget_path)), '-Source', 'https://api.nuget.org/v3/index.json']
    if version != "":
        nuget_cmd.extend(['-Version', version])
    subprocess.run(nuget_cmd, check=True)
    for dirname in os.listdir(os.path.dirname(nuget_path)):
        if dirname.startswith('Agito.AAComm.') and os.path.isdir(os.path.join(os.path.dirname(nuget_path), dirname)):
            new_version = dirname.split('.')[2:]
            new_version = '.'.join(new_version)
            source_dir = os.path.join(os.path.dirname(nuget_path), f'Agito.AAComm.{new_version}/build/AACommServer')
            dest_dir = os.path.dirname(__file__)
            shutil.copy2(os.path.join(source_dir, 'AACommServer.exe'), dest_dir)
            shutil.copy2(os.path.join(source_dir, 'AACommServerAPI.dll'), dest_dir)
            source_dir2 = os.path.join(os.path.dirname(nuget_path), f'Agito.AAComm.{new_version}/lib/net5.0')
            shutil.copy2(os.path.join(source_dir2, 'AAComm.dll'), dest_dir)
            break
    return None
def nuget_version() -> str:
    nuget_path = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main', 'nuget.exe')
    installed = False
    latest_version = None
    for dirname in os.listdir(os.path.dirname(nuget_path)):
        if dirname.startswith('Agito.AAComm.') and os.path.isdir(os.path.join(os.path.dirname(nuget_path), dirname)):
            installed = True
            version = dirname.split('.')[2:]
            latest_version = '.'.join(version)
            print(f"The installed version of Agito.AAComm is {latest_version}.")
            break

    if not installed:
        raise RuntimeError('Agito.AAComm package is not installed.')
    
    return latest_version
def update_nuget() -> None:
    download_nuget(update=True)
    return None
def dotnetfw(version: str = "net5.0") -> None:
    latest_version = nuget_version()
    source_dir = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main', f'Agito.AAComm.{latest_version}')
    dest_dir = os.path.dirname(__file__)    
    if version == "net5.0":
        source_dir = os.path.join(source_dir, 'lib', 'net5.0')
    elif version == "net40":
        source_dir = os.path.join(source_dir, 'lib', 'net40')
    elif version == "net46":
        source_dir = os.path.join(source_dir, 'lib', 'net46')
    elif version == "net48":
        source_dir = os.path.join(source_dir, 'lib', 'net48')
    elif version == "netcoreapp3.1":
        source_dir = os.path.join(source_dir, 'lib', 'netcoreapp3.1')
    else:
        raise ValueError("Invalid .NET framework version specified.")    
    dll_path = os.path.join(source_dir, 'AAComm.dll')
    if not os.path.isfile(dll_path):
        raise FileNotFoundError(f"Could not find AAComm.dll in {source_dir}.")
    shutil.copy2(dll_path, dest_dir)
    return None