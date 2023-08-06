import dataclasses
import datetime
import json
import typing
from urllib.error import HTTPError
from urllib.request import Request, urlopen


@dataclasses.dataclass
class Token:
    access_token: str
    token_type: str
    expires_at: datetime.datetime

    def get_authorization(self) -> str:
        return f"{self.token_type} {self.access_token}"

    def is_expired(self, skew_seconds: int = None):
        if self.expires_at is not None:
            now = datetime.datetime.now()
            if skew_seconds:
                now += datetime.timedelta(seconds=skew_seconds)
            return now >= self.expires_at
        return True


class TokenProvider:
    def __init__(
        self,
        issuer,
        audience,
        client_id,
        client_secret,
        additional_payload: typing.Optional[dict[str, typing.Any]] = None,
    ):
        """
        :param issuer: hostname of the tenant in Auth0, example `spartanapproach-dev.us.auth0.com`
        :param audience: API identifier
        :param client_id:
        :param client_secret:
        :param additional_payload: work-around to customize the token passing additional params in the payload, see
         https://manage.auth0.com/dashboard/us/spartanapproach-dev/actions/library/details/6c3b3d90-9f9c-4b22-b9d6-4046581a7709
        """
        self.issuer = issuer
        self.audience = audience
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: typing.Optional[Token] = None
        self.additional_payload = additional_payload

    def get_token(self) -> Token:
        if self._token is None or self._token.is_expired():
            url = "https://" + self.issuer + "/oauth/token"
            payload = {
                "grant_type": "client_credentials",
                "audience": self.audience,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            if self.additional_payload:
                payload.update(self.additional_payload)

            request_data = json.dumps(payload)
            request = Request(
                url,
                method="POST",
                data=request_data.encode("utf-8"),
                headers={"content-type": "application/json"},
            )

            try:
                response = urlopen(request)
            except HTTPError as error:
                raise RuntimeError(
                    f"Invalid response POST {url} {request_data} >> {error.code}"
                )

            response_data = response.read().decode("utf-8")
            if response.status != 200:
                raise RuntimeError(
                    f"Invalid response POST {url} {request_data} >> {response.status} {response_data}"
                )

            response_dict = json.loads(response_data)
            self._token = Token(
                access_token=response_dict.get("access_token"),
                token_type=response_dict.get("token_type"),
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=response_dict.get("expires_in")),
            )

        return self._token
