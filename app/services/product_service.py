from app.database.db import get_connection


def save_product(product_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO products (
            brand_name,
            manufacturer,
            setid,
            approval_year
        )
        VALUES (?, ?, ?, ?)
    """, (
        product_data.get("brand_name"),
        product_data.get("manufacturer"),
        product_data.get("setid"),
        product_data.get("approval_year")
    ))

    conn.commit()
    conn.close()

    print("Product saved successfully.")