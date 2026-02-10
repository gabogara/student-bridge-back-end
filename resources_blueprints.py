from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

resources_blueprint = Blueprint('hoots_blueprint', __name__)

@resources_blueprint.route("/resources", methods=["GET"])
def resources_index():
    return jsonify({"message": "resorces index lives here"})
