import os

import api
import cli
from behave import *  # noqa F403


def before_tag(context, tag):
    if tag == "withAPI":
        email = os.getenv("ASTRO_USER")
        password = os.getenv("ASTRO_PASS")
        assert email is not None
        assert password is not None

        houstonURL = os.getenv("HOUSTON_URL")
        duration = 1800

        c = api.getClient(houstonURL, email, password, duration)
        assert c is not None
        context.client = c

    if tag.startswith("withWorkspace."):
        print("withWorkspace NOT IMPLEMENTED")

    if tag == "withCLI":
        email = os.getenv("ASTRO_USER")
        password = os.getenv("ASTRO_PASS")
        assert email is not None
        assert password is not None

        houstonURL = os.getenv("HOUSTON_URL")
        duration = 1800

        c = cli.getClient(houstonURL, email, password, duration)
        assert c is not None
        context.client = c

    if tag.startswith("withDeployment."):
        print("withDeployment NOT IMPLEMENTED")
        assert True is False

    if tag == "withTMP":
        print("withTMP NOT IMPLEMENTED")
        assert True is False
