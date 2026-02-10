from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

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
    return jsonify({"message": "resorces index lives here"})
