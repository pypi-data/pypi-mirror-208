import os

import api
import cli
from behave import given, then, when


@given("we have credentials")
def step_impl(context):
    context.email = os.getenv("ASTRO_USER")
    context.password = os.getenv("ASTRO_PASS")
    assert context.email is not None
    assert context.password is not None

    context.houstonURL = os.getenv("HOUSTON_URL")
    context.duration = 1800


@given("we are authenticated")
def step_impl(context):
    assert context.client.token is not None


@given("we have an API client")
def step_impl(context):
    assert context.client is not None


@when("we create an API client")
def step_impl(context):
    c = api.getClient(
        context.houstonURL, context.email, context.password, context.duration
    )
    assert c is not None
    context.client = c


@when("we create a CLI client")
def step_impl(context):
    c = cli.getClient(
        context.houstonURL, context.email, context.password, context.duration
    )
    assert c is not None
    context.client = c


@when("we login with the CLI")
def step_impl(context):
    c = cli.login(context.houstonURL, context.email, context.password, context.duration)
    assert c is not None
    context.client = c


@then("we get a valid token")
def step_impl(context):
    assert context.client.token is not None
