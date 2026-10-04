from capm.output.OutputStream import OutputStream


class Markdown(OutputStream):
    def __init__(self, show_output: bool = False):
        self.show_output = show_output

    def package_run_fail(self, package_id: str, reason: str) -> None:
        print(f'## :stop_sign: {package_id}')

    def package_run_succeed(self, package_id: str) -> None:
        print(f'## :white_check_mark: {package_id}')

    def command_output(self, command_output: str) -> None:
        if self.show_output:
            print(f'```\n{command_output}\n```\n')

    def command_error(self, command_error: str) -> None:
        if self.show_output:
            print(f"```\n{command_error}\n```\n")
