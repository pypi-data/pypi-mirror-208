import os
from random import randint
from subprocess import check_output
from time import sleep

from astronomer_ci.dockerhub import get_next_tag

REPOSITORY = "sjmiller609"
IMAGE = "test-image"


def _build_image(repository, image, tag):
    path = os.path.dirname(os.path.realpath(__file__))
    check_output(f"sudo docker build -t {repository}/{image}:{tag} {path}", shell=True)


def _push_image(repository, image, tag):
    check_output(f"sudo docker push {repository}/{image}:{tag}", shell=True)


def test_get_next_tag_no_tags():
    major = randint(0, 100000)
    minor = randint(0, 100000)
    branch = f"release-{major}.{minor}"
    expected_next_tag = f"{major}.{minor}.0"
    tag = get_next_tag(branch, REPOSITORY, IMAGE)
    assert tag == expected_next_tag, f"Error, expected next tag {expected_next_tag}"


def test_get_next_tag_pushed_most_recently():
    major = randint(0, 100000)
    minor = randint(0, 100000)
    patch = randint(0, 100000)
    branch = f"release-{major}.{minor}"

    for _ in range(0, 5):
        patch += 1
        tag = f"{major}.{minor}.{patch}"
        _build_image(REPOSITORY, IMAGE, tag)
        _push_image(REPOSITORY, IMAGE, tag)

    expected_next_tag = f"{major}.{minor}.{patch + 1}"
    sleep(5)
    tag = get_next_tag(branch, REPOSITORY, IMAGE)

    assert tag == expected_next_tag, f"Error, expected next tag {expected_next_tag}"


def test_get_next_tag_not_pushed_most_recently():
    major = randint(0, 100000)
    minor = randint(0, 100000)
    patch = randint(1000000, 10000000)
    # push the greatest patch number first
    tag = f"{major}.{minor}.{patch}"
    expected_next_tag = f"{major}.{minor}.{patch + 1}"
    branch = f"release-{major}.{minor}"
    _build_image(REPOSITORY, IMAGE, tag)
    _push_image(REPOSITORY, IMAGE, tag)
    for _ in range(0, 5):
        patch = randint(0, 10000)
        tag = f"{major}.{minor}.{patch}"
        _build_image(REPOSITORY, IMAGE, tag)
        _push_image(REPOSITORY, IMAGE, tag)
    sleep(5)
    tag = get_next_tag(branch, REPOSITORY, IMAGE)
    assert tag == expected_next_tag, f"Error, expected next tag {expected_next_tag}"
