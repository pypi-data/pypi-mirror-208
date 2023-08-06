from .service_account import ServiceAccount
from .token_refresher import TokenRefresher

DEFAULT_AUDIENCE = 'https://api.combocurve.com'


class ComboCurveAuth:
    _token_refresher: TokenRefresher
    _api_key: str

    def __init__(self,
                 service_account: ServiceAccount,
                 api_key: str,
                 seconds_before_token_expire: int = 60,
                 audience: str = DEFAULT_AUDIENCE,
                 token_duration=3600) -> None:
        """
        Parameters:
            service_account (ServiceAccount): ComboCurve Service Account
            api_key (str): ComboCurve API key
            seconds_before_token_expire (int): How many seconds before the token expiration to generate a new token.
            audience (str): What the token is intended for.
            token_duration (int): How many seconds the token is going to be valid.
        """
        self._token_refresher = TokenRefresher(service_account, seconds_before_token_expire, audience, token_duration)
        self._api_key = api_key

    def get_auth_headers(self):
        token = self._token_refresher.get_access_token()
        return {'Authorization': f'Bearer {token}', 'x-api-key': self._api_key}
