"""Autonomous Data Collector  Agent entry point script."""

from autonomous_data_collection_agent import cli, __app_name__


def main():
    # The line `cli.app(prog_name=__app_name__)` is calling the `app` function from the `cli` module.
    # The `app` function is responsible for running the command-line interface (CLI) for the
    # Autonomous Data Collector Agent. The `prog_name` argument is used to set the name of the program
    # that appears in the help messages and error messages. In this case, it is set to the value of
    # the `__app_name__` variable, which is "autonomous_data_collection_agent".
    cli.app(prog_name=__app_name__)


if __name__ == "__main__":
    main()
