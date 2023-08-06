"""Provide API client."""

import sys
from typing import Optional, Tuple, Dict, Any

import requests

from spotter.storage import Storage
from spotter.utils import get_current_cli_version


class ApiClient:
    """A client interface for interacting with the API."""

    DEFAULT_ENDPOINT = "https://api.spotter.steampunk.si/api"
    DEFAULT_HEADERS = {
        "Accept": "application/json",
        "User-Agent": f"steampunk-spotter/{get_current_cli_version()}"
    }
    DEFAULT_TIMEOUT = 10

    def __init__(self, base_url: str, storage: Storage, api_token: Optional[str], username: Optional[str],
                 password: Optional[str]):
        """
        Construct ApiClient object.

        :param base_url: Base API endpoint url
        :param storage: Storage object, where tokens are stored
        :param username: Username
        :param password: Password
        """
        self._base_url = base_url.rstrip("/")
        self._storage = storage
        self._api_token = api_token
        self._username = username
        self._password = password

        self._storage_tokens_path = "tokens" if self._storage.exists("tokens") else "tokens.json"
        if self._storage_tokens_path == "tokens":
            self._old_tokens_fallback()

    def _url(self, path: str) -> str:
        """
        Construct the full API endpoint URL based on the base path.

        :return: Full API endpoint URL based on the base path
        """
        return self._base_url + path

    def _check_auth_status(self) -> None:
        """Check if user is logged (if file with tokens exists in the storage)."""
        if not self._storage.exists(self._storage_tokens_path):
            print("You are not logged in!\nTo log in, you should provide your API token or username and password:\n\n"
                  "    - using spotter login command;\n"
                  "    - via --api-token/-t optional argument;\n"
                  "    - by setting SPOTTER_API_TOKEN environment variable;\n"
                  "    - via --username/-u and --password/-p optional arguments;\n"
                  "    - by setting SPOTTER_USERNAME and SPOTTER_PASSWORD environment variables.\n", file=sys.stderr)
            sys.exit(2)

    def _get_endpoint_tokens(self) -> Dict[str, str]:
        """
        Retrieve tokens for particular API endpoint from storage.

        :return: Dict with tokens
        """
        self._check_auth_status()

        tokens = self._storage.read_json(self._storage_tokens_path)
        endpoint_tokens = tokens.get(self._base_url, {})

        if not endpoint_tokens:
            print(f"Error: No {self._base_url} endpoint in {self._storage.path / self._storage_tokens_path}.",
                  file=sys.stderr)
            sys.exit(2)

        if not isinstance(endpoint_tokens, dict):
            print(f"Error: The {self._base_url} JSON entry from {self._storage.path / self._storage_tokens_path} "
                  f"should be of type dict, but is '{type(endpoint_tokens)}'.", file=sys.stderr)
            sys.exit(2)

        return endpoint_tokens

    def _get_api_token(self) -> Optional[str]:
        """
        Retrieve API token from storage.

        :return: API token as string
        """
        endpoint_tokens = self._get_endpoint_tokens()

        if not endpoint_tokens:
            print(f"Error: No {self._base_url} endpoint in {self._storage.path / self._storage_tokens_path}.",
                  file=sys.stderr)
            sys.exit(2)

        if not isinstance(endpoint_tokens, dict):
            print(f"Error: The {self._base_url} JSON entry from {self._storage.path / self._storage_tokens_path} "
                  f"should be of type dict, but is '{type(endpoint_tokens)}'.", file=sys.stderr)
            sys.exit(2)

        return endpoint_tokens.get("api_token", None)

    def _get_access_refresh_tokens(self) -> Tuple[str, str]:
        """
        Retrieve access and refresh token from storage.

        :return: Tokens as tuple of strings (access token, refresh token)
        """
        endpoint_tokens = self._get_endpoint_tokens()

        access_token = endpoint_tokens.get("access", None)
        refresh_token = endpoint_tokens.get("refresh", None)

        if not access_token:
            print(f"Error: No access token in {self._storage.path / self._storage_tokens_path}.", file=sys.stderr)
            sys.exit(2)
        if not refresh_token:
            print(f"Error: No refresh token in {self._storage.path / self._storage_tokens_path}.", file=sys.stderr)
            sys.exit(2)

        return access_token, refresh_token

    def _old_tokens_fallback(self) -> None:
        """Execute a fallback mechanism to ensure that users with old tokens path have the same JSON tokens format."""
        tokens = self._storage.read_json(self._storage_tokens_path)

        access_token = tokens.get("access", None)
        refresh_token = tokens.get("refresh", None)

        if self._base_url not in tokens and access_token and refresh_token:
            self._storage.write_json({self._base_url: tokens}, self._storage_tokens_path)

    def _update_endpoint_tokens(self, updated_tokens: Dict[Any, Any]) -> None:
        """
        Update tokens from storage for particular API endpoint.

        :param updated_tokens: Tokens to be updated as dict that will update the existing JSON from storage
        """
        endpoint_tokens = {}
        if self._storage.exists(self._storage_tokens_path):
            tokens = self._storage.read_json(self._storage_tokens_path)
            endpoint_tokens = tokens.get(self._base_url, {})

        endpoint_tokens.update(updated_tokens)
        self._storage.update_json({self._base_url: endpoint_tokens}, self._storage_tokens_path)

    def login(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """
        Login user to the API using API token or username and password, also verify and store auth tokens to storage.

        Note that we do not use self._request to prevent possible cyclic recursion errors.

        :param timeout: Request timeout
        """
        request_headers = self.DEFAULT_HEADERS.copy()
        updated_auth_tokens = {}

        if self._api_token:
            request_headers.update({"Authorization": f"SPTKN {self._api_token}"})
            updated_auth_tokens.update({"api_token": self._api_token})
        else:
            # old login - generate access and refresh token
            response = requests.post(self._url("/v2/token/"), headers=request_headers,
                                     json={"username": self._username, "password": self._password}, timeout=timeout)
            if response.ok:
                updated_auth_tokens.update(response.json())
                access_token = response.json().get("access", None)
                request_headers.update({"Authorization": f"Bearer {access_token}"})
            else:
                print(self.format_api_error(response), file=sys.stderr)
                sys.exit(2)

        # verify auth tokens and save them to storage
        response = requests.get(self._url("/v3/auth/verify/"), headers=request_headers, timeout=timeout)
        if response.ok:
            self._update_endpoint_tokens(updated_auth_tokens)
        else:
            print(self.format_api_error(response), file=sys.stderr)
            sys.exit(2)

    def _refresh_login(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """
        Login user to the API using the tokens (access and refresh token) from storage.

        :param timeout: Request timeout
        """
        # get existing tokens and then refresh access token and save it to local storage
        # note that we do not use self._request to prevent possible cyclic recursion errors
        _, refresh_token = self._get_access_refresh_tokens()
        response_token_refresh = requests.post(self._url("/v2/token/refresh/"), headers=self.DEFAULT_HEADERS.copy(),
                                               json={"refresh": refresh_token}, timeout=timeout)
        if response_token_refresh.ok:
            refreshed_access_token = response_token_refresh.json().get("access", None)
            if not refreshed_access_token:
                print("Error: Refreshing access token failed.", file=sys.stderr)
                sys.exit(2)

            access_token = refreshed_access_token
            self._storage.update_json({
                self._base_url: {
                    "access": access_token,
                    "refresh": refresh_token
                }
            }, self._storage_tokens_path)
        else:
            print(self.format_api_error(response_token_refresh), file=sys.stderr)
            sys.exit(2)

    def logout(self) -> None:
        """Logout user - remove tokens for the current API endpoint from storage."""
        self._check_auth_status()

        tokens = self._storage.read_json(self._storage_tokens_path)
        endpoint_tokens = tokens.pop(self._base_url, None)
        if endpoint_tokens:
            self._storage.write_json(tokens, self._storage_tokens_path)
        else:
            print(f"You are already logged out because there is no {self._base_url} endpoint "
                  f"in {self._storage.path / self._storage_tokens_path}.", file=sys.stderr)
            sys.exit(0)

    # pylint: disable=too-many-arguments,too-many-branches,too-many-locals
    def _request(self, method: str, path: str, authorize: Optional[bool] = True,
                 headers: Optional[Dict[str, str]] = None, payload: Optional[Dict[str, Any]] = None,
                 timeout: int = DEFAULT_TIMEOUT, allow_auth_retry: bool = True,
                 ignore_response_status_codes: Optional[bool] = False) -> requests.Response:
        """
        Send HTTP request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param payload: Request payload (JSON payload dict)
        :param timeout: Request timeout
        :param allow_auth_retry: Whether to allow reauthenticating and retrying the request
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        # initiate login from start if API token or username and password have been provided and tokens do not exist yet
        if (self._api_token or (self._username and self._password)) and not self._storage.exists(
                self._storage_tokens_path):
            self._storage.remove(self._storage_tokens_path)
            self.login()

        # initiate login from start if endpoint does not exist in tokens
        if self._storage.exists(self._storage_tokens_path):
            tokens = self._storage.read_json(self._storage_tokens_path)
            endpoint_tokens = tokens.get(self._base_url, None)
            if not endpoint_tokens:
                self.login()

        # combine request headers (default + authorization + others)
        request_headers = self.DEFAULT_HEADERS.copy()
        if authorize:
            api_token = self._api_token or self._get_api_token()
            if api_token:
                request_headers.update({"Authorization": f"SPTKN {api_token}"})
            else:
                access_token, _ = self._get_access_refresh_tokens()
                request_headers.update({"Authorization": f"Bearer {access_token}"})
        request_headers.update(headers if headers is not None else {})

        # try to make a request
        try:
            response = requests.request(
                method, self._url(path),
                headers=request_headers, json=payload if payload is not None else {}, timeout=timeout
            )
        except requests.exceptions.RequestException as e:
            print(f"API error: {str(e)}", file=sys.stderr)
            sys.exit(2)

        # if request fails for one time try to log in and make a request again
        if not self._api_token and response.status_code == 401:
            if allow_auth_retry:
                self._refresh_login(timeout)
                # retry, but don't allow any more auth retries
                return self._request(method, path, authorize, headers, payload, timeout, allow_auth_retry=False,
                                     ignore_response_status_codes=ignore_response_status_codes)

            print("Request error after reauthenticating.", file=sys.stderr)
            sys.exit(2)
        else:
            # just return the response no matter what the response status code is
            if ignore_response_status_codes:
                return response
            # check if response is ok and can be converted to JSON
            if response.ok:
                try:
                    response.json()
                    return response
                except ValueError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(2)
            else:
                print(self.format_api_error(response), file=sys.stderr)
                sys.exit(2)

    def get(self, path: str, authorize: Optional[bool] = True, headers: Optional[Dict[str, str]] = None,
            timeout: int = DEFAULT_TIMEOUT, ignore_response_status_codes: Optional[bool] = False) -> requests.Response:
        """
        Send GET request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param timeout: Request timeout
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        return self._request("GET", path, authorize=authorize, headers=headers, timeout=timeout,
                             ignore_response_status_codes=ignore_response_status_codes)

    def post(self, path: str, authorize: Optional[bool] = True, headers: Optional[Dict[str, str]] = None,
             payload: Optional[Dict[str, Any]] = None, timeout: int = DEFAULT_TIMEOUT,
             ignore_response_status_codes: Optional[bool] = False) -> requests.Response:
        """
        Send POST request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param payload: Request payload (JSON payload dict)
        :param timeout: Request timeout in seconds
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        return self._request("POST", path, authorize=authorize, headers=headers, payload=payload, timeout=timeout,
                             ignore_response_status_codes=ignore_response_status_codes)

    def patch(self, path: str, authorize: Optional[bool] = True, headers: Optional[Dict[str, str]] = None,
              payload: Optional[Dict[str, Any]] = None, timeout: int = DEFAULT_TIMEOUT,
              ignore_response_status_codes: Optional[bool] = False) -> requests.Response:
        """
        Send PATCH request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param payload: Request payload (JSON payload dict)
        :param timeout: Request timeout in seconds
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        return self._request("PATCH", path, authorize=authorize, headers=headers, payload=payload, timeout=timeout,
                             ignore_response_status_codes=ignore_response_status_codes)

    def put(self, path: str, authorize: Optional[bool] = True, headers: Optional[Dict[str, str]] = None,
            payload: Optional[Dict[str, Any]] = None, timeout: int = DEFAULT_TIMEOUT,
            ignore_response_status_codes: Optional[bool] = False) -> requests.Response:
        """
        Send PUT request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param payload: Request payload (JSON payload dict)
        :param timeout: Request timeout in seconds
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        return self._request("PUT", path, authorize=authorize, headers=headers, payload=payload, timeout=timeout,
                             ignore_response_status_codes=ignore_response_status_codes)

    def delete(self, path: str, authorize: Optional[bool] = True, headers: Optional[Dict[str, str]] = None,
               timeout: int = DEFAULT_TIMEOUT,
               ignore_response_status_codes: Optional[bool] = False) -> requests.Response:
        """
        Send DELETE request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param timeout: Request timeout in seconds
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        return self._request("DELETE", path, authorize=authorize, headers=headers, timeout=timeout,
                             ignore_response_status_codes=ignore_response_status_codes)

    def format_api_error(self, response: requests.Response) -> str:
        """
        Format API error.

        :param response: Response object
        :return: Formatted API error as string
        """
        try:
            try:
                return f"API error: {response.status_code} - {response.json()['message']}"
            except KeyError:
                return f"API error: {response.status_code} - {response.json()['detail']}"
        except (ValueError, KeyError):
            return f"API error: {response.status_code}"
