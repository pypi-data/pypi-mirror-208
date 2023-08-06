from __future__ import annotations

import re
from datetime import datetime
from datetime import timedelta

try:
    from datetime import UTC
except ImportError:
    from datetime import timezone

    UTC = timezone(timedelta(0), "UTC")

from typing import Any
from typing import Iterable
from typing import MutableMapping
from uuid import uuid4

from jwt import InvalidAlgorithmError
from jwt import InvalidTokenError
from jwt import PyJWKClient
from jwt.algorithms import has_crypto
from jwt.algorithms import requires_cryptography
from jwt.api_jwt import decode_complete
from jwt.api_jwt import encode

from drakaina.contrib.jwt import RESERVED_FIELDS
from drakaina.contrib.jwt import SUPPORTED_ALGORITHMS
from drakaina.contrib.jwt.errors import InvalidJWTTokenError
from drakaina.contrib.jwt.errors import JWTBackendError
from drakaina.contrib.jwt.errors import ValidationJWTTokenError
from drakaina.utils import iterable_str_arg


def datetime_utc_now() -> datetime:
    """Returns the current date/time in the UTC time zone.

    :return: The current date/time is in the UTC time zone.

    """
    return datetime.now(tz=UTC)


def datetime_to_timestamp(dt: datetime) -> int:
    """Converts the specified date/time to unixtime timestamp.

    :param dt: Date/time for conversion.
    :return: Unixtime timestamp.

    """
    return int(dt.timestamp())


def datetime_from_timestamp(ts: int) -> datetime:
    """Converts the specified unixtime timestamp to the python date/time type.

    :param ts: Timestamp for conversion.
    :return: Date/time from timestamp.

    """
    return datetime.fromtimestamp(ts, tz=UTC)


# Claims of specification JWT


def set_issuer(payload: dict[str, Any], value: str, claim: str = "iss"):
    """Sets the issuer of the token.

    https://tools.ietf.org/html/rfc7519#section-4.1.1

    :param payload: Token payload.
    :param value: Value to set the claim.
    :param claim: Claim short name (key).

    """
    payload[claim] = value


def set_subject(payload: dict[str, Any], value: str, claim: str = "sub"):
    """Sets the subject of the token.

    https://tools.ietf.org/html/rfc7519#section-4.1.2

    :param payload: Token payload.
    :param value: Value to set the claim.
    :param claim: Claim short name (key).

    """
    payload[claim] = value


def set_audience(payload: dict[str, Any], value: str, claim: str = "aud"):
    """Sets the audience of the token.

    https://tools.ietf.org/html/rfc7519#section-4.1.3

    :param payload: Token payload.
    :param value: Value to set the claim.
    :param claim: Claim short name (key).

    """
    payload[claim] = value


def set_expiration(
    payload: dict[str, Any],
    expiration_time: datetime | int,
    claim: str = "exp",
):
    """Sets the expiration time of a token.

    https://tools.ietf.org/html/rfc7519#section-4.1.4

    :param payload: Token payload.
    :param expiration_time: Date/time value to set the claim.
    :param claim: Claim short name (key).

    """
    if isinstance(expiration_time, (int, float)):
        payload[claim] = int(expiration_time)
    else:
        payload[claim] = datetime_to_timestamp(expiration_time)


def set_not_before(
    payload: dict[str, Any],
    activation_time: datetime | int,
    claim: str = "nbf",
):
    """Sets the time `Not before`.

    https://tools.ietf.org/html/rfc7519#section-4.1.5

    :param payload: Token payload.
    :param activation_time: Date/time value to set the claim.
    :param claim: Claim short name (key).

    """
    if isinstance(activation_time, (int, float)):
        payload[claim] = int(activation_time)
    else:
        payload[claim] = datetime_to_timestamp(activation_time)


def set_issued_at(
    payload: dict[str, Any],
    now: datetime | int,
    claim: str = "iat",
):
    """Sets the time of token issuance.

    https://tools.ietf.org/html/rfc7519#section-4.1.6

    :param payload: Token payload.
    :param now: Current date/time value to set the claim.
    :param claim: Claim short name (key).

    """
    if isinstance(now, (int, float)):
        payload[claim] = int(now)
    else:
        payload[claim] = datetime_to_timestamp(now)


