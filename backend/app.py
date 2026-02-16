from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask import Flask, flash, jsonify, render_template, request, session, redirect, url_for
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

app.secret_key = "smart_canteen_secret_key"


@app.route("/")
def home():
    return render_template("index.html")


# @app.route("/menu")
# def get_menu():
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM menu WHERE available = TRUE")
#         menu_items = cursor.fetchall()
#         conn.close()
#         return jsonify(menu_items)
#     except Exception as e:
#         return jsonify({"error": str(e)})

# @app.route("/ui")
# def ui():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     if session.get("role") == "admin":
#         return redirect(url_for("admin_orders"))

#     return render_template(
#         "index.html",
#         logged_in=True,
#         username=session.get("user_name")
#     )


# @app.route("/dashboard")
# def user_dashboard():
#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     return render_template(
#         "user_dashboard.html",
#         user_name=session.get("user_name")
#     )





@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 🔑 fetch user by email ONLY
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )
        user = cursor.fetchone()
        conn.close()

        # 🔑 check hashed password
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]

            return redirect("/dashboard")

        flash("Invalid email or password")
        return redirect("/login")

    return render_template("login.html")




@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("user_dashboard.html")









@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'user')",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        # ✅ stay on same page, show message
        flash("Registration successful! Redirecting to login...")
        return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/order", methods=["POST"])
def order():
    if "user_id" not in session:
        return "Please login first ❌"

    data = request.get_json()
    item_id = data.get("item_id")
    user_id = session["user_id"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1️⃣ Create order
        cursor.execute(
            "INSERT INTO orders (user_id) VALUES (%s)",
            (user_id,)
        )
        order_id = cursor.lastrowid

        # 2️⃣ Add item to order_items
        cursor.execute(
            "INSERT INTO order_items (order_id, item_id, quantity) VALUES (%s, %s, %s)",
            (order_id, item_id, 1)
        )

        conn.commit()
        conn.close()

        return jsonify({
    "success": True,
    "order_id": order_id,
    "message": "Order placed successfully"
})


    except Exception as e:
        return f"Order failed ❌ {e}"


@app.route("/my-orders")
def my_orders():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT o.order_id, o.order_time, o.status, m.item_name, oi.quantity
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN menu m ON oi.item_id = m.item_id
        WHERE o.user_id = %s
        ORDER BY o.order_time DESC
    """, (user_id,))

    orders = cursor.fetchall()
    conn.close()

    return jsonify(orders)

@app.route("/admin/orders")
def admin_orders():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access denied ❌", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT o.order_id, o.order_time, o.status,
               u.name AS user_name,
               m.item_name, oi.quantity
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN menu m ON oi.item_id = m.item_id
        ORDER BY o.order_time DESC
    """)

    orders = cursor.fetchall()
    conn.close()

    return render_template("admin_orders.html", orders=orders)

@app.route("/admin/update-order-status", methods=["POST"])
def update_order_status():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    order_id = request.form["order_id"]
    status = request.form["status"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET status = %s WHERE order_id = %s",
        (status, order_id)
    )
    conn.commit()
    conn.close()

    flash("Order status updated successfully ✅")
    return redirect(url_for("admin_orders"))

@app.route("/menu")
def menu():
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT item_id, item_name, price FROM menu")
    items = cursor.fetchall()

    conn.close()
    return items



@app.route("/check-session")
def check_session():
    return str(dict(session))


# @app.route("/debug-session")
# def debug_session():
#     return str(dict(session))


if __name__ == "__main__":
    app.run(debug=True)
