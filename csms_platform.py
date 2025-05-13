# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 12:56:44 2025

@author: USER
"""

from flask import Flask, request, render_template_string, redirect, url_for
import pymysql

app = Flask(__name__, static_folder="/home/vtn-emu/ocpp/examples/v201/") # 確保路徑正確

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

# ======== 修改過的 HTML 模板 (稍後會修改這裡) =========
html_template = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>充電站管理系統</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { padding: 30px; font-family: 'Arial', sans-serif; background-color: #d4edda; padding-top: 80px; /* Add padding top for fixed navbar */ }
        .navbar { padding: 10px 0; }
        .container { background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .nav-tabs { border-bottom: none; margin-bottom: 30px; }
        .nav-tabs .nav-link {
            color: #555;
            border: none;
            border-radius: 20px;
            padding: 12px 20px;
            margin-right: 10px;
            background: #e9ecef;
            transition: 0.3s;
            font-size: 1rem;
        }
        .nav-tabs .nav-link:hover {
            background: #d0d7dd;
            transform: scale(1.05);
        }
        .nav-tabs .nav-link.active {
            background: #007bff;
            color: #fff;
            font-weight: bold;
            box-shadow: 0 0 10px rgba(0,123,255,0.5);
        }
        .card-title { font-size: 1.5rem; font-weight: bold; margin-bottom: 20px; }
        .table { margin-top: 20px; font-size: 0.9rem; }
        .table-striped tbody tr:nth-child(odd) { background-color: #f9f9f9; }
        .table thead { background-color: #343a40; color: white; }
        .pagination { justify-content: center; font-size: 1rem; margin-top: 30px; }
        .btn-primary { border-radius: 20px; }
        /* .content-area { margin-top: 80px; } */ /* Removed this as padding-top is added to body */
        .navbar-light { background-color: #ffffff; }
        .filter-card { margin-bottom: 20px; } /* Style for filter card */
    </style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-light bg-white fixed-top">
    <div class="container-fluid justify-content-center">
        <span class="navbar-brand mb-0 h1 fs-1 fw-bold text-dark">充電站管理系統</span>
    </div>
</nav>

<!-- 主內容 -->
<div class="container">

    <!-- 選單 -->
    <ul class="nav nav-tabs justify-content-center">
        <li class="nav-item">
            <a class="nav-link {% if page == 'charge_station' %}active{% endif %}" href="{{ url_for('home', page='charge_station') }}">
                <i class="bi bi-diagram-3"></i> 充電站架構圖
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if page == 'charge_points' %}active{% endif %}" href="{{ url_for('home', page='charge_points') }}">
                <i class="bi bi-ev-station"></i> 充電樁管理
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if page == 'customer_management' %}active{% endif %}" href="{{ url_for('home', page='customer_management') }}">
                <i class="bi bi-people"></i> 客戶管理
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if page == 'transactions' %}active{% endif %}" href="{{ url_for('home', page='transactions') }}">
                <i class="bi bi-receipt"></i> 交易紀錄
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if page == 'meter_values' %}active{% endif %}" href="{{ url_for('home', page='meter_values') }}">
                <i class="bi bi-speedometer2"></i> 電表資料紀錄
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if page == 'adr_events' %}active{% endif %}" href="{{ url_for('home', page='adr_events') }}">
                <i class="bi bi-broadcast"></i> ADR事件紀錄
            </a>
        </li>
    </ul>

    <!-- 內容顯示 -->
    {% if page == "charge_station" %}
        <div class="card">
            <div class="card-body text-center">
                <h5 class="card-title">充電站架構圖</h5>
                {# 確保 static 路徑正確 #}
                <img src="{{ url_for('static', filename='csms.jpg') }}" alt="充電站圖片" class="img-fluid">
            </div>
        </div>
    {% elif page == "customer_management" %}
        <ul class="nav nav-pills mb-4">
            <li class="nav-item">
                <a class="nav-link {% if subpage == 'registered_users' %}active{% endif %}" href="{{ url_for('home', page='customer_management', subpage='registered_users') }}">已註冊用戶</a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if subpage == 'authorized_users' %}active{% endif %}" href="{{ url_for('home', page='customer_management', subpage='authorized_users') }}">已授權用戶</a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if subpage == 'add_user' %}active{% endif %}" href="{{ url_for('home', page='customer_management', subpage='add_user') }}">新增用戶</a>
            </li>
        </ul>
    {% endif %}

    {# 🔥 新增 Meter Values 篩選表單 #}
    {% if page == "meter_values" %}
    <div class="card filter-card">
        <div class="card-body">
            <h5 class="card-title">篩選條件</h5>
            <form method="GET" action="{{ url_for('home') }}">
                {# Hidden fields to keep track of the current page #}
                <input type="hidden" name="page" value="{{ page }}">
                {# 不需要 subpage，因為 meter_values 沒有子頁面 #}

                <div class="row g-3 align-items-center">
                    <div class="col-auto">
                        <label for="filter_cp_id" class="col-form-label">充電樁 ID:</label>
                    </div>
                    <div class="col-auto">
                        <select class="form-select" id="filter_cp_id" name="filter_cp_id">
                            <option value="">-- 全部 --</option>
                            {# 從後端傳來的 charge_point_ids 列表 #}
                            {% for cp_id in charge_point_ids %}
                            <option value="{{ cp_id }}" {% if cp_id == filter_cp_id %}selected{% endif %}>
                                {{ cp_id }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-auto">
                        <button type="submit" class="btn btn-primary btn-sm">篩選</button>
                         {# 清除篩選按鈕，導回不帶 filter_cp_id 的頁面 #}
                         <a href="{{ url_for('home', page=page) }}" class="btn btn-secondary btn-sm">清除篩選</a>
                    </div>
                </div>
            </form>
        </div>
    </div>
    {% endif %}


    {# 新增用戶表單 或 資料表顯示 #}
    {% if subpage == "add_user" and page == "customer_management" %} {# 確保只在客戶管理頁顯示 #}
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">新增註冊用戶</h5>
                <form method="POST" action="{{ url_for('add_user') }}"> {# 使用 url_for 生成 action URL #}
                    <div class="mb-3">
                        <label class="form-label">ID Token</label>
                        <input type="text" class="form-control" name="id_token" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Type</label>
                        <input type="text" class="form-control" name="type" required>
                    </div>
                    <button type="submit" class="btn btn-primary">送出</button>
                </form>
            </div>
        </div>
    {% elif page != "charge_station" %} {# 如果不是架構圖頁面，就顯示資料表 #}
        <h3 class="mt-4 mb-3">
            {# 動態標題 #}
            {% if page == 'charge_points' %}充電樁管理
            {% elif page == 'customer_management' and subpage == 'registered_users' %}已註冊用戶
            {% elif page == 'customer_management' and subpage == 'authorized_users' %}已授權用戶
            {% elif page == 'transactions' %}交易紀錄
            {% elif page == 'meter_values' %}電表資料紀錄
            {% elif page == 'adr_events' %}ADR事件紀錄
            {% else %}資料表
            {% endif %}
        </h3>
        {% if datas %} {# 只有在有資料時才顯示表格 #}
            <div class="table-responsive">
                <table class="table table-striped table-bordered">
                    <thead class="table-dark">
                        <tr>
                            {% for col in columns %}
                            <th>{{ col }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in datas %}
                        <tr>
                            {% for col in columns %}
                            <td>{{ row[col] }}</td>
                            {% endfor %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <!-- 分頁 -->
            {% if total_pages > 1 %} {# 只有超過一頁才顯示分頁 #}
            <nav aria-label="Page navigation">
                <ul class="pagination justify-content-center">
                    <li class="page-item {% if current_page == 1 %}disabled{% endif %}">
                        {# 🔥 修改分頁連結，加入 filter_cp_id #}
                        <a class="page-link" href="{{ url_for('home', page=page, subpage=subpage, page_num=current_page - 1, filter_cp_id=filter_cp_id if page == 'meter_values' else None) }}">上一頁</a>
                    </li>
                    <li class="page-item disabled"><span class="page-link">頁數：{{ current_page }} / {{ total_pages }}</span></li>
                    <li class="page-item {% if current_page == total_pages %}disabled{% endif %}">
                         {# 🔥 修改分頁連結，加入 filter_cp_id #}
                        <a class="page-link" href="{{ url_for('home', page=page, subpage=subpage, page_num=current_page + 1, filter_cp_id=filter_cp_id if page == 'meter_values' else None) }}">下一頁</a>
                    </li>
                </ul>
            </nav>
            {% endif %}
        {% else %}
             <div class="alert alert-info" role="alert">
               目前沒有資料。
             </div>
        {% endif %} {# endif datas #}
    {% endif %} {# endif subpage == "add_user" / page != "charge_station" #}

</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""


# 首頁
@app.route("/", methods=["GET"])
def home():
    page = request.args.get("page", "charge_points")
    subpage = request.args.get("subpage", "registered_users" if page == "customer_management" else None) # 預設 subpage 只在 customer_management 下
    page_num = int(request.args.get("page_num", 1))
    # 🔥 讀取篩選參數，如果沒有提供，預設為空字串
    filter_cp_id = request.args.get("filter_cp_id", "")

    offset = (page_num - 1) * ITEMS_PER_PAGE

    conn = pymysql.connect(**db_config)
    datas = []
    total_items = 0
    columns = []
    charge_point_ids = [] # 🔥 初始化 charge_point_ids 列表

    try: # 使用 try...finally 確保連線關閉
        with conn.cursor() as cursor:
            # 🔥 如果是 meter_values 頁面，先查詢所有不重複的 charge_point_id
            if page == "meter_values":
                cursor.execute("SELECT DISTINCT charge_point_id FROM metervaule_datas ORDER BY charge_point_id")
                # 將查詢結果 (字典列表) 轉換成單純的 ID 列表
                charge_point_ids = [row['charge_point_id'] for row in cursor.fetchall()]

            # --- 主要資料查詢 ---
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
                else: # add_user 或其他情況
                    query = None # 不需要查詢資料
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
            elif page == "meter_values":
                # 🔥 動態建立查詢語句和參數
                base_query = "SELECT * FROM metervaule_datas"
                base_count_query = "SELECT COUNT(*) FROM metervaule_datas"
                where_clause = ""
                query_params = []
                count_params = []

                # 如果有篩選條件，加入 WHERE 子句
                if filter_cp_id:
                    where_clause = " WHERE charge_point_id = %s"
                    query_params.append(filter_cp_id)
                    count_params.append(filter_cp_id)

                # 組合最終查詢語句
                query = f"{base_query}{where_clause} ORDER BY id DESC LIMIT %s, %s"
                count_query = f"{base_count_query}{where_clause}"

                # 加入分頁參數 (注意順序)
                query_params.extend([offset, ITEMS_PER_PAGE])
                params = tuple(query_params) # 轉換成 tuple
                count_params = tuple(count_params) # 轉換成 tuple

            else: # charge_station 或其他未定義頁面
                query = None

            # --- 執行查詢 ---
            if query:
                cursor.execute(query, params)
                datas = cursor.fetchall()
                if datas:
                    columns = list(datas[0].keys()) # 從第一筆資料取得欄位名稱

                # 執行計算總筆數的查詢
                cursor.execute(count_query, count_params)
                result = cursor.fetchone()
                total_items = result['COUNT(*)'] if result else 0
            elif page == "charge_station":
                 # 架構圖頁面不需要查資料表
                 pass
            else:
                 # 例如 customer_management 的 add_user 子頁面
                 pass # 不需要查詢資料

    finally:
        conn.close() # 確保連線被關閉

    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    # 🔥 將 charge_point_ids 和 filter_cp_id 傳遞給模板
    return render_template_string(html_template, page=page, subpage=subpage, datas=datas, columns=columns,
                                  current_page=page_num, total_pages=total_pages,
                                  charge_point_ids=charge_point_ids, # 新增：傳遞 ID 列表
                                  filter_cp_id=filter_cp_id)       # 新增：傳遞當前篩選值

# 新增註冊用戶
@app.route("/add_user", methods=["POST"])
def add_user():
    id_token = request.form.get("id_token")
    user_type = request.form.get("type")

    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO authorize_datas (id_token, type) VALUES (%s, %s)"
            cursor.execute(sql, (id_token, user_type))
            conn.commit()
    finally:
        conn.close()

    # 使用 url_for 生成重定向 URL，更安全可靠
    return redirect(url_for('home', page='customer_management', subpage='registered_users'))

if __name__ == "__main__":
    # 確保 static_folder 路徑是正確的，指向包含 csms.jpg 的目錄
    # 例如，如果 csms.jpg 在 /home/vtn-emu/ocpp_rubyV1/examples/v201/static/csms.jpg
    # 則 static_folder="/home/vtn-emu/ocpp_rubyV1/examples/v201/static"
    # 如果 csms.jpg 就在 /home/vtn-emu/ocpp_rubyV1/examples/v201/csms.jpg
    # 則 static_folder="/home/vtn-emu/ocpp_rubyV1/examples/v201" (你目前的設定)
    # app.static_folder = "/path/to/your/static/files" # 如果需要，可以在這裡覆蓋
    app.run(host="0.0.0.0", port=5050, debug=True, use_reloader=False)

