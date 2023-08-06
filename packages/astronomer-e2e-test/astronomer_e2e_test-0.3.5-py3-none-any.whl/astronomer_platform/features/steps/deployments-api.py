from api import deployments
from behave import given, then, when


@given("we have a deployment")
def step_impl(context):
    assert context.feature.deployment is not None


@when("(API) we list workspace deployments")
def step_impl(context):
    data = deployments.listing(context.client, context.feature.workspace["uuid"])
    assert data is not None

    d = data["data"]["workspaceDeployments"]
    assert d is not None

    context.deployments = d


@when('(API) we create a "{executor}" deployment "{label}" for "{description}"')
def step_impl(context, executor, label, description):
    data = deployments.create(
        context.client, context.feature.workspace["uuid"], executor, label, description
    )
    assert data is not None

    print("DATA", data)

    d = data["data"]["createDeployment"]
    assert d is not None

    context.feature.deployment = d


@when('(API) we create a "{executor}" deployment "{label}" with null workspaceUuid')
def step_impl(context, executor, label):
    data = deployments.create(
        context.client, None, executor, label, "null workspaceUuid"
    )
    assert data is not None

    # This should be an error
    print("DATA", data)

    # e = data['data']['createDeployment']
    # assert e is not None

    # context.feature.error = e


@when('(API) we delete a deployment "{label}"')
def step_impl(context, label):
    context.deploymentDeleted = False
    data = deployments.delete(context.client, context.feature.deployment["uuid"])
    assert data is not None

    d = data["data"]["deleteDeployment"]
    assert d is not None

    assert context.feature.deployment["uuid"] == d["uuid"]

    del context.feature.deployment
    context.deploymentDeleted = True


@then("a new deployment is returned")
def step_impl(context):
    assert context.feature.deployment is not None


@then("No deployment is returned")
def step_impl(context):
    assert context.feature.deployment is not None


@then("the deployment was deleted")
def step_impl(context):
    assert context.deploymentDeleted is True


@then("a deployment list is returned")
def step_impl(context):
    assert type(context.deployments) is list


@then('deployment length is equal to "{length}"')
def step_impl(context, length):
    assert len(context.deployments) == int(length)
