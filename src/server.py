from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg

app = Flask(__name__)
CORS(app)

# Connect to the PostgreSQL database

try:
    conn = psycopg.connect("dbname=ridam user=postgres password=Singh@786")
    print("✅ Connection successful")
except Exception as e:
    print("❌ Connection failed:", e)
cur = conn.cursor()

@app.route("/", methods=["POST"])
def register():
    data = request.get_json()
    print("Raw incoming data:", data)

    try:
        # Clean input values
        name = data.get("name", "")
        frequency = data.get("Frequency", "").lower()
        extension = data.get("Extension", "").replace(".", "").lower()
        projections = data.get('Projections', '').upper()
        paused = data.get("Paused", "False") == "True"
        rgb = data.get("RGB", "False") == "True"
        category = data.get("Category", "False") == "True"
        band_info = data.get("BandInfo")
        aux_data = data.get("AuxData")
        remarks = data.get("Remarks")
        tags = [t.strip() for t in data.get("Tags", "").split(",") if t.strip()]
        theme_id = data.get("ThemeID")
        sub_theme_id = data.get("SubThemeID")
        metadata = data.get("metadata", [])

        # Insert into DB
        cur.execute("""
            INSERT INTO datasets (
                name, frequency, extension, projections,
                paused, rgb, category,
                band_info, aux_data, remarks, tags,
                theme_id, sub_theme_id, metadata
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            name, frequency, extension, projections,
            paused, rgb, category,
            band_info, aux_data, remarks, tags,
            theme_id, sub_theme_id, metadata
        ))

        inserted_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"id": inserted_id}), 201

    except Exception as e:
        conn.rollback()
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
