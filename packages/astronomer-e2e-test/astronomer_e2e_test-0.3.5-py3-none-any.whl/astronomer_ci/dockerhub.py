#!/usr/bin/env python3
"""
This file is for functions related to
DockerHub and parsing tags from DockerHub.

This is used in Astronomer's automation.
"""
import json
import logging
import re

import packaging
import requests
from packaging.version import parse as semver

from astronomer_ci.exceptions import (
    BrokenScript,
    InvalidConfiguration,
    UnexpectedDockerhubBehavior,
)


def get_next_tag(branch, repository, image):
    """
    Args:
        branch (str): The release branch name
        repository (str): The DockerHub repository name
        image (str): The DockerHub image name

    Returns (str): The next major.minor.patch version for this image
    """

    major_minor_version = _parse_major_minor_from_release_branch(branch)
    logging.info(
        f"We are on a release branch: {branch}, detected major.minor version {major_minor_version}"
    )
    logging.info(
        f"We will find the most recent patch version of {major_minor_version} "
        + f"for {repository}/{image} and return it incremented by one"
    )

    # Get all the tags from Dockerhub
    # order is not assured in any way
    tags = _get_tags(repository, image)
    # Find the greatest patch version with the major, minor
    # version we are using.
    greatest_patch_version = _get_greatest_patch_version(tags, major_minor_version)
    # Increment the greatest patch version
    new_patch_version = greatest_patch_version + 1
    # Format the new version
    new_version = ".".join(
        str(i) for i in [*major_minor_version.split("."), new_patch_version]
    )
    logging.info(f"Determined the next version should be {new_version}")

    new_tag_regex = re.compile(r"\d+\.\d+\.\d+")
    logging.debug(
        f"Sanity checking that the new version matches regex '{new_tag_regex.pattern}'"
    )
    if not new_tag_regex.findall(new_version):
        raise BrokenScript(
            f"Error, did not produce a new tag in the form {new_tag_regex.pattern}"
        )

    return new_version


def _get_tags(repository, image):
    """Normally this would be done with a generator,
    but the order of tags is not consistent, so we
    need to grab all of them to make the result
    deterministic.
    """
    logging.info(f"Fetching versions of {repository}/{image} from DockerHub")
    tag_list = []
    for i in range(1, 1001):
        url = f"https://registry.hub.docker.com/v2/repositories/{repository}/{image}/tags/?page_size=100&page={i}"
        logging.debug(f"Sending request to {url}")
        response = requests.get(url)
        logging.debug(f"Got HTTP {response.status_code}")
        if not response.ok:
            logging.debug("No tags found in this request, done paginating.")
            logging.debug(f"Found tags: {tag_list}")
            return tag_list
        content = json.loads(response.content)
        if content.get("results"):
            names = [tag["name"] for tag in content["results"]]
            tag_list.extend(names)
        logging.debug(f"Found {len(tag_list)} tags so far")
    raise UnexpectedDockerhubBehavior(
        "Did not expect to paginate more than 1000 times."
    )


def _parse_major_minor_from_release_branch(branch):
    release_regex = re.compile(r"release-(\d+\.\d+)")
    logging.debug(
        f"Parsing major, minor version using regex '{release_regex.pattern}' from branch name '{branch}'"
    )
    major_minor_version = release_regex.findall(branch)
    if not len(major_minor_version):
        raise InvalidConfiguration(
            f"Expected branch name matching pattern {release_regex.pattern}"
        )
    logging.debug(f"Parsed '{major_minor_version[0]}' from branch name")
    return major_minor_version[0]


def _get_greatest_patch_version(tags, major_minor_version):
    """
    We are doing a brute-force search rather than searching across a sorted
    list because for this use case, it's better to be safe than to be wrong
    and the marginal improvement is not significant.
    """
    greatest_patch_version = -1
    for tag in tags:
        # skip any tags that do not have at least two dots in them
        if tag.count(".") < 2:
            logging.warning(f"Skipping non semver tag {tag}")
            continue
        # skip any tags not parsed as a semantic version
        try:
            version = semver(tag).release
            if not version:
                raise packaging.version.InvalidVersion
        except packaging.version.InvalidVersion:
            logging.warning(f"Skipping unpraseable semver-ish tag {tag}")
            continue

        this_major_minor = f"{version[0]}.{version[1]}"
        if this_major_minor == major_minor_version:
            logging.debug(f"The version {tag} has a matching major / minor version")
            patch_version = version[2]
            if patch_version > greatest_patch_version:
                logging.debug(
                    f"Now the greatest patch version so far is {patch_version}"
                )
                greatest_patch_version = patch_version
    if greatest_patch_version >= 0:
        logging.debug(
            f"The greatest existing patch version is {greatest_patch_version}"
        )
    else:
        logging.debug(
            f"Did not detect any existing patch version for {major_minor_version}, returning -1"
        )
    return greatest_patch_version
