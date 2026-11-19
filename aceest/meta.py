"""Release metadata: /version shows which build is serving a request.

Used to observe rolling updates, blue-green switches, canary splits and A/B
routing, because every response also carries an X-App-Version header.
"""
from flask import Blueprint, current_app, jsonify

bp = Blueprint("meta", __name__)


@bp.get("/version")
def version():
    return jsonify(
        app="aceest-fitness",
        version=current_app.config["APP_VERSION"],
        features=current_app.config["APP_MODULES"],
    ), 200


@bp.after_app_request
def add_version_header(response):
    response.headers["X-App-Version"] = current_app.config["APP_VERSION"]
    return response
