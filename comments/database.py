"""This module provides the Autonomous Data Collector  Agent database functionality."""

import configparser
import json
from pysondb import PysonDB
from pysondb import errors as pysonErrors
import typer
import os

from autonomous_data_collection_agent import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS, __app_name__

# The code is creating file paths for two JSON database files: `database_endpoint.json` and
# `database_application.json`.
ENDPOINT_DB_FILE_PATH = os.path.join(os.getcwd(), __app_name__, "database_endpoint.json")
APP_DB_FILE_PATH = os.path.join(os.getcwd(), __app_name__, "database_application.json")


def get_database_path(config_file: str, item_type) -> str:
    """
    The function `get_database_path` returns the current path to the database based on the provided
    config file and item type.
    
    :param config_file: The `config_file` parameter is a string that represents the path to the
    configuration file. This file contains information about the application's settings, including the
    path to the database
    :type config_file: str
    :param item_type: The `item_type` parameter is a string that represents the type of item for which
    you want to retrieve the database path
    :return: the current path to the database as a string.
    """

    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return str(config_parser["General"][f"{item_type}_database"])


def init_database(db_path: str) -> int:
    """
    The function `init_database` creates a new database by writing an empty JSON object to a specified
    file path.
    
    :param db_path: The `db_path` parameter is a string that represents the path to the database file
    :type db_path: str
    :return: an integer value. The possible return values are:
    """
    try:
        with open(db_path, 'w') as file:
            json.dump({
            "version": 2,
            "keys": [],
            "data": {}
        }, file)
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR

# The `DBResponse` class represents a response from a database query, containing a list of items and
# an error code.
class DBResponse:
    item_list: list[dict]
    error: int
    def __init__(self, item_list, error):
        self.item_list = item_list
        self.error = error

