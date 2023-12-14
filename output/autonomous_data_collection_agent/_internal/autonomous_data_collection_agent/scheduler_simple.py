# The `SchedulerService` class is responsible for scheduling and processing data collection tasks for
# different applications and endpoints.

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
from crontab import CronTab
import json
import os
import requests
import logging
from autonomous_data_collection_agent import ERRORS, __app_name__, __version__, autonomousagent, config, database, cli, fileencryption, keycloak_auth
import typer
from datetime import datetime
import croniter
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import concurrent.futures
import base64
import urllib

# Initialize the logging library
logging.basicConfig(filename=config.getLogFilePath(), filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%d-%b-%y %H:%M:%S", level=logging.DEBUG)

# The `SchedulerService` class is responsible for scheduling and processing data collection tasks for
class SchedulerService():
    # It sets the
    # service name and display name for the agent. It also creates instances of the FileEncryption and
    # KeycloakAuth classes.
    _svc_name_ = "AutonomousDataCollectionAgent"
    _svc_display_name_ = "AICoE: Autonomous Data Collection Agent"
    _file_encryption = fileencryption.FileEncryption()
    _keycloak_client = keycloak_auth.KeycloakAuth()

    def __init__(self):
        """
        The function sets the default timeout for network requests and initializes a cron schedule.
        """
        socket.setdefaulttimeout(60)  # Set the timeout for network requests
        # self.cron = CronTab('*/30 * * * *')  # Schedule as per the provided cron format

    def SvcStop(self):
        """
        The function `SvcStop` reports the service status as "stop pending" and sets an event to
        indicate that the service should stop.
        """
        #self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        #win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """
        The function `SvcDoRun` logs a message indicating that a Python service has started and then
        calls the `main` function.
        """
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.main()

    def main(self):
        """
        The main function checks if threading is enabled and processes applications accordingly, with an
        option to stop processing based on a stop signal.
        """
        threading_config = config.get_threading_config()
        if threading_config["enabled"] == "True":
            while True:
                self.process_applications(True, int(threading_config["concurrent_threads"]))
                # if win32event.WaitForSingleObject(self.hWaitStop, 60000) == win32event.WAIT_OBJECT_0:
                break
        else:
            while True:
                # if self.cron.next(default_utc=True) <= 0:
                #     self.process_applications()
                self.process_applications()
                print("I have run once so will stop now.")
                exit(0)
                # Check for the stop signal every 60 seconds
                # if win32event.WaitForSingleObject(self.hWaitStop, 60000) == win32event.WAIT_OBJECT_0:
                #     break

    def update_app_processing_status(self):
        """
        The function updates the processing status of active applications and their associated
        endpoints, and logs the completion of the processing.
        """
        all_active_apps = self._get_applications().get_app_by_status(1)
        for app_id in all_active_apps:
            app_data = all_active_apps[app_id]
            if self.endpoint_processing_completed(app_id):
                current_time = datetime.now()
                current_time_str = current_time.strftime("%d-%m-%Y %H:%M:%S")
                cron = croniter.croniter(app_data["sync_frequency"], current_time)
                self._get_endpoints().update_endpoints_by_query(lambda x: x['app_id'] == app_id and  x['status'] == 1 and x['process_status'] == 2, {'process_status': 0, 'failed_count':0})
                self._get_applications().update_app(app_id, {'process_status':0, 'last_sync': current_time_str , 'next_sync': cron.get_next(datetime).strftime("%d-%m-%Y %H:%M:%S")})
                logging.info(f"App processing completed: {app_id} at: {current_time_str}")

    def endpoint_processing_completed(self, app_id):
        """
        The function checks if all active endpoints for a given app ID have completed processing.
        
        :param app_id: The `app_id` parameter represents the ID of an application
        :return: a boolean value indicating whether all active endpoints for a given app ID have
        completed processing.
        """
        disable_failed_endpoints = self._get_endpoints().update_endpoints_by_query(lambda x: x['status'] == 1 and x['process_status'] == 1 and x['failed_count'] == 3, {"status": 0, 'process_status': 0, 'failed_count':0})

        if len(disable_failed_endpoints):
            disabled_failed_endpoints = ', '.join(disable_failed_endpoints)
            logging.warning(f"Disabled the endpoints for App ID: {app_id} which failed 3 times. Endpiont IDs: {disabled_failed_endpoints}")

        all_active_app_endpoint_count = len(self._get_endpoints().get_endpoints_by_query(lambda x: x['app_id'] == app_id and x['status'] == 1))
        completed_app_endpoints = len(self._get_endpoints().get_endpoints_by_query(lambda x: x['app_id'] == app_id and x['status'] == 1 and x['process_status'] == 2))

        return all_active_app_endpoint_count == completed_app_endpoints
    
    def process_applications(self, threading_enabled=False, thread_count=2):
        """
        The `process_applications` function processes applications and their associated endpoints,
        either sequentially or using multithreading if enabled.
        
        :param threading_enabled: The `threading_enabled` parameter is a boolean flag that determines
        whether the processing of endpoints should be done using multiple threads or not. If set to
        `True`, the processing will be done using multiple threads. If set to `False`, the processing
        will be done sequentially without using threads, defaults to False (optional)
        :param thread_count: The `thread_count` parameter specifies the number of threads to be used for
        processing the endpoints. It determines the maximum number of concurrent threads that can be
        executed at a time, defaults to 2 (optional)
        """
        # Get applications which are already under progress
        self.update_app_processing_status()
        applications = self._get_applications().get_app_by_query(lambda x: x['status'] == 1 and x['process_status'] < 2 )
        for app_id in applications:
            app_data = applications[app_id]
            app_name = app_data["name"]
            try:
                if(isinstance(app_data["next_sync"], str)):
                    if app_data["next_sync"] is None or app_data["next_sync"] == "" or str(app_data["next_sync"]).strip() == "":
                            app_data["next_sync"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                next_sync_datetime = datetime.strptime(app_data["next_sync"], "%d-%m-%Y %H:%M:%S")
                # Get the current date and time
                current_datetime = datetime.now()
                # Check if next_sync is due to run now
                if current_datetime >= next_sync_datetime:
                    logging.info(f"next_sync is due to run now for app ID # {app_id} with name {app_name}")
                    self._get_applications().update_app_process_status(app_id, 1)
                    endpoints = self._get_endpoints().get_endpoints_by_query(lambda x: x['app_id'] == app_id and x['status'] == 1 and x['process_status'] < 2)
                    for endpoint_id in endpoints:
                        endpoint_data = endpoints[endpoint_id]
                        endpoint_name = endpoint_data['name']
                        try:
                            self._get_endpoints().update_endpoint_process_status(endpoint_id, 1)
                            if threading_enabled:
                                thread_count = int(thread_count)
                                with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:  # Adjust max_workers as needed
                                    futures = []
                                    # Wait for all futures to complete
                                    concurrent.futures.wait(futures)
                                    future = executor.submit(self.process_endpoint, app_data, endpoint_data, next_sync_datetime)
                                    futures.append(future)
                            else:
                                self.process_endpoint(app_data, endpoint_data, next_sync_datetime)
                                
                            last_sync_datetime =  datetime.strptime(endpoint_data['last_sync'], "%d-%m-%Y %H:%M:%S")    
                            self._get_endpoints().update_endpoint(endpoint_id, {"failed_time": "", "failed_count": 0, "last_sync": last_sync_datetime.strftime("%d-%m-%Y %H:%M:%S"), 'process_status': 2})
                        except Exception as e:
                            self._get_endpoints().update_endpoint(endpoint_id, {"failed_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "failed_count": endpoint_data["failed_count"] + 1})
                            logging.error(f"Error processing endpoint ID: {endpoint_id} with name {endpoint_name}. Error Details : {str(e)}")
            except Exception as err:
                logging.error(f"Error processing app ID: {app_id} with name {app_name}. Error Details: {str(err)}")

    def process_endpoint(self, app_data, endpoint_data, next_sync_datetime):
        """
        The function processes an endpoint by making a request, saving the response, and updating the
        next sync datetime.
        
        :param app_data: The app_data parameter is the data related to the application that is making
        the request. It could include information such as the app's API key, authentication credentials,
        or any other relevant data needed to make the request
        :param endpoint_data: The `endpoint_data` parameter is a dictionary that contains information
        about the specific endpoint being processed. It may include details such as the endpoint URL,
        request method (e.g., GET, POST), headers, and payload data
        :param next_sync_datetime: The `next_sync_datetime` parameter is the datetime value indicating
        the next scheduled synchronization time for the endpoint. It is used to determine when the
        endpoint should be synchronized again
        """
        response = self.make_request(app_data, endpoint_data)
        
        if response:
            self.save_response(app_data, endpoint_data, response, next_sync_datetime)  

    def process_filters(self, data, last_sync):
        """
        The function `process_filters` processes a list of filters by replacing any empty or None values
        with the current datetime, specifically for columns named "CREATED_AT", "UPDATED_AT", and
        "DELETED_AT".
        
        :param data: A list of dictionaries, where each dictionary represents a filter. Each dictionary
        has two keys: "column_name" and "column_value". "column_name" represents the name of the column
        to filter on, and "column_value" represents the value to filter by
        :param last_sync: The last_sync parameter is a variable that represents the last synchronization
        time. It is used to determine if a column value is empty or null. If last_sync is None or an
        empty string, it is replaced with the current datetime
        :return: the modified "data" list after processing the filters.
        """
        if(isinstance(last_sync, str)):
            if last_sync is None or last_sync == "" or str(last_sync).strip() == "":
                    last_sync = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        for item in data:
            column_name = item.get("column_name")
            column_value = item.get("column_value")

            if column_name in ["CREATED_AT", "UPDATED_AT", "DELETED_AT"]:
                if column_value is None or column_value == "" or str(column_value).strip() == "":
                    # Replace the value with the current datetime
                    item["column_value"] = last_sync
        
        return data
    
    def make_request(self, app_data, endpoint_data):
        """
        The `make_request` function sends a request to an API endpoint, retrieves data in paginated
        form, and returns all the data.
        
        :param app_data: The `app_data` parameter is a dictionary that contains information about the
        application. It includes the following keys:
        :param endpoint_data: The `endpoint_data` parameter is a dictionary that contains information
        about the specific endpoint you want to make a request to. It includes the following keys:
        :return: a list of all the data retrieved from the API endpoint.
        """

        app_name = app_data["name"]    
        endpoint_name = endpoint_data["name"]
        
        if isinstance(endpoint_data["payload"], str):
            endpoint_data["payload"] = json.loads(endpoint_data["payload"])

        if len(endpoint_data["payload"]) < 1:
            if isinstance(app_data["default_payload"], str):
                app_data["default_payload"] = json.loads(app_data["default_payload"])
            endpoint_data["payload"] = app_data["default_payload"]

        if isinstance(endpoint_data["filters"], str):
            endpoint_data["filters"] = json.loads(endpoint_data["filters"])
        
        if len(endpoint_data["filters"]) < 1:
            if isinstance(app_data["default_filters"], str):
                app_data["default_filters"] = json.loads(app_data["default_filters"])
            endpoint_data["filters"] = app_data["default_filters"]
        
        endpoint_data["filters"] = self.process_filters(endpoint_data["filters"], endpoint_data["last_sync"])
        
        if isinstance(endpoint_data["page_size"], str):
            endpoint_data["page_size"] = int(endpoint_data["page_size"])
       
        if endpoint_data["page_size"] < 1:
            if isinstance(app_data["default_page_size"], str):
                app_data["default_page_size"] = int(app_data["default_page_size"])
            endpoint_data["page_size"] = app_data["default_page_size"]
        
        if isinstance(app_data["auth_data"], str):
            app_data["auth_data"] = json.loads(endpoint_data["auth_data"])

        request_data = {
            "filters": json.dumps(endpoint_data["filters"]),
            "page_size": endpoint_data["page_size"],
        }

        for key, value in endpoint_data["payload"].items():
            request_data[key] = value

        headers = {}
        # Add additional payload and headers based on auth_type and auth_data
        
        if app_data.get("auth_type") == "BASIC":
            credentials = f"{app_data.get('auth_data', {}).get('key', '')}:{app_data.get('auth_data', {}).get('key', 'secret')}"
            # Encode the credentials in base64
            credentials_encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
            # Create the header
            auth_header = f"Basic {credentials_encoded}"
            headers["Authorization"] = auth_header
        elif app_data.get("auth_type") == "KEYCLOAK":
            self._keycloak_client.set_auth_data(app_data.get("auth_data"))
            
            token = self._keycloak_client.get_token()
            headers = {
                'Authorization': f'Bearer {token}',
            }

        else:
            headers = {}

        # url = f"{app_data.get('url_scheme', 'https')}://{app_data.get('host', 'localhost')}/{endpoint_data.get('url_endpoint', 'data-export-generic-api')}"
        url = f"http://{app_data.get('host', 'localhost')}/{endpoint_data.get('url_endpoint', 'data-export-generic-api')}"
        method = endpoint_data.get("method", "POST")
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        page_number = 1
        all_data = []
        
        while True:
            request_data["page_number"] = page_number

            if method == "POST":
                try:
                    response = requests.post(url, headers=headers, json=request_data )
                except Exception as e:
                    logging.error(f"POST request to {url} failed. Endpoint name: {endpoint_name} App Name :{app_name}. Error: {e}")
            else:
                # Append the query parameters to the URL
                try:
                    #url += "?" + "&".join([f"{key}={value}" for key, value in request_data.items()])
                    url = url + "?" + urllib.parse.urlencode(request_data)
                    response = requests.get(url, headers=headers)
                except Exception as e:
                    logging.error(f"GET request to {url} failed. Endpoint name: {endpoint_name} App Name :{app_name}. Error: {e}")
                
            if response.status_code == 200:
                response_json = response.json()
                total_records = response_json.get("total", 0)
                current_page_data = response_json.get("data", [])
                all_data.extend(current_page_data)
                response_time = response_json.get("response_time", "")
                if response_json:
                    # @todo check if response_time is in valid format DD-MM-YYYY hh:mm:ss
                    endpoint_data["last_sync"] = response_time

                if len(all_data) < total_records:
                    page_number += 1
                else:
                    break
            else:
                logging.error(f"Request to {url} failed with status code {response.status_code}. Endpoint name: {endpoint_name} App Name :{app_name}")
                raise Exception(f"Request to {url} failed with status code {response.status_code}")
        
        return all_data

    def save_response(self, app_data, endpoint_data, response, next_sync_datetime):
        """
        The function saves a response to a JSON file and encrypts it if file encryption is enabled.
        
        :param app_data: app_data is a dictionary that contains information about the application. It
        may include the dump_path, which is the path where the response data will be saved
        :param endpoint_data: The `endpoint_data` parameter is a dictionary that contains information
        about the endpoint. It typically includes details such as the name of the endpoint, its URL,
        request headers, and any other relevant information needed to make the API request
        :param response: The `response` parameter is the data that you want to save. It can be any
        JSON-serializable object
        :param next_sync_datetime: The `next_sync_datetime` parameter is a datetime object that
        represents the next scheduled synchronization time. It is used to generate a timestamp for the
        folder name where the response will be saved
        """
        dump_path = app_data.get("dump_path", "")
        timestamp = next_sync_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        folder_path = os.path.join(dump_path, timestamp)
        os.makedirs(folder_path, exist_ok=True)
        endpoint_name = endpoint_data['name']
        file_path = os.path.join(folder_path, f"{endpoint_name}.json")
        with open(file_path, "w") as file:
            json.dump(response, file, indent=4)
        
        if self._file_encryption.check_if_enabled():
            self._file_encryption.encypt_original_file(file_path)        

    def _get_endpoints(self) -> autonomousagent.Endpoints:
        """
        The function `_get_endpoints` checks if the config file and database file exist, and returns an
        instance of `autonomousagent.Endpoints` if they do.
        :return: an instance of the `autonomousagent.Endpoints` class.
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

    def _get_applications(self) -> autonomousagent.Applications:
        """
        The function `_get_applications` checks if the config file and database file exist, and returns
        an instance of the `Applications` class if they do.
        :return: The method `_get_applications` returns an instance of `autonomousagent.Applications`.
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