from dataclasses import dataclass


@dataclass
class Package:
    image: str
    command: str
    workspace_mode: str = 'ro'
