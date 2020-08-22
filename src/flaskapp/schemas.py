from flask import request
from functools import wraps
from jsonschema import Draft4Validator

import src.flaskapp.config as config
from src.flaskapp.lcs import call_validate_endpoint
from src.flaskapp.util import format_string


def ensure_feature_is_enabled(feature):
    def inner(fn):
        @wraps(fn)
        def wrapper():
            if config.ENABLE_FEATURE[feature] == 1:
                return fn()
            elif config.ENABLE_FEATURE[feature] == 0:
                return {"message": "Feature is disabled"}, 501
            else:
                return {"message": "Wrong Feature value"}, 502

        return wrapper

    return inner


def ensure_json():
    validator = Draft4Validator({"type": "object"})

    def wrapper(fn):
        @wraps(fn)
        def wrapped():
            test_input = request.get_json(force=True)
            errors = [error.message for error in validator.iter_errors(test_input)]
            if errors:
                return {"message": "Invalid Json"}, 505
            else:
                return fn()

        return wrapped

    return wrapper


def ensure_user_logged_in():
    def wrapper(fn):
        @wraps(fn)
        def wrapped():
            # data = request.get_json(force=True)
            # if (
            #     not data
            #     or "user_email" not in data
            #     or not data["user_email"]
            #     or "token" not in data
            #     or not data["token"]
            # ):
            #     return {"message": "Missing email or token"}, 408
            email = data["user_email"]
            # token = data["token"]
            email = format_string(email)
            if call_validate_endpoint(email, token) != 200:
                return {"message": "Invalid request"}, 404
            else:
                return fn()

        return wrapped

    return wrapper
