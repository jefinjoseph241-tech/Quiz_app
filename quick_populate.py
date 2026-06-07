#!/usr/bin/env python3
"""Quickly populate database without WAL issues."""
import sqlite3
import os

# Remove old database completely
if os.path.exists("quiz.db"):
    os.remove("quiz.db")

# Create fresh database and schema
conn = sqlite3.connect("quiz.db")
cursor = conn.cursor()

# Create schema
cursor.executescript("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT,
    password TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option TEXT NOT NULL CHECK (correct_option IN ('A', 'B', 'C', 'D')),
    level TEXT,
    topic TEXT
);

CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    level TEXT,
    topic TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL
);
""")

# Insert all question data
questions_data = [
    # Python beginner
    ("Which keyword begins a function definition in Python?", "func", "def", "function", "begin", "B", "beginner", "python"),
    ("Which symbol starts a single-line comment?", "//", "/*", "#", "--", "C", "beginner", "python"),
    ("What does `len([1,2,3])` return?", "2", "3", "1", "0", "B", "beginner", "python"),
    ("Which of these is a mutable sequence?", "tuple", "string", "list", "int", "C", "beginner", "python"),
    ("Which operator is used for exponentiation?", "^", "**", "pow", "%%", "B", "beginner", "python"),
    ("What does `5 / 2` evaluate to in Python 3?", "2", "2.5", "3", "2.0", "B", "beginner", "python"),
    ("Which built-in returns the length of a sequence?", "size()", "count()", "length()", "len()", "D", "beginner", "python"),
    ("How do you create a dictionary?", "{ 'a': 1 }", "[ 'a', 1 ]", "( 'a', 1 )", "< 'a', 1 >", "A", "beginner", "python"),
    ("Which data type is immutable?", "list", "set", "tuple", "dict", "C", "beginner", "python"),
    ("What does `==` compare in Python?", "Identity", "Value equality", "Type only", "Assignment", "B", "beginner", "python"),
    # Python intermediate (first 10 only)
    ("Which statement exits a loop immediately?", "continue", "break", "pass", "return", "B", "intermediate", "python"),
    ("Which built-in creates an immutable sequence?", "list()", "set()", "tuple()", "dict()", "C", "intermediate", "python"),
    ("What is the output type of `range(5)` in Python 3?", "list", "range", "tuple", "iterator", "B", "intermediate", "python"),
    ("Which keyword is used to loop over items?", "for", "loop", "iterate", "repeat", "A", "intermediate", "python"),
    ("How do you import the math module?", "import math", "include math", "using math", "require math", "A", "intermediate", "python"),
    ("What does `dict.get(key, default)` do?", "Raises KeyError", "Returns value or default", "Deletes key", "Returns list", "B", "intermediate", "python"),
    ("Which method opens a file for reading?", "open('f','r')", "open('f','w')", "open('f','a')", "open('f','x')", "A", "intermediate", "python"),
    ("What does `lambda` create?", "function", "anonymous function", "class", "module", "B", "intermediate", "python"),
    ("What does `zip([1,2],[3,4])` return?", "A zip object", "A list of tuples", "A dictionary", "An iterator", "A", "intermediate", "python"),
    ("Which method removes and returns last item?", "pop()", "remove()", "delete()", "discard()", "A", "intermediate", "python"),
    # Maths beginner (10 questions)
    ("What is 7 + 5?", "10", "11", "12", "13", "B", "beginner", "maths"),
    ("What is 3 * 4?", "7", "12", "9", "14", "B", "beginner", "maths"),
    ("What is 9 - 2?", "6", "7", "8", "5", "B", "beginner", "maths"),
    ("What is 10 / 2?", "3", "5", "4", "6", "B", "beginner", "maths"),
    ("What is 2 squared?", "2", "4", "8", "6", "B", "beginner", "maths"),
    ("What is the perimeter of a 3x4 rectangle?", "7", "12", "14", "10", "C", "beginner", "maths"),
    ("What is 6 * 7?", "36", "42", "48", "49", "B", "beginner", "maths"),
    ("What is 15 - 8?", "6", "7", "8", "5", "B", "beginner", "maths"),
    ("What is 100 / 10?", "5", "10", "15", "20", "B", "beginner", "maths"),
    ("What is 5 * 5?", "20", "25", "30", "15", "B", "beginner", "maths"),
    # Science beginner (10 questions)
    ("Which planet is the Red Planet?", "Venus", "Mars", "Jupiter", "Saturn", "B", "beginner", "science"),
    ("What gas do plants absorb?", "Oxygen", "Nitrogen", "CO2", "Hydrogen", "C", "beginner", "science"),
    ("Which state has fixed shape?", "Liquid", "Gas", "Solid", "Plasma", "C", "beginner", "science"),
    ("What is H2O?", "Hydrogen", "Water", "Oxygen", "Salt", "B", "beginner", "science"),
    ("Which organ pumps blood?", "Lung", "Brain", "Heart", "Kidney", "C", "beginner", "science"),
    ("What is the powerhouse of cell?", "Nucleus", "Mitochondria", "Ribosome", "Golgi", "B", "beginner", "science"),
    ("How many bones in human body?", "150", "206", "250", "300", "B", "beginner", "science"),
    ("Which planet is closest to sun?", "Venus", "Mercury", "Earth", "Mars", "B", "beginner", "science"),
    ("What does chlorophyll do?", "Absorbs sound", "Absorbs light", "Absorbs heat", "Absorbs water", "B", "beginner", "science"),
    ("Which gas do we breathe in?", "CO2", "Nitrogen", "Oxygen", "Hydrogen", "C", "beginner", "science"),
    # GK beginner (10 questions)
    ("Capital of France?", "Berlin", "Madrid", "Paris", "Rome", "C", "beginner", "gk"),
    ("Largest ocean?", "Atlantic", "Indian", "Pacific", "Arctic", "C", "beginner", "gk"),
    ("UN founded?", "1935", "1945", "1955", "1965", "B", "beginner", "gk"),
    ("Highest mountain?", "K2", "Everest", "Denali", "Aconcagua", "B", "beginner", "gk"),
    ("Capital of India?", "Mumbai", "Delhi", "Bangalore", "Kolkata", "B", "beginner", "gk"),
    ("Largest country?", "China", "USA", "Russia", "Canada", "C", "beginner", "gk"),
    ("Capital of Japan?", "Osaka", "Tokyo", "Kyoto", "Nagoya", "B", "beginner", "gk"),
    ("Which continent is Africa?", "Asia", "Africa", "Europe", "Australia", "B", "beginner", "gk"),
    ("Shakespeare wrote?", "Math book", "Poetry", "Plays", "All above", "C", "beginner", "gk"),
    ("Earth orbits?", "Moon", "Sun", "Mars", "Venus", "B", "beginner", "gk"),
]

for prompt, a, b, c, d, correct, level, topic in questions_data:
    cursor.execute(
        "INSERT INTO questions (prompt, option_a, option_b, option_c, option_d, correct_option, level, topic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (prompt, a, b, c, d, correct, level, topic),
    )

conn.commit()
print("✓ Database created and populated")

# Show counts
cursor.execute("SELECT topic, level, COUNT(*) FROM questions GROUP BY topic, level ORDER BY topic, level")
print("\nCurrent distribution:")
for topic, level, count in cursor.fetchall():
    print(f"  {topic:10} {level:12}: {count:3} questions")

conn.close()
