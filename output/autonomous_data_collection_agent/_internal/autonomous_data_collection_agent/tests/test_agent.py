import os
import pytest
from typer.testing import CliRunner
from autonomous_data_collection_agent import (
    __app_name__,
    __version__,
    cli,
    autonomousagent
)

# Create a Pytest fixture to set up a CliRunner
# @pytest.fixture
# def runner():
#     return CliRunner()

# `runner = CliRunner()` is creating an instance of the `CliRunner` class from the `typer.testing`
# module. This `CliRunner` instance is used to invoke the command-line interface (CLI) commands
# defined in the `cli` module. It allows for testing the CLI commands in an isolated environment
# without actually running the application.

runner = CliRunner()

def test_enable_threading_default():
    """
    The function tests if threading is enabled by checking the output of the "enable-threading" command.
    """
    result = runner.invoke(cli.app,["enable-threading", "-e", "True"])
    assert result.exit_code == 0
    assert "Threading is set to enabled." in result.output

def test_enable_threading_disabled():
    """
    The function `test_enable_threading_disabled` tests if the threading is disabled when the
    `enable-threading` command is invoked with the `-e` flag set to `False`.
    """
    result = runner.invoke(cli.app,["enable-threading", "-e", "False"])
    assert result.exit_code == 0
    assert "Threading is set to disabled." in result.output

def test_set_concurrent_threads():
    """
    The function `test_set_concurrent_threads` tests the functionality of setting the concurrent threads
    count to 4.
    """
    result = runner.invoke(cli.app,["set-concurrent-threads", "4", "-f"])
    assert result.exit_code == 0
    assert "Set Concurrent Threads Count to : 4" in result.output

def test_enable_encryption_disabled():
    """
    The function tests if encryption is disabled.
    """
    result = runner.invoke(cli.app, ["enable-encryption", "--enabled", "False"])
    assert result.exit_code == 0
    assert "Encryption is set to disabled." in result.output

def test_enable_encryption_default():
    """
    The function `test_enable_encryption_default` tests whether encryption is successfully enabled.
    """
    result = runner.invoke(cli.app, ["enable-encryption"])
    assert result.exit_code == 0
    assert "Encryption is set to enabled." in result.output

def test_reset_encryption_key():
    """
    The function `test_reset_encryption_key` tests the functionality of resetting an encryption key.
    """
    result = runner.invoke(cli.app, ["reset-encryption-key"], input="y\n")
    assert result.exit_code == 0
    assert "Encryption key is reset." in result.output

def test_check_encryption_enabled():
    """
    The function `test_check_encryption_enabled` tests whether encryption is enabled.
    """
    result = runner.invoke(cli.app, ["check-encryption"])
    assert result.exit_code == 0
    assert "Encryption is" in result.output

def test_add_application():
    """
    The function `test_add_application` tests the functionality of adding a new application using the
    command line interface.
    """
    result = runner.invoke(
        cli.app, ["add-app", "SampleApp", "--short-name", "sampleapp", "--host", "example.com", "--dump-path", "D:\\scrapped_data\\also"]
    )
    assert result.exit_code == 0
    assert "Application 'SampleApp' was added" in result.output

def test_add_application2():
    """
    The function `test_add_application2` tests the functionality of adding an application with updated
    information.
    """
    result = runner.invoke(
        cli.app, ["add-app", "UpdatedApp", "--short-name", "updatedapp", "--host", "exampleupdate.com", "--dump-path", "D:\\scrapped_data\\updated"]
    )
    assert result.exit_code == 0
    assert "Application 'UpdatedApp' was added" in result.output

@pytest.fixture
def sample_application_id()-> str:
    """
    The function `sample_application_id` returns the application ID of a sample application.
    :return: The fixture `sample_application_id` is returning the application ID of the "sampleapp"
    autonomous agent.
    """
    return autonomousagent.get_application_id_by_short_name("sampleapp")

def test_update_application(sample_application_id):
    """
    The function `test_update_application` tests the functionality of updating an application with
    various parameters.
    
    :param sample_application_id: The `sample_application_id` parameter is the unique identifier of the
    application that you want to update. It is used to specify which application should be updated with
    the provided parameters
    """
    result = runner.invoke(cli.app, [
        "update-app",
        sample_application_id,
        "--name", "New Name",
        "--host", "new-host",
        "--url-scheme", "https",
        "--auth-type", "BASIC",
        "--dump-path", "/path/to/dump",
        "--sync-frequency", "*/30 * * * *",
        "--last-sync", "01-01-2023 12:00:00",
        "--next-sync", "01-02-2023 12:00:00",
        "--default-page-size", "1000",
        "--process-status", "1",
        "--status", "1"
    ])
    assert result.exit_code == 0
    assert "Application 'New Name' was updated successfully." in result.output

