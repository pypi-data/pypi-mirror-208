from . import forward_sessions, models
from click.shell_completion import CompletionItem
from sshconf import read_ssh_config
from os.path import expanduser


def sc_schemas(ctx, param, incomplete):
    schemas = models.Schema.index()
    result = []

    for schema_name in schemas:
        if not schema_name.startswith(incomplete):
            continue

        schema = schemas.get(schema_name)
        item = CompletionItem(schema_name, help=f"{len(schema)} session(s) for {schema_name}")
        result.append(item)
    return result


def ac_schemas(incomplete):
    schemas = models.Schema.index()
    result = []

    for schema in schemas:
        if not schema.name.startswith(incomplete):
            continue

        item = (schema.name, f"{len(schema.sessions)} session(s) for {schema.name}")
        result.append(item)
    return result


def sc_active_schemas(ctx, param, incomplete):
    return forward_sessions.list_from_active('schema', incomplete)


def ac_active_schemas(incomplete):
    items = []
    for schema in models.Schema.index():
        if schema.active and schema.name not in items:
            items.append(schema.name)

    return items


def sc_active_remote_port(ctx, param, incomplete):
    return forward_sessions.list_from_active('remote_port')


def sc_active_hosts(ctx, param, incomplete):
    return forward_sessions.list_from_active('hostname')


def ac_hosts(incomplete):
    result = []
    c = read_ssh_config(expanduser("~/.ssh/config"))
    for host in c.hosts():
        if "*" not in host and host.startswith(incomplete):
            hosts = host.split(" ")
            for hostname in hosts:
                result.append(hostname)

    return result


def sc_hosts(ctx, param, incomplete):
    from sshconf import read_ssh_config
    from os.path import expanduser
    result = []
    c = read_ssh_config(expanduser("~/.ssh/config"))
    for host in c.hosts():
        if "*" not in host and host.startswith(incomplete):
            hosts = host.split(" ")
            for hostname in hosts:
                item = CompletionItem(hostname)
                result.append(item)

    return result
