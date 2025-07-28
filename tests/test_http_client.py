import pytest
import requests
from toolbox.api.http_client import HttpClient


def test_http_client_with_ssl_verification_enabled():
    http_client = HttpClient(verify_ssl=True)

    with pytest.raises(requests.exceptions.SSLError):
        http_client.get("https://self-signed.badssl.com/")


def test_http_client_with_ssl_verification_disabled():
    http_client = HttpClient(verify_ssl=False)

    try:
        response = http_client.get("https://self-signed.badssl.com/")
        assert response.status_code in [200, 400, 401, 403, 404, 500]  # Any valid HTTP status
    except requests.exceptions.SSLError:
        pytest.fail("SSL error occurred even with SSL verification disabled")


def test_http_client_default_ssl_verification():
    http_client = HttpClient()

    assert http_client.verify_ssl is True

    with pytest.raises(requests.exceptions.SSLError):
        http_client.get("https://self-signed.badssl.com/")


def test_http_client_post_with_ssl_verification_disabled():
    http_client = HttpClient(verify_ssl=False)

    try:
        response = http_client.post("https://self-signed.badssl.com/", json={"test": "data"})
        assert response.status_code in [200, 400, 401, 403, 404, 405, 500]
    except requests.exceptions.SSLError:
        pytest.fail("SSL error occurred even with SSL verification disabled")


def test_http_client_put_with_ssl_verification_disabled():
    http_client = HttpClient(verify_ssl=False)

    try:
        response = http_client.put("https://self-signed.badssl.com/", json={"test": "data"})
        assert response.status_code in [200, 400, 401, 403, 404, 405, 500]
    except requests.exceptions.SSLError:
        pytest.fail("SSL error occurred even with SSL verification disabled")


def test_http_client_delete_with_ssl_verification_disabled():
    http_client = HttpClient(verify_ssl=False)

    try:
        response = http_client.delete("https://self-signed.badssl.com/")
        assert response.status_code in [200, 400, 401, 403, 404, 405, 500]
    except requests.exceptions.SSLError:
        pytest.fail("SSL error occurred even with SSL verification disabled")


def test_http_client_patch_with_ssl_verification_disabled():
    http_client = HttpClient(verify_ssl=False)

    try:
        response = http_client.patch("https://self-signed.badssl.com/", json={"test": "data"})
        assert response.status_code in [200, 400, 401, 403, 404, 405, 500]
    except requests.exceptions.SSLError:
        pytest.fail("SSL error occurred even with SSL verification disabled")


def test_http_client_with_valid_ssl_certificate():
    http_client_with_ssl = HttpClient(verify_ssl=True)
    response = http_client_with_ssl.get("https://httpbin.org/get")
    assert response.status_code == 200

    http_client_without_ssl = HttpClient(verify_ssl=False)
    response = http_client_without_ssl.get("https://httpbin.org/get")
    assert response.status_code == 200
