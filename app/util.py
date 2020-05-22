from flask import jsonify


def format_string(s):
    if not s:
        return []
    elements = s.split(",")
    for i in range(0, len(elements)):
        elements[i] = elements[i].strip().lower()
    return elements


def return_resp(code, body):
    resp = jsonify({"statusCode": code, "body": body})
    resp.status_code = code
    return resp
