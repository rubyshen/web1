# -*- coding: utf-8 -*-
"""
Created on Tue May 14 15:00:00 2025 # Updated creation date

@author: USER
"""

from flask import Flask, request, render_template, redirect, url_for, jsonify # 修改: 導入 render_template
import pymysql
import random # 新增：導入 random 模組
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

                # 為 charge_station 頁面下方的表格生成模擬的交易紀錄資料
                mock_transaction_data = [
                    {"充電槍ID": "A-01", "充電開始時間": "10/29 16:34:42", "持續時間": "1355s", "充電結束時間": "10/29 22:04:27", "車輛最終SOC": "89%", "已充入電能": "182kw", "充電費用": "989 NTD"},
                    {"充電槍ID": "A-02", "充電開始時間": "10/28 12:54:48", "持續時間": "2867s", "充電結束時間": "10/28 17:26:43", "車輛最終SOC": "75%", "已充入電能": "154kw", "充電費用": "798 NTD"},
                    {"充電槍ID": "B-01", "充電開始時間": "10/28 10:55:14", "持續時間": "3437s", "充電結束時間": "10/28 16:07:12", "車輛最終SOC": "84%", "已充入電能": "167kw", "充電費用": "891 NTD"},
                    {"充電槍ID": "B-02", "充電開始時間": "10/27 12:42:12", "持續時間": "2756s", "充電結束時間": "10/27 17:06:27", "車輛最終SOC": "74%", "已充入電能": "146kw", "充電費用": "754 NTD"},
                    {"充電槍ID": "C-01", "充電開始時間": "10/27 10:24:56", "持續時間": "3548s", "充電結束時間": "10/27 16:27:54", "車輛最終SOC": "83%", "已充入電能": "178kw", "充電費用": "914 NTD"},
                    {"充電槍ID": "C-02", "充電開始時間": "10/26 08:19:01", "持續時間": "4132s", "充電結束時間": "10/26 11:32:18", "車輛最終SOC": "80%", "已充入電能": "160kw", "充電費用": "820 NTD"},
                    {"充電槍ID": "D-01", "充電開始時間": "10/27 12:42:12", "持續時間": "2756s", "充電結束時間": "10/27 17:06:27", "車輛最終SOC": "74%", "已充入電能": "146kw", "充電費用": "754 NTD"},
                    {"充電槍ID": "D-02", "充電開始時間": "10/27 10:24:56", "持續時間": "3548s", "充電結束時間": "10/27 16:27:54", "車輛最終SOC": "83%", "已充入電能": "178kw", "充電費用": "914 NTD"},
                ]

                # 對模擬資料進行分頁
                total_items = len(mock_transaction_data)
                datas = mock_transaction_data[offset : offset + ITEMS_PER_PAGE]
                # 定義表格欄位名稱
                columns = ["充電槍ID", "充電開始時間", "持續時間", "充電結束時間", "車輛最終SOC", "已充入電能", "充電費用"]

                # total_pages 會在函數結尾計算

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
# MOCK_SITES 已被 MOCK_GUNS 取代，因為圖表現在顯示槍而不是站點

# 新的假數據：8 隻充電槍及其位置和所屬站點
MOCK_GUNS = [
    {"gun_id": "A-01", "site": "A區", "diagram_x": 90, "diagram_y": 90, "description": "A區槍1"},
    {"gun_id": "A-02", "site": "A區", "diagram_x": 110, "diagram_y": 110, "description": "A區槍2"},
    {"gun_id": "B-01", "site": "B區", "diagram_x": 290, "diagram_y": 140, "description": "B區槍1"},
    {"gun_id": "B-02", "site": "B區", "diagram_x": 310, "diagram_y": 160, "description": "B區槍2"},
    {"gun_id": "C-01", "site": "C區", "diagram_x": 590, "diagram_y": 190, "description": "C區槍1 (快充)"},
    {"gun_id": "C-02", "site": "C區", "diagram_x": 610, "diagram_y": 210, "description": "C區槍2 (快充)"},
    {"gun_id": "D-01", "site": "D區", "diagram_x": 520, "diagram_y": 290, "description": "D區槍1 (慢充)"},
    {"gun_id": "D-02", "site": "D區", "diagram_x": 560, "diagram_y": 300, "description": "D區槍2 (慢充)"},
]

# MOCK_SITE_STATUSES 已被 api_get_charge_point_statuses 動態生成槍狀態取代
# --- 結束假數據 ---

@app.route("/api/charge_sites", methods=["GET"])
def api_get_charge_sites():
    """
    回傳充電槍的位置、所屬站點和描述資訊，用於前端繪製圖表。
    """
    return jsonify(MOCK_GUNS)

@app.route("/api/charge_point_statuses", methods=["GET"])
def api_get_charge_point_statuses():
    """
    動態生成每個充電槍的狀態。
    - "occupied" 狀態會隨機變動 (True/False)。
    """
    dynamic_gun_statuses = {}
    for gun_info in MOCK_GUNS:
        dynamic_gun_statuses[gun_info['gun_id']] = {"occupied": random.choice([True, False])}
    return jsonify(dynamic_gun_statuses)

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

# --- 新增：充電槍詳細頁面路由 ---
@app.route("/gun/<string:gun_id>", methods=["GET"])
def gun_detail(gun_id):
    """
    渲染單一充電槍的詳細頁面，顯示用電量曲線圖。
    """
    # 將 gun_id 傳遞給模板，以便前端 JavaScript 知道要獲取哪支槍的數據
    return render_template("gun_detail.html", gun_id=gun_id)

# --- 修改：獲取單一充電槍用電量數據的 API ---
@app.route("/api/gun_data/<string:gun_id_from_url>", methods=["GET"])
def api_gun_data(gun_id_from_url):
    from datetime import datetime, timedelta
    # 這裡模擬單一充電槍的用電量數據

    # 模擬一些基於 gun_id 的變化
    base_power = 5
    if 'A' in gun_id_from_url: base_power = 3
    elif 'B' in gun_id_from_url: base_power = 7
    elif 'C' in gun_id_from_url: base_power = 15 # 快充
    elif 'D' in gun_id_from_url: base_power = 4  # 慢充

    now = datetime.now()
    power_data_points = [
        {"time": (now - timedelta(seconds=(35 - j) * 10)).strftime("%H:%M:%S"), "value": round(abs(base_power + random.random() * 5 + (j / 10) * 1.2 - (j / 18) * 1.5 + (random.random() - 0.5) * 2), 2)}
        for j in range(36)
    ]
    # API 回傳一個包含單一槍數據的列表，以匹配 gun_detail.html 中 JS 的 .find() 邏輯
    # 或者，如果 gun_detail.html 的 JS 被修改為直接使用對象，則可以直接回傳對象。
    # 目前保持回傳列表，以減少對 gun_detail.html (如果已創建) 的修改。
    data_for_this_gun = [{"gun_id": gun_id_from_url, "power_data": power_data_points}]
    return jsonify(data_for_this_gun)


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
    # Set use_reloader=False if you encounter issues with multiple database connections
    # due to the reloader process.
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=True)
