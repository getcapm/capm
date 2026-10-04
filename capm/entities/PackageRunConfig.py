from dataclasses import dataclass

from capm.output.OutputFormat import OutputFormat


@dataclass
class PackageRunConfig:
    id: str
    image: str
    version: str
    args: str
    type: str
    workspace_mode: str
    output_format: OutputFormat
    install_command: str | None = None
    entrypoint: str | None = None
    extra_args: str | None = None