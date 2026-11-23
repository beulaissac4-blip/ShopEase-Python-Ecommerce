
import sqlite3

def create_database():
    connection = sqlite3.connect("shop.db")
    cursor = connection.cursor()

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)

    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            total_amount REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Order items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    products = [
        (1, "Classic T-Shirt", 499, "fashion"),
        (2, "Headphones", 1499, "electronics"),
        (3, "Classic Watch", 999, "accessories"),
        (4, "Sport Shoes", 1299, "fashion"),
        (5, "Backpack", 799, "accessories"),
        (6, "Bluetooth Speaker", 1099, "electronics")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO products (id, name, price, category)
        VALUES (?, ?, ?, ?)
    """, products)

    connection.commit()
    connection.close()

if __name__ == "__main__":
    create_database()
    print("Database and order tables created successfully!")
