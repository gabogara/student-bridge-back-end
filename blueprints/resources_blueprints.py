from flask import Blueprint, jsonify, request, g
import psycopg2, psycopg2.extras


from middleware.auth_middleware import token_required
from utils.db_helpers import get_db_connection, consolidate_verifications_in_resources
from utils.mapbox_helpers import geocode_address

resources_blueprint = Blueprint('resources_blueprint', __name__)


@resources_blueprint.route("/resources", methods=["POST"])
@token_required
def create_resource():
    print("create_resource hit")

    connection = get_db_connection()
    try:
        new_resource = request.get_json() or {}

        creator_id = g.user["id"]

        required = ["title", "category", "address", "city"]
        missing = [field for field in required if not new_resource.get(field)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        # --- Geocoding en BACKEND (Mapbox) ---
        coords = geocode_address(new_resource["address"], new_resource["city"])
        if coords is None:
            return jsonify({"error": "Address not found"}), 400
        lat, lng = coords
        print("geocoded coords:", lat, lng)

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
                lat,
                lng,
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

        print("RAW rows sample:", rows[:1])

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



# PUT /resources/:id
@resources_blueprint.route("/resources/<int:resource_id>", methods=["PUT"])
@token_required
def update_resource(resource_id):
    connection = get_db_connection()
    try:
        updated = request.get_json() or {}

        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM resources WHERE id = %s", (resource_id,))
        resource_to_update = cursor.fetchone()
        if resource_to_update is None:
            return jsonify({"error": "Resource not found"}), 404

        if resource_to_update["created_by"] != g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        
        required = ["title", "category", "address", "city"]
        missing = [field for field in required if not updated.get(field)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        # --- Geocoding (Mapbox)
        coords = geocode_address(updated["address"], updated["city"])
        if coords is None:
            return jsonify({"error": "Address not found"}), 400
        lat, lng = coords
        print("updated geocoded coords:", lat, lng)

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
                lat,
                lng,
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

# POST /resources/resource_id/saves
@resources_blueprint.route("/resources/<int:resource_id>/saves", methods=["POST"])
@token_required
def create_save(resource_id):
    connection = get_db_connection()
    try:
        user_id = g.user["id"]
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT id FROM resources WHERE id = %s", (resource_id,))
        resource = cursor.fetchone()
        if resource is None:
            return jsonify({"error": "Resource not found"}), 404

        cursor.execute(
            """
            INSERT INTO saves (resource_id, user_id)
            VALUES (%s, %s)
            ON CONFLICT (resource_id, user_id) DO NOTHING
            RETURNING id
            """,
            (resource_id, user_id),
        )

        inserted = cursor.fetchone()
        connection.commit()

        return jsonify({
            "saved": True,
            "resource_id": resource_id,
            "user_id": user_id,
            "save_id": inserted["id"] if inserted else None
        }), 201

    except Exception as error:
        connection.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()

# GET /saves
@resources_blueprint.route("/saves", methods=["GET"])
@token_required
def my_saves_index():
    connection = get_db_connection()
    try:
        user_id = g.user["id"]
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
                   s.created_at AS "savedAt"
            FROM saves s
            JOIN resources r ON s.resource_id = r.id
            JOIN users u ON r.created_by = u.id
            WHERE s.user_id = %s
            ORDER BY s.created_at DESC
            """,
            (user_id,),
        )

        rows = cursor.fetchall()
        return jsonify(rows), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()


@resources_blueprint.route("/resources/<int:resource_id>", methods=["DELETE"])
@token_required
def delete_resource(resource_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM resources WHERE id = %s", (resource_id,))
        resource_to_delete = cursor.fetchone()
        if resource_to_delete is None:
            return jsonify({"error": "Resource not found"}), 404

        if resource_to_delete["created_by"] != g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401

        cursor.execute("DELETE FROM resources WHERE id = %s", (resource_id,))

        connection.commit()
        return jsonify(resource_to_delete), 200

    except Exception as error:
        connection.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()