# server.py  ─── imports
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg, re, json
from psycopg import sql, types
from psycopg.types.json import Json      # ← NEW
import traceback



app = Flask(__name__)
CORS(app)

# ─────────────────── DB CONNECTION ───────────────────
conn = psycopg.connect(
    "dbname=ridam user=postgres password=Singh@786", 
    autocommit=False,
)
cur = conn.cursor()
cur.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'datasets'
""")
TABLE_COLS = {r[0] for r in cur.fetchall()}  
# ─────────────────── FIELD MAP ───────────────────
def map_field(field_name: str):
    normal = {
        "id":          sql.Identifier("id"),
        "name":        sql.Identifier("name"),
        "frequency":   sql.Identifier("frequency"),
        "extension":   sql.Identifier("extension"),
        "projections": sql.Identifier("projections"),
        "paused":      sql.Identifier("paused"),
        "rgb":         sql.Identifier("rgb"),
        "category":    sql.Identifier("category"),
        "band info":   sql.Identifier("band_info"),
        "aux data":    sql.Identifier("aux_data"),
        "remarks":     sql.Identifier("remarks"),
        "tags":        sql.Identifier("tags"),
        "theme id":    sql.Identifier("theme_id"),
        "sub-theme id": sql.Identifier("sub_theme_id"),
        "product id":  sql.Identifier("product_id"),
        "base path":   sql.Identifier("base_path"),
        "create directory": sql.Identifier("create_dir"),
        "pyramid id":  sql.Identifier("pyramid_id"),
        "from time":   sql.Identifier("from_time"),
        "to time":     sql.Identifier("to_time"),
        "pool":        sql.Identifier("pool"),
    }

    meta = {
        "location":          sql.SQL("metadata ->> 'Location'          AS \"Location\""),
        "city":              sql.SQL("metadata ->> 'City'              AS \"City\""),
        "contact person":    sql.SQL("metadata ->> 'Contact_Person'    AS \"Contact Person\""),
        "organization":      sql.SQL("metadata ->> 'Organization'      AS \"Organization\""),
        "mailing address":   sql.SQL("metadata ->> 'Mailing_Address'   AS \"Mailing Address\""),
        "country":           sql.SQL("metadata ->> 'Country'           AS \"Country\""),
        "contact telephone": sql.SQL("metadata ->> 'Contact_Telephone' AS \"Contact Telephone\""),
    }

    
    key = field_name.strip().lower()
    if key in normal:
        return normal[key]
    if key in meta:
        return meta[key]

    # fallback: treat as a plain column (lower‑case)  
    return sql.Identifier(key)

# ─────────────────── HELPERS ───────────────────
def next_product_id(theme: str, sub: str) -> str:
    like_pat = f"{theme}{sub}P%"
    cur.execute(
        "SELECT product_id FROM datasets "
        "WHERE product_id LIKE %s ORDER BY product_id DESC LIMIT 1",
        (like_pat,),
    )
    row = cur.fetchone()
    last_num = int(re.search(r"P(\d+)$", row[0]).group(1)) if row else 0
    return f"{theme}{sub}P{last_num + 1}"

def next_pyramid_id(prod: str) -> str:
    like_pat = f"{prod}G%"
    cur.execute(
        "SELECT pyramid_id FROM datasets "
        "WHERE pyramid_id LIKE %s ORDER BY pyramid_id DESC LIMIT 1",
        (like_pat,),
    )
    row = cur.fetchone()
    last_num = int(re.search(r"G(\d+)$", row[0]).group(1)) if row else 0
    return f"{prod}G{last_num + 1}"

# ─────────────────── ROUTES ───────────────────
@app.route("/next_product_id/<theme>/<sub>")
def api_next_pid(theme, sub):
    return jsonify({"next": next_product_id(theme, sub)})

@app.route("/next_pyramid_id/<prod>")
def api_next_gid(prod):
    return jsonify({"next": next_pyramid_id(prod)})


# ─────────────────── REGISTER ───────────────────
def handle_register(data: dict):
    try:
        theme, sub = data.get("ThemeID"), data.get("SubThemeID")
        product_id = data.get("productId") or next_product_id(theme, sub)
        pyramid_id = data.get("pyramidId") or next_pyramid_id(product_id)

        pool_raw = data.get("pool")
        if isinstance(pool_raw, str) and pool_raw.strip():
            try:
                pool_json = json.loads(pool_raw)
            except json.JSONDecodeError as e:
                return jsonify({"status":"error","msg":f"Pool field must be valid JSON array: {e}"}), 400
        else:
            pool_json = None

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
            "tags":         [t.strip() for t in data.get("Tags","").split(",") if t.strip()],
            "theme_id":     theme,
            "sub_theme_id": sub,
            "metadata":     json.dumps(data.get("metadata", {})),

            "product_id":  product_id,
            "base_path":   data.get("basePath"),
            "create_dir":  data.get("createDir", True),
            "pyramid_id":  pyramid_id,
            "from_time":   data.get("fromTime"),
            "to_time":     data.get("toTime"),
            "pool":        pool_json,
        }

        cur.execute("""
            INSERT INTO datasets (
              name, frequency, extension, projections,
              paused, rgb, category, band_info, aux_data, remarks, tags,
              theme_id, sub_theme_id, metadata,
              product_id, base_path, create_dir,
              pyramid_id, from_time, to_time, pool
            ) VALUES (
              %(name)s,%(frequency)s,%(extension)s,%(projections)s,
              %(paused)s,%(rgb)s,%(category)s,%(band_info)s,%(aux_data)s,
              %(remarks)s,%(tags)s,%(theme_id)s,%(sub_theme_id)s,%(metadata)s,
              %(product_id)s,%(base_path)s,%(create_dir)s,
              %(pyramid_id)s,%(from_time)s,%(to_time)s,%(pool)s
            ) RETURNING id""", record)

        conn.commit()
        return jsonify({"status":"success","id":cur.fetchone()[0]}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"status":"error","msg":str(e)}), 500

def handle_dashboard():
    """
    Dashboard summary:
      • frequencyCounts   - rows grouped by frequency_enum
      • totalEntries      - total number of rows in datasets
      • last10Datasets    - newest 10 rows (all columns)
      • dailyEntryCounts  - rows inserted per calendar day (last 30 days, IST)
      • poolCounts        - counts per pool label
    """
    try:
        # Frequency counts
        cur.execute("""
            SELECT COALESCE(frequency::text, 'Unknown') AS freq,
                   COUNT(*) AS cnt
            FROM datasets
            GROUP BY freq
        """)
        frequency_counts = {r[0]: r[1] for r in cur.fetchall()}

        # Total entries
        cur.execute("SELECT COUNT(*) FROM datasets")
        total_entries = cur.fetchone()[0]

        # Last 10 datasets
        cur.execute("SELECT * FROM datasets ORDER BY id DESC LIMIT 10")
        cols = [desc[0] for desc in cur.description]
        last10 = [dict(zip(cols, row)) for row in cur.fetchall()]

        # Daily entry counts (last 30 days)
        cur.execute("""
            SELECT to_char(created_at AT TIME ZONE 'Asia/Kolkata', 'YYYY-MM-DD') AS day,
                   COUNT(*) AS entries
            FROM datasets
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY day
            ORDER BY day
        """)
        daily_entry_counts = {r[0]: r[1] for r in cur.fetchall()}

        # Pool counts with proper LATERAL join
        cur.execute("""
            SELECT COALESCE(pool_value, 'Unknown') AS pool,
                   COUNT(*) AS cnt
            FROM (
                SELECT 
                    CASE 
                        WHEN jsonb_typeof(pool) = 'array' THEN elems.pool_elem
                        ELSE NULL
                    END AS pool_value
                FROM datasets
                LEFT JOIN LATERAL jsonb_array_elements_text(pool) AS elems(pool_elem)
                    ON jsonb_typeof(pool) = 'array'
            ) sub
            WHERE pool_value IS NOT NULL
            GROUP BY pool
            ORDER BY cnt DESC
        """)
        pool_counts = {r[0]: r[1] for r in cur.fetchall()}

        return jsonify({
            "status": "success",
            "totalEntries": total_entries,
            "last10Datasets": last10,
            "frequencyCounts": frequency_counts,
            "dailyEntryCounts": daily_entry_counts,
            "poolCounts": pool_counts,
        })

    except Exception as e:
        # Rollback if using transaction
        conn.rollback()
        # Print traceback for debugging (optional)
        traceback.print_exc()
        return jsonify({"status": "error", "msg": str(e)}), 500
# ─────────────────── MANAGE ───────────────────
def handle_manage(data: dict):
    view_entries = data.get("viewEntries", [])
    sort_entries = data.get("sortEntries", [])

    try:
        # If no view fields specified, select ALL fields explicitly:
        if not view_entries:
            # select all fields including metadata keys explicitly:
            fields_to_select = [
                "id",
                "name",
                "frequency",
                "extension",
                "projections",
                "paused",
                "rgb",
                "category",
                "band_info",
                "aux_data",
                "remarks",
                "tags",
                "theme_id",
                "sub_theme_id",
                "product_id",
                "base_path",
                "create_dir",
                "pyramid_id",
                "from_time",
                "to_time",
                "pool",
                # metadata fields extracted as JSON fields:
                "metadata ->> 'Location' AS Location",
                "metadata ->> 'City' AS City",
                "metadata ->> 'Contact_Person' AS \"Contact Person\"",
                "metadata ->> 'Organization' AS Organization",
                "metadata ->> 'Mailing_Address' AS \"Mailing Address\"",
                "metadata ->> 'Country' AS Country",
                "metadata ->> 'Contact_Telephone' AS \"Contact Telephone\"",
            ]
            select_clause = sql.SQL(", ").join(sql.SQL(f) for f in fields_to_select)
        else:
            select_clause = sql.SQL(", ").join(map_field(e["field"]) for e in view_entries)

        # WHERE clause and params for filtering/sorting
        where_sql = sql.SQL("")
        params = []
        if sort_entries:
            conditions = []
            for e in sort_entries:
                field_sql = map_field(e["field"])
                val = e["value"]

                # Handle booleans for paused, etc.
                if e["field"].lower() in ("paused", "rgb", "category"):
                    if isinstance(val, str):
                        val = val.lower() == "true"
                    elif isinstance(val, bool):
                        pass
                    else:
                        val = bool(val)

                # Add condition
                conditions.append(sql.SQL("{} = %s").format(field_sql))
                params.append(val)

            where_sql = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions)

        query = sql.SQL("SELECT {fields} FROM datasets{where}").format(
            fields=select_clause,
            where=where_sql,
        )

        cur.execute(query, params)
        rows = cur.fetchall()
        cols = [c.name for c in cur.description]
        results = [dict(zip(cols, r)) for r in rows]

        # Deserialize JSONB fields before sending response
        for r in results:
            if "metadata" in r and r["metadata"]:
                if isinstance(r["metadata"], str):
                    r["metadata"] = json.loads(r["metadata"])
            if "pool" in r and r["pool"]:
                if isinstance(r["pool"], str):
                    r["pool"] = json.loads(r["pool"])

        return jsonify({"status": "success", "data": results}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

def handle_edit():
    try:
        data = request.get_json(force=True)
        if data.get("type") != "edit":
            return jsonify({"status":"error","message":"Invalid request type"}),400

        patch = data.get("value_edit") or data.get("value")
        if not patch or "id" not in patch:
            return jsonify({"status":"error","message":"Missing dataset id"}),400

        ds_id = patch.pop("id")

        # ── 1. fetch current row ──────────────────────────────────────
        cur.execute("SELECT * FROM datasets WHERE id = %s", (ds_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"status":"error","message":"Dataset not found"}),404
        cols = [d.name for d in cur.description]
        record = dict(zip(cols, row))

        # ── 2. merge edits (metadata handled via meta_map) ────────────
        meta_map = {
            "location":"Location","city":"City","contact person":"Contact_Person",
            "organization":"Organization","mailing address":"Mailing_Address",
            "country":"Country","contact telephone":"Contact_Telephone"
        }
        def boolify(v): return str(v).strip().lower()=="true"

        for k,v in patch.items():
            klc = k.lower()
            if klc in meta_map:                          # --- goes into metadata JSON
                meta = record.get("metadata") or {}
                if isinstance(meta,str): meta=json.loads(meta)
                meta[meta_map[klc]] = v
                record["metadata"] = meta
                continue

            # normal cols
            k_db = klc.replace(" ","_")
            if k_db in ("paused","rgb","category"): v = boolify(v)
            if k_db=="frequency":   v = str(v).lower()
            if k_db=="extension":   v = str(v).lstrip(".").lower()
            if k_db=="projections": v = str(v).upper()
            if k_db=="tags" and isinstance(v,str):
                v = [t.strip() for t in v.split(",") if t.strip()]
            record[k_db] = v

        # serialise jsonb fields
        if isinstance(record.get("metadata"),(dict,list)):
            record["metadata"] = Json(record["metadata"])
        if isinstance(record.get("pool"),(dict,list)):
            record["pool"] = Json(record["pool"])

        # ── 3. delete old row ─────────────────────────────────────────
        cur.execute("DELETE FROM datasets WHERE id = %s",(ds_id,))

        # ── 4. keep only real table columns & drop id for auto‑serial ─
        record.pop("id", None)
        clean_rec = {k:v for k,v in record.items() if k in TABLE_COLS}

        cols_sql = sql.SQL(", ").join(map(sql.Identifier, clean_rec.keys()))
        vals_sql = sql.SQL(", ").join(sql.Placeholder() * len(clean_rec))
        insert_q = sql.SQL("INSERT INTO datasets ({c}) VALUES ({v}) RETURNING id") \
                   .format(c=cols_sql, v=vals_sql)

        cur.execute(insert_q, list(clean_rec.values()))
        new_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({"status":"success","message":"Dataset replaced","new_id":new_id}),200

    except Exception as e:
        conn.rollback()
        print("Error in handle_edit (replace):", e)
        return jsonify({"status":"error","message":str(e)}),500

def handle_delete():
    try:
        data = request.get_json(force=True)
        dataset_id = data.get("id")
        if not dataset_id:
            return jsonify({"status": "error", "message": "Missing dataset id"}), 400

        cur.execute("DELETE FROM datasets WHERE id = %s RETURNING id;", (dataset_id,))
        deleted = cur.fetchone()
        conn.commit()

        if deleted:
            return jsonify({"status": "success", "message": "Dataset deleted"}), 200
        else:
            return jsonify({"status": "error", "message": "Dataset not found"}), 404

    except Exception as e:
        conn.rollback()
        print("Error in handle_delete:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/", methods=["POST"])
def handle_request():
    data = request.get_json(force=True)
    if data.get("type") == "register":
        return handle_register(data)
    elif data.get("type") == "manage":
        return handle_manage(data)
    elif data.get("type") == "edit":
        return handle_edit()
    elif data.get("type") == "dashboard":
        return handle_dashboard()
    elif data.get("type") == "delete":
        return handle_delete()
    return jsonify({"status": "error", "msg": "Unknown type"}), 400


if __name__ == "__main__":
    app.run(debug=True)
