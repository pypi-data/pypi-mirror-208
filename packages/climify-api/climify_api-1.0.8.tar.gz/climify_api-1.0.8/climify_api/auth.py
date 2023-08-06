from time import time
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from climify_api.exceptions import AuthorizationError

class IAuthService:
    def get_token() -> dict:
        pass

    def get_access_token() -> str:
        pass

class AuthService(IAuthService):
    """
    An authentication and authorization service to provide the provide 
    the access token required to call the climify_api.
    """
    def __init__(self, token_url: str, oauth_client_id: str) -> None:
        """Creates an instance of the Climify auth service using the passed 
        auth configuration.

        Args:
            token_url (str): Url to token endpoint of the Open Id or OAuth provider token endpoint
            oauth_client_id (str): Client id of the current application. Is obtained by creating your application
                                    in the OAuth or OpenId providers database. If you do not have access to create
                                    this yourself, write to the Api providers for guidance.
        """
        self.token_url = token_url
        self.client_id = oauth_client_id
        self.token_ttl = None

        self.oauth_session = OAuth2Session(
            client = LegacyApplicationClient(client_id = self.client_id)
        )
        self._token = None

    def get_access_token(self) -> str:
        return self.get_token()['access_token']

    def get_token(self) -> dict:
        if self._token is None:
            raise AuthorizationError('Missing access token. Authenticate to obtain the an access token.')
        
        if self.access_token_has_expired():
            self.refresh_token()
        
        return self._token


    def authenticate(self) -> dict:
        """
        Fetches an access token from the Climify OAuth identity provider
        using username and password (grant type: password).

        If the user is already authenticated and the refresh token is still valid
        it will refresh the token instead of re-authenticating.

        Returns:
            dict: A dictionary containing: 
                - access_token: Token used for future requests
                - refresh_token: Token used to refresh access token
                - token_type
                - expires_in: TTL of the access token
                - refresh_expires_in: TTL of the refresh token
                - session_state
                - scope: OpenId scopes of the token
                - expires_at: EPOCH time at which the access token will expire
        """
        if (self._token is not None and not self.refresh_token_has_expired()):
            return self.refresh_token()

        username = input('Input username: ')
        password = input('Input password: ')

        self._token = self.oauth_session.fetch_token(
            token_url=self.token_url,
            username=username,
            password=password
        )
        self.oauth_session.token = self._token
        self.token_ttl = self._token['expires_in']
        self.refresh_token_expiration_time = time() + self._token['refresh_expires_in']

        return self._token

    def refresh_token(self) -> dict:
        """
        Re-authenticates using the refresh token provided in the initial authentication.

        Raises:
            AuthorizationError: Is raised if no initial authentication has been performed
                                or the refresh token has expired.

        Returns:
            dict: A dictionary containing: 
                - access_token: Token used for future requests
                - refresh_token: Token used to refresh access token
                - token_type
                - expires_in: TTL of the access token
                - refresh_expires_in: TTL of the refresh token
                - session_state
                - scope: OpenId scopes of the token
                - expires_at: EPOCH time at which the access token will expire
        """
        if self._token is None:
            raise AuthorizationError('No refresh token was found. Authenticate to get the initial tokens.')
        
        if self.refresh_token_has_expired():
            raise AuthorizationError('Refresh token has expired. Please reauthenticate.')
        
        self._token = self.oauth_session.refresh_token(
            token_url=self.token_url,
            client_id=self.client_id
        )
        self.oauth_session.token = self._token
        self.refresh_token_expiration_time = time() + self._token['refresh_expires_in']

        return self._token

    def access_token_has_expired(self) -> bool:
        return self._token['expires_at'] < time()
    
    def refresh_token_has_expired(self) -> bool:
        return self.refresh_token_expiration_time < time()