def set_token_id(
    payload: dict[str, Any],
    value: str | bool | None = None,
    claim: str = "jti",
):
    """Sets the token identifier.

    https://tools.ietf.org/html/rfc7519#section-4.1.7

    :param payload: Token payload.
    :param value: Value to set the claim. Default UUID4.
    :param claim: Claim short name (key).

    """
    if value is True or value is None:
        value = uuid4().hex
    payload[claim] = value


def check_expiration(
    payload: dict[str, Any],
    now: datetime,
    claim: str = "exp",
):
    """Checks if the timestamp value has passed in the given claim
    (since the given time value in `now`).
    If yes, it causes a `InvalidTokenError` with an error message.

    :param payload: Token payload.
    :param now: Current date/time value to check the claim.
    :param claim: Claim short name (key).

    :raise InvalidJWTTokenError:
    :raise ValidationJWTTokenError:

    """
    try:
        expiration_value = payload[claim]
    except KeyError:
        raise InvalidJWTTokenError(f"Token has no `{claim}` claim")

    expiration = datetime_from_timestamp(expiration_value)
    if now >= expiration:
        raise ValidationJWTTokenError(f"Token `{claim}` claim has expired")


def check_not_before(
    payload: dict[str, Any],
    now: datetime,
    claim: str = "nbf",
):
    """Checks if the timestamp value has reached the specified claim
    (the moment of the specified `now` time value).
    If so, raises a `InvalidTokenError` with an error message.

    :param payload: Token payload.
    :param now: Current date/time value to check the claim.
    :param claim: Claim short name (key).

    :raise InvalidJWTTokenError:
    :raise ValidationJWTTokenError:

    """
    try:
        not_before_value = payload[claim]
    except KeyError:
        raise InvalidJWTTokenError(f"Token has no `{claim}` claim")

    not_before_value = datetime_from_timestamp(not_before_value)
    if now < not_before_value:
        raise ValidationJWTTokenError(f"Token `{claim}` claim not reached")


# Custom JWT claims


def set_token_type(payload: dict[str, Any], value: str, claim: str = "jtt"):
    """Sets the token type claim.

    :param payload: Token payload.
    :param value: Value to set the claim.
    :param claim: Claim short name (key).

    """
    payload[claim] = value


def set_permission_scopes(
    payload: dict[str, Any],
    scopes: str | Iterable[str],
    claim: str = "scp",
):
    """Sets the claim of the permissions scopes.

    :param payload: Token payload.
    :param scopes: Value to set the claim.
    :param claim: Claim short name (key).

    """
    payload[claim] = ",".join(iterable_str_arg(scopes))


# Token handlers


def decode_jwt_token(
    token: str,
    verify_key: str,
    algorithms: Iterable[str] = SUPPORTED_ALGORITHMS,
    verify: bool = True,
    decode_options: dict[str, bool | list[str]] | None = None,
    verify_values: dict[str, str | Iterable[str] | re.Pattern] | None = None,
    leeway: int | float = 0,
    jwk_url: str | None = None,
) -> dict[str, Any]:
    """Performs validation of the provided token and returns
    its payload dictionary.

    :param token: JWT token.
    :param verify_key: The token verification key.
        May be a signature key in symmetric algorithms, or a public key
        in asymmetric signature algorithms.
    :param algorithms: Supported algorithms.
    :param verify: Verify token.
    :param decode_options: Options argument for `pyjwt.decode`.
        Default PyJWT values:
        `{
            "verify_signature": True,
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": True,
            "verify_aud": True,
            "verify_iss": True,
            "require": [],
        }`
    :param verify_values: Values to be verified.
    :param leeway: Leeway time in seconds.
    :param jwk_url: URL for the PyJWK client.
        It gets the validation key for the specified jwt-token.
    :return: Decoded JWT token payload.

    :raise JWTBackendError: In the case of incorrectly passed
        parameters and arguments.
    :raise ValidationJWTTokenError: In case the token has an invalid signature
        or invalid payload data.

    """

    if jwk_url:
        jwks_client = PyJWKClient(jwk_url)
        verify_key = jwks_client.get_signing_key_from_jwt(token).key

    verify_values = {} if verify_values is None else verify_values.copy()
    options = {"verify_signature": verify, **(decode_options or {})}
    params = {"leeway": leeway}

    # Provide values to check in the pyjwt module
    if "iss" in verify_values and not isinstance(
        verify_values["iss"],
        (Iterable, re.Pattern),  # for pyjwt issuer must be single
    ):
        params["issuer"] = verify_values.pop("iss", None)
    if "aud" in verify_values and not isinstance(
        verify_values["aud"],
        re.Pattern,  # for pyjwt audience must be single or iterable
    ):
        params["audience"] = verify_values.pop("aud")

    try:
        token_data = decode_complete(
            jwt=token,
            key=verify_key,
            algorithms=algorithms,
            options=options,
            **params,
        )
    except InvalidAlgorithmError as error:
        raise JWTBackendError("Invalid algorithm specified") from error
    except InvalidTokenError:
        raise InvalidJWTTokenError("Token is invalid or expired")

    if verify:
        _extra_validation(token_data, verify_values)

    return token_data["payload"]


