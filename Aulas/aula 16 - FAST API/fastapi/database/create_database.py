import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")
cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)")
cursor.execute("CREATE TABLE IF NOT EXISTS prediction (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, intent TEXT NOT NULL, owner_id INTEGER NOT NULL, FOREIGN KEY (owner_id) REFERENCES user(id))")

conn.commit()
conn.close()