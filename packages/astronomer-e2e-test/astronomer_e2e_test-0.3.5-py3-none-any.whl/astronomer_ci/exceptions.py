class AstroException(Exception):
    """Base exception"""

    pass


class BrokenScript(AstroException):
    """This script is not working
    as expected
    """

    pass


class InvalidConfiguration(AstroException):
    """Invalid configuration in the CI pipeline
    For example, trying to do release branch
    stuff on a non-release branch.
    """

    pass


class UnexpectedDockerhubBehavior(AstroException):
    """DockerHub is doing something unanticipated."""

    pass


class UnsafeBehavior(AstroException):
    """The script is aborting for safety
    reasons, for example to not overwrite
    existing data.
    """

    pass
