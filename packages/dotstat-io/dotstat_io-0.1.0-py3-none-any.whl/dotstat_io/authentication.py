import requests
import msal
import requests_kerberos
import json

from enum import IntEnum


class AuthenticationMode(IntEnum):
    INTERACTIVE = 1
    NONINTERACTIVE_WITH_SECRET = 2
    NONINTERACTIVE_WITH_ADFS = 3

# class to manage ADFS authentication using OIDC flows
class AdfsAuthentication():

    # Declare constants
    __ERROR = "An error occurred: "
    __SUCCESS = "Successful authentication"

    # Initialise Adfs_authentication
    def __init__(
        self,
        mode: AuthenticationMode,
        client_id: str,
        sdmx_resource_id: str,
        scopes: list[str] = [],
        authority_url: str = None,
        token_url: str = None,
        redirect_port: int = 3000,
        client_secret: str = None
    ):
        self.__token = None
        self.result = None
        self.mode = mode
        self.client_id = client_id
        self.sdmx_resource_id = sdmx_resource_id
        self.scopes = scopes
        self.authority_url = authority_url
        self.token_url = token_url
        self.redirect_port = redirect_port
        self.client_secret = client_secret

        match self.mode:
            case AuthenticationMode.INTERACTIVE:
                self.app = msal.PublicClientApplication(
                    self.client_id, authority=self.authority_url)
            case AuthenticationMode.NONINTERACTIVE_WITH_SECRET:
                self.app = msal.ConfidentialClientApplication(
                    self.client_id, authority=self.authority_url, client_credential=self.client_secret)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__token = None

    @classmethod
    def interactive(
        cls, 
        client_id: str, 
        sdmx_resource_id: str, 
        scopes: list[str], 
        authority_url: str, 
        redirect_port: int = 3000,
        mode: AuthenticationMode = AuthenticationMode.INTERACTIVE
    ):
        return cls(
            client_id=client_id, 
            sdmx_resource_id=sdmx_resource_id, 
            scopes=scopes, 
            authority_url=authority_url,
            redirect_port=redirect_port,
            mode=mode
        )

    @classmethod
    def nointeractive_with_secret(
        cls, 
        client_id: str, 
        sdmx_resource_id: str,
        scopes: list[str],
        authority_url: str,
        client_secret: str,
        mode: AuthenticationMode = AuthenticationMode.NONINTERACTIVE_WITH_SECRET
    ):
        return cls(
            client_id=client_id,
            sdmx_resource_id=sdmx_resource_id,
            scopes=scopes,
            authority_url=authority_url,   
            client_secret=client_secret,  
            mode=mode
            )

    @classmethod
    def nointeractive_with_adfs(
        cls, 
        client_id: str, 
        sdmx_resource_id: str,
        token_url: str,
        mode: AuthenticationMode = AuthenticationMode.NONINTERACTIVE_WITH_ADFS
    ):
        return cls(
            client_id=client_id, 
            sdmx_resource_id=sdmx_resource_id,
            token_url=token_url,
            mode=mode)


    def get_token(self):
        self.__token = None
        self.result = None
        match self.mode:
            case AuthenticationMode.INTERACTIVE:
                self._acquire_token_interactive()
            case AuthenticationMode.NONINTERACTIVE_WITH_SECRET:
                self._acquire_token_noninteractive_with_secret()
            case AuthenticationMode.NONINTERACTIVE_WITH_ADFS:
                self._acquire_token_noninteractive_with_adfs()

        return self.__token


    # Authentication interactively - aka Authorization Code flow
    def _acquire_token_interactive(self):
        try:

            # We now check the cache to see
            # whether we already have some accounts that the end user already used to sign in before.
            accounts = self.app.get_accounts()
            if accounts:
                account = accounts[0]
            else:
                account = None

            # Firstly, looks up a token from cache, or using a refresh token
            response_silent = self.app.acquire_token_silent(
                self.scopes, account=account)
            if not response_silent:
                # Prompt the user to sign in interactively
                response_interactive = self.app.acquire_token_interactive(
                    scopes=self.scopes, port=self.redirect_port)
                if "access_token" in response_interactive:
                    self.__token = response_interactive.get("access_token")
                    self.result = self.__SUCCESS
                else:
                    self.result = f'{self.__ERROR}{response_interactive.get("error")} Error description: {response_interactive.get("error_description")}'
            else:
                if "access_token" in response_silent:
                    self.__token = response_silent.get("access_token")
                    self.result = self.__SUCCESS
                else:
                    self.result = f'{self.__ERROR}{response_silent.get("error")} Error description: {response_silent.get("error_description")}'
        except Exception as err:
            self.result = f'{self.__ERROR}{err}\n'


    # Authentication non-interactively using any account - aka Client Credentials flow
    def _acquire_token_noninteractive_with_secret(self):
        try:
            response = self.app.acquire_token_for_client(scopes=self.scopes)
            if "access_token" in response:
                self.__token = response.get("access_token")
                self.result = self.__SUCCESS
            else:
                self.result = f'{self.__ERROR}{response.get("error")} Error description: {response.get("error_description")}'

        except Exception as err:
            self.result = f'{self.__ERROR}{err}\n'


    # Authentication non-interactively using service account - aka Windows Client Authentication
    def _acquire_token_noninteractive_with_adfs(self):
        try:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            payload = {
                'client_id': self.client_id,
                'use_windows_client_authentication': 'true',
                'grant_type': 'client_credentials',
                'scope': 'openid',
                'resource': self.sdmx_resource_id
            }

            kerberos_auth = requests_kerberos.HTTPKerberosAuth(
                mutual_authentication=requests_kerberos.OPTIONAL, force_preemptive=True)
            response = requests.post(
                url=self.token_url, data=payload, auth=kerberos_auth)

            if response.status_code != 200:
                message = f'{self.__ERROR} Error code: {response.status_code} Reason: {response.reason}\n'
                if len(response.text) > 0:
                    # Use the json module to load response into a dictionary.
                    response_dict = json.loads(response.text)
                    message += f'{self.__ERROR}{response_dict.get("error")} Error description: {response_dict.get("error_description")}\n'
                    
                self.result = message
            else:
                self.__token = response.json()['access_token']
                self.result = self.__SUCCESS

        except Exception as err:
            self.result = f'{self.__ERROR} {err}\n'
