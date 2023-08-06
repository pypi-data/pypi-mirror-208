import inspect
import os
from glob import glob
from pathlib import Path
from zipfile import ZipFile
from shutil import rmtree

import lusid_drive
from lusid_drive import ApiException
from lumipy import get_client
from time import sleep

sdk_version = '1.12.790'


# noinspection SqlResolve,SqlNoDataSourceInspection
def download_files(lm_client, files, path, pattern):
    sql = f"SELECT [Id], [Name] FROM [Drive.File] WHERE [RootPath] = '{path}' and [Name] like '{pattern}'"

    wait = 30
    df = lm_client.run(sql, quiet=True)
    locations = []
    for _, r in df.iterrows():
        _print(f'Downloading {path}/{r["Name"]}.', 4)

        count = 0
        while True:
            try:
                locations.append(files.download_file(r['Id']))
                break
            except ApiException as ae:
                if count > 3:
                    raise ae
                count += 1
                _print(f'Couldn\'t get file (reason: {ae.reason}). Waiting {wait}s before retry.')
                sleep(wait)

    return locations


def _print(s, n=0):
    indent = ' ' * n
    print(indent + s)


def setup(**kwargs):
    import lumipy.provider
    module_path = inspect.getfile(lumipy.provider).replace('/__init__.py', '')

    bin_path = module_path + '/bin'
    if os.path.exists(bin_path):
        rmtree(bin_path)

    _print('Setting up python providers. 🛠')
    lm_client = get_client(**kwargs)

    lumi_url = lm_client._factory.api_client.configuration._base_path
    cfg = lusid_drive.Configuration(host=lumi_url.split('.com')[0] + '.com/drive')
    cfg.access_token = lm_client.get_token()
    api_client = lusid_drive.ApiClient(cfg)
    files = lusid_drive.FilesApi(api_client)

    drive_path = '/LUSID-support-document-share/Luminesce/'
    zip_name = f'finbourne.luminesce.pythonproviders.{sdk_version}.zip'

    _print('Getting the provider factory dlls zip.', 2)
    zip_path = download_files(lm_client, files, drive_path + 'Providers', zip_name)
    if len(zip_path) != 1:
        raise ValueError(f"Couldn't get {drive_path}/{zip_name}. Please contact support.")

    _print('Unzipping the provider factory dlls.', 2)
    with ZipFile(zip_path[0], 'r') as zf:
        bin_path = module_path + '/bin'
        Path(bin_path).mkdir(parents=True, exist_ok=True)
        zf.extractall(bin_path)

    _print('Cleaning up zip file.', 2)
    os.remove(zip_path[0])

    _print('Getting pem files.', 2)
    pem_paths = download_files(lm_client, files, drive_path + 'Certificates', '%.pem')
    if len(pem_paths) != 2:
        raise ValueError(f"Couldn't get {drive_path}/Certificates/*.pem. Please contact support.")

    dll_path = module_path + '/bin/tools/net6.0/any/'
    for pem_path in pem_paths:
        pem_name = pem_path.split('/')[-1].strip(';')
        _print(f'Copying {pem_name}.', 2)
        target = dll_path + pem_name
        with open(pem_path, 'rb') as pfr:
            with open(target, 'wb') as pfw:
                pfw.write(pfr.read())

    _print('Checking pem files.', 2)
    pems = glob(dll_path + '*.pem')
    if len(pems) != 2:
        raise ValueError(f"Couldn't find pem files at {dll_path}.")

    _print("\nAll set! You can now build and run python Luminesce providers.")

    cmd = 'python -m lumipy.provider run --set=demo '
    _print(f"\nTry running the following command in a terminal:")
    _print(cmd + '\n', 2)
