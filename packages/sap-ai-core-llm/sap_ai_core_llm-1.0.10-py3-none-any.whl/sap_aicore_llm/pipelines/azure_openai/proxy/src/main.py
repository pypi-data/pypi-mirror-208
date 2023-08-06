import os
import requests
import json
from flask import Flask
from flask import request as call_request
from requests.exceptions import HTTPError

config = {}
config["AZURE_API_KEY"] = os.getenv("AzureAPIKey")
config["AZURE_API_URL"] = os.getenv("AzureDeploymentURL")

# Creates Flask serving engine
app = Flask(__name__)

@app.after_request
def apply_security_headers(response):
    headers = get_security_headers()
    for key, value in headers.items():
        response.headers[key] = value
    return response

def get_security_headers():
    headers = {
        "Content-Type": "application/json",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff"
    }
    return headers

@app.errorhandler(HTTPError)
def handle_http_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # replace the body with JSON
    response = {
        "status_code": e.response.status_code,
        "error": f"{type(e).__name__}: {e.response.text}"
    }
 
    response_data = sanitize_json(json.dumps(response))
    return response_data, e.response.status_code, get_security_headers()


@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for errors."""
    response = {
        "status_code": 500,
        "error": f"{type(e).__name__}: {str(e)}"
    }
 
    response_data = sanitize_json(json.dumps(response))
    return response_data, 500, get_security_headers()

def sanitize_json(json_string):
    s = json_string.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s

@app.route("/v1/predict", methods=["POST"])
def predict():
    global config

    payload = json.dumps(call_request.get_json())

    headers = {
        "api-key": str(config['AZURE_API_KEY']),
        "Content-Type": "application/json"
    }

    response = requests.post(config["AZURE_API_URL"], headers=headers, data=payload)

    response.raise_for_status()

    response_data = sanitize_json(json.dumps(response.json()))
    return response_data, 200, get_security_headers()