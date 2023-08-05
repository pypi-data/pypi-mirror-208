import nox


@nox.session(python=["3.10", "3.11"])
def tests(session) -> None:  # pyright: ignore[reportMissingParameterType]
    """Run the test suite."""
    session.install("--upgrade", "pip")
    # session.install("-r", "requirements/requirements-test.txt")  # Does not work on <3.11 because of the hashes.
    session.install("pytest")
    session.install(".")
    session.run("pytest", "-v", "tests")

#     # Here we queue up the test coverage session to run next
#     session.notify("coverage")

# @nox.session
# def coverage(session):
#     session.install("coverage")
#     session.run("coverage")
