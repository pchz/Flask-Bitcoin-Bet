from flask.cli import AppGroup

cli_app_group = AppGroup("cli")

from demabets.cli import commands
