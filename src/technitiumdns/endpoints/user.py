"""User / authentication / session endpoint specs (``/api/user/...`` & ``/api/sso/...``)."""

from __future__ import annotations

from ..models.user import (
    LoginResult,
    SsoStatus,
    TwoFactorInit,
    UpdateCheckResult,
    UserInfo,
)
from . import EndpointSpec, _params


def sso_status() -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/sso/status",
        parser=SsoStatus.from_api,
    )


def login(
    *,
    user: str,
    password: str,
    totp: str | None = None,
    include_info: bool = True,
) -> EndpointSpec:
    data = {"user": user, "pass": password, "includeInfo": include_info}
    if totp is not None:
        data["totp"] = totp
    return EndpointSpec(
        method="POST",
        path="api/user/login",
        data=data,
        parser=LoginResult.from_api,
    )


def create_token(
    *,
    user: str | None = None,
    password: str | None = None,
    totp: str | None = None,
    token_name: str,
) -> EndpointSpec:
    data: dict[str, object] = {"tokenName": token_name}
    if user is not None:
        data["user"] = user
    if password is not None:
        data["pass"] = password
    if totp is not None:
        data["totp"] = totp
    return EndpointSpec(
        method="POST",
        path="api/user/createToken",
        data=data,
        parser=LoginResult.from_api,
    )


def create_single_use_token() -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/user/createSingleUseToken",
        parser=LoginResult.from_api,
    )


def logout() -> EndpointSpec:
    return EndpointSpec(method="POST", path="api/user/logout")


def session_get() -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/user/session/get",
        parser=LoginResult.from_api,
    )


def session_delete() -> EndpointSpec:
    return EndpointSpec(method="POST", path="api/user/session/delete")


def change_password(*, password: str) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/user/changePassword",
        data={"pass": password},
    )


def init_2fa() -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/user/2fa/init",
        parser=TwoFactorInit.from_api,
    )


def enable_2fa(*, totp: str) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/user/2fa/enable",
        data=_params(totp=totp),
    )


def disable_2fa(*, totp: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/user/2fa/disable",
        data=_params(totp=totp),
    )


def get_profile() -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/user/profile/get",
        parser=UserInfo.from_api,
    )


def set_profile(
    *,
    display_name: str | None = None,
    session_timeout_seconds: int | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/user/profile/set",
        data=_params(
            displayName=display_name,
            sessionTimeoutSeconds=session_timeout_seconds,
        ),
    )


def check_for_update() -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/user/checkForUpdate",
        parser=UpdateCheckResult.from_api,
    )
