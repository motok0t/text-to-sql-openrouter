"""Database setup script using only the built-in sqlite3 library.

Creates demo.db with three tables:
- clients (id, name, city, email)
- products (id, name, price)
- orders (id, client_id, product_id, quantity, order_date)

Adds 10 test records to each table, including Moscow residents in clients.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo.db")


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn):
    """Create the three tables: clients, products, orders."""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT,
            email TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL CHECK(price > 0)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            order_date TEXT NOT NULL DEFAULT (date('now')),
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.commit()


def insert_test_data(conn):
    """Insert 10 test records into each table."""
    cursor = conn.cursor()

    # 10 clients - including Moscow residents
    clients = [
        ("Андrei", "Москва", "andrei@test.com"),
        ("Мария", "Москва", "maria@test.com"),
        ("Олег", "СПб", "oleg@test.com"),
        ("Анна", "Казань", "anna@test.com"),
        ("Дмитрий", "Новосибирск", "dmitriy@test.com"),
        ("Елена", "Екатеринбург", "elena@test.com"),
        ("Игорь", "Нижний Новгород", "igor@test.com"),
        ("Светлана", "Казань", "svetlana@test.com"),
        ("Roman", "Москва", "roman@test.com"),
        ("Ольга", "СПб", "olga@test.com"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO clients (name, city, email) VALUES (?, ?, ?)", clients
    )

    # 10 products
    products = [
        ("Ноутбук", 45000.00),
        ("Мышка", 1500.50),
        ("Клавиатура", 3200.00),
        ("Монитор 24\"", 12000.00),
        ("Принтер", 8500.00),
        ("Камеры", 25000.00),
        ("Флешка 64GB", 850.00),
        ("Гарнитура", 3500.00),
        ("Веб-камера", 4500.00),
        ("Наушники", 2800.00),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO products (name, price) VALUES (?, ?)", products
    )

    # 10 orders (order_date has DEFAULT so we omit it from INSERT)
    orders = [
        (1, 1, 2),
        (2, 1, 3),
        (3, 2, 1),
        (4, 3, 4),
        (5, 4, 5),
        (6, 5, 6),
        (7, 6, 7),
        (8, 7, 8),
        (9, 8, 9),
        (10, 9, 10),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO orders (client_id, product_id, quantity) VALUES (?, ?, ?)",
        orders,
    )

    conn.commit()
    print("Inserted test data successfully.")


def main():
    """Main function: create database, tables, and insert test data."""
    # Remove existing database if present
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")

    conn = get_connection()

    print("Creating tables...")
    create_tables(conn)

    print("Inserting test data...")
    insert_test_data(conn)

    conn.close()

    print(f"Database setup complete! File: {DB_PATH}")


if __name__ == "__main__":
    main()