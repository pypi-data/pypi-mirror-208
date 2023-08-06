from behave import when
from cli import deployments


@when('(CLI) we create a "{executor}" deployment "{name}" for "{description}"')
def step_impl(context, executor, name, description):
    output = deployments.create(context.client, name, description, executor)
    assert output is not None
    print("OUTPUT", output)

    lines = output.splitlines()
    print("LINES-PRE", lines)
    # Trim header
    line = lines[1]
    print("LINES-POST", lines)

    fields = line.split()
    d = {"name": fields[0], "uuid": fields[3]}

    print("DEPLOYMENT", d)

    context.feature.deployment = d


@when('(CLI) we delete a deployment "{name}"')
def step_impl(context, name):
    context.deploymentDeleted = False
    output = deployments.delete(context.client, context.feature.deployment["uuid"])
    assert output is not None

    context.deploymentDeleted = True
