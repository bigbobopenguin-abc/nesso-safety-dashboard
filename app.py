import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request

DB_PATH = Path(__file__).resolve().parent / "nesso_sensor_data.db"

app = Flask(__name__)

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NESSO Safety Intelligence Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{--bg:#07111f;--surface:#0d1b2d;--surface2:#12243a;--border:#223955;--text:#f4f8fc;--muted:#91a4ba;--accent:#32b5ff;--accent2:#65d6c4;--warning:#f7b84b;--danger:#ff6474;--critical:#c084fc;--success:#42d392}
*{box-sizing:border-box} body{margin:0;background:linear-gradient(145deg,#06101d,#0b1830 55%,#07111f);color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif;min-height:100vh}.page{width:min(1550px,96%);margin:auto;padding:28px 0 44px}.topbar{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;margin-bottom:20px}.eyebrow{color:var(--accent2);font-size:12px;letter-spacing:.16em;font-weight:800;text-transform:uppercase}.topbar h1{font-size:31px;margin:5px 0 6px}.subtitle{margin:0;color:var(--muted)}.live-pill{background:rgba(66,211,146,.12);border:1px solid rgba(66,211,146,.35);color:#8ff0bd;padding:8px 12px;border-radius:999px;font-size:13px;font-weight:700}.panel,.metric,.chart-card{background:rgba(13,27,45,.92);border:1px solid var(--border);border-radius:15px;box-shadow:0 14px 35px rgba(0,0,0,.18)}.panel{padding:18px;margin-bottom:18px}.section-head{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:14px}.section-title{margin:0;font-size:18px}.section-note{color:var(--muted);font-size:12px}.filter-grid{display:grid;grid-template-columns:1.2fr 1fr 1fr .85fr;gap:12px}label{display:block;color:var(--muted);font-size:12px;margin-bottom:6px}input,select,button{width:100%;border:1px solid var(--border);border-radius:9px;background:var(--surface2);color:var(--text);padding:10px 12px;font-size:14px}input:focus,select:focus,button:focus{outline:2px solid var(--accent);outline-offset:1px}.button-row{display:flex;gap:9px;flex-wrap:wrap;margin-top:13px}.button-row button{width:auto;min-width:116px;cursor:pointer;font-weight:700}.primary{background:var(--accent);border-color:var(--accent);color:#04243a}.status-message{min-height:18px;color:var(--muted);font-size:13px;margin-top:11px}.metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:18px}.metric{padding:15px}.metric-label{font-size:12px;color:var(--muted);margin-bottom:7px}.metric-value{font-size:27px;font-weight:800}.metric small{color:var(--muted)}.charts-grid{display:grid;grid-template-columns:1.65fr 1fr;gap:14px;margin-bottom:18px}.chart-card{padding:17px;min-height:340px}.chart-wrap{height:275px}.latest-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}.worker-card{background:linear-gradient(150deg,var(--surface2),#0e1d30);border:1px solid var(--border);border-top:3px solid var(--accent);border-radius:13px;padding:15px;cursor:pointer;transition:.2s}.worker-card:hover{transform:translateY(-2px);border-color:#3d668f}.worker-card.near-miss{border-top-color:var(--warning)}.worker-card.stf{border-top-color:var(--danger)}.worker-card.ffh{border-top-color:var(--critical)}.worker-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}.worker-name{font-size:18px;font-weight:800}.event-badge{padding:4px 9px;border-radius:999px;background:rgba(255,255,255,.1);font-size:12px;font-weight:800}.worker-stats{display:grid;grid-template-columns:1fr 1fr;gap:8px}.worker-stat{background:rgba(3,12,24,.35);border-radius:8px;padding:8px}.worker-stat span{display:block;color:var(--muted);font-size:11px}.worker-stat strong{font-size:14px}.worker-time{color:var(--muted);font-size:11px;margin-top:10px}.table-wrapper{overflow:auto;max-height:570px;border:1px solid var(--border);border-radius:10px}table{width:100%;border-collapse:collapse;min-width:1180px}th,td{text-align:left;padding:10px;border-bottom:1px solid var(--border);white-space:nowrap;font-size:13px}th{position:sticky;top:0;background:#091527;color:#cfe6f7;z-index:2}tbody tr:hover{background:#142b45}tbody tr.near-miss{background:rgba(146,64,14,.28)}tbody tr.stf{background:rgba(153,27,27,.26)}tbody tr.ffh{background:rgba(88,28,135,.28)}.legend{display:flex;gap:12px;flex-wrap:wrap;color:var(--muted);font-size:12px}.dot{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:5px}.near-dot{background:var(--warning)}.stf-dot{background:var(--danger)}.ffh-dot{background:var(--critical)}.footer{margin-top:28px;padding:34px 20px;text-align:center;border:1px solid var(--border);border-radius:15px;background:rgba(13,27,45,.92);box-shadow:0 14px 35px rgba(0,0,0,.18)}.footer-title{margin:0;color:var(--text);font-size:21px;font-weight:800}.footer-module{margin:8px 0 2px;color:var(--accent);font-size:15px;font-weight:700}.footer-school{margin:0;color:#d7e4f0;font-size:14px}.footer-divider{width:72px;height:2px;border:0;background:var(--accent2);margin:20px auto}.footer-label{margin:0 0 9px;color:var(--muted);font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}.footer-team{margin:0;color:var(--text);font-size:14px;line-height:1.9}.footer-copy{margin:18px 0 0;color:var(--muted);font-size:12px}@media(max-width:1050px){.filter-grid{grid-template-columns:1fr 1fr}.metrics{grid-template-columns:repeat(2,1fr)}.charts-grid{grid-template-columns:1fr}}@media(max-width:620px){.topbar{display:block}.live-pill{display:inline-block;margin-top:12px}.filter-grid,.metrics{grid-template-columns:1fr}.button-row button{width:100%}}
</style>
</head>
<body>
<div class="page">
<header class="topbar">
    <div>
        <div class="eyebrow">
            Data Engineering Project · Nanyang Polytechnic
        </div>

        <h1>NESSO Safety Monitoring Dashboard</h1>

        <p class="subtitle">
            Interactive incident analytics and worker sensor records.
        </p>
    </div>
</header>
<section class="panel"><div class="section-head"><h2 class="section-title">Data filters</h2><span class="section-note">Charts and records update together</span></div><div class="filter-grid">
<div><label>Search worker</label><input id="workerSearch" type="search" list="workerOptions" placeholder="Type worker name"><datalist id="workerOptions"></datalist></div>
<div><label>Start date and time</label><input id="startDateTime" type="datetime-local"></div>
<div><label>End date and time</label><input id="endDateTime" type="datetime-local"></div>
<div><label>Event</label><select id="eventFilter"><option value="">All events</option><option>Standing</option><option>Walking</option><option>Running</option><option>Normal</option><option>Near Miss</option><option>STF</option><option>FFH</option><option>Calibrating</option></select></div>
</div><div class="button-row"><button id="applyButton" class="primary">Search data</button><button id="todayButton">Today</button><button id="dangerButton">Safety incidents</button><button id="resetButton">Clear filters</button></div><div id="statusMessage" class="status-message">Loading data...</div></section>
<section class="metrics"><div class="metric"><div class="metric-label">Records found</div><div id="totalCount" class="metric-value">0</div></div><div class="metric"><div class="metric-label">Workers found</div><div id="workerCount" class="metric-value">0</div></div><div class="metric"><div class="metric-label">Near Miss</div><div id="nearMissCount" class="metric-value">0</div></div><div class="metric"><div class="metric-label">STF</div><div id="stfCount" class="metric-value">0</div></div><div class="metric"><div class="metric-label">FFH</div><div id="ffhCount" class="metric-value">0</div></div></section>
<section class="charts-grid"><article class="chart-card"><div class="section-head"><h2 class="section-title">Daily safety incidents</h2><span class="section-note">Near Miss, STF and FFH by day</span></div><div class="chart-wrap"><canvas id="dailyChart"></canvas></div></article><article class="chart-card"><div class="section-head"><h2 class="section-title">Incident distribution</h2><span class="section-note">Click a segment to filter</span></div><div class="chart-wrap"><canvas id="eventChart"></canvas></div></article></section>
<section class="panel"><div class="section-head"><h2 class="section-title">Latest worker status</h2><span class="section-note">Click a worker card to filter</span></div><div id="latestWorkers" class="latest-grid">Loading...</div></section>
<section class="panel"><div class="section-head"><h2 class="section-title">Retrieved records</h2><div class="legend"><span><i class="dot near-dot"></i>Near Miss</span><span><i class="dot stf-dot"></i>STF</span><span><i class="dot ffh-dot"></i>FFH</span></div></div><div class="table-wrapper"><table><thead><tr><th>ID</th><th>Worker</th><th>Timestamp</th><th>Event</th><th>Acceleration</th><th>Gyroscope</th><th>Accel X</th><th>Accel Y</th><th>Accel Z</th><th>Gyro X</th><th>Gyro Y</th><th>Gyro Z</th></tr></thead><tbody id="dataRows"><tr><td colspan="12">Loading...</td></tr></tbody></table></div></section>
<footer class="footer">
    <h2 class="footer-title">NESSO Safety Monitoring Dashboard</h2>
    <p class="footer-module">Data Engineering Project</p>
    <p class="footer-school">Nanyang Polytechnic</p>
    <hr class="footer-divider">
    <p class="footer-label">Developed by</p>
    <p class="footer-team">
        Lee En Qi (Andrea)<br>
        Sia Yong Xing<br>
        Saniya Maria Sunil
    </p>
    <p class="footer-copy">© 2026 Nanyang Polytechnic</p>
</footer>
</div>
<script>
const workerSearch=document.getElementById('workerSearch'),workerOptions=document.getElementById('workerOptions'),startDateTime=document.getElementById('startDateTime'),endDateTime=document.getElementById('endDateTime'),eventFilter=document.getElementById('eventFilter'),statusMessage=document.getElementById('statusMessage'),dataRows=document.getElementById('dataRows'),latestWorkers=document.getElementById('latestWorkers');let dangerOnly=false,dailyChart,eventChart;
const esc=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');
function eventClass(e){return e==='Near Miss'?'near-miss':e==='STF'?'stf':e==='FFH'?'ffh':''} function num(v,d=3){v=Number(v);return Number.isFinite(v)?v.toFixed(d):'-'} function dbTime(v){return v?v.replace('T',' ')+':00':''}
function params(includeLimit=true){const p=new URLSearchParams(),w=workerSearch.value.trim(),s=dbTime(startDateTime.value),e=dbTime(endDateTime.value);if(w)p.set('worker',w);if(s)p.set('start',s);if(e)p.set('end',e);if(eventFilter.value)p.set('event',eventFilter.value);if(dangerOnly)p.set('danger_only','1');if(includeLimit)p.set('limit','2000');return p.toString()}
async function loadWorkers(){const r=await fetch('/api/workers');const a=await r.json();workerOptions.innerHTML=a.map(x=>`<option value="${esc(x)}"></option>`).join('')}
async function loadLatest(){try{const r=await fetch('/api/latest');const d=await r.json(),names=Object.keys(d).sort();latestWorkers.innerHTML=names.map(n=>{const x=d[n],c=eventClass(x.event);return `<article class="worker-card ${c}" data-worker="${esc(n)}"><div class="worker-top"><div class="worker-name">${esc(n)}</div><div class="event-badge">${esc(x.event)}</div></div><div class="worker-stats"><div class="worker-stat"><span>Acceleration</span><strong>${num(x.acceleration_magnitude_g)} g</strong></div><div class="worker-stat"><span>Gyroscope</span><strong>${num(x.gyroscope_magnitude_deg_s)}°/s</strong></div></div><div class="worker-time">Last reading: ${esc(x.timestamp)}</div></article>`}).join('');document.querySelectorAll('.worker-card').forEach(c=>c.onclick=()=>{workerSearch.value=c.dataset.worker;dangerOnly=false;refreshAll()})}catch(e){latestWorkers.textContent='Unable to load worker status.'}}
function metrics(s){totalCount.textContent=s.total_records??0;workerCount.textContent=s.worker_count??0;nearMissCount.textContent=s.near_miss_count??0;stfCount.textContent=s.stf_count??0;ffhCount.textContent=s.ffh_count??0}
function rows(a){dataRows.innerHTML=a.length?a.map(x=>`<tr class="${eventClass(x.event)}"><td>${x.id}</td><td>${esc(x.sensor_name)}</td><td>${esc(x.timestamp)}</td><td><strong>${esc(x.event)}</strong></td><td>${num(x.acceleration_magnitude_g)}</td><td>${num(x.gyroscope_magnitude_deg_s)}</td><td>${num(x.accel_x_g)}</td><td>${num(x.accel_y_g)}</td><td>${num(x.accel_z_g)}</td><td>${num(x.gyro_x_deg_s)}</td><td>${num(x.gyro_y_deg_s)}</td><td>${num(x.gyro_z_deg_s)}</td></tr>`).join(''):'<tr><td colspan="12">No records match the selected filters.</td></tr>'}
async function loadReadings(){statusMessage.textContent='Searching database...';try{const r=await fetch('/api/readings?'+params());const d=await r.json();if(!r.ok)throw new Error(d.error||'Unable to retrieve data');rows(d.readings);metrics(d.summary);statusMessage.textContent=`${d.summary.total_records} record(s) found. Showing a maximum of ${d.limit} rows.`}catch(e){statusMessage.textContent='Search error: '+e.message}}
async function loadCharts(){const r=await fetch('/api/charts?'+params(false)),d=await r.json();const labels=d.daily.map(x=>x.day),near=d.daily.map(x=>x.near_miss),stf=d.daily.map(x=>x.stf),ffh=d.daily.map(x=>x.ffh);if(dailyChart)dailyChart.destroy();dailyChart=new Chart(document.getElementById('dailyChart'),{type:'line',data:{labels,datasets:[{label:'Near Miss',data:near,tension:.3},{label:'STF',data:stf,tension:.3},{label:'FFH',data:ffh,tension:.3}]},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},plugins:{legend:{labels:{color:'#d7e4f0'}}},scales:{x:{ticks:{color:'#91a4ba'},grid:{color:'rgba(145,164,186,.08)'}},y:{beginAtZero:true,ticks:{color:'#91a4ba'},grid:{color:'rgba(145,164,186,.1)'}}}}});if(eventChart)eventChart.destroy();eventChart=new Chart(document.getElementById('eventChart'),{type:'doughnut',data:{labels:['Near Miss','STF','FFH'],datasets:[{data:[d.distribution.near_miss,d.distribution.stf,d.distribution.ffh]}]},options:{responsive:true,maintainAspectRatio:false,cutout:'64%',plugins:{legend:{position:'bottom',labels:{color:'#d7e4f0'}}},onClick:(evt,els)=>{if(els.length){eventFilter.value=['Near Miss','STF','FFH'][els[0].index];dangerOnly=false;refreshAll()}}}})}
async function refreshAll(){await Promise.all([loadReadings(),loadCharts(),loadLatest()])}
function today(){const n=new Date(),y=n.getFullYear(),m=String(n.getMonth()+1).padStart(2,'0'),d=String(n.getDate()).padStart(2,'0');startDateTime.value=`${y}-${m}-${d}T00:00`;endDateTime.value=`${y}-${m}-${d}T23:59`;dangerOnly=false;refreshAll()} function reset(){workerSearch.value='';startDateTime.value='';endDateTime.value='';eventFilter.value='';dangerOnly=false;refreshAll()}
applyButton.onclick=()=>{dangerOnly=false;refreshAll()};todayButton.onclick=today;dangerButton.onclick=()=>{eventFilter.value='';dangerOnly=true;refreshAll()};resetButton.onclick=reset;workerSearch.addEventListener('keydown',e=>{if(e.key==='Enter'){dangerOnly=false;refreshAll()}});(async()=>{await loadWorkers();await refreshAll();setInterval(loadLatest,5000)})();
</script>
</body></html>
"""


def get_connection():
    """Return a SQLite connection that exposes columns by name."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def database_is_ready():
    """Check that the database and required table exist."""
    if not DB_PATH.exists():
        return False

    try:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = 'sensor_readings'
                """
            ).fetchone()

        return row is not None

    except sqlite3.Error:
        return False


@app.route("/")
def home():
    return render_template_string(PAGE)


@app.route("/api/workers")
def workers():
    """Return every worker/sensor name currently stored in SQL."""
    if not database_is_ready():
        return jsonify([])

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT sensor_name
            FROM sensor_readings
            WHERE sensor_name IS NOT NULL
              AND TRIM(sensor_name) <> ''
            ORDER BY sensor_name COLLATE NOCASE
            """
        ).fetchall()

    return jsonify([row["sensor_name"] for row in rows])


