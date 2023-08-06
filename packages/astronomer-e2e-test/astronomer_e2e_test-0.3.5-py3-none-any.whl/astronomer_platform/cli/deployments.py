from .client import cliRun


def listing(client, workspace):
    process, output = cliRun(["deployment", "list"])
    return output


def create(client, name, description, executor):
    args = ["deployment", "create", name, "-e", executor]
    print("ARGS", args)
    process, output = cliRun(args)
    print("RETURN", process, output)
    return output


def delete(client, uuid):
    process, output = cliRun(["deployment", "delete", uuid])
    return output
