import pathlib

import click

root_path = pathlib.Path.cwd().absolute()
"""Default destination for generated files"""


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def command():
    pass
