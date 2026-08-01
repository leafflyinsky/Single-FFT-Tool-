# -*- coding: utf-8 -*-
"""生成新的HTML文件"""

html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>振动信号分析工具 - 滤波增强版</title>
    <script src="/static/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        /* 上传区域 */
        .upload-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
        }

        .upload-area:hover {
            background: #f8f9ff;
            border-color: #764ba2;
        }

        .upload-area.dragover {
            background: #e8ebff;
            border-color: #764ba2;
        }

        .upload-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }

        .upload-text {
            font-size: 1.2em;
            color: #333;
            margin-bottom: 10px;
        }

        .upload-hint {
            color: #666;
            font-size: 0.9em;
        }

        .file-input {
            display: none;
        }

        .parameters {
            display: flex;
            gap: 20px;
            margin-top: 20px;
            align-items: center;
            flex-wrap: wrap;
        }

        .param-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .param-group label {
            font-weight: 600;
            color: #333;
        }

        .param-group input {
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
            width: 120px;
        }

        .param-group input:focus {
            outline: none;
            border-color: #667eea;
        }

        .analyze-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 1.1em;
            border-radius: 25px;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .analyze-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        /* 滤波器配置区域 */
        .filter-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }

        .filter-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .filter-list {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            min-height: 100px;
            background: #fafafa;
        }

        .filter-item {
            background: white;
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            transition: all 0.3s;
            position: relative;
        }

        .filter-item:hover {
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
        }

        .filter-item.dragging {
            opacity: 0.5;
            transform: scale(1.02);
        }

        .filter-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
        }

        .filter-checkbox {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }

        .filter-name {
            font-weight: 700;
            color: #764ba2;
            font-size: 1.1em;
            flex-grow: 1;
        }

        .filter-drag-handle {
            color: #999;
            font-size: 1.5em;
            cursor: move;
        }

        .filter-params {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }

        .filter-param {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .filter-param label {
            font-size: 0.9em;
            color: #666;
        }

        .filter-param input,
        .filter-param select {
            padding: 6px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.9em;
        }

        .filter-param input:focus,
        .filter-param select:focus {
            outline: none;
            border-color: #667eea;
        }

        /* 去趋势项多选样式 */
        .detrend-options {
            display: flex;
            gap: 20px;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }

        .detrend-option {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .detrend-option input[type="checkbox"] {
            width: 18px;
            height: 18px;
        }

        .detrend-option label {
            font-size: 0.9em;
            color: #333;
            cursor: pointer;
        }

        .btn-group {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }

        .reset-btn {
            background: #95a5a6;
            color: white;
            border: none;
            padding: 10px 25px;
            font-size: 1em;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .reset-btn:hover {
            background: #7f8c8d;
        }

        /* 加载状态 */
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* 结果区域 */
        .results-section {
            display: none;
            margin-top: 30px;
        }

        /* 对比布局 */
        .comparison-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        .comparison-column {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }

        .comparison-column h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.3em;
            text-align: center;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }

        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .chart-container h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.3em;
        }

        .chart-wrapper {
            position: relative;
            height: 350px;
        }

        /* 指标对比表 */
        .metrics-comparison {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .metrics-comparison h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.3em;
        }

        .metrics-table {
            width: 100%;
            border-collapse: collapse;
        }

        .metrics-table th,
        .metrics-table td {
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #eee;
        }

        .metrics-table th {
            background: linear-gradient(135deg, #667eea33 0%, #764ba233 100%);
            color: #764ba2;
            font-weight: 700;
        }

        .metrics-table tr:hover {
            background: #f8f9ff;
        }

        .metric-name {
            font-weight: 600;
            text-align: left;
            color: #333;
        }

        .change-positive {
            color: #27ae60;
        }

        .change-negative {
            color: #e74c3c;
        }

        /* 导出按钮 */
        .export-section {
            text-align: center;
            margin-top: 30px;
        }

        .export-btn {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            border-radius: 25px;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .export-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(39, 174, 96, 0.4);
        }

        /* 错误消息 */
        .error-message {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }

        /* 响应式 */
        @media (max-width: 1200px) {
            .comparison-container {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }

            .parameters {
                flex-direction: column;
                align-items: stretch;
            }

            .param-group {
                width: 100%;
            }

            .analyze-btn {
                width: 100%;
            }

            .filter-params {
                flex-direction: column;
            }

            .detrend-options {
                flex-direction: column;
            }

            .metrics-table {
                font-size: 0.9em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 振动信号分析工具</h1>
            <p>支持7种滤波方法 | 滤波前后对比分析 | 数据导出</p>
        </div>

        <!-- 文件上传区域 -->
        <div class="upload-section">
            <div class="upload-area" id="dropZone">
                <div class="upload-icon">📊</div>
                <div class="upload-text">拖拽CSV文件到这里，或点击选择文件</div>
                <div class="upload-hint">支持单行或多行数据，自动识别数值列</div>
                <input type="file" id="fileInput" class="file-input" accept=".csv,.txt">
            </div>

            <div class="parameters">
                <div class="param-group">
                    <label for="samplingRate">采样率 (Hz):</label>
                    <input type="number" id="samplingRate" value="1000" min="1">
                </div>
            </div>

            <div class="error-message" id="errorMsg"></div>
        </div>

        <!-- 滤波器配置区域 -->
        <div class="filter-section">
            <h2>🎛️ 信号处理设置</h2>
            <p style="color: #666; margin-bottom: 15px;">勾选启用的滤波器，拖动调整顺序（从上到下依次应用）</p>

            <div class="filter-list" id="filterList">
                <!-- 去趋势项（多选） -->
                <div class="filter-item" data-type="detrend">
                    <div class="filter-header">
                        <input type="checkbox" class="filter-checkbox" id="detrend_enabled">
                        <span class="filter-name">📊 去趋势项（可多选）</span>
                        <span class="filter-drag-handle">☰</span>
                    </div>
                    <div class="detrend-options">
                        <div class="detrend-option">
                            <input type="checkbox" id="detrend_mean">
                            <label for="detrend_mean">去均值</label>
                        </div>
                        <div class="detrend-option">
                            <input type="checkbox" id="detrend_linear" checked>
                            <label for="detrend_linear">去线性</label>
                        </div>
                        <div class="detrend-option">
                            <input type="checkbox" id="detrend_quadratic">
                            <label for="detrend_quadratic">去二次项</label>
                        </div>
                    </div>
                </div>

                <!-- 均值滤波 -->
                <div class="filter-item" data-type="mean">
                    <div class="filter-header">
                        <input type="checkbox" class="filter-checkbox" id="mean_enabled">
                        <span class="filter-name">📊 均值滤波（滑动平均）</span>
                        <span class="filter-drag-handle">☰</span>
                    </div>
                    <div class="filter-params">
                        <div class="filter-param">
                            <label>窗口大小:</label>
                            <input type="number" id="mean_window" value="5" min="3" max="20" step="1">
                        </div>
                    </div>
                </div>

                <!-- Hampel滤波 -->
                <div class="filter-item" data-type="hampel">
                    <div class="filter-header">
                        <input type="checkbox" class="filter-checkbox" id="hampel_enabled">
                        <span class="filter-name">🔍 Hampel滤波（异常值检测）</span>
                        <span class="filter-drag-handle">☰</span>
                    </div>
                    <div class="filter-params">
                        <div class="filter-param">
                            <label>窗口大小:</label>
                            <input type="number" id="hampel_window" value="5" min="3" step="2">
                        </div>
                        <div class="filter-param">
                            <label>阈值倍数:</label>
                            <input type="number" id="hampel_sigma" value="3" min="1" max="10" step="0.5">
                        </div>
                    </div>
                </div>

                <!-- 高通滤波 -->
                <div class="filter-item" data-type="highpass">
                    <div class="filter-header">
                        <input type="checkbox" class="filter-checkbox" id="highpass_enabled">
                        <span class="filter-name">⬆️ 高通滤波</span>
                        <span class="filter-drag-handle">☰</span>
                    </div>
                    <div class="filter-params">
                        <div class="filter-param">
                            <label>截止频率 (Hz):</label>
                            <input type="number" id="highpass_cutoff" value="10" min="1">
                        </div>
                        <div class="filter-param">
                            <label>滤波器阶数:</label>
                            <input type="number" id="highpass_order" value="4" min="1" max="10">
                        </div>
                    </div>
                </div>

                <!-- 带通滤波 -->
                <div class="filter-item" data-type="bandpass">
                    <div class="filter-header">
                        <input type="checkbox" class="filter-checkbox" id="bandpass_enabled">
                        <span class="filter-name">🎛️ 带通滤波</span>
                        <span class="filter-drag-handle">☰</span>
                    </div>
                    <div class="filter-params">
                        <div class="filter-param">
                            <label>低频截止 (Hz):</label>
                            <input type="number" id="bandpass_low" value="10" min="1">
                        </div>
                        <div class="filter-param">
                            <label>高频截止 (Hz):</label>
                            <input type="number" id="bandpass_high" value="500" min="1">
                        </div>
                        <div class="filter-param">
                            <label>滤波器阶数:</label>
                            <input type="number" id="bandpass_order" value="4" min="1" max="10">
                        </div>
                    </div>
                </div>

                <!-- SG滤波 -->
                <div class="filter-item" data-type="sg">
                    <div class="filter-header">
                        <input type="checkbox" class="filter-checkbox" id="sg_enabled">
                        <span class="filter-name">📈 SG滤波（平滑）</span>
                        <span class="filter-drag-handle">☰</span>
                    </div>
                    <div class="filter-params">
                        <div class="filter-param">
                            <label>窗口大小:</label>
                            <input type="number" id="sg_window" value="11" min="5" step="2">
                        </div>
                        <div class="filter-param">
                            <label>多项式阶数:</label>
                            <input type="number" id="sg_polyorder" value="3" min="1">
                        </div>
                    </div>
                </div>

                <!-- ACG自动增益 -->
                <div class="filter-item" data-type="acg">
                    <div class="filter-header">
                        <input type="checkbox" class="filter-checkbox" id="acg_enabled">
                        <span class="filter-name">🎚️ ACG自动增益</span>
                        <span class="filter-drag-handle">☰</span>
                    </div>
                    <div class="filter-params">
                        <div class="filter-param">
                            <label>目标RMS值:</label>
                            <input type="number" id="acg_target_rms" value="1.0" min="0.1" max="10" step="0.1">
                        </div>
                    </div>
                </div>
            </div>

            <div class="btn-group">
                <button class="reset-btn" onclick="resetFilters()">🔄 重置参数</button>
                <button class="analyze-btn" id="analyzeBtn" onclick="startAnalysis()" disabled>▶ 开始分析</button>
            </div>
        </div>

        <!-- 加载状态 -->
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>正在分析信号...</p>
        </div>

        <!-- 结果显示区域 -->
        <div class="results-section" id="resultsSection">
            <!-- 对比图表 -->
            <div class="comparison-container">
                <!-- 原始信号 -->
                <div class="comparison-column">
                    <h3>📊 原始信号</h3>
                    <div class="chart-container">
                        <div class="chart-wrapper">
                            <canvas id="originalWaveform"></canvas>
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-wrapper">
                            <canvas id="originalSpectrum"></canvas>
                        </div>
                    </div>
                </div>

                <!-- 滤波后信号 -->
                <div class="comparison-column">
                    <h3>📊 滤波后信号</h3>
                    <div class="chart-container">
                        <div class="chart-wrapper">
                            <canvas id="filteredWaveform"></canvas>
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-wrapper">
                            <canvas id="filteredSpectrum"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 指标对比表 -->
            <div class="metrics-comparison">
                <h3>📋 指标对比表</h3>
                <table class="metrics-table">
                    <thead>
                        <tr>
                            <th>指标名称</th>
                            <th>原始值</th>
                            <th>滤波后</th>
                            <th>变化</th>
                        </tr>
                    </thead>
                    <tbody id="metricsBody">
                        <!-- 动态生成 -->
                    </tbody>
                </table>
            </div>

            <!-- 导出按钮 -->
            <div class="export-section" id="exportSection" style="display: none;">
                <button class="export-btn" onclick="exportCSV()">📥 导出滤波后数据 (CSV)</button>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;
        let filtersApplied = false;
        let filteredData = null;

        // 图表实例
        let charts = {
            originalWaveform: null,
            originalSpectrum: null,
            filteredWaveform: null,
            filteredSpectrum: null
        };

        // 文件上传处理
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            selectedFile = file;
            document.getElementById('analyzeBtn').disabled = false;
            document.querySelector('.upload-text').textContent = `已选择: ${file.name}`;
            document.getElementById('errorMsg').style.display = 'none';
        }

        // 拖拽排序
        const filterList = document.getElementById('filterList');
        let draggedItem = null;

        filterList.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('filter-item')) {
                draggedItem = e.target;
                e.target.classList.add('dragging');
            }
        });

        filterList.addEventListener('dragend', (e) => {
            if (e.target.classList.contains('filter-item')) {
                e.target.classList.remove('dragging');
                draggedItem = null;
            }
        });

        filterList.addEventListener('dragover', (e) => {
            e.preventDefault();
            const afterElement = getDragAfterElement(filterList, e.clientY);
            if (draggedItem && afterElement) {
                filterList.insertBefore(draggedItem, afterElement);
            } else if (draggedItem) {
                filterList.appendChild(draggedItem);
            }
        });

        function getDragAfterElement(container, y) {
            const draggableElements = [...container.querySelectorAll('.filter-item:not(.dragging)')];

            return draggableElements.reduce((closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = y - box.top - box.height / 2;
                if (offset < 0 && offset > closest.offset) {
                    return { offset: offset, element: child };
                } else {
                    return closest;
                }
            }, { offset: Number.NEGATIVE_INFINITY }).element;
        }

        // 使滤波器项可拖拽
        document.querySelectorAll('.filter-item').forEach(item => {
            item.setAttribute('draggable', true);
        });

        // 获取滤波器配置
        function getFiltersConfig() {
            const filters = [];
            const filterItems = document.querySelectorAll('.filter-item');

            filterItems.forEach(item => {
                const type = item.dataset.type;
                const enabled = item.querySelector('.filter-checkbox').checked;
                let params = {};

                if (type === 'detrend') {
                    // 去趋势项多选
                    const detrendTypes = [];
                    if (document.getElementById('detrend_mean').checked) detrendTypes.push('mean');
                    if (document.getElementById('detrend_linear').checked) detrendTypes.push('linear');
                    if (document.getElementById('detrend_quadratic').checked) detrendTypes.push('quadratic');
                    params = {
                        types: detrendTypes
                    };
                } else if (type === 'mean') {
                    params = {
                        window_size: parseInt(document.getElementById('mean_window').value)
                    };
                } else if (type === 'hampel') {
                    params = {
                        window_size: parseInt(document.getElementById('hampel_window').value),
                        n_sigma: parseFloat(document.getElementById('hampel_sigma').value)
                    };
                } else if (type === 'highpass') {
                    params = {
                        cutoff_freq: parseFloat(document.getElementById('highpass_cutoff').value),
                        order: parseInt(document.getElementById('highpass_order').value)
                    };
                } else if (type === 'bandpass') {
                    params = {
                        low_freq: parseFloat(document.getElementById('bandpass_low').value),
                        high_freq: parseFloat(document.getElementById('bandpass_high').value),
                        order: parseInt(document.getElementById('bandpass_order').value)
                    };
                } else if (type === 'sg') {
                    params = {
                        window_size: parseInt(document.getElementById('sg_window').value),
                        polyorder: parseInt(document.getElementById('sg_polyorder').value)
                    };
                } else if (type === 'acg') {
                    params = {
                        target_rms: parseFloat(document.getElementById('acg_target_rms').value)
                    };
                }

                filters.push({
                    type: type,
                    enabled: enabled,
                    params: params
                });
            });

            return filters;
        }

        // 重置滤波器参数
        function resetFilters() {
            document.getElementById('detrend_mean').checked = false;
            document.getElementById('detrend_linear').checked = true;
            document.getElementById('detrend_quadratic').checked = false;
            document.getElementById('mean_window').value = '5';
            document.getElementById('hampel_window').value = '5';
            document.getElementById('hampel_sigma').value = '3';
            document.getElementById('highpass_cutoff').value = '10';
            document.getElementById('highpass_order').value = '4';
            document.getElementById('bandpass_low').value = '10';
            document.getElementById('bandpass_high').value = '500';
            document.getElementById('bandpass_order').value = '4';
            document.getElementById('sg_window').value = '11';
            document.getElementById('sg_polyorder').value = '3';
            document.getElementById('acg_target_rms').value = '1.0';

            // 取消所有勾选
            document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
                checkbox.checked = false;
            });
        }

        // 开始分析
        async function startAnalysis() {
            if (!selectedFile) return;

            const samplingRate = parseInt(document.getElementById('samplingRate').value) || 1000;
            const filtersConfig = getFiltersConfig();

            // 显示加载状态
            document.getElementById('loading').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';
            document.getElementById('errorMsg').style.display = 'none';
            document.getElementById('analyzeBtn').disabled = true;

            // 准备表单数据
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('sampling_rate', samplingRate);
            formData.append('filters', JSON.stringify(filtersConfig));

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    displayResults(data);
                } else {
                    showError(data.error || '分析失败');
                }
            } catch (error) {
                showError('请求失败: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('analyzeBtn').disabled = false;
            }
        }

        function showError(message) {
            const errorMsg = document.getElementById('errorMsg');
            errorMsg.textContent = message;
            errorMsg.style.display = 'block';
        }

        // 显示结果
        function displayResults(data) {
            document.getElementById('resultsSection').style.display = 'block';

            // 绘制原始信号图表
            drawWaveformChart('originalWaveform', data.original_waveform, '原始信号波形', 'rgb(102, 126, 234)');
            drawSpectrumChart('originalSpectrum', data.original_spectrum, '原始信号频谱', 'rgb(118, 75, 162)');

            // 绘制滤波后信号图表
            drawWaveformChart('filteredWaveform', data.filtered_waveform, '滤波后信号波形', 'rgb(39, 174, 96)');
            drawSpectrumChart('filteredSpectrum', data.filtered_spectrum, '滤波后信号频谱', 'rgb(46, 204, 113)');

            // 生成指标对比表
            generateMetricsTable(data.original_result, data.filtered_result);

            // 显示导出按钮（如果有滤波）
            filtersApplied = data.filters_applied;
            if (filtersApplied) {
                document.getElementById('exportSection').style.display = 'block';
                filteredData = data.filtered_waveform.amplitude;
            } else {
                document.getElementById('exportSection').style.display = 'none';
            }
        }

        // 绘制波形图
        function drawWaveformChart(canvasId, waveform, title, color) {
            const ctx = document.getElementById(canvasId).getContext('2d');

            if (charts[canvasId]) {
                charts[canvasId].destroy();
            }

            // 降采样
            const maxPoints = 1000;
            let time = waveform.time;
            let amplitude = waveform.amplitude;

            if (time.length > maxPoints) {
                const step = Math.ceil(time.length / maxPoints);
                time = time.filter((_, i) => i % step === 0);
                amplitude = amplitude.filter((_, i) => i % step === 0);
            }

            charts[canvasId] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: time.map(t => t.toFixed(3)),
                    datasets: [{
                        label: '加速度',
                        data: amplitude,
                        borderColor: color,
                        backgroundColor: color + '20',
                        borderWidth: 1.5,
                        fill: true,
                        tension: 0.1,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        title: {
                            display: true,
                            text: title,
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: '时间 (s)'
                            },
                            ticks: {
                                maxTicksLimit: 10
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: '加速度'
                            }
                        }
                    }
                }
            });
        }

        // 绘制频谱图
        function drawSpectrumChart(canvasId, spectrum, title, color) {
            const ctx = document.getElementById(canvasId).getContext('2d');

            if (charts[canvasId]) {
                charts[canvasId].destroy();
            }

            // 降采样
            const maxPoints = 500;
            let frequency = spectrum.frequency;
            let magnitude = spectrum.magnitude;

            if (frequency.length > maxPoints) {
                const step = Math.ceil(frequency.length / maxPoints);
                frequency = frequency.filter((_, i) => i % step === 0);
                magnitude = magnitude.filter((_, i) => i % step === 0);
            }

            charts[canvasId] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: frequency.map(f => f.toFixed(1)),
                    datasets: [{
                        label: '幅值',
                        data: magnitude,
                        borderColor: color,
                        backgroundColor: color + '20',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        title: {
                            display: true,
                            text: title,
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: '频率 (Hz)'
                            },
                            ticks: {
                                maxTicksLimit: 15
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: '幅值'
                            }
                        }
                    }
                }
            });
        }

        // 生成指标对比表
        function generateMetricsTable(original, filtered) {
            const tbody = document.getElementById('metricsBody');
            tbody.innerHTML = '';

            const metrics = [
                {
                    name: 'RMS (均方根)',
                    original: original.time_domain.rms,
                    filtered: filtered.time_domain.rms,
                    unit: '',
                    decimals: 4
                },
                {
                    name: '峰值 (Peak)',
                    original: original.time_domain.peak,
                    filtered: filtered.time_domain.peak,
                    unit: '',
                    decimals: 4
                },
                {
                    name: '峰值因子 (Crest Factor)',
                    original: original.time_domain.crest_factor,
                    filtered: filtered.time_domain.crest_factor,
                    unit: '',
                    decimals: 4
                },
                {
                    name: '峭度 (Kurtosis)',
                    original: original.time_domain.kurtosis,
                    filtered: filtered.time_domain.kurtosis,
                    unit: '',
                    decimals: 4
                },
                {
                    name: '均值 (Mean)',
                    original: original.time_domain.mean,
                    filtered: filtered.time_domain.mean,
                    unit: '',
                    decimals: 6
                },
                {
                    name: '标准差 (Std)',
                    original: original.time_domain.std,
                    filtered: filtered.time_domain.std,
                    unit: '',
                    decimals: 4
                },
                {
                    name: '主频 (Dominant Frequency)',
                    original: original.frequency_domain.dominant_freq,
                    filtered: filtered.frequency_domain.dominant_freq,
                    unit: ' Hz',
                    decimals: 2
                },
                {
                    name: '主频能量占比',
                    original: original.frequency_domain.energy_ratio,
                    filtered: filtered.frequency_domain.energy_ratio,
                    unit: ' %',
                    decimals: 2
                },
                {
                    name: '频谱中心 (Spectral Centroid)',
                    original: original.frequency_domain.spectral_centroid,
                    filtered: filtered.frequency_domain.spectral_centroid,
                    unit: ' Hz',
                    decimals: 2
                }
            ];

            metrics.forEach(metric => {
                const change = ((metric.filtered - metric.original) / metric.original * 100).toFixed(2);
                const changeClass = change > 0 ? 'change-positive' : (change < 0 ? 'change-negative' : '');
                const changeSymbol = change > 0 ? '+' : '';

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="metric-name">${metric.name}</td>
                    <td>${metric.original.toFixed(metric.decimals)}${metric.unit}</td>
                    <td>${metric.filtered.toFixed(metric.decimals)}${metric.unit}</td>
                    <td class="${changeClass}">${changeSymbol}${change}%</td>
                `;
                tbody.appendChild(row);
            });
        }

        // 导出CSV
        async function exportCSV() {
            if (!filteredData) {
                alert('没有可导出的数据');
                return;
            }

            const samplingRate = parseInt(document.getElementById('samplingRate').value) || 1000;

            try {
                const response = await fetch('/export', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        filtered_data: filteredData,
                        sampling_rate: samplingRate
                    })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = response.headers.get('Content-Disposition').split('filename=')[1];
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    const error = await response.json();
                    alert('导出失败: ' + error.error);
                }
            } catch (error) {
                alert('导出失败: ' + error.message);
            }
        }
    </script>
</body>
</html>
'''

# 写入文件
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML文件生成成功！")