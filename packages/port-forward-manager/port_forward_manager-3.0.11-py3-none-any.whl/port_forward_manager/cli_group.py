import typer
import rich
from rich.prompt import Confirm
from rich.table import Table
from sqlalchemy.exc import IntegrityError

import port_forward_manager.cli_schema
from .cli_schema import prepare_schema_table
from . import database, models

app = typer.Typer(no_args_is_help=True)
db = database.SessionLocal()


def prepare_group_table(show_alias: bool = False, show_link: bool = False, show_schema: bool = True, title: str = 'Schemas'):

    table = Table(show_edge=False)

    table.add_column("#", justify="right", style="green", width=3)
    table.add_column("Name", justify="left", style="yellow", width=30)
    table.add_column("Label", justify="right", style="yellow", width=30)

    return table


@app.command()
def index(name=typer.Argument(None, help='Criteria to search')):
    """
    List groups
    """
    table = prepare_group_table()
    for group in models.Group.index(name):
        row = [
            str(group.id),
            group.name,
            group.label,
        ]
        table.add_row(*row)

    rich.print(table)


@app.command()
def schemas(name=typer.Argument(None, help='Criteria to search')):
    """
    List groups
    """
    table = prepare_schema_table()
    for group in models.Group.index(name):
        for schema in group.schemas:
            row = [
                str(schema.id),
                group.name,
                schema.name,
                schema.label
            ]
            table.add_row(*row)

    rich.print(table)


@app.command()
def create(name=typer.Argument(None, help='Group unique name'),
           label=typer.Argument(None, help='Group label')):
    """
    Create a group
    """
    group = models.Group(name=name, label=label)
    db.add(group)
    try:
        db.commit()
    except IntegrityError as e:
        print(f"Name MUST be unique {e.args}")
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)


@app.command()
def update(group_id=typer.Argument(None, help="Group ID"),
           name=typer.Option(None, help='Group unique name'),
           label=typer.Option(None, help='Group label')):
    """
    Update a group
    """
    group = models.Group.find_by_id(group_id)
    if not group:
        print("Session ID not found")
        exit(401)

    if name:
        group.name = name

    if label:
        group.label = label

    try:
        models.db_session.commit()
    except IntegrityError as e:
        print(f"Name MUST be unique {e.args}")
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)


@app.command()
def delete(group_id: int = typer.Argument(None, help='Group name'),
           force: bool = typer.Option(False, help="Force delete")):
    """Delete session"""

    group = models.Group.find_by_id(group_id)
    if group is None:
        print(f"Group '{group_id}' not found")
        exit()

    if force or Confirm.ask(f"Are you sure you want to delete '{group.label}'?"):
        models.Group.delete(group)
