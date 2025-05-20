# -*- coding: utf-8 -*-
"""
Created on Tue May 14 15:00:00 2025 # Updated creation date

@author: USER
"""

from flask import Flask, request, render_template, redirect, url_for, jsonify # 修改: 導入 render_template
import pymysql
from datetime import datetime, timedelta

app = Flask(__name__) # Flask 會預設使用 'static' 資料夾，並在 'templates' 資料夾中尋找模板

# MySQL 連線設定
db_config = { # Consider moving sensitive info out of code
    "host": "127.0.0.1",
    "user": "openadr",
    "password": "1118",
    "database": "csms",
    "cursorclass": pymysql.cursors.DictCursor
}

# 每頁顯示的資料筆數
ITEMS_PER_PAGE = 10

# 新的主選單進入點
@app.route("/", methods=["GET"])
def main_page():
    """渲染主選單頁面 (main.html)"""
    return render_template("main.html")

# 原本的 home 函數，現在負責處理 "中興院區" 的內容
# url_for('home', ...) 會對應到此函數
@app.route("/zhongxing_campus", methods=["GET"]) # 基本路徑，page 和 subpage 會使用預設值
@app.route("/zhongxing_campus/<page>", methods=["GET"]) # 帶有 page 參數的路徑
@app.route("/zhongxing_campus/<page>/<subpage>", methods=["GET"]) # 帶有 page 和 subpage 參數的路徑
def home(page="charge_points", subpage=None): # page 和 subpage 從 URL 路徑獲取
    # page_num 仍然從查詢參數獲取，用於分頁
    page_num = int(request.args.get("page_num", 1))
    offset = (page_num - 1) * ITEMS_PER_PAGE

    conn = pymysql.connect(**db_config)
    datas = []
    total_items = 0
    columns = []
    header_title = "中興院區充電站管理" # 新增：定義院區特定的標題

    # 根據新的參數傳遞方式，調整 subpage 的預設邏輯
    if subpage is None: # 僅當 subpage 未在 URL 路徑中指定時，才應用預設值
        if page == "customer_management":
            subpage = "registered_users"

    try:
        with conn.cursor() as cursor:
            if page == "charge_points":
                query = "SELECT * FROM charge_points LIMIT %s, %s"
                count_query = "SELECT COUNT(*) FROM charge_points"
                params = (offset, ITEMS_PER_PAGE)
                count_params = ()
                # print(f"DEBUG [charge_points]: Query: {query}, Params: {params}")
            elif page == "charge_station":
                # 主要內容由 Vue 處理，所以主查詢為 None
                query = None
                # 但我們需要額外獲取 charge_points 的資料以在同一頁顯示表格
                cp_table_query = "SELECT * FROM charge_points LIMIT %s, %s"
                cp_table_count_query = "SELECT COUNT(*) FROM charge_points"
                # 使用相同的 offset 和 ITEMS_PER_PAGE 進行分頁
                cursor.execute(cp_table_query, (offset, ITEMS_PER_PAGE))
                datas = cursor.fetchall() # 將 charge_points 資料存入 datas
                columns = list(datas[0].keys()) if datas else [] # 同上
                cursor.execute(cp_table_count_query, ())
                result = cursor.fetchone()
                total_items = result['COUNT(*)'] if result else 0 # 同上

            # 客戶管理邏輯已移至 management_index
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
                # print(f"DEBUG [{page}]: Fetched datas: {datas}")
                if datas:
                    columns = list(datas[0].keys())
                cursor.execute(count_query, count_params)
                result = cursor.fetchone()
                total_items = result['COUNT(*)'] if result else 0
                # print(f"DEBUG [{page}]: Total items: {total_items}")
            # For pages handled by Vue or no data pages, total_items might remain 0 or be set differently
    finally:
        conn.close()

    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if total_items > 0 else 0

    return render_template("home.html", page=page, subpage=subpage, datas=datas, columns=columns,
                                  current_page=page_num, total_pages=total_pages, header_title=header_title) # 修改: 傳遞 header_title