@app.route("/api/latest")
def latest():
    """Return the newest reading for every worker in the database."""
    if not database_is_ready():
        return jsonify({})

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT reading.*
            FROM sensor_readings AS reading
            INNER JOIN (
                SELECT sensor_name, MAX(id) AS latest_id
                FROM sensor_readings
                GROUP BY sensor_name
            ) AS newest
                ON reading.id = newest.latest_id
            ORDER BY reading.sensor_name COLLATE NOCASE
            """
        ).fetchall()

    return jsonify({
        row["sensor_name"]: dict(row)
        for row in rows
    })


@app.route("/api/charts")
def charts():
    """Return daily incident totals and incident distribution for charts."""
    if not database_is_ready():
        return jsonify({"daily": [], "distribution": {"near_miss": 0, "stf": 0, "ffh": 0}})

    worker = request.args.get("worker", "").strip()
    start = request.args.get("start", "").strip()
    end = request.args.get("end", "").strip()
    event = request.args.get("event", "").strip()
    danger_only = request.args.get("danger_only", "") == "1"

    conditions = []
    parameters = []
    if worker:
        conditions.append("LOWER(sensor_name) LIKE LOWER(?)")
        parameters.append(f"%{worker}%")
    if start:
        conditions.append("timestamp >= ?")
        parameters.append(start)
    if end:
        conditions.append("timestamp <= ?")
        parameters.append(end)
    if danger_only:
        conditions.append("event IN ('Near Miss', 'STF', 'FFH')")
    elif event:
        conditions.append("event = ?")
        parameters.append(event)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    with get_connection() as connection:
        daily_rows = connection.execute(
            f"""
            SELECT substr(timestamp, 1, 10) AS day,
                   SUM(CASE WHEN event = 'Near Miss' THEN 1 ELSE 0 END) AS near_miss,
                   SUM(CASE WHEN event = 'STF' THEN 1 ELSE 0 END) AS stf,
                   SUM(CASE WHEN event = 'FFH' THEN 1 ELSE 0 END) AS ffh
            FROM sensor_readings
            {where_clause}
            GROUP BY substr(timestamp, 1, 10)
            HAVING near_miss > 0 OR stf > 0 OR ffh > 0
            ORDER BY day
            """,
            parameters,
        ).fetchall()

        distribution = connection.execute(
            f"""
            SELECT SUM(CASE WHEN event = 'Near Miss' THEN 1 ELSE 0 END) AS near_miss,
                   SUM(CASE WHEN event = 'STF' THEN 1 ELSE 0 END) AS stf,
                   SUM(CASE WHEN event = 'FFH' THEN 1 ELSE 0 END) AS ffh
            FROM sensor_readings
            {where_clause}
            """,
            parameters,
        ).fetchone()

    return jsonify({
        "daily": [dict(row) for row in daily_rows],
        "distribution": {key: (value or 0) for key, value in dict(distribution).items()},
    })


@app.route("/api/readings")
def readings():
    """
    Filter SQL data by:
    - worker: partial worker-name search
    - start: timestamp lower boundary
    - end: timestamp upper boundary
    - event: exact event
    - danger_only=1: Near Miss, STF and FFH
    - limit: maximum returned rows
    """
    if not database_is_ready():
        return jsonify({
            "error": (
                "nesso_sensor_data.db or the sensor_readings "
                "table was not found."
            )
        }), 404

    worker = request.args.get("worker", "").strip()
    start = request.args.get("start", "").strip()
    end = request.args.get("end", "").strip()
    event = request.args.get("event", "").strip()
    danger_only = request.args.get("danger_only", "") == "1"

    try:
        limit = int(request.args.get("limit", "2000"))
    except ValueError:
        limit = 2000

    limit = max(1, min(limit, 10000))

    conditions = []
    parameters = []

    if worker:
        conditions.append(
            "LOWER(sensor_name) LIKE LOWER(?)"
        )
        parameters.append(f"%{worker}%")

    if start:
        conditions.append("timestamp >= ?")
        parameters.append(start)

    if end:
        conditions.append("timestamp <= ?")
        parameters.append(end)

    if danger_only:
        conditions.append(
            "event IN ('Near Miss', 'STF', 'FFH')"
        )
    elif event:
        conditions.append("event = ?")
        parameters.append(event)

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    with get_connection() as connection:
        selected_rows = connection.execute(
            f"""
            SELECT *
            FROM sensor_readings
            {where_clause}
            ORDER BY timestamp DESC, id DESC
            LIMIT ?
            """,
            (*parameters, limit)
        ).fetchall()

        summary_row = connection.execute(
            f"""
            SELECT
                COUNT(*) AS total_records,
                COUNT(DISTINCT sensor_name) AS worker_count,

                SUM(
                    CASE WHEN event = 'Near Miss'
                    THEN 1 ELSE 0 END
                ) AS near_miss_count,

                SUM(
                    CASE WHEN event = 'STF'
                    THEN 1 ELSE 0 END
                ) AS stf_count,

                SUM(
                    CASE WHEN event = 'FFH'
                    THEN 1 ELSE 0 END
                ) AS ffh_count

            FROM sensor_readings
            {where_clause}
            """,
            parameters
        ).fetchone()

    summary = dict(summary_row)

    for key, value in summary.items():
        if value is None:
            summary[key] = 0

    return jsonify({
        "readings": [dict(row) for row in selected_rows],
        "summary": summary,
        "limit": limit
    })


if __name__ == "__main__":
    print(f"Database path: {DB_PATH}")
    print("Open this website in your browser:")
    print("http://127.0.0.1:5000")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
