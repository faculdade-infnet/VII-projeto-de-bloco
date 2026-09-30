import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("INSERT INTO user (username, password) VALUES ('admin', 'admin')")
cursor.execute("INSERT INTO user (username, password) VALUES ('jose', '1234')")

cursor.execute("INSERT INTO prediction (text, intent, owner_id) VALUES ('Meu pedido não chegou', 'reclamacao', 1)")
cursor.execute("INSERT INTO prediction (text, intent, owner_id) VALUES ('Quero cancelar minha compra', 'cancelamento', 1)")
cursor.execute("INSERT INTO prediction (text, intent, owner_id) VALUES ('Qual o prazo de entrega?', 'informacao', 2)")

conn.commit()
conn.close()