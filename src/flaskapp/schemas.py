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


# TODO: Change authentication to stop making LCS requests every time
# TODO: Handle email and token from path params as well as request body
def ensure_user_logged_in(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        data = request.get_json(force=True)
        if (
            not data
            or "user_email" not in data
            or not data["user_email"]
            or "token" not in data
            or not data["token"]
        ):
            return {"message": "Missing email or token"}, 408
        email = format_string(data["user_email"])
        token = data["token"]
        resp, status_code = call_validate_endpoint(email, token)
        if status_code != 200:
            return resp, status_code

        return func(*args, **kwargs)

    return wrapped
