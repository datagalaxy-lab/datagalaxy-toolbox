import pytest
import requests
from toolbox.api.http_client import HttpClient


TEST_URL = "https://example.com"


def test_http_client_with_ssl_verification_enabled(mocker):
    get_mock = mocker.patch(
        "toolbox.api.http_client.requests.get",
        side_effect=requests.exceptions.SSLError,
    )
    http_client = HttpClient(verify_ssl=True)

    with pytest.raises(requests.exceptions.SSLError):
        http_client.get(TEST_URL)

    get_mock.assert_called_once_with(TEST_URL, headers=None, params=None, verify=True)


def test_http_client_with_ssl_verification_disabled(mocker):
    get_mock = mocker.patch("toolbox.api.http_client.requests.get")
    http_client = HttpClient(verify_ssl=False)

    response = http_client.get(TEST_URL)

    assert response is get_mock.return_value
    get_mock.assert_called_once_with(TEST_URL, headers=None, params=None, verify=False)


def test_http_client_default_ssl_verification(mocker):
    get_mock = mocker.patch(
        "toolbox.api.http_client.requests.get",
        side_effect=requests.exceptions.SSLError,
    )
    http_client = HttpClient()

    assert http_client.verify_ssl is True

    with pytest.raises(requests.exceptions.SSLError):
        http_client.get(TEST_URL)

    get_mock.assert_called_once_with(TEST_URL, headers=None, params=None, verify=True)


def test_http_client_post_with_ssl_verification_disabled(mocker):
    post_mock = mocker.patch("toolbox.api.http_client.requests.post")
    http_client = HttpClient(verify_ssl=False)
    payload = {"test": "data"}

    response = http_client.post(TEST_URL, json=payload)

    assert response is post_mock.return_value
    post_mock.assert_called_once_with(
        TEST_URL,
        headers=None,
        json=payload,
        params=None,
        verify=False,
    )


def test_http_client_put_with_ssl_verification_disabled(mocker):
    put_mock = mocker.patch("toolbox.api.http_client.requests.put")
    http_client = HttpClient(verify_ssl=False)
    payload = {"test": "data"}

    response = http_client.put(TEST_URL, json=payload)

    assert response is put_mock.return_value
    put_mock.assert_called_once_with(
        TEST_URL,
        headers=None,
        json=payload,
        params=None,
        verify=False,
    )


def test_http_client_delete_with_ssl_verification_disabled(mocker):
    delete_mock = mocker.patch("toolbox.api.http_client.requests.delete")
    http_client = HttpClient(verify_ssl=False)

    response = http_client.delete(TEST_URL)

    assert response is delete_mock.return_value
    delete_mock.assert_called_once_with(
        TEST_URL,
        headers=None,
        json=None,
        params=None,
        verify=False,
    )


def test_http_client_patch_with_ssl_verification_disabled(mocker):
    patch_mock = mocker.patch("toolbox.api.http_client.requests.patch")
    http_client = HttpClient(verify_ssl=False)
    payload = {"test": "data"}

    response = http_client.patch(TEST_URL, json=payload)

    assert response is patch_mock.return_value
    patch_mock.assert_called_once_with(
        TEST_URL,
        headers=None,
        json=payload,
        params=None,
        verify=False,
    )


def test_http_client_with_valid_ssl_certificate():
    http_client_with_ssl = HttpClient(verify_ssl=True)
    response = http_client_with_ssl.get("https://httpbingo.org/get")
    assert response.status_code == 200

    http_client_without_ssl = HttpClient(verify_ssl=False)
    response = http_client_without_ssl.get("https://httpbingo.org/get")
    assert response.status_code == 200