# --- 新的管理區塊 ---
@app.route("/management", methods=["GET"])
@app.route("/management/<section>", methods=["GET"])
@app.route("/management/<section>/<sub_section>", methods=["GET"])
def management_index(section="site_admin", sub_section=None):
    page_num = int(request.args.get("page_num", 1))
    offset = (page_num - 1) * ITEMS_PER_PAGE
    conn = pymysql.connect(**db_config)
    datas = []
    total_items = 0
    columns = []
    management_header_title = "管理"

    # 預設客戶管理的子區塊
    if section == "customer_admin" and sub_section is None:
        sub_section = "registered_users"

    try:
        with conn.cursor() as cursor:
            if section == "customer_admin":
                if sub_section == "registered_users":
                    query = "SELECT * FROM authorize_datas ORDER BY id DESC LIMIT %s, %s"
                    count_query = "SELECT COUNT(*) FROM authorize_datas"
                    params = (offset, ITEMS_PER_PAGE)
                    count_params = ()
                elif sub_section == "authorized_users":
                    query = "SELECT * FROM authorized_users LIMIT %s, %s"
                    count_query = "SELECT COUNT(*) FROM authorized_users"
                    params = (offset, ITEMS_PER_PAGE)
                    count_params = ()
                elif sub_section == "add_user":
                    query = None # GET 請求顯示表單
                else:
                    query = None
            elif section == "site_admin":
                # 站區管理目前施工中
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
    finally:
        conn.close()

    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if total_items > 0 else 0

    return render_template("management_dashboard.html",
                           section=section,
                           sub_section=sub_section,
                           datas=datas,
                           columns=columns,
                           current_page=page_num,
                           total_pages=total_pages,
                           management_header_title=management_header_title)





# --- 假數據 ---
MOCK_SITES = [
    {"id": 1, "name": "A區充電樁", "diagram_x": 100, "diagram_y": 100, "description": "靠近入口"},
    {"id": 2, "name": "B區充電樁", "diagram_x": 300, "diagram_y": 150, "description": "停車場深處"},
    {"id": 3, "name": "C區快充樁", "diagram_x": 600, "diagram_y": 200, "description": "快速充電專用"},
    {"id": 4, "name": "D區慢充樁", "diagram_x": 550, "diagram_y": 300, "description": "訪客車位"},
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
            cursor.execute("SELECT DISTINCT charge_point_id FROM metervalue_datas ORDER BY charge_point_id")
            charge_point_ids_for_filter = [row['charge_point_id'] for row in cursor.fetchall()]

            base_query = "SELECT * FROM metervalue_datas"
            base_count_query = "SELECT COUNT(*) FROM metervalue_datas"
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

# --- 新增：充電站詳細頁面路由 ---
@app.route("/station/<int:station_id>", methods=["GET"])
def station_detail(station_id):
    # 您可以在這裡從資料庫獲取該充電站的詳細資訊
    # 為了範例，我們只傳遞 station_id
    return render_template("station_detail.html", station_id=station_id)

# --- 新增：獲取充電站充電槍用電量數據的 API ---
@app.route("/api/station_data/<int:station_id>", methods=["GET"])
@app.route("/api/station_data/<int:station_id>", methods=["GET"])
def api_station_data(station_id):
    from datetime import datetime, timedelta
    num_guns = (station_id % 3) + 2
    data = []
    for i in range(num_guns):
        gun_id = f"{station_id}-{i+1}"
        now = datetime.now()
        # 模擬最近 36 筆資料，每 10 秒一筆，往前推
        power_data = [
            {
                "time": (now - timedelta(seconds=(35 - j) * 10)).strftime("%H:%M:%S"),
                "value": round(abs(5 + random.random() * 20 + (j / 10) * 1.2 - (j / 18) * 1.5 + (random.random() - 0.5) * 2), 2)
            }
            for j in range(36)
        ]
        data.append({"gun_id": gun_id, "power_data": power_data})
    return jsonify(data)


# Add new registered user
# 舊的 add_user 路由，如果不再使用可以考慮移除或加上 deprecation 警告
# @app.route("/add_user", methods=["POST"])
# def add_user(): ...

# 新的 add_user 路由，用於管理區塊
@app.route("/management/customer_admin/add_user_submit", methods=["POST"])
def add_user_management():
    id_token = request.form.get("id_token")
    user_type = request.form.get("type")

    if not id_token or not user_type:
        return redirect(url_for('management_index', section='customer_admin', sub_section='add_user'))

    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO authorize_datas (id_token, type) VALUES (%s, %s)"
            cursor.execute(sql, (id_token, user_type))
            conn.commit()
    except pymysql.Error as e:
        print(f"Database error: {e}")
        return redirect(url_for('management_index', section='customer_admin', sub_section='add_user'))
    finally:
        if conn: conn.close()
    return redirect(url_for('management_index', section='customer_admin', sub_section='registered_users'))

if __name__ == "__main__":
    import random # Import random for mock data
    # Set use_reloader=False if you encounter issues with multiple database connections
    # due to the reloader process.
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=True)
