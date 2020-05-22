from functools import wraps
from flask import request
from jsonschema import Draft4Validator
from app.util import return_resp
from app.lcs import call_validate_endpoint
import app.config as config


def ensure_feature_is_enabled(feature):
    def inner(fn):
        def wrapper():
            if config.ENABLE_FEATURE[feature] == 1:
                return fn()
            elif config.ENABLE_FEATURE[feature] == 0:
                return return_resp(501, "Feature is disabled")
            else:
                return return_resp(502, "Wrong Feature value")
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
                return return_resp(505, "Invalid Json")
            else:
                return fn()
        return wrapped
    return wrapper


def ensure_user_logged_in():
    def wrapper(fn):
        @wraps(fn)
        def wrapped():
            data = request.get_json(force=True)
            if not data or 'user_email' not in data or not data['user_email'] or 'token' not in data or not data['token']:
                return return_resp(408, "Missing email or token")
            email = data['user_email']
            token = data['token']
            email = email.strip().lower()
            if call_validate_endpoint(email, token) != 200:
                return return_resp(404, "Invalid request")
            else:
                return fn()
        return wrapped
    return wrapper
