import os
import sqlite3
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

if getattr(sys, "frozen", False):
    APP_ROOT = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    APP_ROOT = Path(__file__).resolve().parent

DATA_ROOT = Path.home() / "AppData" / "Local" / "TeraAI"
DB_PATH = DATA_ROOT / "data" / "tera.db"
HOST = "127.0.0.1"
PORT = 5050


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def setup_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS learnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT NOT NULL,
            topic TEXT NOT NULL,
            note TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            output TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


app = Flask(__name__, template_folder="templates", static_folder="static")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/dashboard")
def dashboard():
    conn = get_db()
    tasks = [dict(x) for x in conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()]
    learnings = [dict(x) for x in conn.execute("SELECT * FROM learnings ORDER BY id DESC").fetchall()]
    conn.close()
    return jsonify({"tasks": tasks, "learnings": learnings})


@app.post("/api/tasks")
def create_task():
    payload = request.get_json(force=True)
    conn = get_db()
    conn.execute(
        "INSERT INTO tasks(area,title,description,status,created_at) VALUES(?,?,?,?,?)",
        (
            payload["area"],
            payload["title"],
            payload.get("description", ""),
            payload["status"],
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.post("/api/learnings")
def create_learning():
    payload = request.get_json(force=True)
    conn = get_db()
    conn.execute(
        "INSERT INTO learnings(area,topic,note,created_at) VALUES(?,?,?,?)",
        (
            payload["area"],
            payload["topic"],
            payload["note"],
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.post("/api/commands")
def run_command():
    payload = request.get_json(force=True)
    cmd = payload["command"]
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=25)
        output = (proc.stdout + "\n" + proc.stderr).strip()
    except Exception as exc:
        output = f"Erro ao executar: {exc}"

    conn = get_db()
    conn.execute(
        "INSERT INTO command_logs(command,output,created_at) VALUES(?,?,?)",
        (cmd, output, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "output": output})


@app.get("/api/export-db")
def export_db():
    export_path = DATA_ROOT / "exports" / "tera_export.db"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as src, sqlite3.connect(export_path) as dst:
        src.backup(dst)
    return send_file(export_path, as_attachment=True)


@app.post("/api/sync-github")
def sync_github():
    try:
        subprocess.run("git add .", shell=True, check=True, cwd=APP_ROOT)
        msg = f'TERA auto-sync {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        subprocess.run(f'git commit -m "{msg}"', shell=True, check=False, cwd=APP_ROOT)
        push = subprocess.run(
            "git push", shell=True, capture_output=True, text=True, check=False, cwd=APP_ROOT
        )
        return jsonify(
            {
                "ok": push.returncode == 0,
                "stdout": push.stdout,
                "stderr": push.stderr,
            }
        )
    except Exception as exc:
        return jsonify({"ok": False, "stderr": str(exc)}), 500


def open_browser():
    webbrowser.open(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    os.makedirs(DATA_ROOT / "data", exist_ok=True)
    os.makedirs(DATA_ROOT / "exports", exist_ok=True)
    setup_db()
    threading.Timer(1.0, open_browser).start()
    app.run(host=HOST, port=PORT, debug=False)
