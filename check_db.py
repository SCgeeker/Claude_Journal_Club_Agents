import sqlite3

conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM zettel_cards')
total = cursor.fetchone()[0]
print(f'Total cards: {total}')

cursor.execute('SELECT paper_id, COUNT(*) FROM zettel_cards GROUP BY paper_id')
print('Cards by paper:')
for row in cursor.fetchall():
    print(f'  Paper {row[0]}: {row[1]} cards')

conn.close()
