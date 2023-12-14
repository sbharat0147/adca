"""This module provides the Autonomous Data Collector Agent CLI."""

# The below code is importing various modules and classes from the `autonomous_data_collection_agent`
# package and other Python standard libraries. It also imports the `Enum` class from the `enum`
# module.
import typer
from datetime import datetime
from autonomous_data_collection_agent import ERRORS, __app_name__, __version__, autonomousagent, config, database, random_data, raw_api
from enum import Enum
from autonomous_data_collection_agent.database import DatabaseHandler
from autonomous_data_collection_agent.fileencryption import FileEncryption
# from autonomous_data_collection_agent.scheduler_simple import SchedulerService
import os
import logging  # Import the logging module

#  configuring the logging module in Python. It sets the log file path using the
# `config.getLogFilePath()` function, sets the file mode to 'a' (append mode), sets the log message
# format, sets the date format, and sets the log level to DEBUG.
logging.basicConfig(filename=config.getLogFilePath(), filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%d-%b-%y %H:%M:%S", level=logging.DEBUG)

# defining a Python application using the `typer` library. The `typer.Typer()`
# function creates an instance of the `Typer` class, which is used to define command-line interfaces
# (CLIs) in Python.
app = typer.Typer()

@app.command()
    
def init(
    endpoint_db_path: str = typer.Option(
        str(database.ENDPOINT_DB_FILE_PATH),
        "--endpoint-db-path",
        "-endpoint-db",
        prompt="endpoint database location?",
    ),
    app_db_path: str = typer.Option(
        str(database.APP_DB_FILE_PATH),
        "--app-db-path",
        "-app-db",
        prompt="application database location?",
    ),
) -> None:
    """
    The `init` function initializes the databases by creating a config file and creating the endpoint
    and app databases.
    
    :param endpoint_db_path: The `endpoint_db_path` parameter is the path to the location where the
    endpoint database will be created or initialized. This is the database that will store information
    about endpoints in your application
    :type endpoint_db_path: str
    :param app_db_path: The `app_db_path` parameter is the location or path where the application
    database will be created or initialized. It is a string that represents the file path of the
    application database
    :type app_db_path: str
    """
    
    # Insert a log message
    logging.info("Initializing the databases")

    db_list = [
        ('endpoint', endpoint_db_path),
        ('app', app_db_path)
    ]
    
    def _run_init():
        app_init_error = config.init_app(db_list)
        if app_init_error:
            typer.secho(
                f'Creating config file failed with "{ERRORS[app_init_error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)

        # Insert a log message
        logging.info("Config file created successfully")

        for db_name, db_path in db_list:
            db_init_error = database.init_database(db_path)
            if db_init_error:
                typer.secho(
                    f'Creating {db_name} database failed with "{ERRORS[db_init_error]}"',
                    fg=typer.colors.RED,
                )
                raise typer.Exit(1)
            else:
                typer.secho(f"The {db_name} database is {db_path}", fg=typer.colors.GREEN)

                # Insert a log message
                logging.info(f"{db_name} database created successfully")

    if os.path.isfile(config.CONFIG_FILE_PATH):
        typer.secho(
            f'\n\nImportant Notice !\n\n',
            fg=typer.colors.RED,
            bold=True,
        )

        red_style = typer.style(text="Config file exists and proceeding further will reset the file and databases. You will lose existing data which is irreversible. Do you still want to proceed?", fg=typer.colors.RED, bold=True)
     
        reset = typer.confirm(
            red_style,
            default=False,  # Set a default value for confirmation
            show_default=True,  # Do not show the default value in the prompt
        )
        if reset:
            _run_init()
        else:
            typer.echo("Operation canceled")
    else:
        _run_init()

@app.command("enable-threading")
def enable_threading(
    is_enabled: str = typer.Option(
        True,
        "--enabled",
        "-e",
        help="Enable threading for concurrent downloads.",
    )
) -> None:
    """
    The function `enable_threading` enables or disables threading for concurrent file downloads and logs
    the status.
    
    :param is_enabled: The `is_enabled` parameter is a string that represents whether threading should
    be enabled or disabled for concurrent file downloads. It is set as a command-line option with a
    default value of `True`
    :type is_enabled: str
    """
    status = False
    if os.path.isfile(config.CONFIG_FILE_PATH):
        status = config.enable_threading(is_enabled)
       
        if str(is_enabled) == "True":
            state = "enabled"
        else:
            state = "disabled"

        if status:
            logging.info(f'Threading failed with "{ERRORS[status]}"')
            typer.secho(
                f'Threading failed with "{ERRORS[status]}"', fg=typer.colors.RED
            )
            raise typer.Exit(1)
        else:
            typer.secho(
                f"""Threading is set to {state}.""",
                fg=typer.colors.GREEN,
            )
            # Insert a log message
            logging.info(f"Threading is set to {state}")

@app.command("set-concurrent-threads")
def set_concurrent_threads(
    thread_count: int = typer.Argument(...,help="Number of threads the CPU can support"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    )
) -> None:
    """
    The function `set_concurrent_threads` sets the number of concurrent threads based on the CPU count
    and prompts the user for confirmation before making the change.
    
    :param thread_count: The `thread_count` parameter is an integer that represents the number of
    threads the CPU can support. It is used to set the concurrent threads count
    :type thread_count: int

    :param force: The `force` parameter is a boolean option that allows you to force the deletion of the
    endpoint without any confirmation prompt. If `force` is set to `True`, the endpoint will be removed
    immediately without any further checks or prompts. If `force` is set to `False` (the default
    :type force: bool
    """

    def _set_threads():
        if os.path.isfile(config.CONFIG_FILE_PATH):
            error = config.set_concurrent_threads(thread_count)

            if error:
                typer.secho(
                    f'Set Concurrent Threads Count failed with "{ERRORS[error]}"', fg=typer.colors.RED
                )
                raise typer.Exit(1)
            else:
                typer.secho(
                    f"""Set Concurrent Threads Count to : {thread_count}""",
                    fg=typer.colors.GREEN,
                )
                # Insert a log message
                logging.info(f"""Set Concurrent Threads Count to : {thread_count}""")

    custom_style = typer.style(text="\nThread count must be thought out as per CPU count on machine as it might chock the machine if set to higher number. Do you still want to proceed?\n\n", fg=typer.colors.CYAN, bold=True)

    if force:
        _set_threads()
    else: 
        set_threads = typer.confirm(
            custom_style,
            default=False,  # Set a default value for confirmation
            show_default=True,  # Do not show the default value in the prompt
        )
    
        if set_threads:
            _set_threads()
        else:
            typer.echo("Operation canceled") 

@app.command("enable-encryption")
def enable_encryption(
    is_enabled: str = typer.Option(
        True,
        "--enabled",
        "-e",
        help="Enable File Encryption.",
    )
) -> None:
    """
    The function `enable_encryption` enables or disables file encryption based on the value of the
    `is_enabled` parameter.
    
    :param is_enabled: A boolean flag indicating whether file encryption should be enabled or not
    :type is_enabled: str
    """
    status = False
    if os.path.isfile(config.CONFIG_FILE_PATH):
        status = config.enable_encryption(is_enabled)
        if str(is_enabled) == "True":
            state = "enabled"
        else:
            state = "disabled"

        if status:
            typer.secho(
                f'Encryption failed with "{ERRORS[status]}"', fg=typer.colors.RED
            )
            raise typer.Exit(1)
        else:
            typer.secho(
                f"""Encryption is set to {state}.""",
                fg=typer.colors.GREEN,
            )

        # Insert a log message
        logging.info(f"File encryption is set to {state}")

@app.command("reset-encryption-key")
def reset_encryption_key() -> None:
    """
    The function `reset_encryption_key()` prompts the user to confirm if they want to reset the
    encryption key, and if confirmed, it resets the key and logs a message.
    """
    def _reset():
        if os.path.isfile(config.CONFIG_FILE_PATH):
            error = config.reset_encryption_key()

            if error:
                typer.secho(
                    f'Encryption key reset failed with "{ERRORS[error]}"', fg=typer.colors.RED
                )
                raise typer.Exit(1)
            else:
                typer.secho(
                    f"""Encryption key is reset.""",
                    fg=typer.colors.GREEN,
                )
                # Insert a log message
                logging.info("Encryption key has been reset.")

    reset = typer.confirm(
        f"Resetting encryption key will result in the loss of currently encrypted data. Do you still want to proceed?"
    )
    if reset:
        _reset()
    else:
        typer.echo("Operation canceled")

@app.command("check-encryption")
def check_encryption() -> None:
    """
    The function `check_encryption()` checks if encryption is enabled and provides a message
    accordingly.
    """
    file_encryption = FileEncryption()
    if file_encryption.check_if_enabled():
        typer.secho(
            'Encryption is enabled.',
            fg=typer.colors.BRIGHT_MAGENTA,
        )
    else:
        typer.secho(
            'Encryption is not enabled. Please, run "autonomous_data_collection_agent enable-encryption" .',
            fg=typer.colors.RED,
        )

def get_endpoints() -> autonomousagent.Endpoints:
    """
    The function `get_endpoints()` returns an instance of the `Endpoints` class for performing
    operations on data.
    :return: an instance of the `autonomousagent.Endpoints` class, which is initialized with the
    `db_path` parameter.
    """
    if os.path.isfile(config.CONFIG_FILE_PATH):
        db_path = database.get_database_path(config.CONFIG_FILE_PATH, 'endpoint')
    else:
        typer.secho(
            'Config file not found. Please, run "autonomous_data_collection_agent init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if os.path.isfile(db_path):
        return autonomousagent.Endpoints(db_path)
    else:
        typer.secho(
            'Database not found. Please, run "autonomous_data_collection_agent init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

def get_applications() -> autonomousagent.Applications:
    """
    The function `get_applications()` returns an instance of the `Applications` class from the
    `autonomousagent` module for operating on data.
    :return: an instance of the `autonomousagent.Applications` class.
    """
    if os.path.isfile(config.CONFIG_FILE_PATH):
        db_path = database.get_database_path(config.CONFIG_FILE_PATH, 'app')
    else:
        typer.secho(
            'Config file not found. Please, run "autonomous_data_collection_agent init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if os.path.isfile(db_path):
        return autonomousagent.Applications(db_path)
    else:
        typer.secho(
            'Database not found. Please, run "autonomous_data_collection_agent init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

# The HttpMethod class is used to restrict methods to GET, POST, and None using named tuple types.
class HttpMethod(Enum):
    """ HttpMethod class for named touple types to restrict methods to GET, POST and None."""
    NONE = "None"
    GET = "GET"
    POST = "POST"

def validate_datetime(datetime_str):
    """
    The function `validate_datetime` validates if a given datetime string is in the format 'DD-MM-YYYY
    hh:mm:ss'.
    
    :param datetime_str: The `datetime_str` parameter is a string representing a date and time in the
    format "DD-MM-YYYY hh:mm:ss"
    :return: The function `validate_datetime` returns a `datetime` object if the input `datetime_str` is
    in the format 'DD-MM-YYYY hh:mm:ss'. If the input is `None` or if it is not in the correct format, a
    `typer.BadParameter` exception is raised.
    """

    try:
        if datetime_str is None:
            return None
        else:
            return datetime.strptime(datetime_str, '%d-%m-%Y %H:%M:%S')
    except ValueError:
        raise typer.BadParameter("Invalid datetime format. Please use 'DD-MM-YYYY hh:mm:ss'.")
    
@app.command("add-endpoint")
def add_endpoint(
    name: str = typer.Argument(...,help="Name of Endpoint"),
    app_short_name: str = typer.Option(..., "--app-name", "-a", help="Application Short Name"),  
    url_endpoint: str = typer.Option(..., "--endpoint", "-e", help="Actual url endpoint without prefix or sufix / i.e. data-export-generic-api "),
    method: HttpMethod = typer.Option("GET", "--method", "-m", help="Request method to use (GET or POST)"),
    payload: str = typer.Option({}, "--payload", "-p", help="JSON payload for the request"),
    filters: str = typer.Option([], "--filters", "-f", help="Filters as a list of fitler dictionaries"),  
    page_size: int = typer.Option(1000, "--page-size", "-ps", min=1, max=10000, help="Page size (default: 1000)"),
    last_sync: str = typer.Option(
        None,
        "--last-sync",
        "-l",
        help="Last synchronization date and time in the format 'DD-MM-YYYY hh:mm:ss'",
        callback=validate_datetime,
    ),
    process_status: int = typer.Option(0, "--process-status", "-prs", min=0, max=2, help="Process status (0=>not processed, 1=>inprocess, or 2=>processed)"),
    status: int = typer.Option(1, "--status", "-s", min=0, max=2, help="Status (0=>distabled, 1=>enabled)"),
) -> None:
    """
    The `add_endpoint` function is used to add a new endpoint with various details such as name,
    application short name, URL endpoint, request method, payload, filters, page size, last
    synchronization date, process status, and status.
    
    :param name: The name of the endpoint. It is a required argument
    :type name: str
    :param app_short_name: The `app_short_name` parameter is used to specify the short name of the
    application to which the endpoint belongs. It is provided as an option with the `--app-name` or `-a`
    flag when running the script
    :type app_short_name: str
    :param url_endpoint: The `url_endpoint` parameter is used to specify the actual URL endpoint without
    the prefix or suffix. For example, if the complete URL is
    `https://example.com/api/data-export-generic-api/`, then the `url_endpoint` value would be
    `data-export-generic-api`
    :type url_endpoint: str
    :param method: The `method` parameter is used to specify the request method to use for the endpoint.
    It is an instance of the `HttpMethod` enum, which can have a value of either "GET" or "POST"
    :type method: HttpMethod
    :param payload: The `payload` parameter is used to specify the JSON payload for the request. It is
    an optional parameter and its default value is an empty dictionary (`{}`). You can provide a JSON
    payload as a string in the format `{"key1": "value1", "key2": "value2
    :type payload: str
    :param filters: The `filters` parameter is used to specify filters for the endpoint. It is expected
    to be a list of filter dictionaries. Each filter dictionary should have the following keys:
    :type filters: str
    :param page_size: The `page_size` parameter determines the number of records to be returned per page
    in the API response. It is an optional parameter with a default value of 1000. The minimum value
    allowed is 1 and the maximum value allowed is 10000
    :type page_size: int
    :param last_sync: The `last_sync` parameter is used to specify the last synchronization date and
    time for the endpoint. It accepts a string value in the format 'DD-MM-YYYY hh:mm:ss'. This parameter
    is optional and can be used to track the last time the endpoint was synchronized
    :type last_sync: str
    :param process_status: The `process_status` parameter is used to specify the process status of the
    endpoint. It can have one of the following values:
    :type process_status: int
    :param status: The `status` parameter is used to specify the status of the endpoint. It can have
    three possible values:
    :type status: int
    """
    # python your_script.py add_endpoint --name "Example Endpoint" --app-name "AOS" --endpoint "example-api-endpoint" --method POST --payload '{"key1": "value1", "key2": "value2"}' --filters '[{"column_name": "name", "operator": "value", "column_value": "value"}, {"column_name": "name", "operator": "value", "column_value": "value"}]' --page-size 500 --last-sync "13-10-2023 14:30:00" --process-status 0 --status 1

    endpoints = get_endpoints()
    endpoint_result = endpoints.add(name, app_short_name, url_endpoint, method.value, payload, filters, page_size, last_sync, process_status, status)
    endpoint = endpoint_result.endpoint
    error = endpoint_result.error

    if error:
        typer.secho(
            f'Adding endpoint failed with "{ERRORS[error]}"', fg=typer.colors.RED
        )
        logging.error(f"Failed to add endpoint: {name} for app: {app_short_name} - Error: {ERRORS[error]}")
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""endpoint: "{endpoint['name']}" was added """
            f"""for app: {app_short_name} """
            f"""with url endpoint: {url_endpoint}""",
            fg=typer.colors.GREEN,
        )
        logging.info(f"Added endpoint: {name} for app: {app_short_name} with URL endpoint: {url_endpoint}")

def cli_render_endpints(endpoints) -> None:
    """
    The `cli_render_endpoints` function lists given endpoints on the screen with specific formatting.
    
    :param endpoints: The `endpoints` parameter is a dictionary that contains information about
    different endpoints. Each key in the dictionary represents an endpoint ID, and the corresponding
    value is a dictionary containing the endpoint details such as name, app ID, URL endpoint, method,
    payload, filters, page size, last sync, process
    """
    if len(endpoints) == 0:
        typer.secho(
            "There are no endpoints in the list yet", fg=typer.colors.RED
        )
        raise typer.Exit()
    typer.secho("\nEndpoint List:\n", fg=typer.colors.BLUE, bold=True)
    columns = (
        "ID.                       ",
        "| Name                                       ",
        "| App Short Name       ",
        "| URL Endpoint                                 ",
        "| Method     ",
        "| Payload                                                                        ",
        "| Filters                                                                                                                                    ",
        "| Page Size  ",
        "| Last Sync                         ",
        "| Process Status  ",
        "| Status  ",
    )
    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers), fg=typer.colors.BLUE)
    app_handler = DatabaseHandler(database.get_database_path(config.CONFIG_FILE_PATH, 'app'))
    
    def _column_len(column_val):
        if column_val is None:
            return 0
        elif isinstance(column_val, int):
            return len(str(column_val))
        else:
            return len(column_val)
        
    for endpoint_id in endpoints:
        endpoint = endpoints[endpoint_id]
        name = endpoint['name']
        app_id = endpoint['app_id']
        url_endpoint = endpoint['url_endpoint']
        method = endpoint['method']
        payload = endpoint['payload']
        filters = endpoint['filters']
        page_size = endpoint['page_size']
        last_sync = endpoint['last_sync']
        process_status = endpoint['process_status']
        status = endpoint['status']

        try:
            app_data = app_handler.get_by_id(app_id)
            app_short_name = app_data.item_list[0]["short_name"]
        except IndexError:
            app_short_name = app_id
        
        typer.secho(
            f"{endpoint_id}{(len(columns[0]) - _column_len(str(endpoint_id))) * ' '}"
            f"| {name}{(len(columns[1]) - _column_len(name)-2) * ' '}"
            f"| {app_short_name}{(len(columns[2]) - _column_len(app_short_name)-2) * ' '}"
            f"| {url_endpoint}{(len(columns[3]) - _column_len(url_endpoint)-2) * ' '}"
            f"| {method}{(len(columns[4]) - _column_len(method)-2) * ' '}"
            f"| {payload}{(len(columns[5]) - _column_len(payload)-2) * ' '}"
            f"| {filters}{(len(columns[6]) - _column_len(filters)-4) * ' '}"
            f"| {page_size}{(len(columns[7]) - _column_len(str(page_size)) - 2) * ' '}"
            f"| {last_sync}{(len(columns[8]) - _column_len(str(last_sync)) - 2) * ' '}"
            f"| {process_status}{(len(columns[9]) - _column_len(str(process_status)) - 4) * ' '}"
            f"| {status}{(len(columns[10]) - _column_len(str(status)) - 4) * ' '}",
            fg=typer.colors.BLUE,
        )

    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)

@app.command("list-endpoints")
def list_endpoints() -> None:
    """
    The function `list_endpoints()` lists all endpoints.
    """
    endpoints = get_endpoints()
    all_endpoints = endpoints.get_endpoint_list()
    cli_render_endpints(all_endpoints)

@app.command("list-app-endpoints")
def list_app_endpoints(app_short_name: str = typer.Argument(..., help='Provide application short name')) -> None:
    """
    The `list_app_endpoints` function lists all endpoints for a given application.
    
    :param app_short_name: The `app_short_name` parameter is a string that represents the short name of
    the application. It is used to filter the endpoints and retrieve only the endpoints that belong to
    the specified application
    :type app_short_name: str
    """
    endpoints = get_endpoints()
    all_endpoints = endpoints.get_app_endpoints(app_short_name)
    
    cli_render_endpints(all_endpoints)

@app.command("get-endpoint")
def get_endpoint(endpoint_id: str = typer.Argument(..., help='Get a endpoint using its ENDPOINT_ID')) -> None:
    """
    The function `get_endpoint` retrieves an endpoint using its ID and displays the result.
    
    :param endpoint_id: The `endpoint_id` parameter is a required argument that represents the ID of the
    endpoint you want to retrieve. It is used to identify the specific endpoint you want to get from a
    collection of endpoints
    :type endpoint_id: str
    """
    endpoints = get_endpoints()
    endpoint_result = endpoints.get_endpoint_by_id(endpoint_id)
    endpoint = endpoint_result.endpoint
    error = endpoint_result.error
    if error:
        typer.secho(
            f'Getting endpoint # "{endpoint_id}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
       cli_render_endpints({endpoint_id: endpoint})

@app.command("get-endpoint-by-name")
def get_endpoint_by_name(endpoint_name: str = typer.Argument(..., help='Get a endpoint using its endpoint name')) -> None:
    """
    The function `get_endpoint_by_name` retrieves an endpoint using its name and displays the result.
    
    :param endpoint_name: The `endpoint_name` parameter is a string that represents the name of the
    endpoint you want to retrieve
    :type endpoint_name: str
    """
    endpoints = get_endpoints()
    endpoint_result = endpoints.get_endpoint_by_name(endpoint_name)
    endpoint = endpoint_result.endpoint
    error = endpoint_result.error
    if error:
        typer.secho(
            f'Getting endpoint name "{endpoint_name}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
       cli_render_endpints(endpoint)

@app.command("get-endpoint-by-process-status")
def get_app_endpoints_by_status(
    process_status: int = typer.Argument(0, min=0, max=2, help='Get a endpoint using its process status'),
    app_short_name: str = typer.Option(..., "-short-name", "-s", help='Provide application short name')
) -> None:
    """
    The function `get_app_endpoints_by_status` retrieves a list of endpoints based on their process
    status and application short name.
    
    :param process_status: An integer representing the process status of an endpoint. It should be
    between 0 and 2
    :type process_status: int
    :param app_short_name: A string representing the short name of the application
    :type app_short_name: str
    """
    endpoints = get_endpoints()
    endpoint_list = endpoints.get_app_endpoints_by_process_status(app_short_name, process_status)
    cli_render_endpints(endpoint_list)

@app.command("get-endpoint-by-status")
def get_app_endpoints_by_status(
    status: int = typer.Argument(0, min=0, max=2, help='Get a endpoint using its status'),
    app_short_name: str = typer.Option(..., "--short-name", "-s", help='Provide application short name')
) -> None:
    """
    The function `get_app_endpoints_by_status` retrieves a list of endpoints based on their status and
    application short name.
    
    :param status: The `status` parameter is an integer that represents the status of an endpoint. It
    should be between 0 and 2, inclusive. This parameter is used to filter the endpoints based on their
    status
    :type status: int
    :param app_short_name: A string parameter that represents the short name of the application. It is
    required and can be provided using the `--short-name` or `-s` option when running the command
    :type app_short_name: str
    """
    endpoints = get_endpoints()
    endpoint_list = endpoints.get_app_endpoints_by_status(app_short_name, status)
    cli_render_endpints(endpoint_list)

@app.command("get-endpoint-by-url")
def get_endpoint_by_url(url_endpoint: str = typer.Argument(..., help='Get a endpoint using its endpoint url')) -> None:
    """
    The function `get_endpoint_by_url` retrieves an endpoint using its URL and displays the result.
    
    :param url_endpoint: The `url_endpoint` parameter is a string that represents the URL of an
    endpoint. It is used to search for a specific endpoint in a collection of endpoints
    :type url_endpoint: str
    """
    endpoints = get_endpoints()
    endpoint_result = endpoints.get_endpoint_by_url(url_endpoint)
    endpoint = endpoint_result.endpoint
    error = endpoint_result.error
    if error:
        typer.secho(
            f'Getting endpoint url "{url_endpoint}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
       cli_render_endpints(endpoint)

@app.command("update-endpoint")
def update_endpoint(
    endpoint_id: str = typer.Argument(..., help="ID of the endpoint to update"),
    name: str = typer.Option(None, "--name", "-n", help="New name of the endpoint"),
    app_short_name: str = typer.Option(None, "--app-name", "-a", help="New application short name"),
    url_endpoint: str = typer.Option(None, "--endpoint", "-e", help="New URL endpoint"),
    method: HttpMethod = typer.Option(None, "--method", "-m", help="New request method (GET or POST)"),
    payload: str = typer.Option(None, "--payload", "-p", help="New JSON payload for the request"),
    filters: str = typer.Option(None, "--filters", "-f", help="New list of filters as JSON string"),
    page_size: int = typer.Option(None, "--page-size", "-ps", min=1, max=10000, help="New page size (default: 1000)"),
    last_sync: str = typer.Option(None, "--last-sync", "-l", help="New last synchronization date and time in the format 'DD-MM-YYYY hh:mm:ss'"),
    process_status: int = typer.Option(None, "--process-status", "-prs", min=0, max=2, help="New process status (0=>not processed, 1=>inprocess, or 2=>processed)"),
    status: int = typer.Option(None, "--status", "-s", min=0, max=2, help="Endpoint status (0=>disabled, 1=>enabled)"),
) -> None:
    """
    The `update_endpoint` function updates an existing endpoint with new details based on the provided
    arguments.
    
    :param endpoint_id: The ID of the endpoint to update. This is a required argument
    :type endpoint_id: str
    :param name: The `name` parameter is used to specify the new name for the endpoint
    :type name: str
    :param app_short_name: The `app_short_name` parameter is used to specify the new application short
    name for the endpoint. It is an optional parameter that can be provided using the `--app-name` or
    `-a` option when calling the `update_endpoint` function. The application short name is used to
    identify the application
    :type app_short_name: str
    :param url_endpoint: The `url_endpoint` parameter is used to specify the new URL endpoint for the
    endpoint. It is an optional parameter and can be provided using the `--endpoint` or `-e` option when
    running the script. The value should be a string representing the new URL endpoint
    :type url_endpoint: str
    :param method: The `method` parameter is used to specify the new request method for the endpoint. It
    is an optional parameter and can be provided using the `--method` or `-m` option when calling the
    `update_endpoint` function. The allowed values for the `method` parameter are "GET" or
    :type method: HttpMethod
    :param payload: The `payload` parameter is used to specify a new JSON payload for the request. It
    allows you to provide data that will be sent along with the request to the endpoint
    :type payload: str
    :param filters: The `filters` parameter is used to specify a new list of filters for the endpoint.
    It should be provided as a JSON string. Filters are used to narrow down the data that is retrieved
    from the endpoint
    :type filters: str
    :param page_size: The `page_size` parameter is an optional parameter that specifies the number of
    items to retrieve per page when making a request to the endpoint. It accepts an integer value
    between 1 and 10000. The default value is 1000
    :type page_size: int
    :param last_sync: The `last_sync` parameter is used to specify the new last synchronization date and
    time for the endpoint. It should be provided in the format "DD-MM-YYYY hh:mm:ss"
    :type last_sync: str
    :param process_status: The `process_status` parameter is used to specify the new process status for
    the endpoint. It accepts an integer value between 0 and 2
    :type process_status: int
    :param status: The `status` parameter is used to specify the status of the endpoint. It can have
    three possible values:
    :type status: int
    """
    # Example usage: python your_script.py update_endpoint --id "231541323453553701" --name "Updated Name" --app-name "Updated App" --method POST --status 0

    endpoints = get_endpoints()
    endpoint_result = endpoints.get_endpoint_by_id(endpoint_id)
    endpoint = endpoint_result.endpoint
    error = endpoint_result.error
    if endpoint is None:
        typer.secho("Endpoint not found.", fg=typer.colors.RED)
        raise typer.Exit(1)

    # Update the endpoint fields if new values are provided
    if name is not None:
        endpoint["name"] = name
    if app_short_name is not None:
        app_handler = DatabaseHandler(database.get_database_path(config.CONFIG_FILE_PATH, 'app'))
        try:
            app_id = next(iter(app_handler.get_by_column("short_name", app_short_name).item_list))
            endpoint["app_id"] = app_id
        except IndexError:
            typer.secho(f"App {app_short_name} not found.", fg=typer.colors.RED)
            raise typer.Exit(1)
    if url_endpoint is not None:
        endpoint["url_endpoint"] = url_endpoint
    if method is not None:
        endpoint["method"] = method
    if payload is not None:
        endpoint["payload"] = payload
    if filters is not None:
        endpoint["filters"] = filters
    if page_size is not None:
        endpoint["page_size"] = page_size
    if last_sync is not None:
        endpoint["last_sync"] = last_sync
    if process_status is not None:
        endpoint["process_status"] = process_status
    if status is not None:
        endpoint["status"] = status

    endpoint_result = endpoints.update_endpoint(endpoint_id, endpoint)
    endpoint = endpoint_result.endpoint
    error = endpoint_result.error
    if error:
        typer.secho(
            f'updating endpoint # {endpoint_id} failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        logging.error(f'updating endpoint # {endpoint_id} failed with "{ERRORS[error]}"')
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""endpoint # {endpoint_id} updated successfully""",
            fg=typer.colors.GREEN,
        )
        logging.info(f"""endpoint # {endpoint_id} updated successfully""")

@app.command("update-endpoint-process-status")
def update_endpoint_process_status(
    endpoint_id: str = typer.Argument(..., help="ID of the endpoint to update"),
    process_status: int = typer.Option(1, "--process-status", "-prs", min=0, max=2, help="Endpoint process status (0=>not processed, 1=>inprocess, or 2=>processed)"),
) -> None:
    """
    The function `update_endpoint_process_status` updates the process status of an existing endpoint.
    
    :param endpoint_id: The `endpoint_id` parameter is a required argument that represents the ID of the
    endpoint you want to update
    :type endpoint_id: str
    :param process_status: The `process_status` parameter is an integer that represents the process
    status of an endpoint. It can have one of three values:
    :type process_status: int
    """
    # Example usage: python your_script.py update_process_endpoint --id "231541323453553701" --process-status 1

    endpoints = get_endpoints()
    endpoint_result = endpoints.update_endpoint_process_status(endpoint_id, process_status)
    error = endpoint_result.error
    if error:
        typer.secho(
            f'updating endpoint # {endpoint_id} failed with process status: "{process_status}"',
            fg=typer.colors.RED,
        )
        logging.error(f'updating endpoint # {endpoint_id} failed with process status: "{process_status}"')
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""endpoint # {endpoint_id} updated successfully with process status: "{process_status}" """,
            fg=typer.colors.GREEN,
        )
        logging.info(f"""endpoint # {endpoint_id} updated successfully with process status: "{process_status}" """)

@app.command("update-endpoint-status")
def update_endpoint_status(
    endpoint_id: str = typer.Argument(..., help="ID of the endpoint to update"),
    status: int = typer.Option(1, "--status", "-s", min=0, max=1, help="Endpoint status (0=>disabled, 1=>enabled)"),
) -> None:
    """
    The `update_endpoint_status` function updates the status of an existing endpoint with the provided
    endpoint ID.
    
    :param endpoint_id: The `endpoint_id` parameter is a required argument that represents the ID of the
    endpoint to update
    :type endpoint_id: str
    :param status: The `status` parameter is an integer that represents the status of the endpoint. It
    can have two possible values: 0 or 1
    :type status: int
    """
    # Example usage: python your_script.py update_endpoint --id "231541323453553701" --name "Updated Name" --app-name "Updated App" --method POST

    endpoints = get_endpoints()
    endpoint_result = endpoints.update_endpoint_status(endpoint_id, status)
    error = endpoint_result.error
    status_txt = "enabled" if status == 1 else "disabled"

    if error:
        typer.secho(
            f'updating endpoint # {endpoint_id} failed with status: "{status_txt}"',
            fg=typer.colors.RED,
        )
        logging.error(f'updating endpoint # {endpoint_id} failed with status: "{status_txt}"')
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""endpoint # {endpoint_id} updated successfully with status: "{status_txt}" """,
            fg=typer.colors.GREEN,
        )
        logging.info(f"""endpoint # {endpoint_id} updated successfully with status: "{status_txt}" """)

@app.command("remove-endpoint")
def remove_endpoint(
    endpoint_id: str = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """
    The `remove_endpoint` function removes an endpoint using its endpoint ID, with an option to force
    deletion without confirmation.
    
    :param endpoint_id: The `endpoint_id` parameter is a required argument that represents the ID of the
    endpoint to be removed
    :type endpoint_id: str
    :param force: The `force` parameter is a boolean option that allows you to force the deletion of the
    endpoint without any confirmation prompt. If `force` is set to `True`, the endpoint will be removed
    immediately without any further checks or prompts. If `force` is set to `False` (the default
    :type force: bool
    """
    endpoints = get_endpoints()

    def _remove():
        endpoint_result = endpoints.remove(endpoint_id)
        error = endpoint_result.error
        if error:
            typer.secho(
                f'Removing endpoint # {endpoint_id} failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            logging.error(f'Removing endpoint # {endpoint_id} failed with "{ERRORS[error]}"')
            raise typer.Exit(1)
        else:
            typer.secho(
                f"""endpoint # {endpoint_id} was removed""",
                fg=typer.colors.GREEN,
            )
            logging.info(f"""endpoint # {endpoint_id} was removed""")

    if force:
        _remove()
    else:
        try:
            endpoint_result = endpoints.get_endpoint_by_id(endpoint_id)
            endpoint = endpoint_result.endpoint
            error = endpoint_result.error
            if error:
                typer.secho("Invalid ENDPOINT_ID", fg=typer.colors.RED)
                raise typer.Exit(1)
        except IndexError:
            typer.secho("Invalid ENDPOINT_ID", fg=typer.colors.RED)
            raise typer.Exit(1)
        delete = typer.confirm(
            f"Delete endpoint # {endpoint_id} with name : {endpoint['name']}?"
        )
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")

@app.command("remove-app-endpoints")
def remove_app_endpoints(
    app_short_name: str = typer.Argument(..., help="New application short name"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """
    The `remove_app_endpoints` function removes endpoints associated with a given application short
    name, with an option to force deletion without confirmation.
    
    :param app_short_name: The `app_short_name` parameter is a required argument that represents the
    short name of the application for which the endpoints need to be removed
    :type app_short_name: str
    :param force: A boolean flag that indicates whether to force the deletion of endpoints without
    confirmation. If set to True, the endpoints will be removed without any further prompts
    :type force: bool
    """
    endpoints = get_endpoints()

    def _remove():
        endpoint_obj = endpoints.remove_all_by_app(app_short_name)
        error = endpoint_obj.error
        if error:
            typer.secho(
                f'Removing endpoints for app # {app_short_name} failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            logging.error(f'Removing endpoints for app # {app_short_name} failed with "{ERRORS[error]}"')
            raise typer.Exit(1)
        else:
            typer.secho(
                f"""endpoints for app # {app_short_name} was removed.""",
                fg=typer.colors.GREEN,
            )
            logging.info(f"""endpoints for app # {app_short_name} was removed.""")

    if force:
        _remove()
    else:
        delete = typer.confirm(
            f"Delete endpoints with app short name : {app_short_name}?"
        )
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")

@app.command(name="clear-endpoints")
def remove_all_endpoints(
    force: bool = typer.Option(
        False,
        prompt="Delete all endpoints?",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """
    The function `remove_all_endpoints` removes all endpoints, with an option to force deletion without
    confirmation.
    
    :param force: The `force` parameter is a boolean flag that determines whether to delete all
    endpoints without confirmation. If `force` is set to `True`, the function will proceed with deleting
    all endpoints. If `force` is set to `False` (the default value), the function will prompt the user
    for
    :type force: bool
    """
    endpoints = get_endpoints()
    if force:
        error = endpoints.remove_all().error
        if error:
            typer.secho(
                f'Removing endpoints failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            logging.error(f'Removing endpoints failed with "{ERRORS[error]}"')
            raise typer.Exit(1)
        else:
            typer.secho("All endpoints were removed", fg=typer.colors.GREEN)
            logging.info("All endpoints were removed")
    else:
        typer.echo("Operation canceled")

# The class `UrlSchemes` is an enumeration that represents different URL schemes, such as "http" and
# "https".
class UrlSchemes(Enum):
    http = "http"
    https = "https"

# The AuthTypes class is an enumeration that represents different types of authentication.
class AuthTypes(Enum):
    NONE = "NONE"
    BASIC = "BASIC"
    KEYCLOAK = "KEYCLOAK"

@app.command(name="add-app")
def add_application(
    name: str = typer.Argument(..., help="Name of the application"),
    short_name: str = typer.Option(..., "--short-name", "-sn", help="Short name of the application"),
    host: str = typer.Option(..., "--host", "-h", help="Host of the application"),
    url_scheme: UrlSchemes = typer.Option("https", "--url-scheme", "-u", help="URL scheme (http or https)"),
    auth_type: AuthTypes = typer.Option("NONE", "--auth-type", "-at", help="Authentication type (NONE, KEYCLOAK, BASIC)"),
    auth_data: str = typer.Option({}, "--authdata", "-c", help="JSON payload for the authdata"),
    dump_path: str = typer.Option(..., "--dump-path", "-d", callback=autonomousagent.Applications.check_and_create_directory, help="Path for dumping the files"), 
    sync_frequency: str = typer.Option(
        "0 23 * * *", 
        "--sync-frequency", 
        "-sf",
        callback=autonomousagent.Applications.is_valid_cronjob,
        help="Sync frequency (cronjob) */30 * * * *"
    ),
    last_sync: str = typer.Option(
        None,
        "--next-sync",
        "-n",
        help="Last synchronization date and time in the format 'DD-MM-YYYY hh:mm:ss'",
        callback=validate_datetime,
    ),
    next_sync: str = typer.Option(
        None,
        "--last-sync",
        "-l",
        help="Last synchronization date and time in the format 'DD-MM-YYYY hh:mm:ss'",
        callback=validate_datetime,
    ),
    default_payload: str = typer.Option({}, "--payload", "-p", help="JSON payload for the request"),
    default_filters: str = typer.Option([], "--filters", "-df", help="Filters as a list of fitler dictionaries"), 
    default_page_size: int = typer.Option(1000, "--default-page-size", "-dp", min=1, max=10000, help="Default page size (1000)"),
    process_status: int = typer.Option(0, "--process-status", "-prs", min=0, max=2, help="Process status (0=>not processed, 1=>inprocess, or 2=>processed)"),
    status: int = typer.Option(1, "--status", "-s", min=0, max=2, help="Applicaiton status (0=>disabled, 1=>enabled)"),
):
    """
    The `add_application` function adds a new application with the provided details.
    
    :param name: The `name` parameter is a required argument that specifies the name of the application
    :type name: str
    :param short_name: The `short_name` parameter is an optional short name for the application. It can
    be provided using the `--short-name` or `-sn` option when calling the `add_application` function
    :type short_name: str
    :param host: The `host` parameter is used to specify the host of the application. It is a required
    parameter and must be provided when calling the `add_application` function
    :type host: str
    :param url_scheme: The `url_scheme` parameter is used to specify the URL scheme for the application.
    It is an optional parameter with a default value of "https". The available options for this
    parameter are "http" and "https"
    :type url_scheme: UrlSchemes
    :param auth_type: The `auth_type` parameter is used to specify the authentication type for the
    application. It can have one of the following values:
    :type auth_type: AuthTypes
    :param auth_data: The `auth_data` parameter is a JSON payload for the authentication data. It is
    used to provide additional information required for authentication, such as credentials or tokens
    :type auth_data: str
    :param dump_path: The `dump_path` parameter is used to specify the path where the files will be
    dumped. It is a required parameter and should be provided when calling the `add_application`
    function
    :type dump_path: str
    :param sync_frequency: The `sync_frequency` parameter is used to specify the frequency at which the
    application should be synchronized. It takes a cronjob expression as its value. For example, `0 23 *
    * *` means the synchronization should occur every day at 23:00
    :type sync_frequency: str
    :param last_sync: The `last_sync` parameter is used to specify the last synchronization date and
    time for the application. It should be provided in the format 'DD-MM-YYYY hh:mm:ss'. If not
    provided, it can be set to `None`
    :type last_sync: str
    :param next_sync: The `next_sync` parameter is used to specify the last synchronization date and
    time for the application. It should be provided in the format 'DD-MM-YYYY hh:mm:ss'. If not
    provided, it can be set to `None`
    :type next_sync: str
    :param default_payload: The `default_payload` parameter is used to specify a JSON payload for the
    request. It allows you to provide default data that will be sent along with the request when
    interacting with the application
    :type default_payload: str
    :param default_filters: The `default_filters` parameter is a list of filter dictionaries. Each
    dictionary represents a filter that can be applied to the application data. The filters are used to
    retrieve specific data from the application
    :type default_filters: str
    :param default_page_size: The `default_page_size` parameter is an integer option that specifies the
    default page size for the application. It determines the number of items or records that will be
    returned in each page of data when making requests to the application. The default value is set to
    1000, but it can be customized
    :type default_page_size: int
    :param process_status: The `process_status` parameter is used to specify the process status of the
    application. It can have one of the following values:
    :type process_status: int
    :param status: The `status` parameter is used to specify the status of the application. It can have
    three possible values:
    :type status: int
    """

    last_sync_datetime = datetime.strptime(last_sync, '%d-%m-%Y %H:%M:%S') if last_sync  else None
    next_sync_datetime = datetime.strptime(next_sync, '%d-%m-%Y %H:%M:%S') if next_sync else None

    applications = get_applications()
    application_result = applications.add(
        name, short_name, host, url_scheme.value, auth_type.value, auth_data, dump_path, sync_frequency, last_sync_datetime, next_sync_datetime, default_payload, default_filters, default_page_size, process_status, status
    )
    application = application_result.application
    error = application_result.error
    if error:
        typer.secho(
            f'Adding application failed with "{ERRORS[error]}"', fg=typer.colors.RED
        )
        logging.error(f'Adding application failed with "{ERRORS[error]}"')
        raise typer.Exit(1)
    else:
        typer.secho(f"Application '{name}' was added. ID: #'{application[0]}'", fg=typer.colors.GREEN)
        logging.info(f"Application #'{application[0]}' was added")

@app.command(name="update-app")
def update_application(
    app_id: str = typer.Argument(..., help="ID of the application to update"),
    name: str = typer.Option(None, "--name", "-n", help="Name of the application"),
    short_name: str = typer.Option(None, "--short-name", "-sn", help="Short name of the application"),
    host: str = typer.Option(None, "--host", "-h", help="Host of the application"),
    url_scheme: UrlSchemes = typer.Option(None, "--url-scheme", "-u", help="URL scheme (http or https)"),
    auth_type: AuthTypes = typer.Option(None, "--auth-type", "-at", help="Authentication type (NA, KEYCLOAK, BASIC)"),
    auth_data: str = typer.Option(None, "--authdata", "-ad", help="JSON payload for the authdata"),
    dump_path: str = typer.Option(None, "--dump-path", "-dp", callback=autonomousagent.Applications.check_and_create_directory, help="Path for dumping the files"), 
    sync_frequency: str = typer.Option(
        None, 
        "--sync-frequency", 
        "-sf",
        callback=autonomousagent.Applications.is_valid_cronjob,
        help="Sync frequency (cronjob) */30 * * * *"
    ),
    last_sync: str = typer.Option(
        None,
        "--next-sync",
        "-ns",
        help="Last synchronization date and time in the format 'DD-MM-YYYY hh:mm:ss'",
        callback=validate_datetime,
    ),
    next_sync: str = typer.Option(
        None,
        "--last-sync",
        "-ls",
        help="Last synchronization date and time in the format 'DD-MM-YYYY hh:mm:ss'",
        callback=validate_datetime,
    ),
    default_payload: str = typer.Option(None, "--payload", "-p", help="JSON payload for the request"),
    default_filters: str = typer.Option(None, "--filters", "-df", help="Filters as a list of fitler dictionaries"), 
    default_page_size: int = typer.Option(None, "--default-page-size", "-dp", min=1, max=10000, help="Default page size (1000)"),
    process_status: int = typer.Option(None, "--process-status", "-prs", min=0, max=2, help="Process status (0=>not processed, 1=>inprocess, or 2=>processed)"),
    status: int = typer.Option(None, "--status", "-s", min=0, max=2, help="Application status (0=>disabled, 1=>enabled)"),
):
    """
    The `update_application` function updates an existing application with the provided details.
    
    :param app_id: The `app_id` parameter is the ID of the application that you want to update. It is a
    required argument and must be provided when calling the `update_application` function
    :type app_id: str
    :param name: The `name` parameter is used to specify the name of the application to be updated
    :type name: str
    :param short_name: The `short_name` parameter is used to specify the short name of the application.
    It is an optional parameter that can be provided when updating an existing application
    :type short_name: str
    :param host: The `host` parameter is used to specify the host of the application. It is an optional
    parameter that can be provided when updating an existing application
    :type host: str
    :param url_scheme: The `url_scheme` parameter is used to specify the URL scheme for the application.
    It is an optional parameter and can be set using the `--url-scheme` or `-u` option. The value of
    `url_scheme` should be one of the values defined in the `UrlSchemes
    :type url_scheme: UrlSchemes
    :param auth_type: The `auth_type` parameter is used to specify the authentication type for the
    application. It accepts three possible values: "NA" (no authentication), "KEYCLOAK" (Keycloak
    authentication), or "BASIC" (basic authentication)
    :type auth_type: AuthTypes
    :param auth_data: The `auth_data` parameter is used to provide a JSON payload for the authentication
    data. This can be used to pass any additional information required for authentication, such as API
    keys or tokens
    :type auth_data: str
    :param dump_path: The `dump_path` parameter is used to specify the path where files will be dumped.
    It is an optional parameter that accepts a string value
    :type dump_path: str
    :param sync_frequency: The `sync_frequency` parameter is used to specify the synchronization
    frequency for the application. It takes a cronjob format string as its value. For example, `*/30 * *
    * *` means the application will be synchronized every 30 minutes
    :type sync_frequency: str
    :param last_sync: The `last_sync` parameter is used to specify the last synchronization date and
    time for the application. It should be provided in the format 'DD-MM-YYYY hh:mm:ss'
    :type last_sync: str
    :param next_sync: The `next_sync` parameter is used to specify the last synchronization date and
    time for the application being updated. It should be provided in the format 'DD-MM-YYYY hh:mm:ss'
    :type next_sync: str
    :param default_payload: The `default_payload` parameter is used to specify a JSON payload for the
    request. This payload will be sent along with the request when the application is used
    :type default_payload: str
    :param default_filters: The `default_filters` parameter is used to specify filters for the
    application. It should be provided as a string representing a list of filter dictionaries. Each
    filter dictionary should contain the filter name and value. For example:
    :type default_filters: str
    :param default_page_size: The `default_page_size` parameter is an optional integer parameter that
    specifies the default page size for pagination. It determines the number of items returned per page
    when making requests to the application. The value should be between 1 and 10000
    :type default_page_size: int
    :param process_status: The `process_status` parameter is used to specify the process status of the
    application. It can have one of the following values:
    :type process_status: int
    :param status: The `status` parameter is used to specify the status of the application. It can have
    three possible values:
    :type status: int
    """

    applications = get_applications()
    application_result = applications.get_app_by_id(app_id)
    application = application_result.application
    error = application_result.error

    if name is not None:
        application["name"] = name
    if short_name is not None:
        application["short_name"] = short_name
    if host is not None:
        application["host"] = host
    if url_scheme is not None:
        application["url_scheme"] = url_scheme.value
    if auth_type is not None:
        application["auth_type"] = auth_type.value
    if auth_data is not None:
        application["auth_data"] = auth_data
    if dump_path is not None:
        application["dump_path"] = dump_path
    if sync_frequency is not None:
        application["sync_frequency"] = sync_frequency
    if last_sync is not None:
        application["last_sync"] = last_sync
    if next_sync is not None:
        application["next_sync"] = next_sync
    if default_payload is not None:
        application["default_payload"] = default_payload
    if default_filters is not None:
        application["default_filters"] = default_filters
    if default_page_size is not None:
        application["default_page_size"] = default_page_size
    if process_status is not None:
        application["process_status"] = process_status
    if status is not None:
        application["status"] = status

    application_result = applications.update_app(APP_ID=app_id, data=application)
    application = application_result.application
    error = application_result.error
    if error:
        typer.secho(
            f'Updating application failed with "{ERRORS[error]}"', fg=typer.colors.RED
        )
        logging.error(f'Updating application failed with "{ERRORS[error]}"')
        raise typer.Exit(1)
    else:
        typer.secho(f"Application '{application['name']}' was updated successfully.", fg=typer.colors.GREEN)
        logging.info(f"Application '{application['name']}' was updated successfully.")

def cli_render_application(applications) -> None:
    """
    The `cli_render_application` function renders a formatted application list in the command-line
    interface.
    
    :param applications: The `applications` parameter is a dictionary that contains information about
    different applications. Each key in the dictionary represents the ID of an application, and the
    corresponding value is another dictionary that contains various attributes of the application, such
    as name, short name, host, URL scheme, authentication type, authentication data,
    """
    if len(applications) == 0:
        typer.secho(
            "There are no application in the list yet", fg=typer.colors.RED
        )
        raise typer.Exit()
    typer.secho("\nApplication List:\n", fg=typer.colors.BLUE, bold=True)
    columns = (
         "ID.                      ",
        "| Name                      ",
        "| Short Name ",
        "| Host                 ",
        "| URL Scheme  ",
        "| Auth Type  ",
        "| Auth Data               ",
        "| Dump Path                                                                                  ",
        "| Sync Frequency  ",
        "| Last Sync             ",
        "| Next Sync             ",
        "| Default Payload              ",
        "| Default Filters                          ",
        "| Default Page Size ",
        "| Process Status ",
        "| Status  ",
    )

    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers), fg=typer.colors.BLUE)
    def _column_len(column_val):
        if column_val is None:
            return 0
        elif isinstance(column_val, int):
            return len(str(column_val))
        else:
            return len(column_val)
    # print(applications)
    # exit(1)   
    for app_id in applications:
        name, short_name, host, url_scheme, auth_type, auth_data, dump_path, sync_frequency, last_sync, next_sync, default_payload, default_filters, default_page_size, process_status, status = applications[app_id].values()

        typer.secho(
            f"{app_id}{(len(columns[0]) - _column_len(str(app_id))) * ' '}"
            f"| {name}{(len(columns[1]) - _column_len(name)-2) * ' '}"
            f"| {short_name}{(len(columns[2]) - _column_len(short_name)-2) * ' '}"
            f"| {host}{(len(columns[3]) - _column_len(host)-2) * ' '}"
            f"| {url_scheme}{(len(columns[4]) - _column_len(url_scheme)-2) * ' '}"
            f"| {auth_type}{(len(columns[5]) - _column_len(auth_type)-2) * ' '}"
            f"| {auth_data}{(len(columns[6]) - _column_len(auth_data)-4) * ' '}"
            f"| {dump_path}{(len(columns[7]) - _column_len(dump_path)-2) * ' '}"
            f"| {sync_frequency}{(len(columns[8]) - _column_len(sync_frequency)-2) * ' '}"
            f"| {last_sync}{(len(columns[9]) - _column_len(last_sync)-6) * ' '}"
            f"| {next_sync}{(len(columns[10]) - _column_len(next_sync)-6) * ' '}"
            f"| {default_payload}{(len(columns[11]) - _column_len(default_payload)-4) * ' '}"
            f"| {default_filters}{(len(columns[12]) - _column_len(default_filters)-4) * ' '}"
            f"| {default_page_size}{(len(columns[13]) - _column_len(default_page_size)-2) * ' '}"
            f"| {process_status}{(len(columns[14]) - _column_len(process_status)-2) * ' '}"
            f"| {status}",
            fg=typer.colors.BLUE,
        )

    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)

@app.command(name="list-apps")
def list_applications() -> None:
    """
    The function `list_applications` retrieves a list of applications and renders them using a
    command-line interface.
    """
    applications = get_applications()
    application_list = applications.get_applications()
    cli_render_application(application_list)

@app.command(name="get-app")
def get_app(app_id: str = typer.Argument(..., help="ID of the application")) -> None:
    """
    The `get_app` function retrieves an application using its ID and displays the application
    information.
    
    :param app_id: The `app_id` parameter is a required argument of type `str`. It represents the ID of
    the application that you want to retrieve
    :type app_id: str
    """
    applications = get_applications()
    application_result = applications.get_app_by_id(app_id)
    application = application_result.application
    error = application_result.error
    if error:
        typer.secho(
            f'Getting application # "{app_id}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
       cli_render_application({app_id:application})

@app.command(name="get-app-by-name")
def get_app_by_name(name: str = typer.Argument(..., help="Name of the application")) -> None:
    """
    The function `get_app_by_name` retrieves an application by its name and displays it using a CLI
    render function.
    
    :param name: The `name` parameter is a string that represents the name of the application. It is a
    required argument and is used to search for the application in the `applications` list
    :type name: str
    """
    applications = get_applications()
    application_result = applications.get_app_by_name(name)
    application = application_result.application
    error = application_result.error
    if error:
        typer.secho(
            f'Getting application # "{name}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
       cli_render_application(application)

@app.command(name="get-app-by-short-name")
def get_app_by_short_name(short_name: str = typer.Argument(..., help="Short name of the application")) -> None:
    """
    The function `get_app_by_short_name` retrieves an application using its short name and displays it
    using a command-line interface.
    
    :param short_name: The `short_name` parameter is a required argument of type `str`. It represents
    the short name of the application that you want to retrieve
    :type short_name: str
    """
    applications = get_applications()
    application_result = applications.get_app_by_short_name(short_name)
    application = application_result.application
    error = application_result.error
    if error:
        typer.secho(
            f'Getting application # "{short_name}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
       cli_render_application(application)

@app.command(name="get-app-by-status")
def get_app_by_status(status: int = typer.Argument(..., help="Status of the application to filter")) -> None:
    """
    The function `get_app_by_status` retrieves applications based on their status and renders them using
    a command-line interface.
    
    :param status: The `status` parameter is an integer that represents the status of the application to
    filter. It is used to retrieve applications that match the specified status
    :type status: int
    """
    applications = get_applications()
    application_list = applications.get_app_by_status(status)
    cli_render_application(application_list)

@app.command(name="get-app-by-process-status")
def get_app_by_process_status(process_status: int = typer.Argument(..., help="Process Status of the application to filter")) -> None:
    """
    The function `get_app_by_process_status` retrieves applications based on their process status and
    renders them using a command-line interface.
    
    :param process_status: The `process_status` parameter is an integer that represents the process
    status of the application. It is used to filter the applications and retrieve only those with the
    specified process status
    :type process_status: int
    """
    applications = get_applications()
    application_list = applications.get_app_by_process_status(process_status)
    cli_render_application(application_list)

@app.command("update-app-status")
def update_app_status(
    app_id: str = typer.Argument(..., help="ID of the app to update"),
    status: int = typer.Option(1, "--status", "-s", min=0, max=1, help="App status (0=>disabled, 1=>enabled)"),
) -> None:
    """
    The `update_app_status` function updates the status of an existing application based on the provided
    app ID and status value.
    
    :param app_id: The `app_id` parameter is a required argument that represents the ID of the
    application to update
    :type app_id: str
    :param status: The `status` parameter is an integer that represents the status of the application.
    It can have two possible values:
    :type status: int
    """
    # Example usage: python your_script.py update_app_status --id "231541323453553701" --name "Updated Name" --app-name "Updated App" --method POST

    applications = get_applications()
    application_result = applications.update_app_status(app_id, status)
    error = application_result.error
    status_txt = "enabled" if status == 1 else "disabled"

    if error:
        typer.secho(
            f'updating application # {app_id} failed with status: "{status_txt}"',
            fg=typer.colors.RED,
        )
        logging.error(f'updating application # {app_id} failed with status: "{status_txt}"')
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""Application # {app_id} updated successfully with status: "{status_txt}" """,
            fg=typer.colors.GREEN,
        )
        logging.info(f"""Application # {app_id} updated successfully with status: "{status_txt}" """)

@app.command("update-app-process-status")
def update_app_process_status(
    app_id: str = typer.Argument(..., help="ID of the app to update"),
    process_status: int = typer.Option(1, "--process-status", "-prs", min=0, max=2, help="App process status (0=>not processed, 1=>inprocess, or 2=>processed)"),
) -> None:
    """
    The function `update_app_process_status` updates the process status of an existing application.
    
    :param app_id: The `app_id` parameter is a required argument that represents the ID of the app to
    update. It is used to identify the specific application that needs its process status updated
    :type app_id: str
    :param process_status: The `process_status` parameter is an integer that represents the status of
    the application process. It can have one of the following values:
    :type process_status: int
    """
    # Example usage: python your_script.py update_app_process_status --id "231541323453553701" --name "Updated Name" --app-name "Updated App" --method POST

    applications = get_applications()
    application_result = applications.update_app_process_status(app_id, process_status)
    error = application_result.error

    if error:
        typer.secho(
            f'updating application # {app_id} failed with status: "{process_status}"',
            fg=typer.colors.RED,
        )
        logging.error(f'updating application # {app_id} failed with status: "{process_status}"')
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""Application # {app_id} updated successfully with status: "{process_status}" """,
            fg=typer.colors.GREEN,
        )
        logging.info(f"""Application # {app_id} updated successfully with status: "{process_status}" """)

@app.command("remove-app")
def remove_app(
    app_id: str = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """
    The `remove_app` function removes an application using its APP_ID, with an option to force deletion
    without confirmation.
    
    :param app_id: The `app_id` parameter is a required argument that represents the ID of the
    application to be removed
    :type app_id: str
    :param force: The `force` parameter is a boolean option that allows you to force the deletion of the
    application without any confirmation prompt. If `force` is set to `True`, the application will be
    removed immediately without any further confirmation. If `force` is set to `False` (the default
    value),
    :type force: bool
    """
    applications = get_applications()

    def _remove():
        application_result = applications.remove(app_id)
        error = application_result.error
        if error:
            typer.secho(
                f'Removing application # {app_id} failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            logging.error( f'Removing application # {app_id} failed with "{ERRORS[error]}"')
            raise typer.Exit(1)
        else:
            typer.secho(
                f"""Application # {app_id} was removed""",
                fg=typer.colors.GREEN,
            )
            logging.info(f"""Application # {app_id} was removed""")

    if force:
        _remove()
    else:
        try:
            application_result = applications.get_app_by_id(app_id)
            application = application_result.application
            error = application_result.error
            if error:
                typer.secho("Invalid APP_ID", fg=typer.colors.RED)
                raise typer.Exit(1)
        except IndexError:
            typer.secho("Invalid APP_ID", fg=typer.colors.RED)
            raise typer.Exit(1)
        delete = typer.confirm(
            f"Delete application # {app_id} with name : {application['name']}?"
        )
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")

@app.command(name="clear-apps")
def remove_all_apps(
    force: bool = typer.Option(
        ...,
        prompt="Delete all applications?",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """
    The function `remove_all_apps` removes all applications, with an option to force deletion
    without confirmation.
    
    :param force: The `force` parameter is a boolean flag that determines whether to delete all
    applications without confirmation. If `force` is set to `True`, the function will proceed with
    deleting all applications. If `force` is set to `False`, the function will cancel the operation
    :type force: bool
    """
    applications = get_applications()
    if force:
        error = applications.remove_all().error
        if error:
            typer.secho(
                f'Removing applications failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            logging.error(f'Removing applications failed with "{ERRORS[error]}"')
            raise typer.Exit(1)
        else:
            typer.secho("All applications were removed", fg=typer.colors.GREEN)
            logging.info("All applications were removed")
    else:
        typer.echo("Operation canceled")

@app.command("generate-fake")
def generate_fake(
    app_count: int = typer.Option(
        10,
        "--apps",
        "-a",
        prompt="App Count :",
        help="Number of fake apps you want to generate.",
    ),
    endpoints_in_app: int = typer.Option(
        10,
        "--endpoints",
        "-e",
        prompt="Enpoints Count in each App :",
        help="Number of fake endpoints you want to generate in each app.",
    ),
) -> None:
    """
    The `generate_fake` function generates random data for a specified number of apps and endpoints in
    each app, and logs the process.
    
    :param app_count: The `app_count` parameter is the number of fake apps you want to generate. It is
    an integer value and has a default value of 10. You can specify a different value using the `--apps`
    or `-a` command-line options
    :type app_count: int
    :param endpoints_in_app: The `endpoints_in_app` parameter represents the number of fake endpoints
    you want to generate in each app
    :type endpoints_in_app: int
    """
    try:
        logging.info(f"Generating Random data for Apps: {app_count} and {endpoints_in_app} endpoints in each app.")
        random_data.generate_random_data(app_count, endpoints_in_app)
    except Exception as err:
        logging.error(f'\nEncountered error in random data generation: {str(err)}\n')
        typer.secho(
            f'\nEncountered error in random data generation: {str(err)}\n',
            fg=typer.colors.BRIGHT_RED,
        )
    else:
        logging.info(f"Random Application Data and endpoint data generated successfully!")
        typer.secho(
            '\nRandom Application Data and endpoint data generated successfully! \n',
            fg=typer.colors.BRIGHT_YELLOW,
        )

@app.command("run-fake-server")
def run_fake_server() -> None:
    """
    The function `run_fake_server` runs fake web server to work with the Scheduler for testing purposes.
    """
    raw_api.run_fake_api()

# @app.command("test-scheduler")
# def test_scheduler() -> None:
#     """
#     The function `test_scheduler` runs the Scheduler for testing purposes through a user interface
#     instead of a service.
#     """
#     scheduler_service = SchedulerService()
#     scheduler_service.main()

def _version_callback(value: bool) -> None:
    """
    The function `_version_callback` prints the name and version of an application and then exits.
    
    :param value: The `value` parameter is a boolean value that determines whether to execute a specific
    code block or not
    :type value: bool
    """
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()
    
@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
):
    """
    The main function takes a boolean argument "version" and returns its value.
    
    :param version: A boolean flag indicating whether to show the application's version and exit
    :type version: bool
    :return: The `version` variable is being returned.
    """
    return version