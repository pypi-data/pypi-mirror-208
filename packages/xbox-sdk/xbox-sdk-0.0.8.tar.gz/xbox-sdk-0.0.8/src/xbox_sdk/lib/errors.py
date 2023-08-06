import requests
from requests import Response


class AuthorizationError(Exception):
    def __init__(self):
        super().__init__()


def assert_response_is_ok(response: Response):
    if response.status_code == 401:
        raise AuthorizationError
    if not response.ok:
        code = response.status_code
        reason = response.reason
        url = response.url
        raise requests.RequestException(f"[{code} Error]: {reason} ({url})")


def assert_response_is_json(response: Response):
    headers = response.headers
    if 'Content-Type' not in headers and 'application/json' not in headers['Content-Type']:
        raise requests.RequestException(f"[JSON Error]: The response did not reply in JSON format ({response.url})")


def assert_response_is_xapi_data(response: Response):
    data = response.json()
    if 'status' not in data:
        message = f"[XAPI Data Error]: Response data does not match XAPI's data standard ({response.url})"
        hint = "[Hint]: Data must be a JSON with keys containing ['status', (optional) 'message', (optional) 'data']"
        raise requests.RequestException(f"{message}\n{hint}")


def assert_success(response: Response):
    assert_response_is_ok(response)
    assert_response_is_json(response)
    #assert_response_is_xapi_data(response)
    data = response.json()

    #if data['status'] != 'success':
    #    raise requests.RequestException(f"[XAPI Error]: {data['message']} ({response.url})")
