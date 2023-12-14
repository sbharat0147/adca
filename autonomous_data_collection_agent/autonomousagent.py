"""This module provides the Autonomous Data Collector Agent model-controller."""

from datetime import datetime
import re
# The above code is importing the `os` module in Python.
import os
import json
import typer
from autonomous_data_collection_agent import config, APP_NOT_FOUND, ENDPOINT_NOT_FOUND, DUPLICATE_RECORD
from autonomous_data_collection_agent.database import DatabaseHandler, get_database_path
import logging  # Import the logging module

logging.basicConfig(filename=config.getLogFilePath(), filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%d-%b-%y %H:%M:%S", level=logging.DEBUG)

# The `CurrentEndpoint` class represents an endpoint with its associated error code.
class CurrentEndpoint:
    endpoint: dict
    error: int
    def __init__(self, endpoint, error):
        self.endpoint = endpoint
        self.error = error
    # Endpoint Object Structure:
    # 
    # The above code is a comment in Python. It starts with a hash symbol (#) which indicates that it
    # is a single-line comment. It is used to provide explanatory notes or documentation within the
    # code. In this case, it appears to be documenting the purpose or description of a variable named
    # "id" which is expected to be an integer.
    
    # endpoint : {
    #     id: int,
    #     app_id: str,
    #     name: str,
    #     url_endpoint: str,
    #     method: (GET | POST),
    #     payload: {table_name: str, ...},
    #     filters: [{
    #         column_name: str (CREATED_AT | UPDATED_AT | DELETED_AT),
    #         operator: (> | < | = | >= | <= | != | <> ),
    #         column_value: DD-MM-YYYY hh:mm:ss
    #     }],
    #     page_size: int,
    #     last_sync: date_time,
    #     process_status: 0 | 1 | 2
    #     failed_count: 0 
    #     failed_time: DD-MM-YYYY hh:mm:ss
    #     status: 0 | 1
    # }

# The class "CurrentApplication" represents a current application with its attributes "application"
# and "error".
class CurrentApplication:
    application: dict
    error: int
    def __init__(self, application, error):
        self.application = application
        self.error = error
    
    # Application Object Structure
    # 
    # application: {
    #     id: int,
    #     name: str,
    #     short_name: str,
    #     host: str,
    #     url_scheme: str (http| https),
    #     auth_type: str (None | KEYCLOAK | BASIC),
    #     auth_data: {},
    #     dump_path: str,
    #     sync_frequency: str (cronjob),
    #     last_sync: date_time,
    #     next_sync: date_time,
    #     default_payload: {},
    #     default_filters: [{
    #         column_name: str (CREATED_AT | UPDATED_AT | DELETED_AT),
    #         operator: (> | < | = | >= | <= | != | <> ),
    #         column_value: DD-MM-YYYY hh:mm:ss
    #     }],
    #     default_page_size: int,
    #     process_status: 0 | 1 | 2
    # }


# The `Endpoints` class provides methods for managing and manipulating endpoint data in a database.
class Endpoints:
    def __init__(self, db_path: str) -> None:
        """
        The function initializes an instance of a class with a database handler object.
        
        :param db_path: The `db_path` parameter is a string that represents the path to the database
        file. It is used to initialize the `DatabaseHandler` object, which will handle all the
        interactions with the database
        :type db_path: str
        """
        self._db_handler = DatabaseHandler(db_path)
    
    def validate_endpoint_data(self, data: dict):
        """
        The function `validate_endpoint_data` validates the data dictionary for a specific endpoint,
        ensuring that the values are of the correct types.
        
        :param data: The `data` parameter is a dictionary that contains information about an endpoint.
        It is used to validate the data types of the values in the dictionary. The dictionary should
        have the following keys:
        :type data: dict
        :return: a boolean value of True.
        """

        if data["name"] is not None:
            if not isinstance(data["name"], str):
                typer.secho(
                    "Endpoint name must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
        if data["app_id"] is not None:
            if not isinstance(data["app_id"], str):
                typer.secho(
                    "Endpoint app id must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
        if data["url_endpoint"] is not None:
            if not isinstance(data["url_endpoint"], str):
                typer.secho(
                    "Endpoint url must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)

        if data["method"] is not None:
            if not isinstance(data["method"], str):
                typer.secho(
                    "Endpoint method must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
        
        if data["payload"] is not None:
            if not (isinstance(data["payload"], str) or isinstance(data["payload"], dict)):
                typer.secho(
                    "Endpoint payload must be of type string or dict", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
            try:
                if isinstance(data["payload"], str): 
                    payload: dict = json.loads(data["payload"])
                    if not isinstance(payload, dict):
                        typer.secho(
                            "Endpoint payload must be valid JSON string of single object", fg=typer.colors.RED
                        )
                        raise typer.Exit(1)
            except json.decoder.JSONDecodeError:
                typer.secho(
                    "Endpoint payload must be valid JSON string", fg=typer.colors.RED
                )
                raise typer.Exit(1)

        if data["filters"] is not None:
            if not (isinstance(data["filters"], str) or isinstance(data["filters"], list)):
                typer.secho(
                    "Endpoint filters must be of type string or list", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
            try:
                if isinstance(data["filters"], str): 
                    filters: list[dict] = json.loads(data["filters"])
                    if not isinstance(filters, list):
                        typer.secho(
                            "Endpoint filters must be valid JSON string of list of objects", fg=typer.colors.RED
                        )
                        raise typer.Exit(1)
            except json.decoder.JSONDecodeError:
                typer.secho(
                    "Endpoint filters must be valid JSON string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
        if data["last_sync"] is not None:
            if not (isinstance(data["last_sync"], str) or isinstance(data["last_sync"], datetime)):
                typer.secho(
                    "Endpoint last sync must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
        
        if data["page_size"] is not None:
            if not isinstance(data["page_size"], int):
                typer.secho(
                    "Endpoint page_size must be of type integer", fg=typer.colors.RED
                )
                raise typer.Exit(1)    
        
        if data["process_status"] is not None:
            if not isinstance(data["process_status"], int):
                typer.secho(
                    "Endpoint process_status must be of type integer", fg=typer.colors.RED
                )
                raise typer.Exit(1) 
        
        if data["status"] is not None:
            if not isinstance(data["status"], int):
                typer.secho(
                    "Endpoint status must be of type integer", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
        return True
    
    def add(self, name: str, app_short_name: str, url_endpoint: str, method: str, payload: dict, filters: list[dict], page_size: int, last_sync: datetime, process_status: int, status: int) -> CurrentEndpoint:
        """
        The function adds a new endpoint to the database with the provided parameters.
        
        :param name: The name of the endpoint to be added to the database. It should be a string
        :type name: str
        :param app_short_name: The `app_short_name` parameter is a string that represents the short name
        of the application to which the endpoint belongs
        :type app_short_name: str
        :param url_endpoint: The `url_endpoint` parameter is a string that represents the URL endpoint
        of the API. It is the address where the API can be accessed
        :type url_endpoint: str
        :param method: The "method" parameter specifies the HTTP method to be used for the endpoint. It
        can have two possible values: "GET" or "POST"
        :type method: str
        :param payload: The `payload` parameter is a dictionary that represents the data to be sent in
        the request body when making a POST request to the specified `url_endpoint`. It contains
        key-value pairs where the keys represent the field names and the values represent the
        corresponding values to be sent
        :type payload: dict
        :param filters: The `filters` parameter is a list of dictionaries. Each dictionary represents a
        filter condition for the endpoint. Each dictionary should have the following keys:
        :type filters: list[dict]
        :param page_size: The `page_size` parameter is an integer that specifies the number of records
        to be returned per page when retrieving data from the endpoint
        :type page_size: int
        :param last_sync: The parameter "last_sync" is of type datetime. It represents the date and time
        of the last synchronization for the endpoint
        :type last_sync: datetime
        :param process_status: The parameter "process_status" represents the status of the endpoint's
        processing. It can have three possible values:
        :type process_status: int
        :param status: The "status" parameter is an integer that represents the status of the endpoint.
        It can have the following values:
        :type status: int
        :return: an instance of the `CurrentEndpoint` class, which contains the endpoint data and an
        error code.
        """

        if type(filters) is str:
            filters = json.loads(filters)

        if type(payload) is str:
            payload = json.loads(payload)
        
        assert method in ["GET", "POST"], "Invalid method. Only 'GET' and 'POST' are allowed."
        assert process_status in [0, 1, 2], "Invalid process status. Only 0, 1 and 2 are allowed."
        for filter in filters:
            assert filter['column_name'] in ["CREATED_AT", "UPDATED_AT", "DELETED_AT"], "Invalid column name. Only 'CREATED_AT', 'UPDATED_AT' and 'DELETED_AT' are allowed."
            assert filter['operator'] in [">", "<", "=", ">=", "<=", "!=", "<>"], "Invalid operator. Only '>', '<', '=', '>=', '<=', '!=', '<>' are allowed."
            datetime.strptime(filter['column_value'], '%d-%m-%Y %H:%M:%S')  # This will raise a ValueError if the date format is incorrect

        app_handler = DatabaseHandler(get_database_path(config.CONFIG_FILE_PATH, 'app'))
        try:
            app_id = str(next(iter(app_handler.get_by_column('short_name', app_short_name).item_list)))
        except IndexError:
            return CurrentEndpoint({}, APP_NOT_FOUND)
        
        if not app_id:
            return CurrentEndpoint({}, APP_NOT_FOUND)
    
        endpoint = {
            "app_id": app_id,
            "name": name,
            "url_endpoint": url_endpoint,
            "method": method,
            "payload": payload,
            "filters": filters,
            "page_size": page_size,
            "last_sync": last_sync,
            "process_status": process_status,
            "failed_count": 0,
            "failed_time": "",
            "status": status
        }

        self.validate_endpoint_data(endpoint)

        duplicate_endpoint_name_obj = self.get_app_endpoint_by_name(app_id, name) 

        if duplicate_endpoint_name_obj.endpoint :
            return CurrentEndpoint({}, DUPLICATE_RECORD)
        
        read = self._db_handler.add_item(endpoint)
        return CurrentEndpoint(endpoint, read.error)
            

    def get_endpoint_list(self) -> list[dict]:
        """
        The function `get_endpoint_list` returns the current endpoint list by reading items from the
        database handler.
        :return: the item list from the database handler.
        """
        read = self._db_handler.read_items()
        return read.item_list
    
    def get_endpoint_by_id(self, ENDPOINT_ID: str) -> CurrentEndpoint:
        """
        The function `get_endpoint_by_id` returns the endpoint with the specified ID.
        
        :param ENDPOINT_ID: The `ENDPOINT_ID` parameter is a string that represents the unique
        identifier of the endpoint you want to retrieve
        :type ENDPOINT_ID: str
        :return: an instance of the `CurrentEndpoint` class.
        """

        read = self._db_handler.get_by_id(ENDPOINT_ID)
        if read.error:
            return CurrentEndpoint({}, read.error)
        try:
            return CurrentEndpoint( read.item_list[0], read.error)
        except IndexError:
            return CurrentEndpoint({}, ENDPOINT_NOT_FOUND)
        
    def get_endpoint_by_name(self, name: str) -> CurrentEndpoint:
        """
        The function `get_endpoint_by_name` returns the endpoint with a given name.
        
        :param name: The `name` parameter is a string that represents the name of the endpoint that you
        want to retrieve
        :type name: str
        :return: an instance of the `CurrentEndpoint` class.
        """

        read = self._db_handler.get_by_column('name', name)
        if read.error:
            return CurrentEndpoint({}, read.error)
        try:
            return CurrentEndpoint( read.item_list, read.error)
        except IndexError:
            return CurrentEndpoint({}, ENDPOINT_NOT_FOUND)
    
    def get_app_endpoint_by_name(self, app_id: str, name: str) -> CurrentEndpoint:
        """
        The function `get_app_endpoint_by_name` returns the endpoint with a specific name for a given
        app ID.
        
        :param app_id: The `app_id` parameter is a string that represents the ID of the application. It
        is used to filter the endpoints based on the specified application ID
        :type app_id: str
        :param name: The `name` parameter is a string that represents the name of the endpoint you want
        to retrieve
        :type name: str
        :return: an instance of the `CurrentEndpoint` class.
        """

        read = self._db_handler.get_by_query(lambda x: x['app_id'] == app_id and x['name'] == name)
        if read.error:
            return CurrentEndpoint({}, read.error)
        try:
            return CurrentEndpoint( read.item_list, read.error)
        except IndexError:
            return CurrentEndpoint({}, ENDPOINT_NOT_FOUND)
    
    def get_endpoint_by_url(self, url_endpoint: str) -> CurrentEndpoint:
        """
        The function `get_endpoint_by_url` returns the endpoint by name based on the provided URL
        endpoint.
        
        :param url_endpoint: The `url_endpoint` parameter is a string that represents the URL endpoint.
        It is used to search for an endpoint in the database
        :type url_endpoint: str
        :return: an instance of the `CurrentEndpoint` class.
        """
        read = self._db_handler.get_by_column('url_endpoint', url_endpoint)
        if read.error:
            return CurrentEndpoint({}, read.error)
        try:
            return CurrentEndpoint( read.item_list, read.error)
        except IndexError:
            return CurrentEndpoint({}, ENDPOINT_NOT_FOUND)
    
    def get_endpoints_by_query(self, query: str) -> list[dict]:
        """
        The function `get_endpoints_by_query` returns a list of endpoints filtered by a custom query.
        
        :param query: A string representing the custom query to filter the endpoint list
        :type query: str
        :return: a list of dictionaries.
        """
        read = self._db_handler.get_by_query(query_str=query)
        return read.item_list
    
    def get_app_endpoints(self, app_short_name: str):
        """
        The function `get_app_endpoints` returns the current endpoint list for a given application short
        name.
        
        :param app_short_name: The `app_short_name` parameter is a string that represents the short name
        of an application
        :type app_short_name: str
        :return: a list of dictionaries, which represents the current endpoint list for the specified
        application.
        """
        app_handler = DatabaseHandler(get_database_path(config.CONFIG_FILE_PATH, 'app'))
        try:
            app_id = str(next(iter(app_handler.get_by_column('short_name', app_short_name).item_list)))
        except IndexError:
            return CurrentEndpoint({}, APP_NOT_FOUND)
        
        if app_id:
            read = self._db_handler.get_by_column('app_id', app_id)
            return read.item_list
        return CurrentEndpoint({}, APP_NOT_FOUND)
    
    def get_app_endpoints_by_process_status(self, app_short_name: str, process_status: int):
        """
        The function `get_app_endpoints_by_process_status` returns the current endpoint list for a given
        application filtered by process status.
        
        :param app_short_name: The `app_short_name` parameter is a string that represents the short name
        of the application. It is used to filter the application by its short name
        :type app_short_name: str
        :param process_status: The `process_status` parameter is an integer that represents the status
        of a process. It is used to filter the endpoint list for a specific application based on the
        process status
        :type process_status: int
        :return: a list of dictionaries that represent the current endpoint list for an application
        filtered by process status.
        """
        
        app_handler = DatabaseHandler(get_database_path(config.CONFIG_FILE_PATH, 'app'))
        all_apps = app_handler.get_by_column('short_name', app_short_name).item_list
        try:
            if all_apps:
                app_id = str(next(iter(app_handler.get_by_column('short_name', app_short_name).item_list)))
        except IndexError:
            return CurrentEndpoint({}, APP_NOT_FOUND)
        
        if app_id:
            read = self._db_handler.get_by_query(lambda x: x['app_id'] == app_id and x['process_status'] == process_status)
            return read.item_list
        return CurrentEndpoint({}, APP_NOT_FOUND)
    
    def get_app_endpoints_by_status(self, app_short_name: str, status: int):
        """
        The function `get_app_endpoints_by_status` returns the current endpoint list for an application
        filtered by status.
        
        :param app_short_name: The `app_short_name` parameter is a string that represents the short name
        of an application. It is used to identify the application in the database
        :type app_short_name: str
        :param status: The "status" parameter is an integer that represents the status of the
        application. It is used to filter the endpoint list for the application based on the specified
        status
        :type status: int
        :return: a list of dictionaries that represent the current endpoint list for an application
        filtered by status.
        """
        
        app_handler = DatabaseHandler(get_database_path(config.CONFIG_FILE_PATH, 'app'))
        try:
            app_id = next(iter(app_handler.get_by_column('short_name', app_short_name).item_list))
        except IndexError:
            return CurrentEndpoint({}, APP_NOT_FOUND)
        
        if app_id:
            read = self._db_handler.get_by_query(lambda x: x['app_id'] == app_id and x['status'] == status)
            return read.item_list
        return CurrentEndpoint({}, APP_NOT_FOUND)
    
    def update_endpoint(self, ENDPOINT_ID: str, data: dict) -> CurrentEndpoint:
        """
        The function updates an endpoint with the provided data and returns the updated endpoint along
        with any errors encountered.
        
        :param ENDPOINT_ID: The `ENDPOINT_ID` parameter is an integer that represents the unique
        identifier of the endpoint that needs to be updated
        :type ENDPOINT_ID: int
        :param data: The `data` parameter is a dictionary that contains the updated information for the
        endpoint
        :type data: dict
        :return: an instance of the `CurrentEndpoint` class. The `CurrentEndpoint` object contains the
        updated endpoint data and any error that occurred during the update process.
        """

        read = self._db_handler.get_by_id(ENDPOINT_ID)
        if read.error:
            return CurrentEndpoint({}, read.error)
        try:
            endpoint = read.item_list[0]
        except IndexError:
            return CurrentEndpoint({}, ENDPOINT_NOT_FOUND)
        
        endpoint.update(data)
        
        self.validate_endpoint_data(endpoint)

        duplicate_endpoint_obj = self.get_app_endpoint_by_name(endpoint["app_id"], endpoint["name"]) 

        if duplicate_endpoint_obj.endpoint and next(iter(duplicate_endpoint_obj.endpoint)) != ENDPOINT_ID:
            return CurrentEndpoint({}, DUPLICATE_RECORD)

        if type(endpoint["last_sync"]) is datetime:
           endpoint["last_sync"] = str(endpoint["last_sync"])

        write = self._db_handler.update_by_id(ENDPOINT_ID, data=endpoint)
        return CurrentEndpoint(endpoint, write.error)
    
    def update_endpoint_status(self, ENDPOINT_ID: str, status: int) -> CurrentEndpoint:
        """
        The function updates the status of an endpoint in a database and returns the updated endpoint
        along with any error that occurred during the update.
        
        :param ENDPOINT_ID: The `ENDPOINT_ID` parameter is an integer that represents the unique
        identifier of the endpoint that needs to be updated
        :type ENDPOINT_ID: int
        :param status: The "status" parameter is an integer that represents the updated status of the
        endpoint
        :type status: int
        :return: an instance of the `CurrentEndpoint` class. The `CurrentEndpoint` object contains the
        updated endpoint information and any error that occurred during the update process.
        """
       
        read = self._db_handler.get_by_id(ENDPOINT_ID)
        if read.error:
            return CurrentEndpoint({}, read.error)
        try:
            endpoint = read.item_list[0]
        except IndexError:
            return CurrentEndpoint({}, ENDPOINT_NOT_FOUND)
        endpoint.update({'status': status})
        write = self._db_handler.update_by_id(ENDPOINT_ID, data={'status': status})
        return CurrentEndpoint(endpoint, write.error)
    
    def update_endpoint_process_status(self, ENDPOINT_ID: int, process_status: int) -> CurrentEndpoint:
        """
        The function updates the process status of an endpoint in a database.
        
        :param ENDPOINT_ID: The ENDPOINT_ID parameter is an integer that represents the unique
        identifier of the endpoint that needs to be updated
        :type ENDPOINT_ID: int
        :param process_status: The `process_status` parameter is an integer that represents the status
        of a process associated with an endpoint
        :type process_status: int
        :return: an instance of the `CurrentEndpoint` class. The `CurrentEndpoint` object contains the
        updated endpoint data and any error that occurred during the update process.
        """

        read = self._db_handler.get_by_id(ENDPOINT_ID)
        if read.error:
            return CurrentEndpoint({}, read.error)
        try:
            endpoint = read.item_list[0]
        except IndexError:
            return CurrentEndpoint({}, ENDPOINT_NOT_FOUND)
        endpoint.update({'process_status': process_status})
        write = self._db_handler.update_by_id(ENDPOINT_ID, data={'process_status': process_status})
        return CurrentEndpoint(endpoint, write.error)
    
    def update_endpoints_by_query(self, query_str: str, data: dict):
        """
        The function `update_endpoints_by_query` updates endpoints based on a query string and returns
        the updated endpoints.
        
        :param query_str: The query string used to filter the endpoints that need to be updated. It is a
        string representation of a lambda function that takes a dictionary as input and returns a
        boolean value. The lambda function is used to define the conditions for updating the endpoints
        :type query_str: str
        :param data: A dictionary containing the updated values for the endpoints
        :type data: dict
        :return: a list of updated endpoints.
        """

        # query_str = lambda x: x['app_id'] == app_id and x['process_status'] == status
        write = self._db_handler.update_by_query(query_str=query_str, data=data)
        if write.error:
            return CurrentEndpoint({}, write.error)
    
        return write.item_list

    def remove(self, ENDPOINT_ID: int) -> CurrentEndpoint:
        """
        The function removes an endpoint from the database using its id or index and returns the result.
        
        :param ENDPOINT_ID: The `ENDPOINT_ID` parameter is an integer that represents the id or index of
        the endpoint that you want to remove from the database
        :type ENDPOINT_ID: int
        :return: The method is returning an instance of the `CurrentEndpoint` class.
        """
        write = self._db_handler.delete_by_id(ENDPOINT_ID)
        if write.error:
            return CurrentEndpoint({}, write.error)
        
        return CurrentEndpoint(ENDPOINT_ID, write.error)

    def remove_all(self) -> CurrentEndpoint:
        """
        The function removes all endpoints from the database.
        :return: The method `remove_all` returns a `CurrentEndpoint` object.
        """
        
        write = self._db_handler.purge()
        return CurrentEndpoint({}, write.error)
    
    def remove_all_by_app(self, app_short_name: str):
        """
        The function removes all endpoints of a specific application from the database.
        
        :param app_short_name: The `app_short_name` parameter is a string that represents the short name
        of an application
        :type app_short_name: str
        :return: a `CurrentEndpoint` object. The `CurrentEndpoint` object contains two attributes:
        `item_list` and `error`. The `item_list` attribute contains the list of deleted endpoints, and
        the `error` attribute contains any error message that occurred during the deletion process.
        """

        app_handler = DatabaseHandler(get_database_path(config.CONFIG_FILE_PATH, 'app'))
        try:
            app_id = next(iter(app_handler.get_by_column('short_name', app_short_name).item_list))
        except IndexError:
            return CurrentEndpoint({}, APP_NOT_FOUND)
        write = self._db_handler.delete_by_query(lambda x: x['app_id'] == app_id)

        if write.error:
            return CurrentEndpoint({}, write.error)
        else:
            return CurrentEndpoint(write.item_list, write.error)

# The `Applications` class is a Python class that provides methods for managing applications in a
# database, including adding, retrieving, updating, and deleting applications.
class Applications:
    def __init__(self, db_path: str) -> None:
        """
        The function initializes an instance of a class with a database handler object.
        
        :param db_path: The `db_path` parameter is a string that represents the path to the database
        file. It is used to initialize the `DatabaseHandler` object, which will handle all the
        interactions with the database
        :type db_path: str
        """
        self._db_handler = DatabaseHandler(db_path)
    
    def is_valid_cronjob(self, sync_frequency):
        """
        The function checks if a given sync frequency string matches the format of a cron job.
        
        :param sync_frequency: The `sync_frequency` parameter is a string that represents the frequency
        at which a cron job should run. It should be in the format of a cron expression, which consists
        of five space-separated fields representing the minute, hour, day of the month, month, and day
        of the week
        :return: The function is_valid_cronjob returns either the sync_frequency if it matches the
        cron_regex pattern, or False if it does not match the pattern. If sync_frequency is None, the
        function returns None.
        """
        # Regular expression to match the cron job format
        # @todo implement it with python-crontab module

        cron_regex = r'^\S+\s+\S+\s+\S+\s+\S+\s+\S+$'

        if sync_frequency is None:
            return None
        elif re.match(cron_regex, sync_frequency):
            return sync_frequency
        else:
            return False
        
    def check_and_create_directory(self, path):
        """
        The function checks if a directory exists and creates it if it doesn't.
        
        :param path: The `path` parameter is a string that represents the directory path that needs to
        be checked and created if it does not exist
        :return: the path of the directory if it is successfully created or if it already exists. If
        there is an error creating the directory, it returns a string indicating the error. If the path
        is None, it returns None.
        """
        try:
            if path is None:
                return None
            # Check if the directory exists
            elif not os.path.exists(path):
                # Directory does not exist, try to create it
                os.makedirs(path)
                return path  # No error, directory created successfully
            else:
                return path  # Directory already exists, no error
        except OSError as e:
            return f"Error creating directory: {str(e)}"
        
    def validate_app_data(self, data: dict):
        """
        The function `validate_app_data` validates the data dictionary for a specific set of keys and
        their corresponding value types.
        
        :param data: The `data` parameter is a dictionary that contains various attributes of an app.
        Each attribute is checked for its type and validity in the `validate_app_data` method
        :type data: dict
        :return: a boolean value of True.
        """

        if data["name"] is not None:
            if not isinstance(data["name"], str):
                typer.secho(
                    "App name must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
        if data["short_name"] is not None:
            if not isinstance(data["short_name"], str):
                typer.secho(
                    "App short name must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
        if data["host"] is not None:
            if not isinstance(data["host"], str):
                typer.secho(
                    "App host must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)

        if data["url_scheme"] is not None:
            if not isinstance(data["url_scheme"], str):
                typer.secho(
                    "App URL Scheme must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
        
        if data["auth_type"] is not None:
            if not isinstance(data["auth_type"], str):
                typer.secho(
                    "App Auth Type must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
        
        if data["auth_data"] is not None:
            if not (isinstance(data["auth_data"], str) or isinstance(data["auth_data"], dict)):
                typer.secho(
                    "App Auth Data must be of type string or dict", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
            try:
                if isinstance(data["auth_data"], str): 
                    auth_data: dict = json.loads(data["auth_data"])
                    if not isinstance(auth_data, dict):
                        typer.secho(
                            "App Auth Data must be valid JSON string of single object", fg=typer.colors.RED
                        )
                        raise typer.Exit(1)
            except json.decoder.JSONDecodeError:
                typer.secho(
                    "App Auth Data must be valid JSON string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
        if data["dump_path"] is not None:
            if not isinstance(data["dump_path"], str):
                typer.secho(
                    "App dump path must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
        
        if data["sync_frequency"] is not None:
            if not isinstance(data["sync_frequency"], str):
                typer.secho(
                    "App sync frequency must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
        
        if data["last_sync"] is not None:
            print(type(data["last_sync"]), data["last_sync"])
            if not (isinstance(data["last_sync"], str) or isinstance(data["last_sync"], datetime)):
                typer.secho(
                    "App last sync must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
        
        if data["next_sync"] is not None:
            if not (isinstance(data["next_sync"], str) or isinstance(data["next_sync"], datetime)):
                typer.secho(
                    "App next sync must be of type string", fg=typer.colors.RED
                )
                raise typer.Exit(1)

        if data["default_payload"] is not None:
            if not (isinstance(data["default_payload"], str) or isinstance(data["default_payload"], dict)):
                typer.secho(
                    "App default_payload must be of type string or dict", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
            try:
                if isinstance(data["default_payload"], str): 
                    default_payload: dict = json.loads(data["default_payload"])
                    if not isinstance(default_payload, dict):
                        typer.secho(
                            "App default_payload must be valid JSON string of single object", fg=typer.colors.RED
                        )
                        raise typer.Exit(1)
            except json.decoder.JSONDecodeError:
                typer.secho(
                    "App default_payload must be valid JSON string", fg=typer.colors.RED
                )
                raise typer.Exit(1)

        if data["default_filters"] is not None:
            if not (isinstance(data["default_filters"], str) or isinstance(data["default_filters"], list)):
                typer.secho(
                    "App default_filters must be of type string or list", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
            try:
                if isinstance(data["default_filters"], str): 
                    default_filters: list[dict] = json.loads(data["default_filters"])
                    if not isinstance(default_filters, list):
                        typer.secho(
                            "App default_filters must be valid JSON string of list of objects", fg=typer.colors.RED
                        )
                        raise typer.Exit(1)
            except json.decoder.JSONDecodeError:
                typer.secho(
                    "App default_filters must be valid JSON string", fg=typer.colors.RED
                )
                raise typer.Exit(1)
                            
        if data["default_page_size"] is not None:
            if not isinstance(data["default_page_size"], int):
                typer.secho(
                    "App default_page_size must be of type integer", fg=typer.colors.RED
                )
                raise typer.Exit(1)    
        
        if data["process_status"] is not None:
            if not isinstance(data["process_status"], int):
                typer.secho(
                    "App process_status must be of type integer", fg=typer.colors.RED
                )
                raise typer.Exit(1) 
        
        if data["status"] is not None:
            if not isinstance(data["status"], int):
                typer.secho(
                    "App status must be of type integer", fg=typer.colors.RED
                )
                raise typer.Exit(1)
            
        return True


    def add(self, name: str, short_name: str, host: str, url_scheme: str, auth_type: str, auth_data: dict, dump_path: str, sync_frequency: str, last_sync: datetime, next_sync: datetime, default_payload: dict, default_filters: list[dict], default_page_size: int, process_status: int, status: int ) -> CurrentApplication:
        """
        The function adds a new application to the database with various parameters and performs
        validation checks.
        
        :param name: The name of the application being added to the database. It should be a string
        :type name: str
        :param short_name: The `short_name` parameter is a string that represents the short name of the
        application being added to the database
        :type short_name: str
        :param host: The `host` parameter represents the host of the application. It is a string that
        specifies the hostname or IP address of the server where the application is hosted
        :type host: str
        :param url_scheme: The `url_scheme` parameter is a string that represents the scheme or protocol
        used in the URL of the application. It can have two possible values: "http" or "https"
        :type url_scheme: str
        :param auth_type: The `auth_type` parameter is a string that represents the type of
        authentication used by the application. It can have one of the following values: None,
        "KEYCLOAK", or "BASIC"
        :type auth_type: str
        :param auth_data: The `auth_data` parameter is a dictionary that contains authentication data
        for the application. It is used to store information required for authentication, such as API
        keys, tokens, or credentials
        :type auth_data: dict
        :param dump_path: The `dump_path` parameter is a string that represents the path where the
        application data will be dumped or stored
        :type dump_path: str
        :param sync_frequency: The `sync_frequency` parameter is a string that represents the frequency
        at which the application should be synchronized. It is typically specified using the cron job
        format, which allows for specifying specific intervals or patterns for synchronization
        :type sync_frequency: str
        :param last_sync: The parameter "last_sync" is of type datetime and represents the date and time
        of the last synchronization for the application
        :type last_sync: datetime
        :param next_sync: The parameter `next_sync` is a datetime object that represents the date and
        time of the next synchronization for the application
        :type next_sync: datetime
        :param default_payload: The `default_payload` parameter is a dictionary that represents the
        default payload data for the application. It contains key-value pairs where the keys represent
        the field names and the values represent the default values for those fields
        :type default_payload: dict
        :param default_filters: The `default_filters` parameter is a list of dictionaries. Each
        dictionary represents a filter that can be applied to the data. Each dictionary should have the
        following keys:
        :type default_filters: list[dict]
        :param default_page_size: The parameter `default_page_size` is an integer that represents the
        default number of items to be returned per page when making API requests
        :type default_page_size: int
        :param process_status: The parameter "process_status" is an integer that represents the status
        of the application's processing. It can have one of the following values:
        :type process_status: int
        :param status: The "status" parameter is an integer that represents the status of the
        application. It can have one of the following values:
        :type status: int
        :return: an instance of the `CurrentApplication` class, along with an error code.
        """

        if type(default_payload) is str:
            default_payload = json.loads(default_payload)
        if type(default_filters) is str:
           default_filters = json.loads(default_filters)
        
        if type(auth_data) is str:
           auth_data = json.loads(auth_data)

        assert url_scheme in ["http", "https"], "Invalid URL scheme. Only 'http' and 'https' are allowed."

        assert auth_type in [None, "NONE", "KEYCLOAK", "BASIC"], "Invalid authentication type. Only None, 'KEYCLOAK' and 'BASIC' are allowed."
        for filter in default_filters:
            assert filter['column_name'] in ["CREATED_AT", "UPDATED_AT", "DELETED_AT"], "Invalid column name. Only 'CREATED_AT', 'UPDATED_AT' and 'DELETED_AT' are allowed."
            assert filter['operator'] in [">", "<", "=", ">=", "<=", "!=", "<>"], "Invalid operator. Only '>', '<', '=', '>=', '<=', '!=', '<>' are allowed."
            datetime.strptime(filter['column_value'], '%d-%m-%Y %H:%M:%S')  # This will raise a ValueError if the date format is incorrect

        assert process_status in [0, 1, 2], "Invalid process status. Only 0, 1 and 2 are allowed."

        if not self.is_valid_cronjob(sync_frequency):
            print(f"'{sync_frequency}' is not a valid cron job frequency.")
        
        if not self.check_and_create_directory(dump_path):
            print(f"'{dump_path}' is not a valid direcotry or couldn't be created.")

        application = {
            "name": name,
            "short_name": short_name,
            "host": host,
            "url_scheme": url_scheme,
            "auth_type": auth_type,
            "auth_data": auth_data,
            "dump_path": dump_path,
            "sync_frequency": sync_frequency,
            "last_sync": last_sync,
            "next_sync": next_sync,
            "default_payload": default_payload,
            "default_filters": default_filters,
            "default_page_size": default_page_size,
            "process_status": process_status,
            "status": status
        }

        self.validate_app_data(application)
        duplicate_app_name_object = self.get_app_by_name(name) 
        duplicate_app_short_name_object = self.get_app_by_short_name(short_name)

        if duplicate_app_name_object.application or duplicate_app_short_name_object.application:
            return CurrentApplication({}, DUPLICATE_RECORD)
        app_result = self._db_handler.add_item(application)
        application = app_result.item_list
        error = app_result.error
        return CurrentApplication(application, error)


    def get_applications(self) -> list[dict]:
        """
        The function `get_applications` returns the current application list.
        :return: a list of dictionaries, which represents the current application list.
        """
        read = self._db_handler.read_items()
        return read.item_list

    def get_app_by_id(self, APP_ID: str) -> CurrentApplication:
        """
        The function `get_app_by_id` returns the endpoint of an application based on its ID.
        
        :param APP_ID: The `APP_ID` parameter is a string that represents the unique identifier of an
        application
        :type APP_ID: str
        :return: an instance of the `CurrentApplication` class.
        """
        read = self._db_handler.get_by_id(APP_ID)
        if read.error:
            return CurrentApplication({}, read.error)
        try:
            return CurrentApplication( read.item_list[0], read.error)
        except IndexError:
            return CurrentApplication({}, APP_NOT_FOUND)
        
    def get_app_by_name(self, name: str) -> CurrentApplication:
        """
        The function `get_app_by_name` returns the current application by name.
        
        :param name: The `name` parameter is a string that represents the name of the application you
        want to retrieve
        :type name: str
        :return: an instance of the `CurrentApplication` class.
        """

        read = self._db_handler.get_by_column('name', name)
        if read.error:
            return CurrentApplication({}, read.error)
        
        try:
            return CurrentApplication( read.item_list, read.error)
        except IndexError:
            return CurrentApplication({}, APP_NOT_FOUND)
    
    def get_app_by_short_name(self, short_name: str) -> CurrentApplication:
        """
        The function returns the current application based on its short name.
        
        :param short_name: The `short_name` parameter is a string that represents the short name of the
        application
        :type short_name: str
        :return: an instance of the `CurrentApplication` class.
        """
        read = self._db_handler.get_by_column('short_name', short_name)
        if read.error:
            return CurrentApplication({}, read.error)
        try:
            return CurrentApplication( read.item_list, read.error)
        except IndexError:
            return CurrentApplication({}, APP_NOT_FOUND)
    
    def get_app_by_status(self, status: int) -> list[dict]:
        """
        The function `get_app_by_status` returns a list of application dictionaries filtered by a given
        status.
        
        :param status: The `status` parameter is an integer that represents the status of the
        applications. It is used to filter the application list and return only the applications that
        have the specified status
        :type status: int
        :return: a list of dictionaries.
        """
        read = self._db_handler.get_by_query(lambda x: x['status'] == status)
        return read.item_list
    
    def get_app_by_query(self, query: str) -> list[dict]:
        """
        The function `get_app_by_query` returns a filtered list of applications based on a custom query.
        
        :param query: The `query` parameter is a string that represents a custom query to filter the
        current application list. It is used to retrieve specific applications based on certain criteria
        :type query: str
        :return: a list of dictionaries.
        """
        # query_str = lambda x: x['id'] == app_id and x['process_status'] == status
        
        read = self._db_handler.get_by_query(query_str=query)
        return read.item_list

    def get_app_by_process_status(self, process_status: int) -> list[dict]:
        """
        The function returns a list of current applications filtered by process status.
        
        :param process_status: The `process_status` parameter is an integer that represents the status
        of the application process. It is used to filter the current application list based on this
        status
        :type process_status: int
        :return: a list of dictionaries.
        """
    
        read = self._db_handler.get_by_query(lambda x: x['process_status'] == process_status and x['status']==1)
        return read.item_list
    
    def update_app(self, APP_ID: str, data: dict) -> CurrentApplication:
        """
        The function updates an application with the provided data and returns the updated application
        along with any errors encountered.
        
        :param APP_ID: The APP_ID parameter is an integer that represents the ID of the application that
        needs to be updated
        :type APP_ID: int
        :param data: The `data` parameter is a dictionary that contains the updated information for the
        application. It can include any fields that need to be updated, such as the application name,
        short name, default payload, default filters, and auth data
        :type data: dict
        :return: an instance of the `CurrentApplication` class.
        """
        read = self._db_handler.get_by_id(APP_ID)
        if read.error:
            return CurrentApplication({}, read.error)
        try:
            application = read.item_list[0]
        except IndexError:
            return CurrentApplication({}, APP_NOT_FOUND)
        
        application.update(data)

        self.validate_app_data(application)

        duplicate_app_name_object = self.get_app_by_name(application["name"]) 
        duplicate_app_short_name_object = self.get_app_by_short_name(application["short_name"])

        if (duplicate_app_name_object.application and next(iter(duplicate_app_name_object.application)) != APP_ID)  or (duplicate_app_short_name_object.application and next(iter(duplicate_app_short_name_object.application)) != APP_ID):
            return CurrentApplication({}, DUPLICATE_RECORD)
        
        if type(application["default_payload"]) is str:
            application["default_payload"] = json.loads(application["default_payload"])
        if type(application["default_filters"]) is str:
           application["default_filters"] = json.loads(application["default_filters"])
        
        if type(application["auth_data"]) is str:
           application["auth_data"] = json.loads(application["auth_data"])

        if type(application["last_sync"]) is datetime:
           application["last_sync"] = str(application["last_sync"])
        
        if type(application["next_sync"]) is datetime:
           application["next_sync"] = str(application["next_sync"])

        write = self._db_handler.update_by_id(APP_ID, data=application)
        return CurrentApplication(application, write.error)
    
    def update_app_status(self, APP_ID: str, status: int) -> CurrentApplication:
        """# The above code is likely updating an application. However, without more context
        # or code, it is difficult to determine the exact functionality or purpose of the
        # "update-app" command.
        
        The function updates the status of an application based on the provided status value.
        
        :param APP_ID: The APP_ID parameter is an integer that represents the ID of the application that
        needs to be updated
        :type APP_ID: int
        :param status: The "status" parameter is an integer that represents the new status of the
        application
        :type status: int
        :return: an instance of the `CurrentApplication` class. The `CurrentApplication` object contains
        the updated application information and any error that occurred during the update process.
        """
        read = self._db_handler.get_by_id(APP_ID)
        if read.error:
            return CurrentApplication({}, read.error)
        try:
            application = read.item_list[0]
        except IndexError:
            return CurrentApplication({}, APP_NOT_FOUND)
        application.update({'status': status})
        write = self._db_handler.update_by_id(APP_ID, data={'status': status})
        return CurrentApplication(application, write.error)
    
    def update_app_process_status(self, APP_ID: int, process_status: int) -> CurrentApplication:
        """
        The function updates the process status of an application in a database.
        
        :param APP_ID: The APP_ID parameter is an integer that represents the ID of the application that
        needs to be updated
        :type APP_ID: int
        :param process_status: The `process_status` parameter is an integer that represents the status
        of the application process
        :type process_status: int
        :return: an instance of the `CurrentApplication` class.
        """
        read = self._db_handler.get_by_id(APP_ID)
        if read.error:
            return CurrentApplication({}, read.error)
        try:
            application = read.item_list[0]
        except IndexError:
            return CurrentApplication({}, APP_NOT_FOUND)
        application.update({'process_status': process_status})
        write = self._db_handler.update_by_id(APP_ID, data={'process_status': process_status})
        return CurrentApplication(application, write.error)
    
    def update_app_by_query(self, query_str: str, data: dict) -> list:
        """
        The function updates applications based on a query string and returns a list of updated items.
        
        :param query_str: The query string used to filter the applications that need to be updated. It
        is a string representation of a lambda function that takes an application object as input and
        returns a boolean value indicating whether the application should be updated or not
        :type query_str: str
        :param data: A dictionary containing the updated data for the applications that match the query
        :type data: dict
        :return: a list of items that were updated in the database.
        """
        # query_str = lambda x: x['id'] == app_id and x['process_status'] == status
        write = self._db_handler.update_by_query(query_str=query_str, data=data)    
        return write.item_list
    
    def delete_app_by_query(self, query_str: str) -> list:
        """
        The function `delete_app_by_query` deletes applications based on a query string and returns the
        list of deleted items.
        
        :param query_str: The query string used to filter the applications to be deleted. It is a string
        that represents a condition or criteria that the applications must meet in order to be deleted
        :type query_str: str
        :return: a list of items that were deleted.
        """
        # query_str = lambda x: x['id'] == app_id and x['process_status'] == status
        write = self._db_handler.delete_by_query(query_str=query_str)    
        return write.item_list

    def remove(self, APP_ID: int) -> CurrentApplication:
        """
        The `remove` function removes an application from the database using its id or index.
        
        :param APP_ID: The `APP_ID` parameter is the ID or index of the application that you want to remove
        from the database
        :type APP_ID: int
        :return: an instance of the `CurrentApplication` class, with an empty dictionary as the data and the
        `error` attribute from the `write` object as the error.
        """
        write = self._db_handler.delete_by_id(APP_ID)
        
        return CurrentApplication({}, write.error)

    def remove_all(self) -> CurrentApplication:
        """
        The `remove_all` function removes all applications from the database and returns the result.
        :return: an instance of the `CurrentApplication` class.
        """
        write = self._db_handler.purge()
        return CurrentApplication({}, write.error)

def get_application_id_by_short_name(app_short_name) -> str:
    """
    The function `get_application_id_by_name` retrieves the application ID based on the given
    application short name.
    
    :param app_short_name: The `app_short_name` parameter is a string that represents the short name of
    an application
    :return: the application ID associated with the given application short name.
    """
    applications = Applications(get_database_path(config.CONFIG_FILE_PATH, 'app'))
    app_response = applications.get_app_by_short_name(app_short_name)
    application = app_response.application
    error = app_response.error

    if error:
        return str(error)
    else:
        if len(application.keys()):
            return list(application.keys())[0]
        else:
            return ''
    
def get_endpoint_id_by_name(endpoint_name):
    """
    The function `get_endpoint_id_by_name` retrieves the ID of an endpoint by its name from a database.
    
    :param endpoint_name: The parameter `endpoint_name` is a string that represents the name of an
    endpoint
    :return: the ID of an endpoint based on its name.
    """
    endpoints = Endpoints(get_database_path(config.CONFIG_FILE_PATH, 'endpoint'))
    endpoint_result = endpoints.get_endpoint_by_name(endpoint_name)
    endpoint = endpoint_result.endpoint
    error = endpoint_result.error
    
    if error:
        return error
        
    else:
        if len(endpoint.keys()):
            return list(endpoint.keys())[0]
        else:
            return {}