"""This module provides to initialize and configure the Autonomous Data Collector Agent.

:param db_paths: A list of tuples containing the names and paths of the databases to be created
:type db_paths: []
:return: The module provides several functions that return an integer value indicating the success
or failure of the operation. The specific values returned are:
"""

import configparser
from cryptography.fernet import Fernet
import typer
import os

from autonomous_data_collection_agent import DB_WRITE_ERROR, DIR_ERROR, FILE_ERROR, SUCCESS, __app_name__

# The code is creating file paths for the configuration file and log file.
CONFIG_DIR_PATH = os.path.join(os.getcwd(), __app_name__)
CONFIG_FILE_PATH = CONFIG_DIR_PATH + "/" + "config.ini"
LOG_FILE_PATH = CONFIG_DIR_PATH  + "/" +  "app.log"

def init_app(db_paths: []) -> int:
    """
    The `init_app` function initializes the application by performing various setup tasks such as
    creating a configuration file, creating a database, creating a logfile, generating an encryption
    key, setting up Keycloak configuration, and setting up threading configuration.
    
    :param db_paths: The `db_paths` parameter is a list of paths to the databases that need to be
    created
    :type db_paths: []
    :return: an integer value.
    """
    config_code = _init_config_file()
    if config_code != SUCCESS:
        return config_code
    database_code = _create_database(db_paths)
    if database_code != SUCCESS:
        return database_code

    logfile_error_code = _create_logfile(LOG_FILE_PATH)
    if logfile_error_code != SUCCESS:
        return logfile_error_code
    else:
        typer.secho(f"Logfile is successfully created at {LOG_FILE_PATH}", fg=typer.colors.BRIGHT_MAGENTA)
   
    encryption_error_code = _create_encryption_key()
    if encryption_error_code != SUCCESS:
        return encryption_error_code
    else:
        typer.secho(f"Encryption key generated succesfully. ", fg=typer.colors.YELLOW)
    

    keycloak_error_code = _create_keycloak_config()
    if keycloak_error_code != SUCCESS:
        return keycloak_error_code
    else:
        typer.secho(f"Keycloak config basic setup done. Please update details for realtime use.", fg=typer.colors.BLUE)

    
    threading_error_code = _create_threading_config()
    if threading_error_code != SUCCESS:
        return threading_error_code
    else:
        typer.secho(f"Threading config basic setup done. Please update details for realtime use.", fg=typer.colors.BRIGHT_CYAN)

    return SUCCESS


def _init_config_file() -> int:
    """
    The function initializes a configuration file by creating a directory and a file, and returns a
    success code if successful.
    :return: an integer value. The possible return values are:
    - `SUCCESS` if the configuration directory and file were successfully created or already exist.
    - `DIR_ERROR` if there was an error creating the configuration directory.
    - `FILE_ERROR` if there was an error creating the configuration file.
    """
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return DIR_ERROR
    try:
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return FILE_ERROR
    return SUCCESS

def _create_threading_config() -> int:
    """
    The function `_create_threading_config()` creates a threading configuration file with enabled
    threading and a specified number of concurrent threads.
    :return: an integer value. If the write operation to the config file is successful, it will return
    the value of the constant `SUCCESS`. If there is an error while writing to the file, it will return
    the value of the constant `DB_WRITE_ERROR`.
    """
    config_parser = configparser.ConfigParser()
    config_parser.read(CONFIG_FILE_PATH)
    config_parser["Threading"] = {"enabled": True, "concurrent_threads": 2 }

    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return DB_WRITE_ERROR
    return SUCCESS

def enable_threading(is_enabled: bool = True) -> int:
    """
    The function enables or disables threading by updating a configuration file.
    
    :param is_enabled: A boolean value indicating whether threading should be enabled or not, defaults
    to True
    :type is_enabled: bool (optional)
    :return: an integer value. If the write operation to the configuration file is successful, it will
    return the value of the constant `SUCCESS`. If there is an error while writing to the file, it will
    return the value of the constant `DB_WRITE_ERROR`.
    """
    config_parser = configparser.ConfigParser()
    # Read the existing file first
    config_parser.read(CONFIG_FILE_PATH)
    # Add the new section
    config_parser["Threading"]["enabled"] = str(is_enabled)
    try:
        with open(CONFIG_FILE_PATH, "w") as file:
            config_parser.write(file)
    except OSError:
        return DB_WRITE_ERROR
    return SUCCESS

