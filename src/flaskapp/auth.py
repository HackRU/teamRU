from functools import wraps
import requests
import jwt
from flask import request

import src.flaskapp.config as config
from src.flaskapp.util import format_string


def call_validate_endpoint(token):
    payload = {"token": token}
    resp = requests.post(f"{config.LCS_BASE_URL}/validate", json=payload)
    resp_parsed = resp.json()
    status_code = resp_parsed["statusCode"]
    if resp_parsed["statusCode"] != 200:
        # {"statusCode":400,"body":"User email not found."}
        # {"statusCode": 403, "body": "Permission denied"}
        return {"message": f'LCS Error: {resp_parsed["body"]}'}, status_code

    return {"message": "Successfully authenticated"}, 200


# Nice to have: Change authentication to stop making LCS requests every time
def authenticate(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.headers.get("token")
        if not token:
            return {"message": "Missing token"}, 401

        resp, status_code = call_validate_endpoint(token)
        if status_code != 200:
            return resp, status_code

        try:
            decoded_payload = jwt.decode(token, verify=False)
        except jwt.exceptions.InvalidTokenError as err:
            return {"message": f"Failed to decode JWT: {err}"}, 400

        if "email" not in decoded_payload:
            return {"message": "JWT does not contain email field"}, 400

        email = format_string(decoded_payload["email"])

        return func(email, *args, **kwargs)

    return wrapped
