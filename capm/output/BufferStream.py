from capm.output.OutputFormat import OutputFormat
from capm.output.OutputStream import OutputStream


class BufferStream(OutputStream):
    def __init__(self, show_command_output: bool = False):
        self.show_command_output = show_command_output
        self.buffer: list[str] = []

    def package_run_fail(self, package_id: str, reason: str) -> None:
        self.buffer.append(f'[{package_id}] {reason}')

    def package_run_succeed(self, package_id: str) -> None:
        self.buffer.append(f'[{package_id}] Package executed successfully')

    def command_output(self, command_output: str, output_format: OutputFormat) -> None:
        if self.show_command_output:
            self.buffer.append(command_output)

    def command_error(self, command_error: str, output_format: OutputFormat) -> None:
        self.buffer.append(command_error)
