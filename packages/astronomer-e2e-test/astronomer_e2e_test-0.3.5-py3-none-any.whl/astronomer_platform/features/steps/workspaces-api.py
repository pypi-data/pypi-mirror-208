from api import workspaces
from behave import given, then, when


@given("we have a workspace")
def step_impl(context):
    assert context.feature.workspace is not None


@when("(API) we list workspaces")
def step_impl(context):
    data = workspaces.listing(context.client)
    assert data is not None

    w = data["data"]["workspaces"]
    assert w is not None

    context.workspaces = w


@when('(API) we create a workspace "{label}" for "{description}"')
def step_impl(context, label, description):
    data = workspaces.create(context.client, label, description)
    assert data is not None

    w = data["data"]["createWorkspace"]
    assert w is not None

    context.feature.workspace = w


@when("(API) we delete a workspace")
def step_impl(context):
    context.workspaceDeleted = False
    data = workspaces.delete(context.client, context.feature.workspace["uuid"])
    assert data is not None

    w = data["data"]["deleteWorkspace"]
    assert w is not None

    assert context.feature.workspace["uuid"] == w["uuid"]
    context.workspaceDeleted = True


@then("a new workspace is returned")
def step_impl(context):
    assert context.feature.workspace is not None


@then("the workspace was deleted")
def step_impl(context):
    assert context.workspaceDeleted is True


@then("a workspace list is returned")
def step_impl(context):
    assert type(context.workspaces) is list


@then('workspace length is equal to "{length}"')
def step_impl(context, length):
    assert len(context.workspaces) == int(length)
