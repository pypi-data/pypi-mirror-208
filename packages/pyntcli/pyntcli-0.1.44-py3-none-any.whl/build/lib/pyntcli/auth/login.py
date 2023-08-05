from base64 import b64decode
import requests
import webbrowser
import uuid
import urllib.parse
import datetime
import time
import json
import os

from pyntcli.ui import ui_thread
from pyntcli.store import CredStore

class LoginException(Exception):
    pass

class Timeout(LoginException):
    pass

class InvalidTokenInEnvVarsException(LoginException):
    pass

PYNT_CREDENTIALS = "PYNT_CREDENTIALS"

class Login():
    def __init__(self) -> None:
        self.delay = 5
        self.base_authorization_url = "https://pynt.io/login?"
        self.poll_url = "https://n592meacjj.execute-api.us-east-1.amazonaws.com/default/cli_validate_login"
        self.login_wait_period = (60 *3) #3 minutes

    def create_login_request(self): 
        request_id = uuid.uuid4()
        request_url = self.base_authorization_url + urllib.parse.urlencode({"request_id": request_id, "utm_source": "cli"})
        webbrowser.open(request_url)

        ui_thread.print(ui_thread.PrinterText("To continue, you need to log in to your account.")\
                                 .with_line("You will now be redirected to the login page.") \
                                 .with_line("") \
                                 .with_line("If you are not automatically redirected, please click on the link provided below (or copy to your web browser)") \
                                 .with_line(request_url))
        return request_id

    def get_token_using_request_id(self, request_id):
        with ui_thread.spinner("Waiting...", "point"):
            start = time.time()
            while start + self.login_wait_period > time.time():
                response = requests.get(self.poll_url, params={"request_id": request_id})
                if response.status_code == 200:
                    return response.json()
                time.sleep(self.delay)
            raise Timeout()
    
    def login(self):
        id = self.create_login_request()
        token = self.get_token_using_request_id(id)
        with CredStore() as store: 
            store.put("token", token)


def refresh_request(refresh_token):
    return requests.post("https://auth.pynt.io/default/refresh", json={"refresh_token": refresh_token})

def refresh_token():
    token = None
    with CredStore() as store: 
        token = store.get("token")

    if not token: 
        Login().login()
    
    access_token = token.get("access_token")
    if access_token and not is_jwt_expired(access_token):
        return

    refresh = token.get("refresh_token", None)
    if not refresh:
        Login().login()
        return

    refresh_response = refresh_request(refresh) 
    if refresh_response.status_code != 200:
        Login().login()
        return 

    with CredStore() as store:
        token["access_token"] = refresh_response.json()["token"]
        store.put("token", token)

def decode_jwt(jwt_token):
    splited = jwt_token.split(".")
    if len(splited) != 3: 
        return None

    return json.loads(b64decode(splited[1] + '=' * (-len(splited[1]) % 4)))

def user_id():
    with CredStore() as store:
        token = store.get("token")
        if not token:
            return None 

        decoded = decode_jwt(token["access_token"])
        if not decoded:
            return None
        
        return decoded.get("sub", None)

    return None

def is_jwt_expired(jwt_token):
    decoded = decode_jwt(jwt_token)
    if not decoded:
        return True

    exp = decoded.get("exp", None)
    if not exp: 
        return True 
    
    return datetime.datetime.fromtimestamp(exp) < datetime.datetime.now() + datetime.timedelta(minutes=1) 

def validate_creds_structure(data):
    try: 
        creds = json.loads(data.replace("\n", ""))
        token = creds.get("token", None)
        if not token:
            raise InvalidTokenInEnvVarsException()
        if not isinstance(token, dict):
            raise InvalidTokenInEnvVarsException()
        
        refresh_token = token.get("refresh_token", None)
        if not refresh_token:
            raise InvalidTokenInEnvVarsException()
        
        return token
    except json.JSONDecodeError:    
        raise InvalidTokenInEnvVarsException()
  

def should_login(): 
    env_creds = os.environ.get(PYNT_CREDENTIALS, None)
    if env_creds:
        validated_creds = validate_creds_structure(env_creds)
        with CredStore() as store:
            store.put("token", validated_creds)

    with CredStore() as store:
        token = store.get("token")

        if not token or token == store.connector.default_value:
            return True
            
        if not token.get("refresh_token"):
            return True 
        
        return False
