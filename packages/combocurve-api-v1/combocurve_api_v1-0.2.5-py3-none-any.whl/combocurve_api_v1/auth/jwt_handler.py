import datetime
import jwt

from .service_account import ServiceAccount

JWT_ALGORITHM = 'RS256'

MAX_EXPIRATION_DELTA = 60 * 60 * 24 * 7  # 7 days
MIN_EXPIRATION_DELTA = 60 * 60  # 1 hour


class JWTHandler:
    _service_account: ServiceAccount
    _audience: str
    _seconds_before_expire: int
    _expiration_time: datetime.timedelta

    def __init__(self, service_account: ServiceAccount, seconds_before_expire: int, audience: str,
                 token_duration: int) -> None:

        if token_duration < MIN_EXPIRATION_DELTA or token_duration > MAX_EXPIRATION_DELTA:
            raise ValueError(f'token_duration should be greater than or equal to {MIN_EXPIRATION_DELTA} and less than'
                             + ' or equal to {MAX_EXPIRATION_DELTA}')
        self._service_account = service_account
        self._audience = audience
        self._expiration_time = datetime.timedelta(seconds=token_duration)
        self._seconds_before_expire = seconds_before_expire

    def generate_token(self) -> str:
        now = datetime.datetime.utcnow()

        return jwt.encode(
            {
                'iss': self._service_account.client_email,
                'sub': self._service_account.client_email,
                'aud': self._audience,
                'iat': now,
                'exp': now + self._expiration_time,
            },
            self._service_account.private_key,
            algorithm=JWT_ALGORITHM,
            headers={
                'kid': self._service_account.private_key_id,
                'typ': 'JWT',
                'alg': JWT_ALGORITHM,
            })

    def is_token_expired(self, token: str) -> bool:
        decoded = jwt.decode(token,
                             self._service_account.private_key,
                             algorithms=JWT_ALGORITHM,
                             options={"verify_signature": False})
        exp_time = datetime.datetime.utcfromtimestamp(decoded['exp'])

        if exp_time - datetime.datetime.utcnow() < datetime.timedelta(seconds=self._seconds_before_expire):
            return True
        return False
