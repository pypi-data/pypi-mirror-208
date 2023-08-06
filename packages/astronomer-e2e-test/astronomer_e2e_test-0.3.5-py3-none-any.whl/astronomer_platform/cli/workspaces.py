from .client import cliRun


def listing():
    _, output = cliRun(["workspace", "list"])
    return output


def setActive(client, uuid):
    _, output = cliRun(["workspace", "switch", uuid])
    return output


def create(client, name, description):
    _, output = cliRun(["workspace", "create", name])
    return output


def delete(client, uuid):
    _, output = cliRun(["workspace", "delete", uuid])
    return output
