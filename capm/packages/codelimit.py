import docker
from docker.errors import ContainerError


def run() -> int:
    client = docker.from_env()
    print('Pulling codelimit image...')
    client.images.pull('getcodelimit/codelimit:latest')
    print('Running codelimit container...')
    try:
        output = client.containers.run('getcodelimit/codelimit:latest', 'scan .')
        print(output.decode('utf-8'))
        return 0
    except ContainerError as e:
        return e.exit_status
