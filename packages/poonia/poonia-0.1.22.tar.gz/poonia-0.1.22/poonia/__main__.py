import click

from .commands.epub import epub
from .commands.ff import ff
from .commands.fs import fs
from .commands.io import io
from .commands.run import run
from .commands.sqexec import sqexec
from .commands.tpl import tpl


@click.group()
def main():
    pass


main.add_command(epub)
main.add_command(ff)
main.add_command(fs)
main.add_command(io)
main.add_command(run)
main.add_command(sqexec)
main.add_command(tpl)


if __name__ == '__main__':
    main()
