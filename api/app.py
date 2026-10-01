import os
import time

import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "clienthub")
DB_USER = os.getenv("DB_USER", "clienthub_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "clienthub_pass")


def get_connection(retries=10, delay=3):
    """Ouvre une connexion MySQL (avec quelques tentatives au démarrage)."""
    last_error = None
    for _ in range(retries):
        try:
            return pymysql.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
            )
        except pymysql.MySQLError as e:
            last_error = e
            time.sleep(delay)
    raise last_error


def init_table():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS clients (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL
                )
                """
            )
    finally:
        conn.close()


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/clients", methods=["GET"])
def list_clients():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM clients ORDER BY id")
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@app.route("/clients", methods=["POST"])
def add_client():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "champ 'name' requis"}), 400
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO clients (name) VALUES (%s)", (name,))
            return jsonify({"id": cur.lastrowid, "name": name}), 201
    finally:
        conn.close()


if __name__ == "__main__":
    init_table()
    app.run(host="0.0.0.0", port=5000)
