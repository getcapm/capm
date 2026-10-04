from abc import ABC, abstractmethod


class OutputStream(ABC):
    def start_status(self, message: str) -> None:
        pass

    def update_status_info(self, message: str) -> None:
        pass

    @abstractmethod
    def package_run_fail(self, package_id: str, reason: str) -> None:
        pass

    @abstractmethod
    def package_run_succeed(self, package_id: str) -> None:
        pass

    @abstractmethod
    def command_output(self, command_output: str) -> None:
        pass

    @abstractmethod
    def command_error(self, command_error: str) -> None:
        pass
