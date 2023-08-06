import typing as t
from gettext import gettext as _

from click import ClickException, echo, secho
from click._compat import get_text_stderr


class EcsmgmtClickException(ClickException):
    def show(self, file: t.Optional[t.IO] = None) -> None:
        if file is None:
            file = get_text_stderr()

        secho(_('Error: '), nl=False, fg='red', bold=True)
        echo(_('{message}').format(message=self.format_message()), file=file)
