import datetime
import json
import typing
from urllib.request import urlopen

from jose import jwt


class TokenPayload(dict):
    """
    Helper class to access properties inside the token payload
    """

    def __init__(self, raw_payload: dict, raw_token: str = None) -> None:
        super().__init__(raw_payload)
        self.raw_token = raw_token

    @classmethod
    def parse(cls, raw_token: str):
        return cls(jwt.get_unverified_claims(raw_token), raw_token=raw_token)

    def get_claim(
        self, claim_name: str, claim_default_value: typing.Optional[typing.Any] = None
    ) -> typing.Any:
        """
        Returns the claim value if present, or claim_default_value
        """
        return self.get(claim_name, claim_default_value)

    def get_required_claim(self, claim_name: str) -> typing.Any:
        """
        Returns the claim value if present, or fails with 401
        """
        claim_value = self.get_claim(claim_name)
        if not claim_value:
            raise AuthError(
                status_code=401,
                code="invalid_token",
                description=f"Missing '{claim_name}' claim.",
            )
        return claim_value


class AuthError(Exception):
    def __init__(self, status_code: int, code: str, description: str):
        super().__init__()
        self.status_code = status_code
        self.code = code
        if description and not description.endswith("."):
            description = f"{description}."
        self.description = description

    @property
    def details(self):
        return {"code": self.code, "description": self.description}


class _JwksProvider:
    """
    Provides the JSON Web Key Sets.
    See https://auth0.com/docs/tokens/json-web-tokens/json-web-key-sets
    """

    def __init__(self, auth0_domain: str) -> None:
        """
        :param auth0_domain: the domain
        """
        self.auth0_domain = auth0_domain

    def get(self):
        url = "https://" + self.auth0_domain + "/.well-known/jwks.json"
        return json.loads(urlopen(url).read())


class _JwksProviderWithCache(_JwksProvider):
    """
    Extends _JwksProvider. Implements caching.
    See https://auth0.com/docs/tokens/json-web-tokens/json-web-key-sets
    """

    def __init__(self, auth0_domain: str, ttl_in_seconds: int) -> None:
        """
        :param auth0_domain: the domain
        :param ttl_in_seconds: time-to-live in seconds
        """
        super().__init__(auth0_domain)
        self.ttl_in_seconds = ttl_in_seconds
        self.__jwks = None
        self.__expires_at = None

    def get(self):
        if not self.__expires_at or self.__expires_at <= datetime.datetime.now():
            self.__jwks = super().get()
            self.__expires_at = datetime.datetime.now() + datetime.timedelta(
                seconds=self.ttl_in_seconds
            )
        return self.__jwks


TP = typing.TypeVar("TP", bound=TokenPayload)


class TokenVerifier:
    def __init__(
        self,
        auth0_domain: str,
        api_audience: str,
        jwks_cache_ttl: typing.Optional[int] = None,
    ):
        self._auth0_domain = auth0_domain
        self._api_audience = api_audience
        # this is not safe to change without double-checking configuration in Auth0 dashboard + current codebase
        self._algorithms = ["RS256"]
        self._jwks_provider = (
            _JwksProviderWithCache(auth0_domain, jwks_cache_ttl)
            if jwks_cache_ttl
            else _JwksProvider(auth0_domain)
        )

    @staticmethod
    def _extract_token_from_auth_header(auth_header: str) -> str:
        """
        Obtains the access token from the Authorization Header
        """
        if not auth_header:
            raise AuthError(
                status_code=401,
                code="missing_header",
                description="Authorization header is expected.",
            )

        parts = auth_header.split()

        if parts[0].lower() != "bearer":
            raise AuthError(
                status_code=401,
                code="invalid_header",
                description="Authorization header must start with Bearer.",
            )
        elif len(parts) == 1:
            raise AuthError(
                status_code=401, code="invalid_header", description="Token not found."
            )
        elif len(parts) > 2:
            raise AuthError(
                status_code=401,
                code="invalid_header",
                description="Authorization header must be Bearer token.",
            )

        token = parts[1]
        return token

    @staticmethod
    def _extract_permissions_from_token(token: str) -> typing.List[str]:
        """
        Extracts permissions from the access token.
        Permission are added to tokens by enabling Role-Based Access Control for APIs.
        See https://auth0.com/docs/authorization/rbac/enable-role-based-access-control-for-apis
        """
        permissions = []
        unverified_claims = jwt.get_unverified_claims(token)

        token_scope = unverified_claims.get("scope")
        if token_scope:
            permissions += token_scope.split()

        token_permissions = unverified_claims.get("permissions")
        if token_permissions and isinstance(token_permissions, list):
            permissions += token_permissions

        return list(set(permissions))  # remove possible duplicates

    @staticmethod
    def parse_token(
        token: str,
        token_payload_class: typing.Type[TP] = TokenPayload,
    ) -> TP:
        """
        Decodes the token payload

        :param token: the token as string
        :param token_payload_class: optional subclass of TokenPayload
        :returns The dict representation of the claims set, assuming the signature is valid
                and all requested data validation passes.
        """
        return token_payload_class.parse(token)

    def verify_auth_header(
        self,
        auth_header: str,
        permissions: typing.List[str] = None,
        token_payload_class: typing.Type[TP] = TokenPayload,
    ) -> TokenPayload:
        token = self._extract_token_from_auth_header(auth_header)
        return self.verify_token(
            token, permissions=permissions, token_payload_class=token_payload_class
        )

    def verify_token(
        self,
        token: str,
        permissions: typing.List[str] = None,
        token_payload_class: typing.Type[TP] = TokenPayload,
    ) -> TP:
        """
        Decodes and verifies the token payload

        :param token: the token as string
        :param permissions: list of permissions required for to the token to be valid
        :param token_payload_class: optional subclass of TokenPayload
        :returns The dict representation of the claims set, assuming the signature is valid
                and all requested data validation passes.
        """
        if not token:
            raise AuthError(
                status_code=401, code="invalid_token", description="Token is missing."
            )

        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError:
            raise AuthError(
                status_code=401,
                code="invalid_header",
                description="Invalid header. Use an RS256 signed JWT Access Token.",
            )
        if unverified_header["alg"] == "HS256":
            raise AuthError(
                status_code=401,
                code="invalid_header",
                description="Invalid header. Use an RS256 signed JWT Access Token.",
            )
        rsa_key = {}

        jwks = self._jwks_provider.get()
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }

        if rsa_key:
            try:
                raw_payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=self._algorithms,
                    audience=self._api_audience,
                    issuer="https://" + self._auth0_domain + "/",
                )
            except jwt.ExpiredSignatureError:
                raise AuthError(
                    status_code=401,
                    code="token_expired",
                    description="Token is expired.",
                )

            except jwt.JWTClaimsError:
                raise AuthError(
                    status_code=401,
                    code="invalid_claims",
                    description="Incorrect claims, please check the audience and issuer.",
                )

            except Exception as error:
                raise AuthError(
                    status_code=401, code="invalid_token", description=str(error)
                )

            """Check permissions
            """
            if permissions:
                token_permissions = self._extract_permissions_from_token(token)
                for permission in permissions:
                    if permission not in token_permissions:
                        raise AuthError(
                            status_code=403,
                            code="missing_permission",
                            description=f"You don't have access to this resource. Permission '{permission}' is missing.",
                        )

            return token_payload_class.parse(raw_token=token)

        raise AuthError(
            status_code=401,
            code="invalid_header",
            description="Unable to find appropriate key.",
        )
