import typer

from mb_cli import settings

app = typer.Typer()

from mb_cli.cli import ex

app.add_typer(ex.app, name='exchange', help='Exchange commands.', rich_help_panel='Sub-commands')

from rich import print
from rich.style import Style
from rich.console import Console

console = Console()


@app.command('version', rich_help_panel='Utility')
def version():
    """
    Show version of the app and exit.
    """
    print(f'Version: v{settings.VERSION}')

    link_style = Style(italic=True, link='https://codeberg.org/notmtth/mb-cli', color='blue')
    console.print('Go to repo', style=link_style)

    typer.Exit()



