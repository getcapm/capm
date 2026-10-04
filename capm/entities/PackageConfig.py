from dataclasses import dataclass

from capm.output.OutputFormat import OutputFormat


@dataclass
class PackageConfig:
    id: str
    version: str | None = None
    args: str | None = None
    extra_args: str | None = None
    workspace_mode: str | None = None
    output_format: OutputFormat | None = None