# The `DatabaseHandler` class provides methods for interacting with a database, including adding,
# retrieving, updating, and deleting items.
class DatabaseHandler:
    def __init__(self, db_path: str) -> None:
        """
        The function initializes an instance of a class with a given database path.
        
        :param db_path: The `db_path` parameter is a string that represents the path to the database
        file. It is used to initialize the `self._db_path` attribute of the class. This attribute stores
        the path to the database file, which will be used to create an instance of the `PysonDB`
        :type db_path: str
        """
        self._db_path = db_path
        self._db = PysonDB(self._db_path)
    
    def add_item(self, item: dict) -> DBResponse:
        """
        The function `add_item` adds an item to a database and returns the ID of the added item.
        
        :param item: The `item` parameter is a dictionary that represents the item to be added to the
        database
        :type item: dict
        :return: a `DBResponse` object.
        """
        try:
            # returns id of the item
            return DBResponse([self._db.add(item)], SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_WRITE_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)

    def get_by_id(self, id: int) -> DBResponse:
        """
        The function `get_by_id` retrieves a record from a database based on its ID and returns a
        `DBResponse` object.
        
        :param id: The `id` parameter is an integer that represents the unique identifier of the item
        you want to retrieve from the database
        :type id: int
        :return: The code is returning a `DBResponse` object.
        """
        try:
            return DBResponse([self._db.get_by_id(id)], SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)
    
    def get_by_query(self, query_str: str) -> DBResponse:
        """
        The function `get_by_query` retrieves data from a database based on a query string and returns a
        `DBResponse` object.
        
        :param query_str: The `query_str` parameter is a string that represents a query to be executed
        on the database. It can be a lambda expression that filters the data based on certain
        conditions. For example, `lambda x: x['name'] == 'abi'` filters the data where the value of the
        '
        :type query_str: str
        :return: The code is returning a `DBResponse` object.
        """
        # example query lambda x: x['name'] == 'abi' or lambda x: x['knows_python'] is False
        try:
            return DBResponse(self._db.get_by_query(query=query_str), SUCCESS) 
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)
    
    def get_by_column(self, column_name: str, column_value: str) -> DBResponse:
        """
        The function `get_by_column` retrieves data from a database based on a specified column name and
        value.
        
        :param column_name: The `column_name` parameter is a string that represents the name of the
        column in the database table that you want to query
        :type column_name: str
        :param column_value: The `column_value` parameter is the value that you want to match in the
        specified column. It is used in the query to filter the results and retrieve the rows where the
        value in the specified column matches the `column_value`
        :type column_value: str
        :return: a `DBResponse` object.
        """
        # example query lambda x: x['name'] == 'abi' or lambda x: x['knows_python'] is False
    
        try:
            return  DBResponse(self._db.get_by_query(query=lambda x: x[column_name] == column_value), SUCCESS) 
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)
        
    def read_items(self) -> DBResponse:
        """
        The function reads items from a database and returns a response object.
        :return: The code is returning a `DBResponse` object.
        """
        try:
            return DBResponse(self._db.get_all(), SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)

    def update_by_id(self, id: int, data: dict) -> DBResponse:
        """
        The function updates a record in a database by its ID and returns a DBResponse object.
        
        :param id: The `id` parameter is an integer that represents the unique identifier of the data
        entry that needs to be updated in the database
        :type id: int
        :param data: The `data` parameter is a dictionary that contains the updated values for the
        record with the specified `id`
        :type data: dict
        :return: a `DBResponse` object.
        """
        try:
            return DBResponse(self._db.update_by_id(str(id), data), SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)
    
    def update_by_query(self, query_str: str, data: dict) -> DBResponse:
        """
        The function `update_by_query` updates data in a database based on a query string and returns a
        response.
        
        :param query_str: The `query_str` parameter is a string that represents a query condition. It
        can be a lambda function that takes a dictionary as input and returns a boolean value. The
        lambda function is used to filter the data in the database based on certain conditions
        :type query_str: str
        :param data: The `data` parameter is a dictionary that contains the updated values for the
        fields in the database. It is used to specify the new values that should be applied to the
        documents that match the query
        :type data: dict
        :return: a `DBResponse` object.
        """
         # example query lambda x: x['name'] == 'abi' or lambda x: x['knows_python'] is False
        try:
            return DBResponse(self._db.update_by_query(query_str, new_data=data), SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)

    def delete_by_id(self, id: int) -> DBResponse:
        """
        The function `delete_by_id` deletes a record from the database based on the given ID and returns
        a DBResponse object indicating the success or failure of the operation.
        
        :param id: The `id` parameter is an integer that represents the unique identifier of the item to
        be deleted from the database
        :type id: int
        :return: a `DBResponse` object.
        """
        try:
            self._db.delete_by_id(id)
            return DBResponse([], SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)
    
    def delete_by_query(self, query_str: str) -> DBResponse:
        """
        The function `delete_by_query` deletes records from a database based on a given query string and
        returns a response indicating the success or failure of the operation.
        
        :param query_str: The `query_str` parameter is a string that represents a query used to filter
        and select specific data in the database. It can be a lambda expression that defines the
        conditions for deleting data. For example, `lambda x: x['name'] == 'abi'` would delete all
        records where the
        :type query_str: str
        :return: The function `delete_by_query` returns a `DBResponse` object.
        """
         # example query lambda x: x['name'] == 'abi' or lambda x: x['knows_python'] is False
        try:
            return  DBResponse(self._db.delete_by_query(query_str), SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)

    def write_items(self, item_list: list[dict]) -> DBResponse:
        """
        The function writes a list of items to a database and returns a response indicating success or
        failure.
        
        :param item_list: The `item_list` parameter is a list of dictionaries. Each dictionary
        represents an item and contains key-value pairs representing the item's attributes
        :type item_list: list[dict]
        :return: a `DBResponse` object.
        """
        # test = '[{"column_name":"created_at", "operator":"<", "column_value":"15-03-1988 10:58:15"}]'
        try:
            item_list_ids = self._db.add_many(item_list, json_response= True)
            return DBResponse(item_list_ids, SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse(item_list, DB_WRITE_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)
    
    def purge(self) -> DBResponse:
        """
        The `purge` function purges the database and returns a `DBResponse` object with an empty list
        and a success status, or an error status if there is a file IO problem or an ID does not exist
        error.
        :return: a `DBResponse` object.
        """
        try:
            self._db.purge()
            return DBResponse([], SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse([], DB_READ_ERROR)
        except pysonErrors.IdDoesNotExistError as error:
            typer.secho(
                    f"ID Not found/mismatch Error: {error.message}", fg=typer.colors.RED
                )
            raise typer.Exit(1)

# python -m autonomous_data_collection_agent update-app 331280544566123098 -df "[{\"column_name\":\"CREATED_AT\",\"operator\":\"=\",\"column_value\":\"15-03-1988 10:58:15\"},{\"column_name\":\"UPDATED_AT\",\"operator\":\"=\", \"column_value\":\"15-03-1988 10:58:15\"}]"