from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg
from psycopg import sql
import json

app = Flask(__name__)
CORS(app)

# ──────────────────────────────────────────────────────────
# DB CONNECTION (update password before running!)
# ──────────────────────────────────────────────────────────
try:
    conn = psycopg.connect(
        "dbname=ridam user=postgres password=Singh@786",
        autocommit=False,
    )
    cur = conn.cursor()
    print("✅  PostgreSQL connection established")
except Exception as e:
    print("❌  Connection failed:", e)
    raise

# ──────────────────────────────────────────────────────────
# FIELD MAP  UI‑label → SQL identifier or JSON path
# ──────────────────────────────────────────────────────────
FIELD_MAP = {
    "Name":          sql.Identifier("name"),
    "Frequency":     sql.Identifier("frequency"),
    "Extension":     sql.Identifier("extension"),
    "Projections":   sql.Identifier("projections"),
    "Paused":        sql.Identifier("paused"),
    "RGB":           sql.Identifier("rgb"),
    "Category":      sql.Identifier("category"),
    "Band Info":     sql.Identifier("band_info"),
    "Aux Data":      sql.Identifier("aux_data"),
    "Remarks":       sql.Identifier("remarks"),
    "Tags":          sql.Identifier("tags"),
    "Theme ID":      sql.Identifier("theme_id"),
    "Sub-Theme ID":  sql.Identifier("sub_theme_id"),

    # metadata JSONB paths
    "Location":          sql.SQL("metadata ->> 'Location'"),
    "City":              sql.SQL("metadata ->> 'City'"),
    "Contact Person":    sql.SQL("metadata ->> 'Contact_Person'"),
    "Organization":      sql.SQL("metadata ->> 'Organization'"),
    "Mailing Address":   sql.SQL("metadata ->> 'Mailing_Address'"),
    "Country":           sql.SQL("metadata ->> 'Country'"),
    "Contact Telephone": sql.SQL("metadata ->> 'Contact_Telephone'"),
}

def map_field(label: str) -> sql.SQL:
    if label not in FIELD_MAP:
        raise ValueError(f"Unknown field: {label}")
    return FIELD_MAP[label]

# ──────────────────────────────────────────────────────────
# ROUTE DISPATCHER
# ──────────────────────────────────────────────────────────
@app.route("/", methods=["POST"])
def handle_request():
    data = request.get_json(force=True)
    match data.get("type"):
        case "register":
            return handle_register(data)
        case "manage":
            return handle_manage(data)
        case "dashboard":
            return handle_dashboard()
        case _:
            return jsonify({"status": "error", "message": "Unknown request type"}), 400

# ──────────────────────────────────────────────────────────
# REGISTER HANDLER
# ──────────────────────────────────────────────────────────
def handle_register(data: dict):
    try:
        record = {
            "name":         data.get("name", ""),
            "frequency":    data.get("Frequency", "").lower(),
            "extension":    data.get("Extension", "").lstrip(".").lower(),
            "projections":  data.get("Projections", "").upper(),
            "paused":       data.get("Paused", "False") == "True",
            "rgb":          data.get("RGB", "False") == "True",
            "category":     data.get("Category", "False") == "True",
            "band_info":    data.get("BandInfo"),
            "aux_data":     data.get("AuxData"),
            "remarks":      data.get("Remarks"),
            "tags":         [t.strip() for t in data.get("Tags", "").split(",") if t.strip()],
            "theme_id":     data.get("ThemeID"),
            "sub_theme_id": data.get("SubThemeID"),
            "metadata":     json.dumps(data.get("metadata", {})),
        }

        cur.execute(
            """
            INSERT INTO datasets (
              name, frequency, extension, projections,
              paused, rgb, category, band_info, aux_data, remarks, tags,
              theme_id, sub_theme_id, metadata
            ) VALUES (
              %(name)s, %(frequency)s, %(extension)s, %(projections)s,
              %(paused)s, %(rgb)s, %(category)s, %(band_info)s, %(aux_data)s,
              %(remarks)s, %(tags)s, %(theme_id)s, %(sub_theme_id)s, %(metadata)s
            ) RETURNING id
            """,
            record,
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"status": "success", "id": new_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# ──────────────────────────────────────────────────────────
# MANAGE HANDLER (dynamic SELECT)
# ──────────────────────────────────────────────────────────
def handle_manage(data: dict):
    view_entries = data.get("viewEntries", [])
    sort_entries = data.get("sortEntries", [])

    try:
        select_clause = sql.SQL("*") if not view_entries else sql.SQL(", ").join(map_field(e["field"]) for e in view_entries)

        where_sql = sql.SQL("")
        params: list = []
        if sort_entries:
            conds = []
            for e in sort_entries:
                field_sql = map_field(e["field"])
                val = e["value"]
                conds.append(sql.SQL("{} = %s").format(field_sql))
                params.append(val.lower() == "true" if e["field"] in ("Paused", "RGB", "Category") else val)
            where_sql = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conds)

        query = sql.SQL("SELECT {fields} FROM datasets{where}").format(fields=select_clause, where=where_sql)
        cur.execute(query, params)
        rows = cur.fetchall()
        cols = [c.name for c in cur.description]
        return jsonify({"status": "success", "data": [dict(zip(cols, r)) for r in rows]}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# ──────────────────────────────────────────────────────────
# DASHBOARD HANDLER
# ──────────────────────────────────────────────────────────
def handle_dashboard():
    try:

        # 6. frequency counts
        cur.execute("SELECT frequency, COUNT(*) FROM datasets GROUP BY frequency")
        frequency_counts = {r[0] or "Unknown": r[1] for r in cur.fetchall()}

        # 1. total datasets
        cur.execute("SELECT COUNT(*) FROM datasets")
        total_tables = cur.fetchone()[0]

        # 2. last 10 datasets - get all columns dynamically
        cur.execute("SELECT * FROM datasets ORDER BY id DESC LIMIT 10")
        cols = [c.name for c in cur.description]
        last10 = [dict(zip(cols, r)) for r in cur.fetchall()]

        # 3. tag counts
        cur.execute("SELECT tag, COUNT(*) FROM (SELECT unnest(tags) AS tag FROM datasets) AS x GROUP BY tag")
        tag_counts = {r[0]: r[1] for r in cur.fetchall()}

        # 4. theme counts
        cur.execute("SELECT theme_id, COUNT(*) FROM datasets GROUP BY theme_id")
        theme_counts = {r[0] or "Unknown": r[1] for r in cur.fetchall()}

        # 5. category counts
        cur.execute("SELECT category::text, COUNT(*) FROM datasets GROUP BY category")
        category_counts = {r[0]: r[1] for r in cur.fetchall()}

        return jsonify({
            "frequencyCounts": frequency_counts,
            "status": "success",
            "totalTables": total_tables,
            "last10Datasets": last10,
            "tagCounts": tag_counts,
            "themeCounts": theme_counts,
            "categoryCounts": category_counts,
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
