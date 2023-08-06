import logging
import os
import sys

import click

from astronomer_ci.dockerhub import get_next_tag
from astronomer_ci.github import publish_release


def _configure_logging():
    level = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
    logging.basicConfig(stream=sys.stderr, level=level)


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    if debug:
        os.environ["DEBUG"] = "1"
    click.echo(f'Debug mode is {"on" if debug else "off"}')
    _configure_logging()


@cli.command()
@click.option(
    "--branch",
    required=True,
    help='The name of the release branch (e.g. "release-0.1")',
)
@click.option(
    "--repository",
    required=True,
    help='The name of the DockerHub repository (e.g. "astronomerinc"',
)
@click.option(
    "--image",
    required=True,
    help='The image to find the next version for (e.g. "ap-houston-api")',
)
def get_next_version(branch, repository, image):
    print(get_next_tag(branch, repository, image))


@cli.command()
@click.option(
    "--version",
    required=False,
    default=None,
    help='The name of version to release (e.g. "v1.0.0")',
)
@click.option(
    "--github-repository",
    required=True,
    help='The name of the GitHub repository (e.g. "houston-api")',
)
@click.option(
    "--github-organization",
    required=True,
    help='The name of the GitHub organization (e.g. "astronomer")',
)
@click.option(
    "--committish",
    required=True,
    help='The small Git commit hash ("committish") you want for the release',
)
def publish_github_release(version, github_repository, github_organization, committish):
    publish_release(version, github_repository, github_organization, committish)


# leave this here for backwards compatibility
def astronomer_next_version():
    get_next_version()


def main():
    cli()
