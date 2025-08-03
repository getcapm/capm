import os
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from typer import Context
from typer.core import TyperGroup

from capm.config import load_config_from_file
from capm.package import run_package, load_packages
from capm.version import version

CONFIG_FILE = Path('.capm.yml')


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        return list(self.commands)


cli = typer.Typer(cls=OrderCommands, no_args_is_help=True, add_completion=False)


@cli.command(help="Run code analysis")
def run():
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} does not exist.")
        sys.exit(1)
    packages = load_packages()
    package_configs = load_config_from_file(CONFIG_FILE)
    for package_config in package_configs:
        package = packages[package_config.id]
        exit_code = run_package(package, package_config)
        if exit_code != 0:
            sys.exit(exit_code)


def _version_callback(show: bool):
    if show:
        print(f"CAPM version: {version}")
        raise typer.Exit()


@cli.callback()
def main(
        version: Annotated[
            Optional[bool],
            typer.Option(
                "--version", "-V", help="Show version", callback=_version_callback
            ),
        ] = None,
):
    """CAPM: Code Analysis Package Manager"""

    if version:
        raise typer.Exit()


if __name__ == "__main__":
    cli()
