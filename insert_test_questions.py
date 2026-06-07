#!/usr/bin/env python3
import sqlite3

db = sqlite3.connect('quiz.db')

# Insert sample questions
questions = [
    ("What is 2+2?", "3", "4", "5", "6", "B", "beginner", "maths"),
    ("What is 5+5?", "10", "11", "12", "13", "A", "beginner", "maths"),
    ("What is 7+3?", "10", "11", "12", "13", "A", "beginner", "maths"),
    ("What is the capital of France?", "Berlin", "Paris", "London", "Madrid", "B", "beginner", "gk"),
    ("Which planet is closest to the Sun?", "Venus", "Mercury", "Earth", "Mars", "B", "beginner", "science"),
    ("What keyword defines a function in Python?", "func", "def", "function", "define", "B", "beginner", "python"),
    ("What is 10 * 10?", "100", "110", "120", "130", "A", "intermediate", "maths"),
    ("What is the capital of Japan?", "Tokyo", "Osaka", "Kyoto", "Yokohama", "A", "intermediate", "gk"),
    ("What is photosynthesis?", "Process of making food using sunlight", "Process of respiration", "Breaking down food", "None of the above", "A", "intermediate", "science"),
    ("What is a list in Python?", "A string of characters", "An ordered collection of items", "A dictionary", "A function", "B", "intermediate", "python"),
    ("What is 2^10?", "512", "1024", "2048", "4096", "B", "advanced", "maths"),
    ("Who wrote Romeo and Juliet?", "Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain", "B", "advanced", "gk"),
    ("What is the chemical formula for water?", "CO2", "H2O", "O2", "H2SO4", "B", "advanced", "science"),
    ("What is a decorator in Python?", "A function that modifies another function", "A class", "A variable", "A loop", "A", "advanced", "python"),
    ("What is 7 + 5?", "10", "11", "12", "13", "C", "beginner", "maths"),
    ("What is the area of a rectangle with sides 3 and 4?", "7", "12", "9", "14", "B", "beginner", "maths"),
    ("What is 9 * 8?", "72", "81", "69", "64", "A", "beginner", "maths"),
    ("Solve for x: 2x + 3 = 11.", "3", "4", "5", "6", "B", "intermediate", "maths"),
    ("What is 3/4 + 1/2?", "5/4", "1/4", "3/8", "5/8", "A", "intermediate", "maths"),
    ("What is the derivative of x^2?", "x", "2x", "x^2", "2", "B", "intermediate", "maths"),
    ("What is the integral of 1/x dx?", "ln|x| + C", "x + C", "1/(x^2) + C", "e^x + C", "A", "advanced", "maths"),
    ("What is sin(90°)?", "0", "1", "-1", "Undefined", "B", "advanced", "maths"),
    ("What is the limit of (1+1/n)^n as n approaches infinity?", "1", "e", "Infinity", "0", "B", "advanced", "maths"),
    # Science
    ("Which state of matter has a definite shape and volume?", "Liquid", "Gas", "Solid", "Plasma", "C", "beginner", "science"),
    ("What planet is known as the Red Planet?", "Venus", "Mars", "Jupiter", "Saturn", "B", "beginner", "science"),
    ("What gas do plants primarily absorb?", "Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen", "C", "beginner", "science"),
    ("What is the powerhouse of the cell?", "Nucleus", "Mitochondria", "Ribosome", "Golgi apparatus", "B", "intermediate", "science"),
    ("What is Newton's second law about?", "Action-reaction", "F = ma", "Energy conservation", "Gravitational force", "B", "intermediate", "science"),
    ("What is the chemical symbol for table salt's main ion?", "NaCl", "Na+", "Cl-", "K+", "B", "intermediate", "science"),
    ("Which law relates pressure and volume of a gas at constant temperature?", "Boyle's law", "Charles's law", "Ohm's law", "Hooke's law", "A", "advanced", "science"),
    ("What is the main chain in DNA made of?", "Amino acids", "Nucleotides", "Fatty acids", "Monosaccharides", "B", "advanced", "science"),
    ("Which form of energy is associated with motion of electrons?", "Thermal", "Chemical", "Electrical", "Nuclear", "C", "advanced", "science"),
    # General Knowledge (gk)
    ("What is the capital of France?", "Berlin", "Madrid", "Paris", "Rome", "C", "beginner", "gk"),
    ("Which ocean is the largest?", "Atlantic", "Indian", "Pacific", "Arctic", "C", "beginner", "gk"),
    ("Which organization was founded in 1945 to promote peace?", "NATO", "UN", "EU", "WHO", "B", "beginner", "gk"),
    ("Who wrote the play 'Romeo and Juliet'?", "Charles Dickens", "William Shakespeare", "Leo Tolstoy", "Mark Twain", "B", "intermediate", "gk"),
    ("Which continent is the Sahara Desert located in?", "Asia", "Africa", "Australia", "South America", "B", "intermediate", "gk"),
    ("What currency is used in Japan?", "Dollar", "Euro", "Yen", "Won", "C", "intermediate", "gk"),
    ("Which ancient wonder was located in the city of Giza?", "Hanging Gardens", "Colossus of Rhodes", "Great Pyramid", "Temple of Artemis", "C", "advanced", "gk"),
    ("What is the longest river in the world by most measures?", "Amazon", "Nile", "Yangtze", "Mississippi", "B", "advanced", "gk"),
    ("Which amendment in many constitutions protects freedom of speech?", "First", "Second", "Third", "Fourth", "A", "advanced", "gk"),
]

for q in questions:
    db.execute(
        "INSERT INTO questions (prompt, option_a, option_b, option_c, option_d, correct_option, level, topic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        q
    )

db.commit()

# Count questions
count = db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
print(f"✓ Inserted {len(questions)} questions")
print(f"Total questions: {count}")

# Show by level/topic
rows = db.execute("""
SELECT COUNT(*) as cnt, COALESCE(level, 'beginner') as level, COALESCE(topic, 'python') as topic
FROM questions
GROUP BY level, topic
ORDER BY level, topic
""").fetchall()

print("\nQuestions by level/topic:")
for row in rows:
    print(f"  {row[1]:12} {row[2]:8} {row[0]:3}")

db.close()
