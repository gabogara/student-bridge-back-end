from flask import Flask, jsonify, g
from flask_cors import CORS
import os
import psycopg2
import psycopg2.extras
from auth_middleware import token_required
from auth_blueprint import authentication_blueprint
from resources_blueprints import resources_blueprint

app = Flask(__name__)
CORS(app)
app.register_blueprint(authentication_blueprint)
app.register_blueprint(resources_blueprint)



from db_helpers import get_db_connection

@app.route('/')
def index():
    return "Hello world"

@app.route('/users')
@token_required
def users_index():
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT id, username FROM users;")
    users = cursor.fetchall()
    connection.close()
    return jsonify(users), 200


@app.route("/users/<int:user_id>")
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


app.run(debug=True, port=5001)
