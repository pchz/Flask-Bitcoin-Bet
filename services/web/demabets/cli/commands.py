from demabets import db
from demabets.cli import cli_app_group


@cli_app_group.command("create_db")
def create_db():
    """
    CLI command for generating all database tables from SQLAlchemy models.
    """
    db.create_all()
