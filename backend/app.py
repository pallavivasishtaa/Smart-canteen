from flask import Flask, jsonify
from db_config import get_db_connection

app = Flask(__name__)

@app.route("/")
def home():
    return "Smart Canteen Backend Running 🚀"

@app.route("/menu", methods=["GET"])
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

if __name__ == "__main__":
    app.run(debug=True)


