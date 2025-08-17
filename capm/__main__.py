import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, Optional, Any

import inquirer
import typer
import yaml
from typer import Context
from typer.core import TyperGroup

import capm.version
from capm.config import load_config_from_file, save_config_to_file
from capm.entities.PackageConfig import PackageConfig
from capm.entities.PackageDefinition import PackageDefinition
from capm.package.package import run_package, load_packages
from capm.utils.utils import fail, succeed, console

CONFIG_FILE = Path('.capm.yml')


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        return list(self.commands)


cli = typer.Typer(cls=OrderCommands, no_args_is_help=True, add_completion=False)
package_repository: dict[str, PackageDefinition] = {}


@cli.command(help="Add a package")
def add(package: Annotated[str, typer.Argument(help="Package name")]):
    if package not in package_repository:
        fail(f"Package '{package}' does not exist.")
        sys.exit(1)
    config = load_config_from_file(CONFIG_FILE)
    for p in config.packages:
        if p.id == package:
            fail(f"Package '{package}' is already added.")
            sys.exit(1)
    config.packages.append(PackageConfig(package))
    save_config_to_file(config, CONFIG_FILE)
    succeed(f'Package \'{package}\' added successfully.')


@cli.command(help="Run all configured package")
def check(show_output: Annotated[bool | None, typer.Option(help="Show output of package", show_default=False)] = None):
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} does not exist.")
        sys.exit(1)
    config = load_config_from_file(CONFIG_FILE)
    for package_config in config.packages:
        if package_config.id not in package_repository:
            fail(f"Package '{package_config.id}' does not exist.")
            sys.exit(1)
        package_definition = package_repository[package_config.id]
        exit_code = run_package(package_definition, package_config,
                                show_output if show_output is not None else False)
        if exit_code != 0:
            sys.exit(exit_code)


@cli.command(help="Create new package")
def create():
    questions = [
        inquirer.List('image', 'Base image for package?',
                      ["docker.io/library/python:3.11-slim", "docker.io/library/node:22-alpine"]),
        inquirer.Text('version', 'Version of package?'),
        inquirer.Text('install_command', 'Install command?'),
        inquirer.Text('entrypoint', 'Entrypoint?'),
        inquirer.Text('args', 'Arguments?'),
        inquirer.Text('repository', 'Repository?'),
        inquirer.Text('about', 'About?'),
        inquirer.Text('website', 'Website?'),
        inquirer.Text('technology', 'Technology?'),
        inquirer.List('type', 'Type?', ['linter', 'formatter', 'analyzer', 'duplication', 'complexity', 'other']),
    ]
    optional = ['install_command', 'entrypoint', 'repository', 'about', 'website', 'technology']
    answers = inquirer.prompt(questions)
    if not answers:
        return
    package_definition = PackageDefinition(**answers)

    def dict_factory(x: list[tuple[str, Any]]) -> dict:
        result = {}
        for k, v in x:
            if v is None or v == '' and k in optional:
                continue
            result[k] = v
        return result

    print(yaml.dump(asdict(package_definition, dict_factory=dict_factory)))


@cli.command(help="Show information about package")
def info():
    print(f"{'PACKAGE':20s} {'VERSION':8s}")
    packages = sorted(package_repository.keys())
    for k in packages:
        v = package_repository[k]
        print(f"{k:20s} {str(v.version):8s}")


@cli.command(name="list", help="List package")
def list_packages():
    config = load_config_from_file(CONFIG_FILE)
    if not config.packages:
        print("No package found.")
        return
    for package in config.packages:
        print(f"{package.id}")


@cli.command(help="Remove a package")
def remove(package: Annotated[str, typer.Argument(help="Package name")]):
    config = load_config_from_file(CONFIG_FILE)
    config.packages = [p for p in config.packages if p.id != package]
    save_config_to_file(config, CONFIG_FILE)
    succeed(f'Package \'{package}\' removed successfully.')


@cli.command(help='Run single package')
def run(_: Annotated[str, typer.Argument(metavar='PACKAGE', help="Package name")],
        __: Annotated[str, typer.Argument(metavar='ARGS', help="Arguments for the package")]):
    pass


def _version_callback(show: bool):
    if show:
        global package_repository
        package_repository = load_packages()
        console.print(f"CAPM v. {capm.version.version} [{len(package_repository)} package definitions]")
        raise typer.Exit()


@cli.callback()
def cli_callback(
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


def main():
    global package_repository
    package_repository = load_packages()
    if len(sys.argv) > 1 and sys.argv[1] == 'run' and len(sys.argv) >= 3:
        package = sys.argv[2]
        if package not in package_repository:
            fail(f"Package '{package}' does not exist.")
            sys.exit(1)
        package_definition = package_repository[package]
        args = ' '.join(sys.argv[3:])
        exit_code = run_package(package_definition, PackageConfig(package, args=args), True)
        if exit_code != 0:
            sys.exit(exit_code)
    else:
        cli()


if __name__ == "__main__":
    main()
