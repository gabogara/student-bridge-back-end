from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required


from auth_middleware import token_required
from db_helpers import get_db_connection, consolidate_verifications_in_resources

resources_blueprint = Blueprint('hoots_blueprint', __name__)

@resources_blueprint.route("/resources", methods=["POST"])
@token_required
def create_resource():
    connection = get_db_connection()
    try:
        new_resource = request.get_json()
        creator_id = g.user["id"]

        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            INSERT INTO resources (created_by, title, description, category, address, city, lat, lng, requirements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                creator_id,
                new_resource["title"],
                new_resource.get("description"),
                new_resource["category"],
                new_resource["address"],
                new_resource["city"],
                new_resource["lat"],
                new_resource["lng"],
                new_resource.get("requirements"),
            ),
        )
        resource_id = cursor.fetchone()["id"]

        cursor.execute(
            """
            SELECT r.id,
                   r.created_by AS resource_author_id,
                   r.title,
                   r.description,
                   r.category,
                   r.address,
                   r.city,
                   r.lat,
                   r.lng,
                   r.requirements,
                   r.hidden_reason,
                   r.hidden_at,
                   r.created_at AS "createdAt",
                   r.updated_at AS "updatedAt",
                   u.username AS author_username
            FROM resources r
            JOIN users u ON r.created_by = u.id
            WHERE r.id = %s
            """,
            (resource_id,),
        )
        created_resource = cursor.fetchone()

        connection.commit()
        return jsonify(created_resource), 201

    except Exception as error:
        connection.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()


@resources_blueprint.route("/resources", methods=["GET"])
def resources_index():
    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            SELECT r.id,
                   r.created_by AS resource_author_id,
                   r.title,
                   r.description,
                   r.category,
                   r.address,
                   r.city,
                   r.lat,
                   r.lng,
                   r.requirements,
                   r.hidden_reason,
                   r.hidden_at,
                   r.created_at AS "createdAt",
                   r.updated_at AS "updatedAt",
                   u.username AS author_username,

                   v.id AS verification_id,
                   v.status AS verification_status,
                   v.note AS verification_note,
                   v.created_at AS "verificationCreatedAt",
                   u_v.username AS verification_author_username,
                   v.user_id AS verification_author_id

            FROM resources r
            INNER JOIN users u ON r.created_by = u.id
            LEFT JOIN verifications v ON r.id = v.resource_id
            LEFT JOIN users u_v ON v.user_id = u_v.id
            ORDER BY r.created_at DESC, v.created_at DESC
            """
        )

        rows = cursor.fetchall()
        consolidated = consolidate_verifications_in_resources(rows)
        return jsonify(consolidated), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()

@resources_blueprint.route("/resources/<int:resource_id>", methods=["GET"])
def show_resource(resource_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            SELECT r.id,
                   r.created_by AS resource_author_id,
                   r.title,
                   r.description,
                   r.category,
                   r.address,
                   r.city,
                   r.lat,
                   r.lng,
                   r.requirements,
                   r.hidden_reason,
                   r.hidden_at,
                   r.created_at AS "createdAt",
                   r.updated_at AS "updatedAt",
                   u.username AS author_username,

                   v.id AS verification_id,
                   v.status AS verification_status,
                   v.note AS verification_note,
                   v.created_at AS "verificationCreatedAt",
                   u_v.username AS verification_author_username,
                   v.user_id AS verification_author_id

            FROM resources r
            INNER JOIN users u ON r.created_by = u.id
            LEFT JOIN verifications v ON r.id = v.resource_id
            LEFT JOIN users u_v ON v.user_id = u_v.id
            WHERE r.id = %s
            ORDER BY v.created_at DESC
            """,
            (resource_id,),
        )

        rows = cursor.fetchall()
        if not rows:
            return jsonify({"error": "Resource not found"}), 404

        processed = consolidate_verifications_in_resources(rows)[0]
        return jsonify(processed), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()


@resources_blueprint.route("/resources/<int:resource_id>", methods=["PUT"])
@token_required
def update_resource(resource_id):
    connection = get_db_connection()
    try:
        updated = request.get_json()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM resources WHERE id = %s", (resource_id,))
        resource_to_update = cursor.fetchone()
        if resource_to_update is None:
            return jsonify({"error": "Resource not found"}), 404

        if resource_to_update["created_by"] != g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401

        cursor.execute(
            """
            UPDATE resources
            SET title = %s,
                description = %s,
                category = %s,
                address = %s,
                city = %s,
                lat = %s,
                lng = %s,
                requirements = %s,
                updated_at = NOW()
            WHERE id = %s
            RETURNING id
            """,
            (
                updated["title"],
                updated.get("description"),
                updated["category"],
                updated["address"],
                updated["city"],
                updated["lat"],
                updated["lng"],
                updated.get("requirements"),
                resource_id,
            ),
        )
        updated_id = cursor.fetchone()["id"]

        cursor.execute(
            """
            SELECT r.id,
                   r.created_by AS resource_author_id,
                   r.title,
                   r.description,
                   r.category,
                   r.address,
                   r.city,
                   r.lat,
                   r.lng,
                   r.requirements,
                   r.hidden_reason,
                   r.hidden_at,
                   r.created_at AS "createdAt",
                   r.updated_at AS "updatedAt",
                   u.username AS author_username
            FROM resources r
            JOIN users u ON r.created_by = u.id
            WHERE r.id = %s
            """,
            (updated_id,),
        )
        updated_resource = cursor.fetchone()

        connection.commit()
        return jsonify(updated_resource), 200

    except Exception as error:
        connection.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()