def set_concurrent_threads(thread_count: int = 2) -> int:
    """
    The function sets the number of concurrent threads in a configuration file.
    
    :param thread_count: The `thread_count` parameter is an integer that represents the number of
    concurrent threads you want to set, defaults to 2
    :type thread_count: int (optional)
    :return: an integer value. If the file write operation is successful, it will return the value of
    the constant `SUCCESS`. If there is an error while writing to the file, it will return the value of
    the constant `DB_WRITE_ERROR`.
    """
    config_parser = configparser.ConfigParser()
    # Read the existing file first
    config_parser.read(CONFIG_FILE_PATH)
    # Add the new section

    config_parser["Threading"]["concurrent_threads"] = str(thread_count)
   
    try:
        with open(CONFIG_FILE_PATH, "w") as file:
            config_parser.write(file)
    except OSError:
        return DB_WRITE_ERROR
    return SUCCESS

def _create_keycloak_config() -> int:
    """
    The function `_create_keycloak_config()` creates a Keycloak configuration file with default values.
    :return: an integer value. If the writing of the configuration file is successful, it will return
    the value of the constant `SUCCESS`. If there is an error while writing the file, it will return the
    value of the constant `DB_WRITE_ERROR`.
    """
    config_parser = configparser.ConfigParser()
    config_parser.read(CONFIG_FILE_PATH)
    keycloak_config_keys = ['keycloak_url', 'client_id', 'client_secret', 'realm_name']
    keycloak_obj = {}
    for config_key in keycloak_config_keys:
        keycloak_obj[config_key] =  ""

    config_parser["Keycloak"] = keycloak_obj

    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return DB_WRITE_ERROR
    return SUCCESS

def _create_database(db_paths: []) -> int:
    """
    The function `_create_database` creates a database configuration file with the provided database
    paths.
    
    :param db_paths: The `db_paths` parameter is a list of tuples. Each tuple contains two elements: the
    `db_name` and the `db_path`. The `db_name` is a string representing the name of the database, and
    the `db_path` is a string representing the path to the database file
    :type db_paths: []
    :return: an integer value. If the writing of the database configuration file is successful, it will
    return the value of the constant `SUCCESS`. If there is an error while writing the file, it will
    return the value of the constant `DB_WRITE_ERROR`.
    """
    config_parser = configparser.ConfigParser()
    config_parser.read(CONFIG_FILE_PATH)
    db_obj = {}
    for db_name, db_path in db_paths:
        db_obj[f"{db_name}_database"] =  db_path

    config_parser["General"] = db_obj
    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return DB_WRITE_ERROR
    return SUCCESS

def _create_logfile(log_file_path: str) -> int:
    """
    The function `_create_logfile` creates a log file path in a configuration file and creates an empty
    log file if it doesn't exist.
    
    :param log_file_path: The `log_file_path` parameter is a string that represents the path where the
    log file will be created
    :type log_file_path: str
    :return: an integer value. If the file write operations are successful, it returns the value of the
    constant `SUCCESS`. If there is an error while writing to the file, it returns the value of the
    constant `DB_WRITE_ERROR`.
    """
    config_parser = configparser.ConfigParser()
    # Read the existing file first
    config_parser.read(CONFIG_FILE_PATH)
    # Add the new section
    config_parser["General"]["log_file_path"] = str(log_file_path)
    try:
        with open(CONFIG_FILE_PATH, "w") as file:
            config_parser.write(file)
        
        if not os.path.isfile(log_file_path):
            with open(log_file_path, "w") as file:
                file.close()
    except OSError:
        return DB_WRITE_ERROR
    return SUCCESS

