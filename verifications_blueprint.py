from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2.extras
from auth_middleware import token_required

verifications_blueprint = Blueprint("verifications_blueprint", __name__)

@verifications_blueprint.route("/resources/<int:resource_id>/verifications", methods=["POST"])
@token_required
def create_verification(resource_id):
    connection = get_db_connection()
    try:
        data = request.get_json()
        author_id = g.user["id"]

        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            INSERT INTO verifications (resource_id, user_id, status, note)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (resource_id, author_id, data["status"], data["note"]),
        )
        verification_id = cursor.fetchone()["id"]

        cursor.execute(
            """
            SELECT v.id AS verification_id,
                   v.status,
                   v.note,
                   v.created_at AS "createdAt",
                   v.user_id AS verification_author_id,
                   u.username AS verification_author_username
            FROM verifications v
            JOIN users u ON v.user_id = u.id
            WHERE v.id = %s
            """,
            (verification_id,),
        )
        created = cursor.fetchone()

        connection.commit()
        return jsonify(created), 201

    except Exception as error:
        connection.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()


@verifications_blueprint.route("/resources/<int:resource_id>/verifications/<int:verification_id>", methods=["PUT"])
@token_required
def update_verification(resource_id, verification_id):
    connection = get_db_connection()
    try:
        data = request.get_json()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            "SELECT * FROM verifications WHERE id = %s AND resource_id = %s",
            (verification_id, resource_id),
        )
        verification_to_update = cursor.fetchone()
        if verification_to_update is None:
            return jsonify({"error": "Verification not found"}), 404

        if verification_to_update["user_id"] != g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401

        cursor.execute(
            """
            UPDATE verifications
            SET status = %s, note = %s
            WHERE id = %s AND resource_id = %s
            RETURNING *
            """,
            (data["status"], data["note"], verification_id, resource_id),
        )
        updated = cursor.fetchone()

        connection.commit()
        return jsonify({"verification": updated}), 200

    except Exception as error:
        connection.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()