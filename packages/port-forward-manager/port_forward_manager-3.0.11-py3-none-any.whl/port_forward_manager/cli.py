import os.path
import yaml
from sshconf import read_ssh_config
import pkg_resources
import simplejson
import typer
import time
from rich.prompt import Confirm
import rich

from .cli_autocomplete import sc_schemas, sc_hosts
from . import tools, forward_sessions, models, cli_group, cli_schema, cli_session, cli_ssh_group


app = typer.Typer(no_args_is_help=True)
app.add_typer(cli_group.app, name='group', help="Group management")
app.add_typer(cli_schema.app, name='schema', help="Schema management")
app.add_typer(cli_session.app, name='session', help="Session management")
app.add_typer(cli_ssh_group.app, name='ssh_group', help="SSH group management")
tools.load_settings()


@app.command()
def shutdown():
    """
    Stop all active sessions
    """

    settings = tools.settings()

    forward_sessions.update_state()
    for schema in models.Schema.index():
        for session in schema.sessions:
            if session.connected:
                forward_sessions.stop(session)
            session.active = False
        schema.active = False

    time.sleep(settings.wait_after_stop)
    forward_sessions.show_active_sessions()
    models.db_session.commit()


@app.command()
def status(schema: str = typer.Option(None, shell_complete=sc_schemas),
           host: str = typer.Option(None, shell_complete=sc_hosts),
           port: int = None,
           json: bool = typer.Option(False, '--json', '-j', help="Output JSON")):
    """
    Show active sessions
    """

    forward_sessions.show_active_sessions(schema, host, port)


@app.command()
def state():
    """
    Show current state in JSON format
    """

    ssh_config = read_ssh_config(os.path.expanduser("~/.ssh/config"))
    ssh_hosts = []
    for host in ssh_config.hosts():
        if "*" in host:
            continue
        hosts = host.split(" ")
        for hostname in hosts:
            ssh_hosts.append(hostname)

    forward_sessions.refresh_state()
    time.sleep(0.5)
    forward_sessions.update_state()
    current_state = {
        'groups': models.Group.get_state(),
        'schemas': models.Schema.get_state(),
        'sessions': models.Session.get_state(),
        'ssh_groups': models.SSHGroup.get_state(),
        'ssh_hosts': ssh_hosts
    }
    print(simplejson.dumps(current_state, indent=2))


@app.command()
def version():
    """
    Show PFM version
    """

    current_version = pkg_resources.get_distribution("port-forward-manager").version
    rich.print(f"Port Forward Manager [bold white]v{current_version}[/]")


@app.command()
def db_wipe():
    """Wipe the whole database clean"""
    if Confirm.ask("This action will wipe all groups, schemas and sessions, are you sure?"):
        models.reset_database()
        models.init_database()


@app.command()
def yaml_export(export_path: str = typer.Argument(None, help="YAML configuration file")):
    """Import groups, schemas and sessions from configuration file"""
    export_data = {
        'export_format': 'db_dump',
        'groups': models.Group.get_state(),
        'schemas': models.Schema.get_state(),
        'sessions': models.Session.get_state(),
        'ssh_groups': models.SSHGroup.get_state(),
    }

    yaml_string = yaml.dump(export_data)
    if export_path:
        tools.write_file(export_path, yaml_string)
    else:
        print(yaml_string)


@app.command()
def yaml_import(export_path: str = typer.Argument(..., help="YAML configuration file"),
                wipe: bool = typer.Option(False, help="Wipe DB")):
    """Import groups, schemas and sessions from configuration file"""
    settings = tools.load_yaml_file(export_path)

    change_count = 0

    if settings.get('export_format') != 'db_dump':
        rich.print("[red]Invalid export file format[/]")
        exit()

    if wipe:
        if Confirm.ask("This action will wipe all groups, schemas and sessions, are you sure?"):
            models.reset_database()
            models.init_database()

    rich.print("Importing PFM DB DUMP")
    groups = {}
    schemas = {}

    # Import groups
    for group_definition in settings.get('groups', []):
        group_name = group_definition.get('name')
        groups[group_definition.get('id')] = group_definition.get('name')
        group = models.Group.find_by_name(group_name)
        if not group:
            change_count += 1
            rich.print(f"* Importing group {group_name}")
            group = models.Group(name=group_name, label=group_definition.get('label'))
            models.Group.add(group)

    # Import schemas
    for schema_definition in settings.get('schemas', []):
        group_name = groups.get(schema_definition.get('group_id'))
        group = models.Group.find_by_name(group_name)
        if not group:
            rich.print(f"IGNORING schema - Error could not find group {group_name}")
            continue
        schemas[schema_definition.get('id')] = schema_definition.get('name')
        schema_name = schema_definition.get('name')

        schema = models.Schema.find_by_name(schema_name)
        if not schema:
            change_count += 1
            rich.print(f"* Importing schema {schema_name}")
            schema = models.Schema(name=schema_name,
                                   label=schema_definition.get('label'),
                                   active=False)

            group.schemas.append(schema)

    models.db_session.commit()

    # Import sessions
    for session_definition in settings.get('sessions'):
        schema_name = schemas.get(session_definition.get('schema_id'))
        schema = models.Schema.find_by_name(schema_name)
        if not schema:
            rich.print(f"IGNORING session - Error could not find schema '{schema_name}'")
            continue

        session_type = session_definition.get('type', 'local')
        hostname = session_definition.get('hostname')
        remote_port = session_definition.get('remote_port')
        if remote_port:
            remote_port = int(remote_port)

        session = schema.get_session(session_type, hostname, remote_port)
        if not session:
            change_count += 1
            print(f"    * Importing session {session_type} {hostname} {remote_port}")
            auto_start = session_definition.get('auto_start')
            if auto_start or auto_start == 'true':
                auto_start = True
            session = models.Session(label=session_definition.get('label'),
                                     type=session_type,
                                     active=False,
                                     hostname=session_definition.get('hostname'),
                                     remote_address=session_definition.get('remote_address', '127.0.0.1'),
                                     remote_port=session_definition.get('remote_port'),
                                     local_address=session_definition.get('local_address', '127.0.0.1'),
                                     local_port=session_definition.get('local_port'),
                                     local_port_dynamic=session_definition.get('local_port') is None,
                                     url_format=session_definition.get('url', ''),
                                     auto_start=auto_start)
            schema.sessions.append(session)

    # Import SSH groups
    for ssh_group in settings.get('sshGroups'):
        schema_name = schemas.get(ssh_group.get('schema_id'))
        schema = models.Schema.find_by_name(schema_name)
        if not schema:
            rich.print(f"IGNORING session - Error could not find schema '{schema_name}'")
            continue

        group_name = ssh_group.get('group_name')
        label = ssh_group.get('label')

        group = schema.get_ssh_group(group_name)
        if not group:
            change_count += 1
            print(f"    * Importing SSH group {group_name} {label}")

            group = models.SSHGroup(label=label, group_name=group_name)
            schema.ssh_groups.append(group)

    models.db_session.commit()

    if change_count == 0:
        rich.print("No changes...")
    else:
        rich.print("There were {} items imported.".format(change_count))


def run():
    # models.reset_database()
    models.init_database()
    app()


if __name__ == "__main__":
    app()
