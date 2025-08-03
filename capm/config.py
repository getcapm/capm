from pathlib import Path

import yaml

from capm.entities.PackageConfig import PackageConfig


def load_config(data: str) -> list[PackageConfig]:
    entries = yaml.safe_load(data)
    if not isinstance(entries, list):
        raise RuntimeError(f"Expected a list, got {type(entries)}")
    return [PackageConfig(**e) for e in entries]


def load_config_from_file(path: Path) -> list[PackageConfig]:
    with open(path, 'r') as file:
        return load_config(file.read())
