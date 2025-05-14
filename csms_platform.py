# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 12:56:44 2025

@author: USER
"""

from flask import Flask, request, render_template_string, redirect, url_for, jsonify
import pymysql

app = Flask(__name__) # Flask 會預設使用 'static' 資料夾

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

# ======== 修改過的 HTML 模板 =========
html_template = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>充電站管理系統</title>
    {# <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"> #}
    <link href="https://bootswatch.com/5/cerulean/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { padding: 30px; font-family: 'Arial', sans-serif; background-color: #f0f2f5; /* padding-top will be set by JS */ }
        .navbar { padding: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .container-fluid { background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-top: 20px; }
        
        /* Styles for the new vertical nav pills */
        .nav-pills.flex-column .nav-item {
            width: 100%; /* Make nav items take full width of their column */
        }
        .nav-pills.flex-column .nav-link {
            color: #495057; /* Darker text for better readability */
            border: none;
            border-radius: 0.375rem; /* Bootstrap's default border-radius */
            padding: 0.75rem 1rem;   /* Standard padding */
            margin-bottom: 5px;    /* Space between vertical items */
            background: #e9ecef;
            transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out, transform 0.2s ease-in-out;
            font-size: 0.9rem; 
            text-align: left;      /* Align text to the left */
            display: flex;         /* For icon alignment */
            align-items: center;   /* Vertically align icon and text */
        }
        .nav-pills.flex-column .nav-link i {
            margin-right: 0.5rem; /* Space between icon and text */
            font-size: 1.1rem;    /* Slightly larger icons */
        }
        .nav-pills.flex-column .nav-link:hover {
            background-color: #0d6efd; /* Primary color on hover */
            color: #fff;
            transform: translateX(3px); /* Slight move effect on hover */
        }
        .nav-pills.flex-column .nav-link.active {
            background: #0d6efd; /* Primary color for active */
            color: #fff;
            font-weight: bold;
            box-shadow: 0 0 10px rgba(13,110,253,0.4);
        }
        .card-title { font-size: 1.5rem; font-weight: bold; margin-bottom: 20px; color: #333; }
        .table { margin-top: 20px; font-size: 0.9rem; }
        .table-striped tbody tr:nth-child(odd) { background-color: #f8f9fa; }
        .table thead { background-color: #343a40; color: white; }
        .pagination { justify-content: center; font-size: 1rem; margin-top: 30px; }
        .btn-primary { border-radius: 0.375rem; } /* Standard Bootstrap radius */
        .navbar-light { background-color: #ffffff; }
        .filter-card { margin-bottom: 20px; border: 1px solid #dee2e6; border-radius: 0.375rem;}
        .content-area { /* For the right column content */
            padding-left: 15px; /* Add some padding if needed */
        }
        #konva-diagram-container {
            width: 100%; /* Make it take the full width of its column */
            max-width: 100%; /* Ensure it doesn't exceed parent width */
            /* Set a max-height or aspect-ratio to prevent excessive height with tall images */
            /* For example, max-height: 70vh; (70% of viewport height) */
            /* Or, maintain an aspect ratio if you know it, e.g., padding-bottom: 56.25%; for 16:9, but this is trickier with Konva */
            overflow: hidden; /* Hide parts of the Konva canvas that are too large */
        }
    </style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-light bg-white fixed-top">
    <div class="container-fluid justify-content-center">
        <span class="navbar-brand mb-0 h1 fs-2 fw-bold text-dark">充電站管理系統</span>
    </div>
</nav>

<!-- 主內容 -->
<div class="container-fluid">
    <div class="row">
        <!-- 左側選單 -->
        <div class="col-md-3">
            <ul class="nav nav-pills flex-column">
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
        </div>

        <!-- 右側內容顯示 -->
        <div class="col-md-9 content-area">
            {% if page == "charge_station" %} {# CHARGE STATION CONTENT - Vue will handle this #}
                {% raw %}
                <div id="charge-station-diagram-app">
                    <h5 class="card-title mb-3">充電站架構圖</h5>
                    <div v-if="loading" class="d-flex justify-content-center my-3">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">載入中...</span>
                        </div>
                    </div>                   
                    <!-- Container for Konva Stage -->
                    <div v-show="!loading" ref="konvaContainerRef" id="konva-diagram-container" style="border: 1px solid #ccc;">
                        <!-- Konva will draw here -->
                    </div>
                    <div v-if="!loading && stageConfig.width === 0" class="alert alert-warning mt-3">
                        無法載入背景圖片或設定畫布尺寸。
                    </div>
                </div>
                {% endraw %}
            {% elif page == "customer_management" %} {# CUSTOMER MANAGEMENT SUBMENU - Jinja handles this part inside raw, but Vue script is outside #}
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
            {% elif page != "meter_values" %}
                 <!-- Placeholder for other Jinja-rendered content if needed, ensure it's correctly handled with raw/endraw if it contains Vue-like syntax -->
            {% endif %}

            {# 🔥 Meter Values 區域將由 Vue 控制 #}
            {% if page == "meter_values" %}
            {% raw %}
            <div id="meter-values-app">
                <div class="card filter-card">
                    <div class="card-body">
                        <h5 class="card-title">篩選條件</h5>
                        <div class="row g-3 align-items-center">
                            <div class="col-auto">
                                <label for="vue_filter_cp_id" class="col-form-label">充電樁 ID:</label>
                            </div>
                            <div class="col-auto">
                                <select class="form-select" id="vue_filter_cp_id" v-model="selectedCpId" @change="fetchMeterData(1)">
                                    <option value="">-- 全部 --</option>
                                    <option v-for="cpId in chargePointOptions" :key="cpId" :value="cpId">
                                        {{ cpId }}
                                    </option>
                                </select>
                            </div>
                            <div class="col-auto">
                                 <button @click="clearFilter" class="btn btn-secondary btn-sm">清除篩選</button>
                            </div>
                        </div>
                    </div>
                </div>

                <h3 class="mt-4 mb-3">電表資料紀錄</h3>
                <div v-if="loading" class="d-flex justify-content-center my-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">載入中...</span>
                    </div>
                </div>
                <div v-if="!loading && meterRecords.length === 0" class="alert alert-info">目前沒有資料。</div>
                <div v-if="!loading && meterRecords.length > 0">
                    <div class="table-responsive">
                        <table class="table table-striped table-bordered table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th v-for="col in columns" :key="col">{{ col }}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="row in meterRecords" :key="row.id">
                                    <td v-for="col in columns" :key="col">{{ row[col] }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <!-- Vue Pagination -->
                    <nav aria-label="Page navigation" v-if="totalPages > 1">
                        <ul class="pagination justify-content-center">
                            <li class="page-item" :class="{ disabled: currentPage === 1 }"><a class="page-link" href="#" @click.prevent="fetchMeterData(currentPage - 1)">上一頁</a></li>
                            <li class="page-item disabled"><span class="page-link">頁數：{{ currentPage }} / {{ totalPages }}</span></li>
                            <li class="page-item" :class="{ disabled: currentPage === totalPages }"><a class="page-link" href="#" @click.prevent="fetchMeterData(currentPage + 1)">下一頁</a></li>
                        </ul>
                    </nav>
                </div>
            </div>
            {% endraw %}
            {% endif %} {# END METER VALUES #}


            {# 新增用戶表單 或 資料表顯示 - This part is outside raw, so Jinja processes it #}
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
            {% elif page != "charge_station" and page != "meter_values" %} {# 如果不是架構圖頁面且不是 meter_values (因為 meter_values 由 Vue 處理)，就顯示資料表 #}
                <h3 class="mt-4 mb-3">
                    {# 動態標題 #}
                    {% if page == 'charge_points' %}充電樁管理
                    {% elif page == 'customer_management' and subpage == 'registered_users' %}已註冊用戶
                    {% elif page == 'customer_management' and subpage == 'authorized_users' %}已授權用戶
                    {% elif page == 'transactions' %}交易紀錄
                    {# meter_values title is handled by Vue now, but if you need a general title for other tables: #}
                    {% elif page == 'adr_events' %}ADR事件紀錄
                    {% else %}資料表
                    {% endif %}
                </h3>
                {% if datas %} {# 只有在有資料時才顯示表格 #}
                    <div class="table-responsive">
                        <table class="table table-striped table-bordered table-hover">
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
                                <a class="page-link" href="{{ url_for('home', page=page, subpage=subpage, page_num=current_page - 1) }}">上一頁</a>
                            </li>
                            <li class="page-item disabled"><span class="page-link">頁數：{{ current_page }} / {{ total_pages }}</span></li>
                            <li class="page-item {% if current_page == total_pages %}disabled{% endif %}">
                                <a class="page-link" href="{{ url_for('home', page=page, subpage=subpage, page_num=current_page + 1) }}">下一頁</a>
                            </li>
                        </ul>
                    </nav>
                    {% endif %}
                {% elif page != "customer_management" or (page == "customer_management" and subpage != "add_user") %} {# 避免在 add_user 頁面也顯示 "目前沒有資料" #}
                     <div class="alert alert-info" role="alert">
                       目前沒有資料。
                     </div>
                {% endif %} {# endif datas #}
            {% endif %} {# endif subpage == "add_user" / page != "charge_station" #}
        </div> <!-- end col-md-9 -->
    </div> <!-- end row -->
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
{# Original unpkg links - commented out for testing #}
{# <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script> #}
{# <script src="https://unpkg.com/konva@latest/konva.min.js"></script> #}
<script src="https://cdn.jsdelivr.net/npm/vue@3.4.27/dist/vue.global.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/konva@9.3.6/konva.min.js"></script>

<script>
// 從全域 Vue 物件中解構出需要的方法
const { ref, onMounted, computed, createApp } = Vue;

// Vue app for Meter Values
const meterValuesAppSetup = {
    setup() {
        const meterRecords = ref([]);
        const columns = ref([]);
        const chargePointOptions = ref([]);
        const selectedCpId = ref('');
        const currentPage = ref(1);
        const totalPages = ref(1);
        const loading = ref(true);

        const fetchMeterData = async (pageNum = 1) => {
            loading.value = true;
            currentPage.value = pageNum;
            let url = `{{ url_for('api_meter_values') }}?page_num=${currentPage.value}`;
            if (selectedCpId.value) {
                url += `&filter_cp_id=${selectedCpId.value}`;
            }
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                meterRecords.value = data.data;
                columns.value = data.columns;
                totalPages.value = data.total_pages;
                currentPage.value = data.current_page;
                if (chargePointOptions.value.length === 0 && data.charge_point_ids) {
                     chargePointOptions.value = data.charge_point_ids;
                }
            } catch (error) {
                console.error("Error fetching meter data:", error);
                meterRecords.value = [];
            } finally {
                loading.value = false;
            }
        };

        const clearFilter = () => {
            selectedCpId.value = '';
            fetchMeterData(1);
        };

        onMounted(() => {
            fetchMeterData();
        });

        return {
            meterRecords,
            columns,
            chargePointOptions,
            selectedCpId,
            currentPage,
            totalPages,
            loading,
            fetchMeterData,
            clearFilter
        };
    }
};

if (document.getElementById('meter-values-app')) {
    createApp(meterValuesAppSetup).mount('#meter-values-app');
}

// Vue app for Charge Station Diagram
const chargeStationDiagramAppSetup = {
    setup() {
        const konvaContainerRef = ref(null); // Ref for the Konva container div
        let stageInstance = null; // Holds Konva.Stage instance
        let mainLayer = null;     // Holds Konva.Layer instance
        let contentGroup = null;  // Group for all scalable content (background, sites)
        let tooltipLabel = null;  // Holds Konva.Label for tooltip

        const sites = ref([]); // Array of site objects {id, name, diagram_x, diagram_y}
        const siteStatuses = ref({}); // Object: { site_id: { available_guns: X, used_guns: Y } }
        const loading = ref(true);
        const csmsImageSrc = ref("{{ url_for('static', filename='csms.jpg') }}"); 

        const initialSiteCapacities = ref({}); // To store total guns per site
        // Reactive properties for stage dimensions and background image
        const stageConfig = ref({ width: 0, height: 0 });
        const konvaBgImage = ref(null); // Stores the loaded HTMLImageElement
        const contentScale = ref(1); // Scale factor for the content group

        // Reactive properties for tooltip
        const tooltipVisible = ref(false);
        const tooltipText = ref('');
        const tooltipConfig = ref({ x: 0, y: 0, opacity: 0.9 }); 

        const fetchSitesData = async () => {
            // This remains the same
            try {
                const response = await fetch("{{ url_for('api_get_charge_sites') }}"); // Jinja renders this URL
                if (!response.ok) throw new Error('Failed to fetch sites');
                sites.value = await response.json();
            } catch (error) {
                console.error("Error fetching sites:", error);
            }
        };

        const fetchSiteStatusesData = async () => {
            // This remains the same
            try {
                const response = await fetch("{{ url_for('api_get_charge_point_statuses') }}"); // Jinja renders this URL
                if (!response.ok) throw new Error('Failed to fetch site statuses');
                const statuses = await response.json();
                siteStatuses.value = statuses; // Assign to the ref
                // Store initial capacities
                Object.keys(statuses).forEach(siteId => {
                    const status = statuses[siteId];
                    initialSiteCapacities.value[siteId] = (status.available_guns || 0) + (status.used_guns || 0) + (status.other_status_guns || 0);
                });
            } catch (error) {
                console.error("Error fetching site statuses:", error);
            }
        };

        const loadBackgroundImageAndInitStage = () => {
            console.log("CS DIAGRAM: loadBackgroundImageAndInitStage() called. Image src:", csmsImageSrc.value);
            if (!konvaContainerRef.value) {
                console.error("CS DIAGRAM: konvaContainerRef is not available in loadBackgroundImageAndInitStage. Aborting.");
                loading.value = false; // Prevent infinite loading
                return;
            }

            const img = new window.Image(); // Use window.Image as Konva is global
            img.onload = () => {
                console.log("CS DIAGRAM: Background image LOADED. Dimensions:", img.width, "x", img.height);
                konvaBgImage.value = img; // Store the loaded image element

                // Calculate scale to fit image within the container dimensions
                // The stage dimensions (stageConfig) are already set from the container
                const containerWidth = stageConfig.value.width;
                const containerHeight = stageConfig.value.height;

                if (containerWidth > 0 && containerHeight > 0 && img.width > 0 && img.height > 0) {
                    const scaleX = containerWidth / img.width;
                    const scaleY = containerHeight / img.height;
                    contentScale.value = Math.min(scaleX, scaleY); // Maintain aspect ratio, fit entirely
                    console.log("CS DIAGRAM: Calculated contentScale:", contentScale.value, "based on container:", containerWidth, "x", containerHeight, "and image:", img.width, "x", img.height);
                } else {
                    contentScale.value = 1; // Default scale if dimensions are problematic
                    console.warn("CS DIAGRAM: Could not calculate scale, using 1. Container/Image dimensions might be zero.");
                }
                // The stageConfig (width/height of the canvas) should NOT change here. It's fixed by the container.
                // We scale the *content* (background image, sites) instead.
                // Drawing is handled by watchEffect
            };
            img.onerror = () => {
                console.error("CS DIAGRAM: Background image FAILED to load for Konva. Src:", img.src);
                // stageConfig is already set from container, no need to change it to fallback here
                konvaBgImage.value = null;
                contentScale.value = 1; // Reset scale
                // No need to set stage to fallback dimensions, it should use container's
                console.log("CS DIAGRAM: After img.onerror, stageConfig (container size):", JSON.parse(JSON.stringify(stageConfig.value)));
            };
            img.src = csmsImageSrc.value;
        };

        // Konva event handlers
        const handleKonvaMouseEnter = (konvaEvt) => {
            // console.log("CS DIAGRAM: MouseEnter site", konvaEvt.target.getParent()?.attrs?.siteData?.name || konvaEvt.target?.attrs?.siteData?.name);
            const group = konvaEvt.target.getParent() || konvaEvt.target; // Event might be on rect or group
            const site = group.attrs.siteData;
            if (!site || !stageInstance) return;

            // Adjust pointer position based on content group scale
            let pointerPosition = stageInstance.getPointerPosition();
            if (!pointerPosition) return;

            // If content is scaled, transform pointer to scaled coordinates
            // This part is not strictly needed if sites are on mainLayer and their coords are already scaled
            // But keeping it for reference if interaction with scaled contentGroup items was needed.
            // if (contentGroup && contentGroup.scaleX() !== 1) { 
            //     const transform = contentGroup.getAbsoluteTransform().copy().invert();
            //     pointerPosition = transform.point(pointerPosition);
            // }

            const status = siteStatuses.value[site.id] || { available_guns: 'N/A', used_guns: 'N/A' };
            
            tooltipText.value = `${site.name}\\n可用: ${status.available_guns}\\n使用中: ${status.used_guns}`;
            // Tooltip position needs to be in stage coordinates, not scaled content coordinates
            tooltipConfig.value.x = stageInstance.getPointerPosition().x + 15;
            tooltipConfig.value.y = stageInstance.getPointerPosition().y + 15;
            tooltipVisible.value = true;
            // Opacity is handled by the watcher for tooltipConfig
        };

        const handleKonvaMouseLeave = (konvaEvt) => {
            tooltipVisible.value = false;
        };

        const handleKonvaMouseMove = (konvaEvt) => {
            if (tooltipVisible.value && stageInstance) {
                let pointerPosition = stageInstance.getPointerPosition();
                if (!pointerPosition) return;
                // Tooltip position is in stage coordinates
                tooltipConfig.value.x = pointerPosition.x + 15;
                tooltipConfig.value.y = pointerPosition.y + 15;
            }
        };

        onMounted(async () => {
            console.log("CS DIAGRAM: onMounted() called. konvaContainerRef.value:", konvaContainerRef.value);
            loading.value = true;

            loadBackgroundImageAndInitStage();
            await Promise.all([fetchSitesData(), fetchSiteStatusesData()]);
            console.log("CS DIAGRAM: Data fetching complete. Sites:", sites.value.length, "Site Statuses:", Object.keys(siteStatuses.value).length);
            loading.value = false;

            // After loading is false, the v-show condition might change.
            // We need to wait for the DOM to update if konvaContainerRef was hidden.
            Vue.nextTick(() => {
                if (konvaContainerRef.value) {
                    const containerRect = konvaContainerRef.value.getBoundingClientRect();
                    stageConfig.value.width = containerRect.width;
                    stageConfig.value.height = Math.min(containerRect.width * (9/16), 600); // Or your preferred height logic
                    
                    console.log("CS DIAGRAM: Container dimensions for stage (after nextTick):", stageConfig.value.width, "x", stageConfig.value.height);

                    if (stageConfig.value.width > 0 && stageConfig.value.height > 0) {
                        if (!stageInstance) { // Initialize Konva stage if not already done
                            stageInstance = new Konva.Stage({
                                container: konvaContainerRef.value,
                                width: stageConfig.value.width,
                                height: stageConfig.value.height,
                            });
                            mainLayer = new Konva.Layer();
                            stageInstance.add(mainLayer);
                            contentGroup = new Konva.Group(); // Group for background image
                            mainLayer.add(contentGroup);
                            
                            tooltipLabel = new Konva.Label({ /* ... tooltip config ... */ });
                            tooltipLabel.add(new Konva.Tag({ fill: '#333', stroke: '#555', cornerRadius: 3, pointerDirection: 'down', pointerWidth: 10, pointerHeight: 10, lineJoin: 'round', shadowColor: 'black', shadowBlur: 5, shadowOpacity: 0.4 }));
                            tooltipLabel.add(new Konva.Text({ name: 'tooltipTextNode', text: '', fontFamily: 'Arial', fontSize: 12, padding: 8, fill: 'white' }));
                            mainLayer.add(tooltipLabel); // Tooltip is on mainLayer, not scaled
                            console.log("CS DIAGRAM: Konva Stage, Layer, ContentGroup, TooltipLabel initialized.");
                        } else { // If stage already exists (e.g. from a resize event later), just update size
                            stageInstance.width(stageConfig.value.width);
                            stageInstance.height(stageConfig.value.height);
                            console.log("CS DIAGRAM: Konva Stage dimensions updated.");
                        }
                        // Trigger recalculation of scale if image is already loaded
                        if (konvaBgImage.value) {
                            loadBackgroundImageAndInitStage(); // This will re-calculate scale based on new stageConfig
                        }
                    } else {
                        console.warn("CS DIAGRAM: Container dimensions are still zero after nextTick. Cannot initialize/update Konva stage properly.");
                    }
                } else {
                    console.error("CS DIAGRAM: konvaContainerRef is null after nextTick!");
                }
                console.log("CS DIAGRAM: onMounted complete (after nextTick). loading:", loading.value, "konvaBgImage present:", !!konvaBgImage.value, "stageConfig:", JSON.parse(JSON.stringify(stageConfig.value)));
            
                // Start simulation after everything is mounted and data is fetched
                if (Object.keys(siteStatuses.value).length > 0 && Object.keys(initialSiteCapacities.value).length > 0) {
                    console.log("CS DIAGRAM: Starting site status simulation.");
                    setInterval(() => {
                        Object.keys(siteStatuses.value).forEach(siteId => {
                            const totalGuns = initialSiteCapacities.value[siteId] || 5; // Fallback to 5 if not found
                            const currentStatus = siteStatuses.value[siteId];
                            if (!currentStatus) return; // Skip if status for siteId somehow disappeared

                            const currentOtherGuns = currentStatus.other_status_guns || 0;

                            let newUsedGuns = Math.floor(Math.random() * (totalGuns - currentOtherGuns + 1));
                            if (newUsedGuns < 0) newUsedGuns = 0;

                            let newAvailableGuns = totalGuns - newUsedGuns - currentOtherGuns;
                            if (newAvailableGuns < 0) newAvailableGuns = 0;

                            // Ensure consistency if rounding or logic makes sum exceed total temporarily
                            if (newUsedGuns + newAvailableGuns + currentOtherGuns > totalGuns) {
                                newAvailableGuns = totalGuns - newUsedGuns - currentOtherGuns;
                                if (newAvailableGuns < 0) newAvailableGuns = 0; // Recorrect if needed
                            }
                            currentStatus.used_guns = newUsedGuns; // Directly mutate the reactive object's properties
                            currentStatus.available_guns = newAvailableGuns;
                        });
                    }, 1000); // Update every 1 second
                }
            });
            // Drawing is handled by watchEffect
        });

        // Watch for changes to draw/redraw Konva elements
        Vue.watchEffect(() => {
            console.log(
                "CS DIAGRAM: watchEffect triggered. Loading:", loading.value, 
                "Stage OK:", !!(stageInstance && mainLayer), 
                "BG Image OK:", !!konvaBgImage.value, 
                "Sites count:", sites.value.length,
                "stageConfig:", JSON.parse(JSON.stringify(stageConfig.value)) 
            );

            if (!stageInstance || !mainLayer || !contentGroup || loading.value) {
                if(loading.value) console.log("CS DIAGRAM: watchEffect - still loading. Returning.");
                else if (!stageInstance || !mainLayer || !contentGroup) console.log("CS DIAGRAM: watchEffect - stage, layer or contentGroup not ready. Returning.");
                return;
            }
            
            if (stageConfig.value.width === 0) {
                console.warn("CS DIAGRAM: watchEffect - stageConfig.width is 0. Canvas might be hidden or drawing will be on 0-width canvas. Drawing aborted.");
                return; 
            }

            // Clear previous drawings
            console.log("CS DIAGRAM: watchEffect - Clearing previous drawings.");
            contentGroup.destroyChildren(); // Clear only children of contentGroup (i.e., the background image)
            mainLayer.find('.site-marker-group').forEach(group => group.destroy()); // Clear site markers from mainLayer

            // Apply scale ONLY to the content group (which will hold the background)
            if (contentGroup) {
                contentGroup.scaleX(contentScale.value);
                contentGroup.scaleY(contentScale.value);
                console.log("CS DIAGRAM: watchEffect - Applied scale", contentScale.value, "to contentGroup.");
            }            

            // 1. Draw Background Image
            if (konvaBgImage.value && stageConfig.value.width > 0) {
                console.log("CS DIAGRAM: watchEffect - Drawing background image.");
                // Background image dimensions are its original dimensions; scaling is handled by contentGroup
                const bgImage = new Konva.Image({
                    x: 0, y: 0,
                    image: konvaBgImage.value,
                    width: konvaBgImage.value.width,  // 使用圖片原始寬度
                    height: konvaBgImage.value.height, // 使用圖片原始高度
                    name: 'background-image' // Add a name for easier selection/removal
                });
                contentGroup.add(bgImage); // Add to contentGroup
            } else {
                console.warn("CS DIAGRAM: watchEffect - Background image not drawn. konvaBgImage:", !!konvaBgImage.value, "stageConfig.width:", stageConfig.value.width);
            }

            // 2. Draw Sites (directly on mainLayer, with scaled coordinates)
            console.log("CS DIAGRAM: watchEffect - Drawing", sites.value.length, "sites.");
            sites.value.forEach(site => {
                const group = new Konva.Group({
                    // Scale the original coordinates to fit the stage
                    x: site.diagram_x * contentScale.value,
                    y: site.diagram_y * contentScale.value,
                    name: 'site-marker-group', // Add a name for easier selection/removal
                    siteData: site // Store site data directly on the Konva node
                });

                const availableGuns = siteStatuses.value[site.id]?.available_guns ?? -1; // Default to -1 if status not found, to avoid red
                const rectFillColor = availableGuns === 0 ? 'rgba(220, 53, 69, 0.8)' : 'rgba(0, 123, 255, 0.7)'; // Red if 0, else blue
                const rectStrokeColor = availableGuns === 0 ? 'rgb(139, 0, 0)' : '#0056b3'; // Darker red for stroke, else default blue stroke


                group.add(new Konva.Rect({
                    width: 80, height: 40, // These are now absolute pixel values, not scaled
                    fill: rectFillColor, stroke: rectStrokeColor, strokeWidth: 2, cornerRadius: 5,
                    shadowColor: 'black', shadowBlur: 5, shadowOpacity: 0.3,
                    shadowOffsetX: 2, shadowOffsetY: 2
                }));
                group.add(new Konva.Text({
                    text: `${site.name}\\n(可用: ${siteStatuses.value[site.id]?.available_guns ?? 'N/A'})`, // Display site name and available guns
                    fontSize: 10, // Slightly smaller font if needed to fit more text
                    fill: 'white', 
                    padding: 5, align: 'center', verticalAlign: 'middle',
                    width: 80, height: 40, listening: false // Text doesn't need to listen for events
                }));
                // Tooltip functionality remains the same, triggered by mouseenter/leave/move on the group

                group.on('mouseenter', handleKonvaMouseEnter);
                group.on('mouseleave', handleKonvaMouseLeave);
                group.on('mousemove', handleKonvaMouseMove);
                mainLayer.add(group); // Add site markers directly to mainLayer
            });
            
            // Ensure tooltip is always on top, with checks
            if (tooltipLabel && mainLayer) { // Ensure mainLayer exists
                console.log("CS DIAGRAM: watchEffect - Attempting moveToTop. Tooltip parent:", tooltipLabel.getParent(), "Tooltip layer:", tooltipLabel.getLayer(), "MainLayer parent:", mainLayer.getParent());
                if (tooltipLabel.getLayer()) { // Check if it's part of a layer
                    tooltipLabel.moveToTop();
                } else {
                    console.warn("CS DIAGRAM: watchEffect - tooltipLabel has no layer or parent. Re-adding to mainLayer and then moveToTop.");
                    mainLayer.add(tooltipLabel); // Re-add it to the mainLayer (not contentGroup)
                    tooltipLabel.moveToTop();    // Now try moveToTop on mainLayer
                }
            }
            console.log("CS DIAGRAM: watchEffect - batchDraw called after moveToTop attempt.");
            mainLayer.batchDraw(); // Redraw the layer efficiently
        });

        // Watch for tooltip state changes to update the Konva Label
        Vue.watch([tooltipVisible, tooltipText, tooltipConfig], ([visible, text, config]) => {
            if (tooltipLabel) {
                tooltipLabel.visible(visible);
                const textNode = tooltipLabel.findOne('.tooltipTextNode');
                if (textNode) textNode.text(text);
                tooltipLabel.position({ x: config.x, y: config.y });
                tooltipLabel.opacity(config.opacity !== undefined ? config.opacity : 0.9);
                if (tooltipLabel.getLayer()) {
                    tooltipLabel.getLayer().batchDraw();
                }
            }
        }, { deep: true }); // Use deep watch for tooltipConfig object

        return { // Return values needed by the template
            loading,
            stageConfig, // Used for v-if/v-show
            konvaContainerRef, // For the div element
            sites, // Potentially for debugging or other template logic
            siteStatuses // Potentially for debugging
        };
    }
};

if (document.getElementById('charge-station-diagram-app')) {
    const app = createApp(chargeStationDiagramAppSetup);
    // app.use(VueKonva); // No longer using VueKonva plugin
    app.mount('#charge-station-diagram-app');
}

// Dynamically adjust body padding-top based on navbar height
function adjustBodyPadding() {
    const navbar = document.querySelector('.navbar.fixed-top');
    if (navbar) {
        document.body.style.paddingTop = navbar.offsetHeight + 'px';
    }
}

// Adjust on initial load
window.addEventListener('load', adjustBodyPadding);
// Adjust on window resize
window.addEventListener('resize', adjustBodyPadding);

</script>
</body>
</html>
"""


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

    return render_template_string(html_template, page=page, subpage=subpage, datas=datas, columns=columns,
                                  current_page=page_num, total_pages=total_pages)

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
