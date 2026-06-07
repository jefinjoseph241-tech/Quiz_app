#!/usr/bin/env python3
import sqlite3

db = sqlite3.connect('quiz.db')
db.row_factory = sqlite3.Row
rows = db.execute('SELECT COUNT(*) AS total, COALESCE(topic, "python") AS topic, level FROM questions GROUP BY topic, level ORDER BY topic, level').fetchall()
for r in rows:
    print(f'{r[0]:3} {r[1]:8} {r[2]:12}')
print()
total = db.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
print(f'Total questions: {total}')
db.close()
