
# The above code generates random data for applications and endpoints and adds them to the respective
# databases.
# :return: The function `generate_random_data` returns a boolean value `True` indicating that the
# random data generation process was successful.

import os
import random
from faker import Faker
import json
from autonomous_data_collection_agent import ERRORS, __app_name__, __version__, autonomousagent, config, database

# # Get the current script's directory
# current_script_dir = os.path.dirname(os.path.abspath(__file__))

# # Append the parent directory (sample code) to the Python path
# sample_code_dir = os.path.join(current_script_dir, 'sample code')
# sys.path.append(sample_code_dir)

def generate_random_datetime():
    # Initialize the Faker library for generating fake data
    fake = Faker()
    # Function to generate a random date and time
    return fake.date_time_between(start_date="-30d", end_date="now")

# Function to generate a random payload as a dictionary
def generate_random_payload():
    # Initialize the Faker library for generating fake data
    fake = Faker()
    # Function to generate a random date and time
    return {"table_name": fake.word()}

# Function to generate random filters as a list of dictionaries
def generate_random_filters():
    # Initialize the Faker library for generating fake data
    fake = Faker()
    # Function to generate a random date and time
    return [
        {"column_name": random.choice(["CREATED_AT", "UPDATED_AT", "DELETED_AT"]),
         "operator": random.choice([">", "<", "=", ">=", "<=", "!=", "<>"]),
         "column_value": fake.date_time_this_decade().strftime("%d-%m-%Y %H:%M:%S")},
        {"column_name": random.choice(["CREATED_AT", "UPDATED_AT", "DELETED_AT"]),
         "operator": random.choice([">", "<", "=", ">=", "<=", "!=", "<>"]),
         "column_value": fake.date_time_this_decade().strftime("%d-%m-%Y %H:%M:%S")}
    ]

# Function to generate a random application data
def generate_random_application():
    # Initialize the Faker library for generating fake data
    fake = Faker()
    base_dump_dir = r'D:\scrapped_data'
    # Function to generate a random date and time
    short_name = fake.unique.word()
    return {
        "name": fake.company(),
        "short_name": short_name,
        # "host": urllib.parse.urlparse(fake.uri()).netloc,
        "host": 'localhost:1006',
        "url_scheme": random.choice(["http", "https"]),
        #"auth_type": random.choice([None, "KEYCLOAK", "BASIC"]),
        "auth_type":"BASIC",
        "auth_data": json.dumps({"key": fake.word(), "secret": fake.word()}),
        "dump_path": os.path.join(base_dump_dir, short_name),
        "sync_frequency": f"{random.randint(0, 59)} {random.randint(0, 23)} * * *",  # Random cron job frequency
        "last_sync": generate_random_datetime().strftime("%d-%m-%Y %H:%M:%S"),
        "next_sync": generate_random_datetime().strftime("%d-%m-%Y %H:%M:%S"),
        "default_payload": json.dumps(generate_random_payload()),
        "default_filters": json.dumps(generate_random_filters()),
        "default_page_size": random.randint(1, 100),
        "process_status": random.choice([0, 1, 2]),
        "status": random.choice([0, 1])
    }

# Function to generate random endpoint data
def generate_random_endpoint(app_short_name):
    # Initialize the Faker library for generating fake data
    fake = Faker()
    # Function to generate a random date and time
    return {
        "name": fake.word(),
        "app_short_name": app_short_name,
        "url_endpoint": fake.uri_path(),
        "method": random.choice(["GET", "POST"]),
        "payload": json.dumps(generate_random_payload()),
        "filters": json.dumps(generate_random_filters()),
        "page_size": random.randint(1, 100),
        "last_sync": generate_random_datetime().strftime("%d-%m-%Y %H:%M:%S"),
        "process_status": random.choice([0, 1, 2]),
        "status": random.choice([0, 1])
    }

def generate_random_data(app_count: int = 10, endpoints_in_app: int = 10): 
    # Usage example to generate random data for an application and endpoint
    endpoint_db_path = database.get_database_path(config.CONFIG_FILE_PATH, 'endpoint')
    endpoints = autonomousagent.Endpoints(endpoint_db_path)
    app_db_path = database.get_database_path(config.CONFIG_FILE_PATH, 'app')
    apps = autonomousagent.Applications(app_db_path)

    # Generate 10 applications and 100 endpoints (10 per application)
    for _ in range(app_count):
        random_app_data = generate_random_application()
        
        #print("Random Application Data:")
        # print(random_app_data)
        # Add the random_app_data to your database
        apps.add(**random_app_data)
        for _ in range(endpoints_in_app):
            random_endpoint_data = generate_random_endpoint(random_app_data["short_name"])
            endpoints.add(**random_endpoint_data)
            #print("Random Endpoint Data:")
            #print(random_endpoint_data)
    return True