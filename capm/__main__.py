import os
import sys
from os import path
from pathlib import Path

import yaml

from capm.config import load_config_from_file
from capm.entities.Package import Package
from capm.utils import run_package

CONFIG_FILE = Path('.capm.yml')


def load_packages() -> dict[str, Package]:
    result: dict[str, Package] = {}
    packages_dir = Path(__file__).parent.joinpath('packages')
    yml_files = [packages_dir.joinpath(f) for f in os.listdir(packages_dir) if
                 packages_dir.joinpath(f).is_file() and f.endswith('.yml')]
    for yml_file in yml_files:
        with open(yml_file, 'r') as file:
            d = yaml.safe_load(file)
            package_id = path.splitext(path.basename(yml_file))[0]
            result[package_id] = Package(**d)
    print(f"Loaded {len(result)} package definitions")
    return result


def main():
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} does not exist.")
        sys.exit(1)
    packages = load_packages()
    package_configs = load_config_from_file(CONFIG_FILE)
    for package_config in package_configs:
        print(f"Package ID: {package_config.id}")
        package = packages[package_config.id]
        exit_code = run_package(package.image, package.command, package.workspace_mode)
        if exit_code != 0:
            print(f"Error running package {package}, exit code: {exit_code}")
            sys.exit(exit_code)
        else:
            print(f"Package {package_config.id} executed successfully.")


if __name__ == "__main__":
    main()