def encode_jwt_token(
    signing_key: str,
    algorithm: str = "HS256",
    payload: dict[str, Any] | None = None,
    issuer: str | None = None,
    subject: str | None = None,
    audience: str | None = None,
    expiration: datetime | timedelta | int | None = None,
    not_before: datetime | timedelta | int | bool | None = None,
    issued_at: datetime | int | bool | None = None,
    token_id: int | str | bool | None = None,
    token_type: str | None = None,
    permission_scopes: str | Iterable[str] | None = None,
    headers: dict[str, Any] | None = None,
) -> str:
    """Returns an encoded token with the specified payload and
    specified parameters.

    The claims from the specification for JWT tokens are expected in
    the corresponding key parameters.

    :param signing_key: The secret key to sign a token.
    :param algorithm: Token Signing Algorithm.
    :param payload: Token payload.
    :param issuer: Issuer.
    :param subject: Subject.
    :param audience: Audience.
    :param expiration: Expiration time.
    :param not_before: Not before time.
        If `True`, the current time is applied.
    :param issued_at: Issued at the time.
        If `True`, the current time is applied. Default: `True`.
    :param token_id: Token ID.
        If `True`, then uuid4 is generated.
    :param token_type: The type of token, if you need it.
        It has the standard claim `jtt'.
    :param permission_scopes: Scope of permits, if you need them.
        It has the standard claim `scp'.
    :param headers: JWT token headers. RFC7519#section5
    :return: Encoded JWT token.

    """
    _validate_algorithm(algorithm)

    if not isinstance(payload, (dict, MutableMapping)):
        payload = {}
    else:
        payload = payload.copy()
        _validate_payload(payload)

    if issuer:
        set_issuer(payload, issuer)
    if subject:
        set_subject(payload, subject)
    if audience:
        set_audience(payload, audience)

    now = datetime_utc_now()

    if expiration:
        if isinstance(expiration, timedelta):
            expiration = now + expiration
        set_expiration(payload, expiration)
    if not_before:
        if isinstance(not_before, timedelta):
            not_before = now + not_before
        elif not_before is True:
            not_before = now
        set_not_before(payload, not_before)
    if issued_at:
        if issued_at is True:
            issued_at = now
        set_issued_at(payload, issued_at)

    if token_id:
        set_token_id(payload, token_id)

    if token_type:
        set_token_type(payload, token_type)
    if permission_scopes:
        set_permission_scopes(payload, permission_scopes)

    return encode(
        payload=payload,
        key=signing_key,
        algorithm=algorithm,
        headers=headers,
    )


# Helpful functions


