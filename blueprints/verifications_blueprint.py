from flask import Blueprint, jsonify, request, g
from utils.db_helpers import get_db_connection
import psycopg2.extras
from middleware.auth_middleware import token_required

verifications_blueprint = Blueprint("verifications_blueprint", __name__)

# POST /resources/resource_id/verifications
@verifications_blueprint.route("/resources/<int:resource_id>/verifications", methods=["POST"])
@token_required
def create_verification(resource_id):
    connection = get_db_connection()
    try:
        data = request.get_json() or {}
        author_id = g.user["id"]

        required = ["status", "note"]
        missing = [field for field in required if not data.get(field)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
        
        allowed_statuses = [
            "Active",
            "Temporarily Closed",
            "No Longer Available",
            "Info Needs Update",
        ]
        if data["status"] not in allowed_statuses:
            return jsonify({"error": "Invalid status"}), 400

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


# PUT /resources/resource_id/verifications/verifications_id
@verifications_blueprint.route("/resources/<int:resource_id>/verifications/<int:verification_id>", methods=["PUT"])
@token_required
def update_verification(resource_id, verification_id):
    connection = get_db_connection()
    try:
        data = request.get_json() or {}
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        required = ["status", "note"]
        missing = [field for field in required if not data.get(field)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        allowed_statuses = [
            "Active",
            "Temporarily Closed",
            "No Longer Available",
            "Info Needs Update",
        ]
        if data["status"] not in allowed_statuses:
            return jsonify({"error": "Invalid status"}), 400

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
            RETURNING id
            """,
            (data["status"], data["note"], verification_id, resource_id),
        )

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
        updated = cursor.fetchone()

        connection.commit()
        return jsonify(updated), 200

    except Exception as error:
        connection.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()



# DELETE /resources/resource_id/verifications/verifications_id
@verifications_blueprint.route("/resources/<int:resource_id>/verifications/<int:verification_id>", methods=["DELETE"],
)
@token_required
def delete_verification(resource_id, verification_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Validate that it exists and belongs to that resource_id
        cursor.execute(
            "SELECT * FROM verifications WHERE id = %s AND resource_id = %s",
            (verification_id, resource_id),
        )
        verification_to_delete = cursor.fetchone()
        if verification_to_delete is None:
            return jsonify({"error": "Verification not found"}), 404

        # 2) Validate ownership
        if verification_to_delete["user_id"] != g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401

        cursor.execute(
            "DELETE FROM verifications WHERE id = %s AND resource_id = %s",
            (verification_id, resource_id),
        )

        connection.commit()
        return jsonify({"message": "Verification deleted successfully"}), 200

    except Exception as error:
        connection.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()