def test_list_applications():
    """
    The function `test_list_applications` tests the functionality of the `list-apps` command in a CLI
    application.
    """
    result = runner.invoke(cli.app, ["list-apps"])
    assert result.exit_code == 0
    assert "Application List:" in result.output

def test_get_application(sample_application_id):
    """
    The function `test_get_application` tests the `get-app` command of a CLI application by invoking it
    with a sample application ID and asserting that the exit code is 0 and the output contains the
    string "Application List:".
    
    :param sample_application_id: The `sample_application_id` parameter is the ID of a specific
    application that you want to retrieve. It is used as an argument when invoking the `cli.app` command
    with the `get-app` subcommand
    """
    result = runner.invoke(cli.app, ["get-app", sample_application_id])
    assert result.exit_code == 0
    assert "Application List:" in result.output

def test_add_endpoint():
    """
    The function `test_add_endpoint` tests the functionality of adding an endpoint to a sample app.
    """
    result = runner.invoke(cli.app, [
        "add-endpoint",
        "Sample Endpoint",
        "--app-name", "sampleapp",
        "--endpoint", "sample-api-endpoint",
        "--method", "GET",
        "--page-size", "100",
    ])
    assert result.exit_code == 0
    assert "was added" in result.output

@pytest.fixture
def sample_endpoint_id():
    """
    The function `sample_endpoint_id` returns the endpoint ID of a sample endpoint.
    :return: The function `sample_endpoint_id()` is returning the endpoint ID of the endpoint named
    "Sample Endpoint".
    """
    return autonomousagent.get_endpoint_id_by_name("Sample Endpoint")

def test_list_endpoints():
    """
    The function `test_list_endpoints` tests the functionality of the `list-endpoints` command in a
    Python CLI application.
    """
    result = runner.invoke(cli.app, ["list-endpoints"])
    assert result.exit_code == 0
    assert "Endpoint List" in result.output

def test_get_endpoint(sample_endpoint_id):
    """
    The function `test_get_endpoint` tests the functionality of the `get-endpoint` command in a CLI
    application.
    
    :param sample_endpoint_id: The `sample_endpoint_id` is a parameter that represents the ID of a
    specific endpoint. It is used as an input to the `get-endpoint` command in the `cli.app` module
    """
    result = runner.invoke(cli.app, ["get-endpoint", sample_endpoint_id])
    assert result.exit_code == 0
    assert f"Endpoint List:" in result.output

def test_get_endpoint_by_name():
    """
    The function `test_get_endpoint_by_name` tests the functionality of the `get-endpoint-by-name`
    command in a CLI application.
    """
    result = runner.invoke(cli.app, ["get-endpoint-by-name", "Sample Endpoint"])
    assert result.exit_code == 0
    assert "Endpoint List:" in result.output

def test_generate_fake():
    """
    The function `test_generate_fake` tests the successful generation of random application data and
    endpoint data.
    """
    result = runner.invoke(cli.app, ["generate-fake", "--apps", "5", "--endpoints", "10"])
    assert result.exit_code == 0
    assert "Random Application Data and endpoint data generated successfully!" in result.output

# def test_fake_server():
#     result = runner.invoke(cli.app, "run-fake-server")
#     assert result.exit_code == 0

def test_test_scheduler():
    """
    The function `test_test_scheduler()` tests the `test-scheduler` command in the `cli` module.
    """
    result = runner.invoke(cli.app, "test-scheduler")
    assert result.exit_code == 0  # You may need to adjust the expected exit code

def test_update_endpoint(sample_endpoint_id):
    """
    The function `test_update_endpoint` tests the functionality of updating an endpoint with a new app
    name.
    
    :param sample_endpoint_id: The `sample_endpoint_id` parameter is the ID of the endpoint that you
    want to update. It is used as an argument when invoking the `update-endpoint` command
    """
    result = runner.invoke(cli.app, [
        "update-endpoint",
        sample_endpoint_id,
        "--app-name", "updatedapp",
    ])
    assert result.exit_code == 0
    assert "updated successfully" in result.output

def test_remove_endpoint(sample_endpoint_id):
    """
    The function `test_remove_endpoint` tests the functionality of removing an endpoint using the
    command line interface.
    
    :param sample_endpoint_id: The `sample_endpoint_id` parameter is the ID of the endpoint that you
    want to remove. It is used as an argument when invoking the `remove-endpoint` command in the CLI
    """
    result = runner.invoke(cli.app, [
        "remove-endpoint",
        sample_endpoint_id,
        "--force"
    ])
    assert result.exit_code == 0
    assert "was removed" in result.output

