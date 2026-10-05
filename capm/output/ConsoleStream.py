from capm.output.OutputFormat import OutputFormat
from capm.output.OutputStream import OutputStream
from capm.utils.Spinner import Spinner


class ConsoleStream(OutputStream):
    def __init__(self, show_command_output: bool = False):
        self.show_command_output = show_command_output
        self._spinner: Spinner = Spinner()

    def start_status(self, message: str) -> None:
        self.update_status_info(message)
        self._spinner.start()

    def update_status_info(self, message: str) -> None:
        self._spinner.text = message

    def package_run_fail(self, package_id: str, reason: str) -> None:
        self._spinner.fail(f'[{package_id}] {reason}')

    def package_run_succeed(self, package_id: str) -> None:
        self._spinner.succeed(f'[{package_id}] Package executed successfully')

    def command_output(self, command_output: str, output_format: OutputFormat) -> None:
        if self.show_command_output:
            print(command_output)

    def command_error(self, command_error: str, output_format: OutputFormat) -> None:
        print(command_error)
