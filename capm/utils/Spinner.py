import sys

from halo import Halo

from capm.utils.cli_utils import info, succeed, fail


class Spinner:
    def __init__(self):
        if sys.stdout.isatty():
            self._spinner = Halo(text='', spinner='dots')
        else:
            self._spinner = None

    def start(self):
        if self._spinner:
            self._spinner.start()

    @property
    def text(self):
        return self._spinner.text

    @text.setter
    def text(self, text: str):
        if self._spinner:
            self._spinner.text = text
        else:
            info(text)

    def succeed(self, text: str):
        if self._spinner:
            self._spinner.succeed(text)
        else:
            succeed(text)

    def fail(self, text: str):
        if self._spinner:
            self._spinner.fail(text)
        else:
            fail(text)
