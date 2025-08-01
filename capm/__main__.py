import importlib
import os
import sys

import yaml

CONFIG_FILE = '.capm.yml'


def load_config() -> list[str]:
    with open(CONFIG_FILE, 'r') as file:
        config_data = file.read()
    entries = yaml.safe_load(config_data)
    if not isinstance(entries, list):
        raise ValueError(f"Expected a list in {CONFIG_FILE}, got {type(entries)}")
    return [e['id'] for e in entries if 'id' in e]


def main():
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} does not exist.")
        sys.exit(1)
    packages = load_config()
    for package in packages:
        print(f"Package ID: {package}")
        mod = importlib.import_module(f'packages.{package}')
        mod.run()



if __name__ == "__main__":
    main()
