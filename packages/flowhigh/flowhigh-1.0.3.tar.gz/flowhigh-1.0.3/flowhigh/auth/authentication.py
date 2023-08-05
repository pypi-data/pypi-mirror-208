import datetime
import json
import os
from os.path import expanduser

import requests
import time


class Authentication:
    _base_url = "https://auth.sonra.io/oauth/"
    _CLIENT_ID = "TA2gGqeNX59sJiIgvuTxsSu1o09OjEUM"
    _AUDIENCE = "https://flowhigh.sonra.io/api/"
    _SCOPE = "offline_access+openid"

    # The secret location where the JSON containing the access token is stored.
    TOKEN_PATH = os.path.join(
        expanduser("~"),
        '.parseql',
        'parseql.json',
    )

    @classmethod
    def authenticate_user(cls) -> str:
        """
        Authenticates the user by checking if the access token exists in the secret folder.
        If it doesn't then try to authenticate the user by requesting device code from OAuth

        :return: Access token IF the user is authenticated ELSE `NONE`
        """
        token_json = cls.get_parseql_token_from_storage()
        if not token_json:
            return cls.request_device_code()
        else:
            return cls.evaluate_token(token_json)

    @classmethod
    def evaluate_token(cls, token_json: dict) -> str:
        """
        Check if the access token has expired. If it has expired then try to refresh it if possible.
        If the refresh token is not available then try to authenticate the user by requesting device code.

        :param token_json: The json file containing access token
                           and refresh token which is loaded from the secret folder
        :return: The Access token IF the user is authenticated ELSE `None`
        """
        if "access_token" in token_json:
            # Refresh token if access token has expired
            if (datetime.datetime.strptime(token_json['issued_at'], '%Y-%m-%d %H:%M:%S.%f')
                    + datetime.timedelta(seconds=token_json['expires_in']) <= datetime.datetime.utcnow()):
                if "refresh_token" in token_json:
                    return cls.refresh_access_token(token_json['refresh_token'])
                else:
                    return cls.request_device_code()
            else:
                return token_json['access_token']

        return None

    @classmethod
    def refresh_access_token(cls, refresh_token: str):
        """
        Requests a new access token using the refresh token.

        :param refresh_token: The refresh token obtained from the json in the secret location
        :return: Access token IF the user is authenticated ELSE `None`
        """
        url = cls._base_url + "token"
        payload = "grant_type=refresh_token" \
                  + "&client_id=" + cls._CLIENT_ID \
                  + "&refresh_token=" + refresh_token
        headers = {'content-type': "application/x-www-form-urlencoded"}

        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            json_data = json.loads(response.content)
            if "access_token" in json_data:
                cls.save_token(json_data)
                return json_data['access_token']
        # If refresh token has expired/invalid_grant
        elif response.status_code == 403:
            json_data = json.loads(response.content)
            if "Unknown or invalid refresh token" in json_data['error_description']:
                return cls.request_device_code()
        return None

    @classmethod
    def request_device_code(cls) -> str:
        """
        Send a POST Request to OAuth to receive the user code for the current user and then try to receive an access token.
        :return: Access token IF user is authenticated ELSE `None`
        """
        url = cls._base_url + "device/code"
        payload = "client_id=" + cls._CLIENT_ID + "&scope=" + cls._SCOPE + "&audience=" + cls._AUDIENCE
        headers = {'content-type': "application/x-www-form-urlencoded"}
        response = requests.post(url, data=payload, headers=headers)
        json_data = json.loads(response.content)

        if "user_code" in json_data:
            user_code = json_data['user_code']
            verification_uri = json_data['verification_uri']
            complete_uri = json_data['verification_uri_complete']
            device_code = json_data['device_code']
            polling_interval = json_data["interval"]

            print("Visit {0} and enter {1} \nOR \nUse {2} to authenticate automatically".
                  format(verification_uri, user_code, complete_uri))

            return cls.request_token(device_code, polling_interval)
        else:
            print(response.content)
            return None

    @classmethod
    def request_token(cls, device_code: str, polling_interval: int) -> str:
        """
        Send POST request to OAuth to receive an access token by polling
        until none of the handled responses are received or until a valid access token is received.

        :param device_code: The device code of the current user. Obtained from POST Request to OAuth
        :param polling_interval: The frequency at which POST request is to be sent to OAuth to receive token
        :return: Access token IF user is authenticated ELSE `None`
        """
        url = cls._base_url + "token"
        payload = "grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code=" \
                  + device_code + "&client_id=" + cls._CLIENT_ID
        headers = {'content-type': "application/x-www-form-urlencoded"}

        while True:
            # Keep polling until we receive a response which is handled above
            time.sleep(polling_interval)
            response = requests.post(url, data=payload, headers=headers)
            json_data = json.loads(response.content)

            if 'error' in json_data:
                if json_data["error"] == "authorization_pending":
                    continue
                elif json_data["error"] == "slow_down":
                    polling_interval += 1
                    continue
                elif json_data["error"] == "expired_token":
                    print("Token expired, restart the authentication")
                    break
                elif json_data["error"] == "access_denied":
                    print("ACCESS DENIED")
                    print(json_data["error_description"])
                    break
                else:
                    print(json_data)
                    break

            elif response.status_code == 200:
                if "access_token" in json_data:
                    # add UTC time to check expiration
                    cls.save_token(json_data)
                    return json_data['access_token']
            else:
                print(json_data)
                break

        # If we don't get a valid response or if we encounter any errors
        return None

    @classmethod
    def save_token(cls, token: dict):
        """
        Save the JSON containing access token to the secret folder.
        :param token:  JSON containing the Access token that needs to be saved
        :return: Save the response json with access token to a file
        """
        token['issued_at'] = datetime.datetime.utcnow()
        try:
            os.makedirs(os.path.dirname(cls.TOKEN_PATH), exist_ok=True)
            with open(cls.TOKEN_PATH, "w") as token_file:
                token_file.write(json.dumps(token, indent=4, sort_keys=True, default=str))
        except:
            raise Exception("Unable to save token. Please make sure you have permission to write in the token folder")

    @classmethod
    def get_parseql_token_from_storage(cls) -> dict:
        """
        Search for the JSON file containing access token.
        :return: JSON containing the access token IF it exists ELSE `None`
        """
        token = None
        if os.path.isfile(cls.TOKEN_PATH):
            try:
                with open(cls.TOKEN_PATH, 'r') as infile:
                    token = infile.read()
                token = json.loads(token)
            except:
                os.remove(cls.TOKEN_PATH)
                raise Exception("Unable to Read the token file in storage. Deleting the file, try again. If it doesn't "
                                "work the second time, check for permissions")

        return token