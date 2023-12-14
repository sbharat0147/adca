# The `KeycloakAuth` class is used to authenticate and obtain an access token from a Keycloak server.

import requests
from autonomous_data_collection_agent import ERRORS, __app_name__, __version__, config
import logging

class KeycloakAuth:
    _keycloak_config = config.getKeycloakConfig()
    _keycloak_url = ""
    _client_id = ""
    _client_secret = ""
    _realm_name = ""

    def __init__(self, auth_data = None):
        """
        The function initializes the class instance with authentication data, either from the provided
        argument or from the class configuration.
        
        :param auth_data: The `auth_data` parameter is a dictionary that contains authentication data
        such as the Keycloak URL, client ID, client secret, and realm name. It is an optional parameter,
        meaning it can be None or an empty dictionary. If `auth_data` is provided and not empty, the
        values from
        """
        if auth_data and len(auth_data):
            self._keycloak_url = auth_data["keycloak_url"]
            self._client_id = auth_data["client_id"]
            self._client_secret = auth_data["client_secret"]
            self._realm_name = auth_data["realm_name"]
        else:
            self._keycloak_url = self._keycloak_config["keycloak_url"]
            self._client_id = self._keycloak_config["client_id"]
            self._client_secret = self._keycloak_config["client_secret"]
            self._realm_name = self._keycloak_config["realm_name"]
    
    def set_auth_data(self, auth_data):
        """
        The function sets authentication data for a Keycloak client.
        
        :param auth_data: The `auth_data` parameter is a dictionary that contains the following keys:
        """
        if auth_data and len(auth_data):
            self._keycloak_url = auth_data["keycloak_url"]
            self._client_id = auth_data["client_id"]
            self._client_secret = auth_data["client_secret"]
            self._realm_name = auth_data["realm_name"]
    
    def get_token(self):
        """
        The function `get_token` sends a request to Keycloak to obtain an access token using client
        credentials.
        :return: the access token from the response JSON.
        """
        data = {
            'grant_type': 'client_credentials',
            'client_id': self._client_id ,
            'client_secret': self._client_secret,
        }
        try:
            response = requests.post(f"{self._keycloak_url}/auth/realms/{self._realm_name}/protocol/openid-connect/token", data=data)
            return response.json()["access_token"]
        except Exception as e:
            logging.error(f"Keycloak token requets failed. Error: {e}")
        
        return None