from flask import Flask, jsonify, render_template
from db_config import get_db_connection
import os

# Get absolute paths to frontend folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, "../frontend/templates")
STATIC_DIR = os.path.join(BASE_DIR, "../frontend/static")

# Create Flask app with custom template & static paths
app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

@app.route("/")
def home():
    return "Smart Canteen Backend Running 🚀"

@app.route("/menu")
def get_menu():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM menu WHERE available = TRUE")
        menu_items = cursor.fetchall()
        conn.close()
        return jsonify(menu_items)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/ui")
def ui():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
