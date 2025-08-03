import os
import sys
from pathlib import Path

from capm.config import load_config_from_file
from capm.package import run_package, load_packages

CONFIG_FILE = Path('.capm.yml')


def main():
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} does not exist.")
        sys.exit(1)
    packages = load_packages()
    package_configs = load_config_from_file(CONFIG_FILE)
    for package_config in package_configs:
        package = packages[package_config.id]
        exit_code = run_package(package_config.id, package)
        if exit_code != 0:
            sys.exit(exit_code)


if __name__ == "__main__":
    main()
