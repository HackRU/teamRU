import jwt
from flask import request
from functools import wraps
from jsonschema import Draft4Validator

import src.flaskapp.config as config
from src.flaskapp.lcs import call_validate_endpoint
from src.flaskapp.util import format_string


def ensure_feature_is_enabled(feature):
    def inner_decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if config.ENABLE_FEATURE[feature]:
                return func(*args, **kwargs)
            else:
                return {"message": "Feature is disabled"}, 501

        return wrapped

    return inner_decorator


validator = Draft4Validator({"type": "object"})


def ensure_json(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        test_input = request.get_json(force=True)
        errors = [error.message for error in validator.iter_errors(test_input)]
        if errors:
            return {"message": "Invalid Json"}, 422
        else:
            return func(*args, **kwargs)

    return wrapped


# TODO: Change authentication to stop making LCS requests every time (long term goal)
def ensure_user_logged_in(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.headers.get("token")
        if not token:
            return {"message": "Missing token"}, 401

        # resp, status_code = call_validate_endpoint(token)
        # if status_code != 200:
        #     return resp, status_code

        try:
            decoded_payload = jwt.decode(token, verify=False)
        except jwt.exceptions.InvalidTokenError as err:
            return {"message": "Failed to decode JWT"}, 400

        email = decoded_payload["email"]

        return func(email, *args, **kwargs)

    return wrapped
