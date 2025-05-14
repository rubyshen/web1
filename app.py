# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 12:56:44 2025

@author: USER
"""

from flask import Flask, request, render_template, redirect, url_for, jsonify # 修改: 導入 render_template
import pymysql

app = Flask(__name__) # Flask 會預設使用 'static' 資料夾，並在 'templates' 資料夾中尋找模板

# MySQL 連線設定
db_config = {
    "host": "127.0.0.1",
    "user": "openadr",
    "password": "1118",
    "database": "csms",
    "cursorclass": pymysql.cursors.DictCursor
}

# 每頁顯示的資料筆數
ITEMS_PER_PAGE = 10

# 首頁
@app.route("/", methods=["GET"])
def home():
    page = request.args.get("page", "charge_points")
    subpage = request.args.get("subpage", "registered_users" if page == "customer_management" else None) # 預設 subpage 只在 customer_management 下
    page_num = int(request.args.get("page_num", 1))

    offset = (page_num - 1) * ITEMS_PER_PAGE

    conn = pymysql.connect(**db_config)
    datas = []
    total_items = 0
    columns = []

    try:
        with conn.cursor() as cursor:
            if page == "charge_points":
                query = "SELECT * FROM charge_points LIMIT %s, %s"
                count_query = "SELECT COUNT(*) FROM charge_points"
                params = (offset, ITEMS_PER_PAGE)
                count_params = ()
            elif page == "customer_management":
                if subpage == "registered_users":
                    query = "SELECT * FROM authorize_datas LIMIT %s, %s"
                    count_query = "SELECT COUNT(*) FROM authorize_datas"
                    params = (offset, ITEMS_PER_PAGE)
                    count_params = ()
                elif subpage == "authorized_users":
                    query = "SELECT * FROM authorized_users LIMIT %s, %s"
                    count_query = "SELECT COUNT(*) FROM authorized_users"
                    params = (offset, ITEMS_PER_PAGE)
                    count_params = ()
                else: # add_user
                    query = None
            elif page == "transactions":
                query = "SELECT * FROM charging_datas ORDER BY id DESC LIMIT %s, %s"
                count_query = "SELECT COUNT(*) FROM charging_datas"
                params = (offset, ITEMS_PER_PAGE)
                count_params = ()
            elif page == "adr_events":
                query = "SELECT * FROM adr_events ORDER BY id DESC LIMIT %s, %s"
                count_query = "SELECT COUNT(*) FROM adr_events"
                params = (offset, ITEMS_PER_PAGE)
                count_params = ()
            elif page == "meter_values" or page == "charge_station": # Data fetched by Vue via API
                query = None
            else:
                query = None

            if query:
                cursor.execute(query, params)
                datas = cursor.fetchall()
                if datas:
                    columns = list(datas[0].keys())
                cursor.execute(count_query, count_params)
                result = cursor.fetchone()
                total_items = result['COUNT(*)'] if result else 0
            # For pages handled by Vue or no data pages, total_items remains 0 unless set otherwise
    finally:
        conn.close()

    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if total_items > 0 else 0

    return render_template("home.html", page=page, subpage=subpage, datas=datas, columns=columns,
                                  current_page=page_num, total_pages=total_pages) # 修改: 使用 render_template

# --- 假數據 ---
MOCK_SITES = [
    {"id": 1, "name": "A區充電站", "diagram_x": 200, "diagram_y": 400, "description": "靠近入口"},
    {"id": 2, "name": "B區充電站", "diagram_x": 600, "diagram_y": 600, "description": "停車場深處"},
    {"id": 3, "name": "C區快充站", "diagram_x": 1900, "diagram_y": 700, "description": "快速充電專用"},
    {"id": 4, "name": "D區慢充", "diagram_x": 2800, "diagram_y": 1000, "description": "訪客車位"},
]

MOCK_SITE_STATUSES = {
    # site_id: { available_guns: X, used_guns: Y, other_status_guns: Z }
    "1": {"available_guns": 3, "used_guns": 1, "other_status_guns": 0},
    "2": {"available_guns": 2, "used_guns": 2, "other_status_guns": 1},
    "3": {"available_guns": 1, "used_guns": 0, "other_status_guns": 0},
    # Site 4 might not have status yet, or it's all available
    "4": {"available_guns": 4, "used_guns": 0, "other_status_guns": 0},
}
# --- 結束假數據 ---

@app.route("/api/charge_sites", methods=["GET"])
def api_get_charge_sites():
    # This will be replaced with DB query later
    return jsonify(MOCK_SITES)

@app.route("/api/charge_point_statuses", methods=["GET"])
def api_get_charge_point_statuses():
    # This will be replaced with DB query later
    return jsonify(MOCK_SITE_STATUSES)

# API endpoint for Meter Values (Vue controlled)
@app.route("/api/meter_values", methods=["GET"])
def api_meter_values():
    page_num = int(request.args.get("page_num", 1))
    filter_cp_id = request.args.get("filter_cp_id", "")
    offset = (page_num - 1) * ITEMS_PER_PAGE

    conn = pymysql.connect(**db_config)
    datas = []
    total_items = 0
    columns = []
    charge_point_ids_for_filter = []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT charge_point_id FROM metervaule_datas ORDER BY charge_point_id")
            charge_point_ids_for_filter = [row['charge_point_id'] for row in cursor.fetchall()]

            base_query = "SELECT * FROM metervaule_datas"
            base_count_query = "SELECT COUNT(*) FROM metervaule_datas"
            where_clause = ""
            query_params_list = []
            count_params_list = []

            if filter_cp_id:
                where_clause = " WHERE charge_point_id = %s"
                query_params_list.append(filter_cp_id)
                count_params_list.append(filter_cp_id)

            final_query = f"{base_query}{where_clause} ORDER BY id DESC LIMIT %s, %s"
            query_params_list.extend([offset, ITEMS_PER_PAGE])
            final_count_query = f"{base_count_query}{where_clause}"

            cursor.execute(final_query, tuple(query_params_list))
            datas = cursor.fetchall()
            if datas:
                columns = list(datas[0].keys())

            cursor.execute(final_count_query, tuple(count_params_list))
            result = cursor.fetchone()
            total_items = result['COUNT(*)'] if result else 0
    finally:
        conn.close()

    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if total_items > 0 else 0
    return jsonify({
        "data": datas,
        "columns": columns,
        "total_items": total_items,
        "current_page": page_num,
        "per_page": ITEMS_PER_PAGE,
        "total_pages": total_pages,
        "charge_point_ids": charge_point_ids_for_filter
    })

# Add new registered user
@app.route("/add_user", methods=["POST"])
def add_user():
    id_token = request.form.get("id_token")
    user_type = request.form.get("type")

    if not id_token or not user_type:
        return redirect(url_for('home', page='customer_management', subpage='add_user'))

    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO authorize_datas (id_token, type) VALUES (%s, %s)"
            cursor.execute(sql, (id_token, user_type))
            conn.commit()
    except pymysql.Error as e:
        print(f"Database error: {e}")
        return redirect(url_for('home', page='customer_management', subpage='add_user'))
    finally:
        conn.close()

    return redirect(url_for('home', page='customer_management', subpage='registered_users'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True, use_reloader=True)
