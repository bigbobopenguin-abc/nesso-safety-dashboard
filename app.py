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
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>Nesso Safety Dashboard</title>

    <style>
        :root {
            --background: #0f172a;
            --panel: #111827;
            --panel-light: #1f2937;
            --border: #374151;
            --text: #f9fafb;
            --muted: #9ca3af;
            --accent: #38bdf8;
            --normal: #1f2937;
            --near-miss: #92400e;
            --near-miss-border: #f59e0b;
            --stf: #991b1b;
            --stf-border: #ef4444;
            --ffh: #581c87;
            --ffh-border: #c084fc;
            --success: #166534;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: var(--background);
            color: var(--text);
            font-family: Arial, Helvetica, sans-serif;
        }

        .page {
            width: min(1500px, 96%);
            margin: 0 auto;
            padding: 24px 0 40px;
        }

        h1 {
            margin: 0 0 6px;
            font-size: 30px;
        }

        .subtitle {
            margin: 0 0 22px;
            color: var(--muted);
        }

        .panel {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 18px;
        }

        .filter-grid {
            display: grid;
            grid-template-columns:
                minmax(180px, 1.2fr)
                minmax(180px, 1fr)
                minmax(180px, 1fr)
                minmax(150px, 0.8fr);
            gap: 14px;
        }

        label {
            display: block;
            margin-bottom: 6px;
            color: var(--muted);
            font-size: 14px;
        }

        input,
        select,
        button {
            width: 100%;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--panel-light);
            color: var(--text);
            padding: 10px 12px;
            font-size: 15px;
        }

        input:focus,
        select:focus,
        button:focus {
            outline: 2px solid var(--accent);
            outline-offset: 1px;
        }

        .button-row {
            display: flex;
            gap: 10px;
            margin-top: 14px;
            flex-wrap: wrap;
        }

        button {
            width: auto;
            min-width: 130px;
            cursor: pointer;
            font-weight: 600;
        }

        .primary-button {
            background: var(--accent);
            color: #082f49;
            border-color: var(--accent);
        }

        .status-message {
            margin-top: 12px;
            color: var(--muted);
            min-height: 20px;
        }

        .metrics {
            display: grid;
            grid-template-columns: repeat(5, minmax(130px, 1fr));
            gap: 12px;
            margin-bottom: 18px;
        }

        .metric {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 15px;
        }

        .metric-label {
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 7px;
        }

        .metric-value {
            font-size: 27px;
            font-weight: 700;
        }

        .latest-grid {
            display: grid;
            grid-template-columns: repeat(
                auto-fit,
                minmax(230px, 1fr)
            );
            gap: 12px;
        }

        .worker-card {
            border: 1px solid var(--border);
            border-left: 5px solid var(--accent);
            border-radius: 10px;
            padding: 14px;
            background: var(--panel-light);
        }

        .worker-card.near-miss {
            background: var(--near-miss);
            border-left-color: var(--near-miss-border);
        }

        .worker-card.stf {
            background: var(--stf);
            border-left-color: var(--stf-border);
        }

        .worker-card.ffh {
            background: var(--ffh);
            border-left-color: var(--ffh-border);
        }

        .worker-name {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .event-badge {
            display: inline-block;
            border-radius: 999px;
            padding: 4px 9px;
            font-size: 13px;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.16);
            margin-bottom: 8px;
        }

        .small {
            color: #d1d5db;
            font-size: 13px;
            margin: 5px 0;
        }

        .table-wrapper {
            overflow-x: auto;
            border: 1px solid var(--border);
            border-radius: 10px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 1180px;
        }

        th,
        td {
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid var(--border);
            white-space: nowrap;
            font-size: 14px;
        }

        th {
            position: sticky;
            top: 0;
            background: #0b1220;
            color: #dbeafe;
            z-index: 1;
        }

        tbody tr:hover {
            filter: brightness(1.15);
        }

        tbody tr.near-miss {
            background: var(--near-miss);
            border-left: 5px solid var(--near-miss-border);
        }

        tbody tr.stf {
            background: var(--stf);
            border-left: 5px solid var(--stf-border);
        }

        tbody tr.ffh {
            background: var(--ffh);
            border-left: 5px solid var(--ffh-border);
        }

        .section-title {
            margin: 0 0 14px;
            font-size: 20px;
        }

        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 12px;
            color: var(--muted);
            font-size: 13px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .legend-box {
            width: 15px;
            height: 15px;
            border-radius: 3px;
        }

        .near-box {
            background: var(--near-miss);
            border: 1px solid var(--near-miss-border);
        }

        .stf-box {
            background: var(--stf);
            border: 1px solid var(--stf-border);
        }

        .ffh-box {
            background: var(--ffh);
            border: 1px solid var(--ffh-border);
        }

        @media (max-width: 950px) {
            .filter-grid {
                grid-template-columns: 1fr 1fr;
            }

            .metrics {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 600px) {
            .filter-grid {
                grid-template-columns: 1fr;
            }

            .metrics {
                grid-template-columns: 1fr;
            }

            button {
                width: 100%;
            }
        }
    </style>
</head>

<body>
<div class="page">
    <h1>Nesso Safety Monitoring Dashboard</h1>
    <p class="subtitle">
        Search workers and retrieve sensor records by date, time and event.
    </p>

    <section class="panel">
        <h2 class="section-title">Filters</h2>

        <div class="filter-grid">
            <div>
                <label for="workerSearch">Search worker</label>
                <input
                    id="workerSearch"
                    type="search"
                    list="workerOptions"
                    placeholder="Type worker name"
                    autocomplete="off"
                >
                <datalist id="workerOptions"></datalist>
            </div>

            <div>
                <label for="startDateTime">Start date and time</label>
                <input id="startDateTime" type="datetime-local">
            </div>

            <div>
                <label for="endDateTime">End date and time</label>
                <input id="endDateTime" type="datetime-local">
            </div>

            <div>
                <label for="eventFilter">Event</label>
                <select id="eventFilter">
                    <option value="">All events</option>
                    <option value="Standing">Standing</option>
                    <option value="Walking">Walking</option>
                    <option value="Running">Running</option>
                    <option value="Normal">Normal</option>
                    <option value="Near Miss">Near Miss</option>
                    <option value="STF">STF</option>
                    <option value="FFH">FFH</option>
                    <option value="Calibrating">Calibrating</option>
                </select>
            </div>
        </div>

        <div class="button-row">
            <button id="applyButton" class="primary-button" type="button">
                Search data
            </button>

            <button id="todayButton" type="button">
                Today
            </button>

            <button id="dangerButton" type="button">
                Near Miss + STF
            </button>

            <button id="resetButton" type="button">
                Clear filters
            </button>
        </div>

        <div id="statusMessage" class="status-message" aria-live="polite">
            Loading data...
        </div>
    </section>

    <section class="metrics">
        <div class="metric">
            <div class="metric-label">Records found</div>
            <div id="totalCount" class="metric-value">0</div>
        </div>

        <div class="metric">
            <div class="metric-label">Workers found</div>
            <div id="workerCount" class="metric-value">0</div>
        </div>

        <div class="metric">
            <div class="metric-label">Near Miss</div>
            <div id="nearMissCount" class="metric-value">0</div>
        </div>

        <div class="metric">
            <div class="metric-label">STF</div>
            <div id="stfCount" class="metric-value">0</div>
        </div>

        <div class="metric">
            <div class="metric-label">FFH</div>
            <div id="ffhCount" class="metric-value">0</div>
        </div>
    </section>

    <section class="panel">
        <h2 class="section-title">Latest worker status</h2>
        <div id="latestWorkers" class="latest-grid">
            Loading...
        </div>
    </section>

    <section class="panel">
        <h2 class="section-title">Retrieved records</h2>

        <div class="legend">
            <div class="legend-item">
                <span class="legend-box near-box"></span>
                Near Miss
            </div>

            <div class="legend-item">
                <span class="legend-box stf-box"></span>
                STF
            </div>

            <div class="legend-item">
                <span class="legend-box ffh-box"></span>
                FFH
            </div>
        </div>

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Worker</th>
                        <th>Timestamp</th>
                        <th>Event</th>
                        <th>Acceleration</th>
                        <th>Gyroscope</th>
                        <th>Accel X</th>
                        <th>Accel Y</th>
                        <th>Accel Z</th>
                        <th>Gyro X</th>
                        <th>Gyro Y</th>
                        <th>Gyro Z</th>
                    </tr>
                </thead>

                <tbody id="dataRows">
                    <tr>
                        <td colspan="12">Loading...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
</div>

<script>
    const workerSearch = document.getElementById("workerSearch");
    const workerOptions = document.getElementById("workerOptions");
    const startDateTime = document.getElementById("startDateTime");
    const endDateTime = document.getElementById("endDateTime");
    const eventFilter = document.getElementById("eventFilter");

    const statusMessage = document.getElementById("statusMessage");
    const dataRows = document.getElementById("dataRows");
    const latestWorkers = document.getElementById("latestWorkers");

    let dangerOnly = false;

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function eventClass(eventName) {
        if (eventName === "Near Miss") {
            return "near-miss";
        }

        if (eventName === "STF") {
            return "stf";
        }

        if (eventName === "FFH") {
            return "ffh";
        }

        return "";
    }

    function displayNumber(value, decimals = 3) {
        const number = Number(value);

        if (!Number.isFinite(number)) {
            return "-";
        }

        return number.toFixed(decimals);
    }

    function convertInputToDatabaseTime(value) {
        if (!value) {
            return "";
        }

        return value.replace("T", " ") + ":00";
    }

    function buildQuery() {
        const params = new URLSearchParams();

        const worker = workerSearch.value.trim();
        const start = convertInputToDatabaseTime(startDateTime.value);
        const end = convertInputToDatabaseTime(endDateTime.value);
        const event = eventFilter.value;

        if (worker) {
            params.set("worker", worker);
        }

        if (start) {
            params.set("start", start);
        }

        if (end) {
            params.set("end", end);
        }

        if (event) {
            params.set("event", event);
        }

        if (dangerOnly) {
            params.set("danger_only", "1");
        }

        params.set("limit", "2000");

        return params.toString();
    }

    async function loadWorkers() {
        try {
            const response = await fetch("/api/workers");

            if (!response.ok) {
                throw new Error("Could not retrieve worker names.");
            }

            const workers = await response.json();

            workerOptions.innerHTML = workers
                .map(
                    worker =>
                        `<option value="${escapeHtml(worker)}"></option>`
                )
                .join("");
        } catch (error) {
            console.error(error);
        }
    }

    async function loadLatest() {
        try {
            const response = await fetch("/api/latest");

            if (!response.ok) {
                throw new Error("Could not retrieve latest worker data.");
            }

            const data = await response.json();
            const workerNames = Object.keys(data).sort();

            if (workerNames.length === 0) {
                latestWorkers.innerHTML = "No worker data is available.";
                return;
            }

            latestWorkers.innerHTML = workerNames
                .map(name => {
                    const reading = data[name];

                    if (!reading) {
                        return `
                            <article class="worker-card">
                                <div class="worker-name">
                                    ${escapeHtml(name)}
                                </div>
                                <div class="small">No data yet</div>
                            </article>
                        `;
                    }

                    const cssClass = eventClass(reading.event);

                    return `
                        <article class="worker-card ${cssClass}">
                            <div class="worker-name">
                                ${escapeHtml(name)}
                            </div>

                            <div class="event-badge">
                                ${escapeHtml(reading.event)}
                            </div>

                            <div class="small">
                                Acceleration:
                                ${displayNumber(
                                    reading.acceleration_magnitude_g
                                )} g
                            </div>

                            <div class="small">
                                Gyroscope:
                                ${displayNumber(
                                    reading.gyroscope_magnitude_deg_s
                                )} deg/s
                            </div>

                            <div class="small">
                                ${escapeHtml(reading.timestamp)}
                            </div>
                        </article>
                    `;
                })
                .join("");
        } catch (error) {
            latestWorkers.innerHTML =
                `Latest data error: ${escapeHtml(error.message)}`;
        }
    }

    function updateMetrics(summary) {
        document.getElementById("totalCount").textContent =
            summary.total_records ?? 0;

        document.getElementById("workerCount").textContent =
            summary.worker_count ?? 0;

        document.getElementById("nearMissCount").textContent =
            summary.near_miss_count ?? 0;

        document.getElementById("stfCount").textContent =
            summary.stf_count ?? 0;

        document.getElementById("ffhCount").textContent =
            summary.ffh_count ?? 0;
    }

    function renderRows(readings) {
        if (readings.length === 0) {
            dataRows.innerHTML = `
                <tr>
                    <td colspan="12">
                        No records match the selected filters.
                    </td>
                </tr>
            `;
            return;
        }

        dataRows.innerHTML = readings
            .map(reading => {
                const cssClass = eventClass(reading.event);

                return `
                    <tr class="${cssClass}">
                        <td>${escapeHtml(reading.id)}</td>
                        <td>${escapeHtml(reading.sensor_name)}</td>
                        <td>${escapeHtml(reading.timestamp)}</td>
                        <td><strong>${escapeHtml(reading.event)}</strong></td>

                        <td>
                            ${displayNumber(
                                reading.acceleration_magnitude_g
                            )}
                        </td>

                        <td>
                            ${displayNumber(
                                reading.gyroscope_magnitude_deg_s
                            )}
                        </td>

                        <td>${displayNumber(reading.accel_x_g)}</td>
                        <td>${displayNumber(reading.accel_y_g)}</td>
                        <td>${displayNumber(reading.accel_z_g)}</td>

                        <td>${displayNumber(reading.gyro_x_deg_s)}</td>
                        <td>${displayNumber(reading.gyro_y_deg_s)}</td>
                        <td>${displayNumber(reading.gyro_z_deg_s)}</td>
                    </tr>
                `;
            })
            .join("");
    }

    async function loadReadings() {
        statusMessage.textContent = "Searching database...";

        try {
            const response = await fetch(
                `/api/readings?${buildQuery()}`
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(
                    errorData.error || "Unable to retrieve data."
                );
            }

            const data = await response.json();

            renderRows(data.readings);
            updateMetrics(data.summary);

            statusMessage.textContent =
                `${data.summary.total_records} record(s) found. ` +
                `Showing a maximum of ${data.limit} rows.`;
        } catch (error) {
            statusMessage.textContent =
                `Search error: ${error.message}`;

            dataRows.innerHTML = `
                <tr>
                    <td colspan="12">
                        ${escapeHtml(error.message)}
                    </td>
                </tr>
            `;
        }
    }

    function setTodayFilter() {
        const now = new Date();

        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, "0");
        const day = String(now.getDate()).padStart(2, "0");

        startDateTime.value = `${year}-${month}-${day}T00:00`;
        endDateTime.value = `${year}-${month}-${day}T23:59`;

        dangerOnly = false;
        loadReadings();
    }

    function resetFilters() {
        workerSearch.value = "";
        startDateTime.value = "";
        endDateTime.value = "";
        eventFilter.value = "";
        dangerOnly = false;

        loadReadings();
    }

    document
        .getElementById("applyButton")
        .addEventListener("click", () => {
            dangerOnly = false;
            loadReadings();
        });

    document
        .getElementById("todayButton")
        .addEventListener("click", setTodayFilter);

    document
        .getElementById("dangerButton")
        .addEventListener("click", () => {
            eventFilter.value = "";
            dangerOnly = true;
            loadReadings();
        });

    document
        .getElementById("resetButton")
        .addEventListener("click", resetFilters);

    workerSearch.addEventListener("keydown", event => {
        if (event.key === "Enter") {
            dangerOnly = false;
            loadReadings();
        }
    });

    async function initialise() {
        await loadWorkers();
        await Promise.all([
            loadReadings(),
            loadLatest()
        ]);

        // Refresh only the latest worker cards every 3 seconds.
        setInterval(loadLatest, 3000);
    }

    initialise();
</script>
</body>
</html>
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
