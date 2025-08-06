from pathlib import Path

import yaml

from capm.entities.PackageConfig import PackageConfig


def load_config(data: str) -> list[PackageConfig]:
    entries = yaml.safe_load(data)
    if not entries or not isinstance(entries, dict):
        return []
    package_configs = entries.get('packages', [])
    return [PackageConfig(**pc) for pc in package_configs]


def load_config_from_file(path: Path) -> list[PackageConfig]:
    with open(path, 'r') as file:
        return load_config(file.read())


class Settings:
    workspace_dir: Path = Path('/capm/workspace')
    reports_dir: Path = Path('/capm/reports')


config = Settings()
