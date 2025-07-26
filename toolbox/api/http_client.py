import requests
from typing import Optional, Dict, Any


class HttpClient:
    """
    Centralized HTTP client that wraps requests and manages SSL verification.
    """

    def __init__(self, verify_ssl: bool = True):
        self.verify_ssl = verify_ssl

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a GET request with SSL verification control."""
        return requests.get(url, headers=headers, params=params, verify=self.verify_ssl)

    def post(self, url: str, headers: Optional[Dict[str, str]] = None, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a POST request with SSL verification control."""
        return requests.post(url, headers=headers, json=json, params=params, verify=self.verify_ssl)

    def put(self, url: str, headers: Optional[Dict[str, str]] = None, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a PUT request with SSL verification control."""
        return requests.put(url, headers=headers, json=json, params=params, verify=self.verify_ssl)

    def delete(self, url: str, headers: Optional[Dict[str, str]] = None, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a DELETE request with SSL verification control."""
        return requests.delete(url, headers=headers, json=json, params=params, verify=self.verify_ssl)

    def patch(self, url: str, headers: Optional[Dict[str, str]] = None, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a PATCH request with SSL verification control."""
        return requests.patch(url, headers=headers, json=json, params=params, verify=self.verify_ssl)