def test_remove_app_endpoints():
    """
    The function `test_remove_app_endpoints` tests the functionality of removing endpoints for a sample
    app.
    """
    result = runner.invoke(cli.app, [
        "remove-app-endpoints",
        "sampleapp",
        "--force"
    ])
    assert result.exit_code == 0
    assert "was removed" in result.output

def test_clear_endpoints():
    """
    The function `test_clear_endpoints` tests the functionality of the `clear-endpoints` command in a
    CLI application.
    """
    result = runner.invoke(cli.app, ["clear-endpoints", "--force"])
    assert result.exit_code == 0
    assert "All endpoints were removed" in result.output

def test_get_app_by_name():
    """
    The function `test_get_app_by_name` tests the functionality of the `get-app-by-name` command in the
    CLI by asserting that the exit code is 0 and that the output does not contain the error message
    "Getting application # 'UpdatedApp' failed".
    """
    result = runner.invoke(cli.app, ["get-app-by-name", "UpdatedApp"])
    assert result.exit_code == 0
    assert "Getting application # 'UpdatedApp' failed" not in result.output

def test_get_app_by_short_name():
    """
    The function `test_get_app_by_short_name` tests the functionality of the `get-app-by-short-name`
    command in the CLI by checking if the command executes successfully and if the output does not
    contain an error message.
    """
    result = runner.invoke(cli.app, ["get-app-by-short-name","updatedapp"])
    assert result.exit_code == 0
    assert "Getting application # 'updatedapp' failed" not in result.output

def test_get_app_by_status():
    """
    The function `test_get_app_by_status` tests the functionality of the `get-app-by-status` command in
    the CLI by asserting that the exit code is 0 and that the output does not contain the error message
    "Getting application # 1 failed with status:".
    """
    result = runner.invoke(cli.app, ["get-app-by-status","1"])
    assert result.exit_code == 0
    assert "Getting application # 1 failed with status:" not in result.output

def test_get_app_by_process_status():
    """
    The function `test_get_app_by_process_status` tests the `get-app-by-process-status` command of a CLI
    application and checks that it does not fail with a specific status.
    """
    result = runner.invoke(cli.app, ["get-app-by-process-status", "1"])
    assert result.exit_code == 0
    assert "Getting application # 1 failed with status:" not in result.output

def test_update_app_status(sample_application_id):
    """
    The function `test_update_app_status` tests the functionality of updating the status of a sample
    application.
    
    :param sample_application_id: The `sample_application_id` parameter is the ID of the application
    that you want to update the status for. It is used as an argument when invoking the `cli.app`
    command to update the application status
    """
    result = runner.invoke(cli.app, ["update-app-status", sample_application_id, "--status", "0"])
    assert result.exit_code == 0
    assert f"Application # {sample_application_id} updated successfully with status:" in result.output

def test_update_app_process_status(sample_application_id):
    """
    The function `test_update_app_process_status` tests the functionality of updating the process status
    of a sample application.
    
    :param sample_application_id: The `sample_application_id` parameter is the ID of the application
    that you want to update the process status for
    """
    result = runner.invoke(cli.app, ["update-app-process-status", sample_application_id, "--process-status", "2"])
    assert result.exit_code == 0
    assert f"Application # {sample_application_id} updated successfully with status:" in result.output

def test_remove_app(sample_application_id):
    """
    The function `test_remove_app` tests the functionality of removing an application using the command
    line interface.
    
    :param sample_application_id: The `sample_application_id` parameter is the ID of the application
    that you want to remove. It is used as an argument when invoking the `remove-app` command in the CLI
    """
    result = runner.invoke(cli.app, ["remove-app", sample_application_id, "--force"])
    assert result.exit_code == 0
    assert f"Application # {sample_application_id} was removed" in result.output

def test_clear_apps():
    """
    The function `test_clear_apps` tests the functionality of the `clear-apps` command by asserting that
    the exit code is 0 and that the output contains the message "All applications were removed".
    """
    result = runner.invoke(cli.app, ["clear-apps", "--force"])
    assert result.exit_code == 0
    assert "All applications were removed" in result.output

def test_version_callback():
    """
    The function `test_version_callback` checks if the output of the command `--version` contains the
    current version of the application.
    """
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__version__}" in result.output

def test_main():
    """
    The function `test_main()` runs a command line interface (CLI) application and asserts that the exit
    code is 0.
    """
    result = runner.invoke(cli.app)
    assert result.exit_code == 2  # You may need to adjust the expected exit code