from os import path, listdir
from pathlib import Path
from time import sleep

import docker
import yaml
from docker.errors import ContainerError, DockerException, APIError

from capm.config import run_commands
from capm.entities.PackageConfig import PackageConfig
from capm.entities.PackageDefinition import PackageDefinition
from capm.entities.PackageRunConfig import PackageRunConfig
from capm.output.OutputStream import OutputStream
from capm.utils.cli_utils import fail
from capm.version import version

package_repository: dict[str, PackageDefinition] = {}


def load_packages() -> dict[str, PackageDefinition]:
    result: dict[str, PackageDefinition] = {}
    packages_dir = Path(__file__).parent / 'definitions'
    yml_files = [packages_dir.joinpath(f) for f in listdir(packages_dir) if
                 packages_dir.joinpath(f).is_file() and f.endswith('.yml')]
    for yml_file in yml_files:
        with open(yml_file, 'r') as file:
            d = yaml.safe_load(file)
            package_id = path.splitext(path.basename(yml_file))[0]
            try:
                package_definition = PackageDefinition(**d)
                result[package_id] = package_definition
            except TypeError as e:
                fail(f'Error loading package \'{package_id}\': {str(e)}')
                raise e
    return result


def _image_exists(docker_client, image_name: str) -> bool:
    try:
        docker_client.images.get(image_name)
        return True
    except docker.errors.ImageNotFound:
        return False


def _build_image(docker_client, package_run_config: PackageRunConfig) -> tuple[int, str]:
    base_image = package_run_config.image
    if not _image_exists(docker_client, base_image):
        docker_client.images.pull(base_image)
    if package_run_config.install_command:
        package_version = package_run_config.version
        install_command = package_run_config.install_command.format(version=package_version)
        install_command = install_command.replace('"', '\\"').replace("'", "\\'")
        install_command = ' && '.join(install_command.strip().split('\n'))
        command = f'/bin/sh -c \'({install_command}) >/dev/null 2>&1\''
        try:
            container = docker_client.containers.run(base_image, tty=True, remove=True, detach=True)
            exec_result = container.exec_run(command)
            if exec_result.exit_code != 0:
                return exec_result.exit_code, exec_result.output.decode('utf-8')
            output = container.logs()
            container.commit(f'capm-{package_run_config.id}', version)
            container.stop()
            return 0, output.decode('utf-8')
        except DockerException as e:
            raise e
        finally:
            try:
                docker_client.containers.prune()
            except APIError as e:
                if e.response.status_code == 404:
                    sleep(5)  # Sometimes the first try fails, for example in GitHub Actions
                    docker_client.containers.prune()
                else:
                    raise e
    else:
        return 0, ''


def _run_image(docker_client, image_name: str, package_run_config: PackageRunConfig, codebase_path: Path = Path('.')) \
        -> tuple[int, str]:
    report_dir = str(run_commands.reports_dir.joinpath(package_run_config.id))
    command = ''
    if package_run_config.entrypoint:
        command = package_run_config.entrypoint + ' '
    args = package_run_config.args.format(workspace=str(run_commands.workspace_dir), report_dir=report_dir)
    if package_run_config.extra_args:
        args = package_run_config.extra_args + ' ' + args
    command += args
    mode = package_run_config.workspace_mode
    volumes = {str(codebase_path.resolve()): {'bind': str(run_commands.workspace_dir), 'mode': mode}}
    try:
        output = docker_client.containers.run(image_name, command, volumes=volumes, tty=True, remove=False,
                                              log_config={'type': 'json-file'},
                                              working_dir=str(run_commands.workspace_dir))
        exit_code = 0
    except ContainerError as e:
        output = e.container.logs()
        exit_code = int(e.exit_status)
    finally:
        docker_client.containers.prune()
    return exit_code, output.decode('utf-8')


def _merge(package_definition: PackageDefinition, package_config: PackageConfig) -> PackageRunConfig:
    image = package_definition.image
    package_type = package_definition.type
    package_version = package_config.version if package_config.version else package_definition.version
    args = package_config.args if package_config.args else package_definition.args
    workspace_mode = package_config.workspace_mode if package_config.workspace_mode else (
        package_definition.workspace_mode)
    output_format = package_config.output_format if package_config.output_format else (
        package_definition.output_format)
    install_command = package_definition.install_command
    entrypoint = package_definition.entrypoint
    extra_args = package_config.extra_args
    return PackageRunConfig(package_config.id, image, package_version, args, package_type, workspace_mode,
                            output_format, install_command, entrypoint, extra_args)


def run_package(package_definition: PackageDefinition, package_config: PackageConfig, output_stream: OutputStream,
                codebase_path: Path = Path('.')) -> int:
    package_run_config = _merge(package_definition, package_config)
    docker_client = docker.from_env()
    output_stream.start_status('Loading')
    if package_definition.install_command:
        image_name = f'capm-{package_run_config.id}:{version}'
        if not _image_exists(docker_client, image_name):
            output_stream.update_status_info(f'[{package_run_config.id}] Building image: {image_name}')
            try:
                exit_code, logs = _build_image(docker_client, package_run_config)
                if exit_code != 0:
                    output_stream.package_run_fail(package_run_config.id,
                                                   f'Error building image, exit code: {exit_code}')
                    output_stream.command_error(logs, package_run_config.output_format)
                    return exit_code
            except ContainerError as e:
                exit_code = int(e.exit_status)
                output_stream.package_run_fail(package_run_config.id, f'Error building image, exit code: {exit_code}')
                output_stream.command_error(e.container.logs().decode('utf-8'), package_run_config.output_format)
                return exit_code
            except DockerException as e:
                output_stream.package_run_fail(package_run_config.id, f'Error building image, reason: {str(e)}')
                return 1
    else:
        image_name = package_definition.image
        if not _image_exists(docker_client, image_name):
            output_stream.update_status_info(f'[{package_run_config.id}] Pulling image: {image_name}')
            docker_client.images.pull(image_name)
    output_stream.update_status_info(f'[{package_run_config.id}] Running image: ({image_name})')
    exit_code, logs = _run_image(docker_client, image_name, package_run_config, codebase_path)
    if exit_code == 0:
        output_stream.package_run_succeed(package_run_config.id)
        output_stream.command_output(logs, package_run_config.output_format)
    else:
        output_stream.package_run_fail(package_run_config.id, f'Error running package, exit code: {exit_code}')
        output_stream.command_error(logs, package_run_config.output_format)
    return exit_code
