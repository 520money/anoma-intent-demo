# Isometric Island 3D 预览
Intent-centric demo (prototype)
================================

This is a minimal prototype of an intent-centric app. It models:

- Intents: desired outcomes with parameters and tags
- Capabilities: what the system can do
- Solver: naive matcher to pick a capability and execute a handler
- CLI: create an intent and see the result

Quick start
-----------

Requirements: Python 3.9+

Run a transfer intent:

```bash
python -m src.cli transfer --param to=alice --param amount=10
```

Run a notify intent:

```bash
python -m src.cli notify --param to=bob --param text="hello"
```

JSON output:

```bash
python -m src.cli transfer --param to=alice --param amount=10 --json
```

Files
-----

- `src/intents.py`: intent and capability models; registry
- `src/solver.py`: naive solver and default registry/handlers
- `src/cli.py`: command-line entry point
 - `src/web.py`: minimal Flask web UI and JSON API

Web UI
------

Install Flask (one-time):

```bash
py -3 -m pip install flask
```

Run the web app:

```bash
py -3 -m src.web
```

Then open `http://127.0.0.1:5000` in your browser. Fill intent name, tags, and parameters, click Run.

Explain mode and Swap
---------------------

CLI explain and swap examples:

```bash
python -m src.cli swap --param from_token=ETH --param to_token=USDC --param amount=1 --explain
```

Web UI:
- Check "Explain" to show ranking details
- Swap example params:
```
from_token=ETH
to_token=USDC
amount=1
```

Notes
-----
- Matching weights: params have higher weight (0.7) than tags (0.3)
- If tags are left empty, the app infers tags from the intent name (transfer/notify/swap)

One-click start on Windows
--------------------------

Double-click `run_app.bat` to:
- Create a virtual environment (`.venv`) if missing
- Install dependencies from `requirements.txt`
- Start the web app on `http://127.0.0.1:5000`

Build Windows exe
-----------------

Create a standalone exe with PyInstaller:

```bash
build_exe.bat
```

After it completes, run (web or desktop):

```bash
dist\IntentDemo.exe
dist\IntentDemoGUI.exe
```

The web exe launches the browser automatically; the GUI exe opens a desktop window.

Desktop GUI (without browser)
-----------------------------

Run from source:

```bash
run_gui.bat
```

Deploy to Render (public URL)
-----------------------------

1. Push this repo to GitHub
2. On Render, create a new Web Service from this repo
3. It reads `render.yaml` automatically, or set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 2 -b 0.0.0.0:$PORT src.web:app`
4. After deploy, you get a public URL like `https://anoma-intent-demo.onrender.com`

Notes:
- The app binds to `0.0.0.0` and reads `$PORT` for cloud runtimes

基于 Three.js 的简易 3D 建模预览。使用 `world.json` 世界模型生成地形、道路、树林、建筑与地标，并可导出为 GLTF。

## 快速开始

1. 直接双击打开 `index.html` 即可离线运行。
   - 若浏览器阻止 `file://` 读取 `world.json`，页面会自动使用内置的默认模型。
2. 推荐使用本地静态服务器以确保能读取 `world.json`：
   - Python: `python -m http.server 8080`
   - Node: `npx serve -p 8080`
   - 然后访问 `http://localhost:8080/`。

## 目录结构

- `index.html` 页面与基础 UI（导出、重置视角）
- `src/main.js` Three.js 场景与生成逻辑
- `world.json` 世界模型（百分比坐标）

## 世界模型说明（简化）

```json
{
  "nodes": [ { "id": "camp", "type": "camp", "pos": { "x": 40, "y": 52 } } ],
  "edges": [ { "from": "beach", "to": "camp", "type": "road" } ]
}
```

- `type` 支持：`mountain` `building` `forest` `camp` `water` `landmark` `poi` `area`
- `edges.type` 支持：`road` `trail` `stairs`，`bridge: true` 表示桥面

## 导出

- 点击页面左上角“导出 GLB”，将下载 `island.glb.gltf`（JSON 版 glTF）。
- 如需二进制 `*.glb`，可改用 GLTFExporter 参数 `{ binary: true }`。

## 自定义

- 编辑 `world.json` 可调整兴趣点与道路；坐标为 0–100 的百分比，映射到方形岛屿。
- 在 `src/main.js` 中扩展几何体生成逻辑可获得更精细的外观。
