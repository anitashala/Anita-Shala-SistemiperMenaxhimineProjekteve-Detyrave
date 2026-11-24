import mysql.connector

from app import config


def get_db():
    """Dependency e FastAPI: hap një lidhje për çdo kërkesë dhe e mbyll në fund."""
    connection = mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
    )
    try:
        yield connection
    finally:
        connection.close()


def fetch_all(db, sql, params=()):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()


def fetch_one(db, sql, params=()):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return cursor.fetchone()
    finally:
        cursor.close()


def execute(db, sql, params=(), commit=True):
    """Ekzekuton INSERT/UPDATE/DELETE me parametra (kurrë tekst i bashkuar) dhe kthen ID-në e re."""
    cursor = db.cursor()
    try:
        cursor.execute(sql, params)
        last_id = cursor.lastrowid
    finally:
        cursor.close()
    if commit:
        db.commit()
    return last_id
