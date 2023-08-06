from behave import when
from cli import workspaces


@when("(CLI) we list workspaces")
def step_impl(context):
    output = workspaces.listing()
    assert output is not None

    lines = output.splitlines()
    print("LINES-PRE", lines)
    # Trim header
    lines = lines[1:]
    print("LINES-POST", lines)

    W = []
    for line in lines:
        fields = line.split()
        w = {"name": fields[0], "uuid": fields[1]}
        W.push(w)

    print("WORKSPACES", W)

    context.workspaces = W


@when('(CLI) we can switch to workspace "{name}"')
def step_impl(context, name):
    context.workspaceDeleted = False
    w = context.feature.workspace
    output = workspaces.setActive(context.client, w["uuid"])
    assert output is not None

    context.workspaceDeleted = True


@when('(CLI) we create a workspace "{label}" for "{description}"')
def step_impl(context, label, description):
    output = workspaces.create(context.client, label, description)
    assert output is not None

    lines = output.splitlines()
    print("LINES-PRE", lines)
    # Trim header
    line = lines[1]
    print("LINES-POST", lines)

    fields = line.split()
    w = {"name": fields[0], "uuid": fields[1]}

    print("WORKSPACE", w)

    context.feature.workspace = w


@when("(CLI) we delete a workspace")
def step_impl(context):
    context.workspaceDeleted = False
    output = workspaces.delete(context.client, context.feature.workspace["uuid"])
    assert output is not None

    context.workspaceDeleted = True
