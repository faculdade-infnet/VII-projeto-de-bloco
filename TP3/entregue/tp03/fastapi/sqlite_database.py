import sqlite3
from database.connection import DATABASE_NAME

conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

# Apaga as tabelas antigas para o script poder ser executado de novo sem erro de usuário duplicado
cursor.execute("DROP TABLE IF EXISTS prediction")
cursor.execute("DROP TABLE IF EXISTS user")

cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)")
cursor.execute("CREATE TABLE IF NOT EXISTS prediction (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, intent TEXT NOT NULL, owner_id INTEGER NOT NULL, FOREIGN KEY (owner_id) REFERENCES user(id))")

cursor.execute("INSERT INTO user (username, password) VALUES ('admin', 'admin')")
cursor.execute("INSERT INTO user (username, password) VALUES ('jose', '1234')")
cursor.execute("INSERT INTO user (username, password) VALUES ('maria', '1234')")

cursor.execute("INSERT INTO prediction (text, intent, owner_id) VALUES ('Meu pedido não chegou', 'reclamacao', 1)")
cursor.execute("INSERT INTO prediction (text, intent, owner_id) VALUES ('Quero cancelar minha compra', 'cancelamento', 1)")
cursor.execute("INSERT INTO prediction (text, intent, owner_id) VALUES ('Qual o prazo de entrega?', 'informacao', 2)")

conn.commit()
conn.close()