def _create_encryption_key() -> int:
    """
    The function creates an encryption key and writes it to a configuration file.
    :return: an integer value. If the file write operation is successful, it returns the value of the
    constant `SUCCESS`. If there is an error while writing the file, it returns the value of the
    constant `DB_WRITE_ERROR`.
    """
    config_parser = configparser.ConfigParser()
    # Read the existing file first
    config_parser.read(CONFIG_FILE_PATH)
    # Add the new section
    config_parser["Encryption"] = dict({"key": Fernet.generate_key(), "enabled": False})
    try:
        with open(CONFIG_FILE_PATH, "w") as file:
            config_parser.write(file)
    except OSError:
        return DB_WRITE_ERROR
    return SUCCESS

def enable_encryption(is_enabled: bool = True) -> int:
    """
    The function enables encryption by updating the configuration file with the specified encryption
    status.
    
    :param is_enabled: A boolean value indicating whether encryption should be enabled or not, defaults
    to True
    :type is_enabled: bool (optional)
    :return: an integer value. If the file write operation is successful, it will return the value of
    the constant `SUCCESS`. If there is an error while writing to the file, it will return the value of
    the constant `DB_WRITE_ERROR`.
    """
    config_parser = configparser.ConfigParser()
    # Read the existing file first
    config_parser.read(CONFIG_FILE_PATH)
    # Add the new section
    config_parser["Encryption"]["enabled"] = str(is_enabled)
    try:
        with open(CONFIG_FILE_PATH, "w") as file:
            config_parser.write(file)
    except OSError:
        return DB_WRITE_ERROR
    return SUCCESS

def reset_encryption_key() -> int:
    """
    The function `reset_encryption_key` generates a new encryption key and updates it in a configuration
    file.
    :return: an integer value. If the file write operation is successful, it returns the value of the
    constant `SUCCESS`. If there is an error while writing to the file, it returns the value of the
    constant `DB_WRITE_ERROR`.
    """
    config_parser = configparser.ConfigParser()
    # Read the existing file first
    config_parser.read(CONFIG_FILE_PATH)
    # Add the new section

    config_parser["Encryption"]["key"] = str(Fernet.generate_key())
   
    try:
        with open(CONFIG_FILE_PATH, "w") as file:
            config_parser.write(file)
    except OSError:
        return DB_WRITE_ERROR
    return SUCCESS

def getLogFilePath():
    """
    The function `getLogFilePath` returns the log file path from a configuration file, or a default log
    file path if the configuration file is not found or an error occurs.
    :return: the value of the "log_file_path" key from the "General" section of the configuration file
    if it exists. If there is an exception or the key does not exist, it will return the value of the
    LOG_FILE_PATH variable.
    """
    config_parser = configparser.ConfigParser()
   
    try:
        # Read the existing file first
        config_parser.read(CONFIG_FILE_PATH)
        return config_parser["General"]["log_file_path"]
    except Exception as e:
        return LOG_FILE_PATH

def getKeycloakConfig():
    """
    The above function reads a Keycloak configuration file using configparser and returns the Keycloak
    section of the configuration.
    :return: The function `getKeycloakConfig()` returns the configuration values for Keycloak from a
    config file.
    """
    config_parser = configparser.ConfigParser()
   
    try:
        # Read the existing file first
        config_parser.read(CONFIG_FILE_PATH)
        return config_parser["Keycloak"]
    except Exception as e:
        typer.secho(
            f'Keycloak Config File Error : {str(e)}',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

def get_threading_config():
    """
    The function `get_threading_config()` reads a threading configuration file and returns the
    configuration settings.
    :return: The function `get_threading_config()` returns the configuration settings for threading from
    a config file.
    """
    config_parser = configparser.ConfigParser()
   
    try:
        # Read the existing file first
        config_parser.read(CONFIG_FILE_PATH)
        return config_parser["Threading"]
    except Exception as e:
        typer.secho(
            f'Threading Config File Error : {str(e)}',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)