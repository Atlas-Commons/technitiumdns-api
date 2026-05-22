"""Tests for the URL/param/auth/envelope helpers in ``_transport``."""

from __future__ import annotations

import pytest

from technitiumdns import _transport
from technitiumdns.exceptions import (
    InvalidTokenError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
    TechnitiumError,
    TwoFactorRequiredError,
)


class TestBuildUrl:
    def test_strips_trailing_slash(self) -> None:
        assert _transport.build_url("http://dns:5380/", "/api/foo") == "http://dns:5380/api/foo"

    def test_no_double_slash(self) -> None:
        assert _transport.build_url("http://dns:5380", "api/foo") == "http://dns:5380/api/foo"


class TestEncodeValue:
    def test_bool_true_lowercase(self) -> None:
        assert _transport.encode_value(True) == "true"

    def test_bool_false_lowercase(self) -> None:
        assert _transport.encode_value(False) == "false"

    def test_int(self) -> None:
        assert _transport.encode_value(42) == "42"

    def test_list_comma_join(self) -> None:
        assert _transport.encode_value([1, 2, "x"]) == "1,2,x"


class TestEncodeParams:
    def test_drops_none(self) -> None:
        out = _transport.encode_params({"a": 1, "b": None, "c": True})
        assert out == {"a": "1", "c": "true"}

    def test_adds_token_fallback(self) -> None:
        out = _transport.encode_params({}, token="abc")
        assert out == {"token": "abc"}

    def test_does_not_override_explicit_token(self) -> None:
        out = _transport.encode_params({"token": "xyz"}, token="abc")
        assert out == {"token": "xyz"}


class TestAuthHeaders:
    def test_empty_when_no_token(self) -> None:
        assert _transport.auth_headers(None) == {}

    def test_bearer_format(self) -> None:
        assert _transport.auth_headers("abc") == {"Authorization": "Bearer abc"}


class TestProcessEnvelope:
    def test_ok_returns_response(self) -> None:
        payload = {"status": "ok", "response": {"a": 1}}
        assert _transport.process_envelope(payload) == {"a": 1}

    def test_ok_without_response_returns_whole_payload(self) -> None:
        payload = {"status": "ok", "server": "s1", "ssoEnabled": True}
        assert _transport.process_envelope(payload) == payload

    def test_invalid_token_raises(self) -> None:
        with pytest.raises(InvalidTokenError) as exc_info:
            _transport.process_envelope({"status": "invalid-token", "errorMessage": "no good"})
        assert exc_info.value.status == "invalid-token"
        assert exc_info.value.error_message == "no good"

    def test_2fa_required_raises(self) -> None:
        with pytest.raises(TwoFactorRequiredError) as exc_info:
            _transport.process_envelope({"status": "2fa-required", "errorMessage": "give totp"})
        assert exc_info.value.status == "2fa-required"

    def test_generic_error_raises(self) -> None:
        with pytest.raises(TechnitiumError) as exc_info:
            _transport.process_envelope(
                {
                    "status": "error",
                    "errorMessage": "boom",
                    "stackTrace": "trace",
                    "innerErrorMessage": "inner",
                }
            )
        err = exc_info.value
        assert err.status == "error"
        assert err.error_message == "boom"
        assert err.stack_trace == "trace"
        assert err.inner_error_message == "inner"


class TestRaiseForHttpStatus:
    def test_2xx_noop(self) -> None:
        _transport.raise_for_http_status(200, {})
        _transport.raise_for_http_status(204, {})

    def test_401_maps_to_invalid_token(self) -> None:
        with pytest.raises(InvalidTokenError):
            _transport.raise_for_http_status(401, {"errorMessage": "x"})

    def test_403_maps_to_permission(self) -> None:
        with pytest.raises(PermissionDeniedError):
            _transport.raise_for_http_status(403, {})

    def test_404_maps_to_not_found(self) -> None:
        with pytest.raises(NotFoundError):
            _transport.raise_for_http_status(404, {})

    def test_5xx_maps_to_server_error(self) -> None:
        with pytest.raises(ServerError):
            _transport.raise_for_http_status(503, "unavailable")
