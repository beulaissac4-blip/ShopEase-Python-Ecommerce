
from flask import Flask, render_template, jsonify, request
import sqlite3

app = Flask(__name__)


# -----------------------------
# GET PRODUCTS
# -----------------------------
def get_products():
    connection = sqlite3.connect("shop.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return products


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# PRODUCTS API
# -----------------------------
@app.route("/products")
def products():
    return jsonify(get_products())


# -----------------------------
# CHECKOUT
# -----------------------------
@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    customer_name = data.get("customer_name")
    cart_items = data.get("items")

    if not customer_name or not cart_items:
        return jsonify({"error": "Customer name and cart are required"}), 400

    connection = sqlite3.connect("shop.db")
    cursor = connection.cursor()

    total_amount = 0
    order_items = []

    for item in cart_items:
        product_id = item.get("id")
        quantity = int(item.get("quantity", 1))

        if quantity <= 0:
            connection.close()
            return jsonify({"error": "Invalid quantity"}), 400

        cursor.execute(
            "SELECT name, price FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        if product:
            name, price = product
            total_amount += price * quantity
            order_items.append((name, quantity, price))

    if not order_items:
        connection.close()
        return jsonify({"error": "No valid products found"}), 400

    cursor.execute(
        "INSERT INTO orders (customer_name, total_amount) VALUES (?, ?)",
        (customer_name, total_amount)
    )

    order_id = cursor.lastrowid

    for name, quantity, price in order_items:
        cursor.execute(
            """
            INSERT INTO order_items
            (order_id, product_name, quantity, price)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, name, quantity, price)
        )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Order placed successfully!",
        "order_id": order_id,
        "total_amount": total_amount
    })


# -----------------------------
# ORDER HISTORY PAGE
# -----------------------------
@app.route("/orders")
def order_history():
    return render_template("orders.html")


# -----------------------------
# ORDER HISTORY API
# -----------------------------
@app.route("/api/orders")
def get_orders():
    connection = sqlite3.connect("shop.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, customer_name, total_amount, order_date
        FROM orders
        ORDER BY id DESC
    """)

    orders = [dict(row) for row in cursor.fetchall()]

    for order in orders:
        cursor.execute("""
            SELECT product_name, quantity, price
            FROM order_items
            WHERE order_id = ?
        """, (order["id"],))

        order["items"] = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return jsonify(orders)


# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@app.route("/admin")
def admin_dashboard():
    connection = sqlite3.connect("shop.db")
    cursor = connection.cursor()

    # Total Products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Total Orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    # Total Sales
    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders")
    total_sales = cursor.fetchone()[0]

    # Recent Orders
    cursor.execute("""
        SELECT id, customer_name, total_amount, order_date
        FROM orders
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_orders = cursor.fetchall()

    connection.close()

    return render_template(
        "admin.html",
        total_products=total_products,
        total_orders=total_orders,
        total_sales=total_sales,
        recent_orders=recent_orders
    )


# -----------------------------
# RUN APPLICATION
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
