from os import path, listdir
from pathlib import Path

import docker
import yaml
from docker.errors import ContainerError
from halo import Halo  # type: ignore

from capm.entities.Package import Package

WORKSPACE_DIR = '/capm/workspace'


def load_packages() -> dict[str, Package]:
    result: dict[str, Package] = {}
    packages_dir = Path(__file__).parent.joinpath('packages')
    yml_files = [packages_dir.joinpath(f) for f in listdir(packages_dir) if
                 packages_dir.joinpath(f).is_file() and f.endswith('.yml')]
    for yml_file in yml_files:
        with open(yml_file, 'r') as file:
            d = yaml.safe_load(file)
            package_id = path.splitext(path.basename(yml_file))[0]
            result[package_id] = Package(**d)
    print(f"Loaded {len(result)} package definitions")
    return result


def run_package(id: str, package: Package, path: Path = Path('.')) -> int:
    client = docker.from_env()
    spinner = Halo(text='Loading', spinner='dots')
    spinner.start()
    image = package.image
    spinner.text = f'[{id}] Pulling image: {image}'
    client.images.pull(image)
    spinner.text = f'[{id}] Running image: ({image})'
    command = package.command.format(workspace=WORKSPACE_DIR)
    volumes = {str(path.resolve()): {'bind': '/capm/workspace', 'mode': package.workspace_mode}}
    try:
        client.containers.run(image, command, volumes=volumes)
        spinner.succeed(f'[{id}] Package executed successfully')
        return 0
    except ContainerError as e:
        spinner.fail(f"[{id}] Error running package, exit code: {e.exit_status}")
        print(e.container.logs().decode('utf-8'))
        return e.exit_status