def copy_payload(
    payload: dict[str, Any],
    no_copy: Iterable[str] = ("exp", "nbf", "iat", "jti", "jtt", "scp"),
) -> tuple[dict[str, Any], ...]:
    """This function helps to copy the data of the old token and prepare
    the payload and parameters of the new token creation function.

    The data that can be safely copied will be returned by the first mapping.
    And the data of the JWT specification fields expected by
    the `encode_jwt_token` function as function parameters will be
    returned by the second mapping.

    This can be applied e.g. when updating an old token, keeping
    permanent data, and updating data critical for token verification
    and rotation.

    Example ::

        >>> payload, params = copy_payload(old_token_payload)
        >>> token = encode_jwt_token("_secret_", payload=payload, **params)

    :param payload: The payload for copying.
    :param no_copy: Claims that don't require copying.
    :return: A tuple of two elements, where the first is a filtered copy
        of the payload and the second is a mapping with parameters
        to pass to the `encode_jwt_token` function.

    """
    payload = payload.copy()

    # Mapping as { claim_abbr: param_name }
    encode_params_map = {
        "iss": "issuer",
        "sub": "subject",
        "aud": "audience",
        "exp": "expiration",
        "nbf": "not_before",
        "iat": "issued_at",
        "jti": "token_id",
        "jtt": "token_type",
        "scp": "permission_scopes",
    }
    # Preparing parameters for the `encode_jwt_token` function
    new_encode_params = {}
    for claim, param_name in encode_params_map.items():
        if claim in payload and claim not in no_copy:
            new_encode_params[param_name] = payload.pop(claim)

    # Copying the remaining payload
    new_payload = {
        claim: value for claim, value in payload.items() if claim not in no_copy
    }

    return new_payload, new_encode_params


def _extra_validation(
    decoded_token: dict[str, dict[str, Any] | str],
    verify_values: dict[str, str | Iterable[str] | re.Pattern | dict] = None,
):
    """Performs an additional check that is not performed by the pyjwt module.

    The check is performed by comparing the data provided for the check with
    the data included in the token payload with the same keys.

    :param decoded_token: Dict returned from `pyjwt.decode_complete`. Must
        contain a `header' and `payload'.
    :param verify_values: Dict with data to be validated. The keys must match
        the dictionary fields with the token payload.
    :raise ValidationJWTTokenError: In case the token has an invalid
        payload or header data.

    """
    if verify_values is None:
        verify_values = {}

    header = decoded_token["header"]
    verify_header_values = verify_values.pop("header", {})
    try:
        for key, verify_value in verify_header_values.items():
            token_value = header.get(key)
            if isinstance(verify_value, (str, int)):
                assert token_value == verify_value
            elif isinstance(verify_value, (list, set, tuple)):
                assert token_value in verify_value
            elif isinstance(verify_value, re.Pattern):
                assert re.match(verify_value, token_value)
    except AssertionError as error:
        raise ValidationJWTTokenError("Invalid token header") from error

    payload = decoded_token["payload"]
    try:
        for key, verify_value in verify_values.items():
            token_value = payload.get(key)
            if isinstance(verify_value, (str, int)):
                assert token_value == verify_value
            elif isinstance(verify_value, (list, set, tuple)):
                assert token_value in verify_value
            elif isinstance(verify_value, re.Pattern):
                assert verify_value.match(token_value)
    except AssertionError as error:
        raise ValidationJWTTokenError("Invalid token payload") from error


def _validate_algorithm(algorithm: str):
    """Check that the specified algorithm is recognized, and that
    `cryptography' is installed for those algorithms that require it.

    :param algorithm: Algorithm to verify.
    :raise JWTBackendError: If the algorithm is not recognized or not supported.
    :raise ModuleNotFoundError: If the `cryptography' package is not installed.

    """
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise JWTBackendError(f"Unrecognized algorithm type '{algorithm}'")

    if algorithm in requires_cryptography and not has_crypto:
        raise ModuleNotFoundError(
            f"To use `{algorithm}` you must install the `cryptography` package",
        )


def _validate_payload(payload: dict[str, Any]):
    """Checks that the payload does not use reserved fields.

    :param payload: Payload to verify.
    :raise JWTBackendError: If the provided payload has reserved fields.

    """
    for reserved_jwt_claim in RESERVED_FIELDS:
        if reserved_jwt_claim in payload:
            if reserved_jwt_claim == "jtt":
                raise JWTBackendError(
                    f"The claim `{reserved_jwt_claim}` is reserved in "
                    f"Drakaina to be specified as `token_type`.",
                )
            elif reserved_jwt_claim == "scp":
                raise JWTBackendError(
                    f"The claim `{reserved_jwt_claim}` is reserved in "
                    f"Drakaina to be specified as `permission_scopes`.",
                )
            raise JWTBackendError(
                "Please use keyword arguments to fill in "
                "the JWT specification fields.",
            )
