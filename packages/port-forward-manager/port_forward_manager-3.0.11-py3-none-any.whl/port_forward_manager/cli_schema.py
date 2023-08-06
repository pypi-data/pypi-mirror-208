import time

import rich
from rich.table import Table
from rich.prompt import Confirm
import typer
from sqlalchemy.exc import IntegrityError
from . import database, models, tools, forward_sessions
from .cli_autocomplete import ac_schemas, ac_active_schemas, sc_active_hosts, sc_active_remote_port
from .cli_session import prepare_sessions_table
from .forward_sessions import show_active_sessions
from sqlalchemy.orm.session import make_transient

app = typer.Typer(no_args_is_help=True)
db = database.SessionLocal()


def prepare_schema_table(show_alias: bool = False, show_link: bool = False, show_schema: bool = True, title: str = 'Schemas'):

    table = Table(show_edge=False)

    table.add_column("#", justify="right", style="green", width=3)
    table.add_column("Group", justify="left", style="yellow", width=20)
    table.add_column("Schema name", justify="left", style="yellow", width=30)
    table.add_column("Schema label", justify="right", style="yellow", width=30)

    return table


@app.command()
def create(group_id: int = typer.Argument(..., help='Group name'),
           schema_name: str = typer.Argument(..., help='Schema unique name'),
           label: str = typer.Argument(..., help='Schema label')):
    """
    Create a schema
    """
    group = models.Group.find_by_id(group_id)
    if group is None:
        print(f"Group '{group_id}' doesn't exist")
        exit(401)

    if models.Schema.find_by_name(schema_name):
        print(f"Schema '{schema_name}' already exists")
        exit(401)

    schema = models.Schema(name=schema_name, label=label, group_id=group.id)
    group.schemas.append(schema)

    models.db_session.commit()


@app.command()
def update(schema_id: int = typer.Argument(..., help='Schema ID'),
           group_id: int = typer.Option(None, help='Group ID'),
           name: str = typer.Option(None, help='Schema unique name'),
           label: str = typer.Option(None, help='Schema label')):
    """
    Create a schema
    """
    schema = models.Schema.find_by_id(schema_id)
    if schema is None:
        print(f"Schema '{schema_id}' doesn't exist")
        exit(401)

    if group_id:
        group = models.Group.find_by_id(group_id)
        if not group:
            print("Group is invalid")
        else:
            schema.group_id = group_id

    if name:
        schema.name = name

    if label:
        schema.label = label

    models.db_session.commit()


@app.command()
def index(schema_filter: str = typer.Argument(None, autocompletion=ac_schemas)):
    """
    List configured schemas
    """
    settings = tools.settings()
    table = prepare_schema_table(True, settings.show_schema_link, True)

    for schema in models.Schema.index(schema_filter):
        if schema.group_id is None:
            print(f"Schema #{schema.id} group is INVALID")
            row = [
                str(schema.id),
                'INVALID GROUP',
                schema.name,
                schema.label,
            ]
        else:
            row = [
                str(schema.id),
                schema.group.name,
                schema.name,
                schema.label,
            ]
        table.add_row(*row)

    if table.row_count > 0:
        table.rows[table.row_count - 1].end_section = True

    rich.print(table)


@app.command()
def clone(schema_id: int = typer.Argument(..., help='Schema ID'),
          group_id: int = typer.Option(None, help='Group ID'),
          name: str = typer.Option(None, help='Schema name'),
          label: str = typer.Option(None, help='Schema label'),):

    schema_original = models.Schema.find_by_id(schema_id)
    if schema_original is None:
        print(f"Schema {schema_id} not found")
        exit(3)

    if group_id is None:
        group_id = schema_original.group_id

    group = models.Group.find_by_id(group_id)
    if not group:
        print(f"Group {group_id} not found")
        exit(3)

    print(f"Clone schema {schema_original.name}")
    if not name:
        name = f"{schema_original.name}_clone"

    if not label:
        label = f"{schema_original.label} clone"
    schema_clone = models.Schema(name=name, label=label)
    group.schemas.append(schema_clone)

    for session_original in schema_original.sessions:
        session_clone = models.Session.clone(session_original)
        schema_clone.sessions.append(session_clone)

    models.db_session.commit()


@app.command()
def delete(schema_id: int = typer.Argument(None, help='Schema ID'),
           force: bool = typer.Option(False, help="Force delete")):
    """Delete session"""

    schema = models.Schema.find_by_id(schema_id)
    if schema is None:
        print("Schema not found")
        exit()

    if force or Confirm.ask(f"Are you sure you want to delete '{schema.label}'?"):
        models.Schema.delete(schema)


@app.command()
def sessions(schema_filter: str = typer.Argument(None, autocompletion=ac_schemas)):
    """
    List configured schemas
    """
    settings = tools.settings()
    table = prepare_sessions_table()

    for schema in models.Schema.index(schema_filter):
        for session in schema.sessions:
            row = [
                str(schema.id),
                schema.name,
                session.hostname,
                session.type,
                session.local_address,
                '-----' if session.local_port_dynamic else session.local_port.__str__(),
                session.remote_address,
                session.remote_port.__str__(),
                session.label
            ]
            table.add_row(*row)
        if table.row_count > 0:
            table.rows[table.row_count - 1].end_section = True

    rich.print(table)


@app.command()
def start(schema_name: str = typer.Argument(..., autocompletion=ac_schemas),
          force: bool = typer.Option(None, help="Force sessions reconnection")):
    """
    Start a schema of forwarding sessions
    """
    settings = tools.settings()
    forward_sessions.update_state()

    schema = models.Schema.find_by_name(schema_name)
    schema.active = True

    if schema is None:
        print("[b]Schema '{0}' is unknown[/b]".format(schema_name))
        exit(-1)

    for session in schema.sessions:
        session.schema_id = schema.id
        forward_sessions.start(session, force)
        session.active = True

    time.sleep(settings.wait_after_start)
    show_active_sessions()
    models.db_session.commit()


@app.command()
def stop(schema_name: str = typer.Argument(None, autocompletion=ac_active_schemas),
         hostname: str = typer.Option(None, shell_complete=sc_active_hosts),
         port: str = typer.Option(None, shell_complete=sc_active_remote_port)):
    """
    Stop sessions from active schema, host or port
    """

    if not schema_name and not hostname and not port:
        print("[b]Pick a schema, host or host and port or --all[/b]")
        exit(-1)

    settings = tools.settings()
    forward_sessions.update_state()

    if schema_name:
        schema = models.Schema.find_by_name(schema_name)
        for session in schema.sessions:

            forward_sessions.stop(session)
            session.active = False
        schema.active = False

    time.sleep(settings.wait_after_stop)
    show_active_sessions()
    models.db_session.commit()
