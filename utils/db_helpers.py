import os
import psycopg2


def get_db_connection():
    connection = psycopg2.connect(
        host='localhost',
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USERNAME'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    return connection

def consolidate_verifications_in_resources(resources_with_verifications):
    consolidated_resources = []

    for row in resources_with_verifications:
        resource_exists = False

        for consolidated in consolidated_resources:
            if row["id"] == consolidated["id"]:
                resource_exists = True
                # si hay verificación, la agregamos
                if row["verification_id"] is not None:
                    consolidated["verifications"].append({
                        "verification_id": row["verification_id"],
                        "status": row["verification_status"],
                        "note": row["verification_note"],
                        "createdAt": row.get("verificationCreatedAt"),
                        "verification_author_username": row["verification_author_username"],
                        "verification_author_id": row["verification_author_id"],
                    })
                break

        if not resource_exists:
            row["verifications"] = []
            if row["verification_id"] is not None:
                row["verifications"].append({
                    "verification_id": row["verification_id"],
                    "status": row["verification_status"],
                    "note": row["verification_note"],
                    "createdAt": row.get("verificationCreatedAt"),
                    "verification_author_username": row["verification_author_username"],
                    "verification_author_id": row["verification_author_id"],
                })

            # limpiar campos "flat" (igual que hoot.pop...)
            row.pop("verification_id", None)
            row.pop("verification_status", None)
            row.pop("verification_note", None)
            row.pop("verification_author_username", None)
            row.pop("verification_author_id", None)
            row.pop("verificationCreatedAt", None)

            consolidated_resources.append(row)

    return consolidated_resources