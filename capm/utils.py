from pathlib import Path

import docker
from docker.errors import ContainerError

WORKSPACE_DIR = '/capm/workspace'


def run_package(image: str, command: str, workspace_mode: str = 'ro', path: Path = Path('.')) -> int:
    client = docker.from_env()
    print(f'Pulling image: {image}...')
    client.images.pull(image)
    print(f'Running image ({image}) container...')
    command = command.format(workspace=WORKSPACE_DIR)
    try:
        client.containers.run(image, command,
                              volumes={str(path.resolve()): {'bind': '/capm/workspace', 'mode': workspace_mode}})
        return 0
    except ContainerError as e:
        print(e.container.logs().decode('utf-8'))
        return e.exit_status
