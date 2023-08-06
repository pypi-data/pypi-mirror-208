from .service_account import ServiceAccount
from .jwt_handler import JWTHandler


class TokenRefresher:
    _jwt_handler: JWTHandler
    _token: str

    def __init__(self, service_account: ServiceAccount, seconds_before_expire: int, audience: str,
                 token_duration: int) -> None:
        self._jwt_handler = JWTHandler(service_account, seconds_before_expire, audience, token_duration)
        self._token = None

    def get_access_token(self):
        if self._token is None or self._jwt_handler.is_token_expired(self._token):
            self._token = self._jwt_handler.generate_token()

        return self._token
