from flask import Blueprint
from middleware.auth_middleware import token_required
import psycopg2.extras
from flask import jsonify, g
from utils.db_helpers import get_db_connection

users_blueprint = Blueprint("users_blueprint", __name__)

@users_blueprint.route("/users", methods=["GET"])
@token_required
def users_index():
    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT id, username FROM users;")
        users = cursor.fetchall()
        return jsonify(users), 200
    finally:
        connection.close()


@users_blueprint.route("/users/<int:user_id>", methods=["GET"])
@token_required
def users_show(user_id):
    # auth ownership
    if user_id != g.user["id"]:
        return jsonify({"err": "Unauthorized"}), 403

    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT id, username FROM users WHERE id = %s;", (user_id,))
        user = cursor.fetchone()
        if user is None:
            return jsonify({"err": "User not found"}), 404
        return jsonify(user), 200
    finally:
        connection.close()