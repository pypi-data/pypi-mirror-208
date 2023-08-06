import logging
import os
import re
from subprocess import check_output

import git
import yaml
from github import Github

from astronomer_ci.exceptions import InvalidConfiguration, UnsafeBehavior


def _validate_version(version):
    version_regex = re.compile(r"(^v\d+\.\d+\.\d+-?(rc(\.\d+)?|alpha(\.\d+)?)?$)")
    if len(version) > 32:
        raise InvalidConfiguration(
            "A semantic version should not be longer than 32 characters."
        )
    if not version_regex.findall(version):
        raise InvalidConfiguration(
            f"The version provided {version}, does not"
            + f" match the pattern '{version_regex.pattern}'. You can"
            + " try it out on regex101.com, which existed at the"
            + " time of writing. A common issue is you forgot to add"
            + " a 'v' at the start of the version. It should look"
            + " something like this v1.2.3, this v1.2.3-rc.1, or this"
            + " v1.2.3-alpha.1"
        )


def _get_client():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise InvalidConfiguration(
            "Please provide the GITHUB_TOKEN environment variable"
        )
    return Github(token)


def _get_repo(repo, org, github_client=None):
    """Get the PyGithub repo object
    given the repo and org name
    """
    if not github_client:
        github_client = _get_client()
    logging.debug(f"Using {org}/{repo}")
    return github_client.get_repo(f"{org}/{repo}")


def generate_release_names(repo, org, github_client=None):
    """Generate releases for a Github
    repository, yielding the name
    of each tag.
    """
    repo = _get_repo(repo, org, github_client=github_client)
    logging.debug("Searching though releases...")
    for iteration, release in enumerate(repo.get_releases()):
        if not iteration % 10:
            logging.debug(f"Processed {iteration} releases...")
        tag = release.tag_name
        if tag != release.title:
            raise UnsafeBehavior(
                "Astronomer releases are expected to have a title "
                + f"matching the tag name. On {org}/{repo}, we found a release "
                + f"{release.title} with tag {tag}, and this is not expected. "
                + "Please manually resolve this issue."
            )
        try:
            _validate_version(tag)
        except InvalidConfiguration as invalid_config:
            raise UnsafeBehavior(
                f"Found a release with tag {tag} on {org}/{repo}."
                + "This is not an expected format for a release tag, "
                + "so this script is aborting to be safe. Please delete "
                + "that release and tag from the repository. See error: "
                + str(invalid_config)
            ) from invalid_config

        yield tag


def publish_release(
    version, repo, org, committish, pre_release=False, github_client=None
):
    """Safely deploy a release to Github"""
    # If 'version' is None, then check in the current directory for
    # Chart.yaml
    if not version:
        if not os.path.isfile("Chart.yaml"):
            raise InvalidConfiguration(
                "Either --version must be provided, or Chart.yaml must be in the current directory"
            )
        with open("Chart.yaml") as f:
            version = yaml.safe_load(f.read())["version"]
            version = f"v{version}"
    _validate_version(version)
    # First check that there are no releases
    # matching this release version
    for tag in generate_release_names(repo, org, github_client=github_client):
        if tag == version:
            raise UnsafeBehavior(
                f"We found an existing release with version {version}. Aborting!"
            )
    # Check that we are in a git repository
    _ = git.Repo().git_dir
    # Generate the release notes
    commits = check_output(
        'git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"* %ai %h: %s" | awk \'{$4=""; print $0}\'',
        shell=True,
    ).decode("utf-8")
    authors = check_output(
        "git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:\"%aE\" | awk '!a[$0]++'",
        shell=True,
    ).decode("utf-8")
    release_notes = f"## Changes:\n\n{commits}\n## Authors:\n{authors}"
    logging.debug(f"Generated release notes:\n{release_notes}")
    repo = _get_repo(repo, org, github_client=github_client)
    logging.debug(f"Publishing release {version}...")
    _ = repo.create_git_release(
        version,
        version,
        release_notes,
        draft=False,
        prerelease=pre_release,
        target_committish=committish,
    )
    logging.info(f"Published release {version}")
