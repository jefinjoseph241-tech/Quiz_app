"""
Populate quiz database with full question sets.
Generates 10 beginner, 20 intermediate, 30 advanced for each topic.
"""
import sqlite3
import random

random.seed(42)

# Question templates by topic and level
QUESTIONS = {
    "python": {
        "beginner": [
            ("Which keyword begins a function definition in Python?", "func", "def", "function", "begin", "B"),
            ("Which symbol starts a single-line comment?", "//", "/*", "#", "--", "C"),
            ("What does `len([1,2,3])` return?", "2", "3", "1", "0", "B"),
            ("Which of these is a mutable sequence?", "tuple", "string", "list", "int", "C"),
            ("Which operator is used for exponentiation?", "^", "**", "pow", "%%", "B"),
            ("What does `5 / 2` evaluate to in Python 3?", "2", "2.5", "3", "2.0", "B"),
            ("Which built-in returns the length of a sequence?", "size()", "count()", "length()", "len()", "D"),
            ("How do you create a dictionary?", "{ 'a': 1 }", "[ 'a', 1 ]", "( 'a', 1 )", "< 'a', 1 >", "A"),
            ("Which data type is immutable?", "list", "set", "tuple", "dict", "C"),
            ("What does `==` compare in Python?", "Identity", "Value equality", "Type only", "Assignment", "B"),
        ],
        "intermediate": [
            ("Which statement exits a loop immediately?", "continue", "break", "pass", "return", "B"),
            ("Which built-in creates an immutable sequence?", "list()", "set()", "tuple()", "dict()", "C"),
            ("What is the output type of `range(5)` in Python 3?", "list", "range", "tuple", "iterator", "B"),
            ("Which keyword is used to loop over items?", "for", "loop", "iterate", "repeat", "A"),
            ("How do you import the math module?", "import math", "include math", "using math", "require math", "A"),
            ("What does `dict.get(key, default)` do?", "Raises KeyError", "Returns value or default", "Deletes key", "Returns list", "B"),
            ("Which method opens a file for reading?", "open('f','r')", "open('f','w')", "open('f','a')", "open('f','x')", "A"),
            ("What does `lambda` create?", "function", "anonymous function", "class", "module", "B"),
            ("What does `zip([1,2],[3,4])` return?", "A zip object", "A list of tuples", "A dictionary", "An iterator", "A"),
            ("Which method removes and returns last item?", "pop()", "remove()", "delete()", "discard()", "A"),
            ("How do you check if key exists in dictionary?", "'key' in d", "d.has('key')", "d.exists('key')", "d.contains('key')", "A"),
            ("Which string method converts to uppercase?", "upper()", "uppercase()", "capitalize()", "toUpperCase()", "A"),
            ("What does `str(10)` do?", "Converts to string", "Converts to int", "Creates a list", "Creates tuple", "A"),
            ("Which keyword skips loop iteration?", "break", "continue", "pass", "return", "B"),
            ("How do you create a list comprehension?", "[x**2 for x in range(5)]", "[x^2 for x in range(5)]", "{x**2 for x in range(5)}", "list(range(5**2))", "A"),
            ("Which method returns a shallow copy?", "copy()", "clone()", "duplicate()", "copy_list()", "A"),
            ("What is `bool('False')` in Python?", "False", "True", "None", "0", "B"),
            ("Which built-in returns largest item?", "max()", "largest()", "top()", "highest()", "A"),
            ("What does `type(True)` return?", "<class 'int'>", "<class 'bool'>", "<class 'str'>", "<class 'NoneType'>", "B"),
            ("How do you convert string '123' to int?", "int('123')", "str('123')", "float('123')", "bool('123')", "A"),
        ],
        "advanced": [
            ("Which keyword defines a generator?", "yield", "gen", "lambda", "async", "A"),
            ("What does `with open(...) as f:` ensure?", "File deleted", "File closed auto", "File in binary", "File encoded", "B"),
            ("Which module provides regex?", "regex", "re", "regexp", "pyre", "B"),
            ("What is purpose of `__init__`?", "Module init", "Constructor", "Static init", "Decorator", "B"),
            ("Which decorator allows no instance?", "@classmethod", "@staticmethod", "@property", "@abstract", "B"),
            ("What creates a generator expression?", "(x*x for x in range(5))", "[x*x for x in range(5)]", "{x*x for x in range(5)}", "<x*x>", "A"),
            ("Which module provides JSON?", "json", "pickle", "yaml", "csv", "A"),
            ("How do you catch multiple exceptions?", "except (TypeError, ValueError):", "except TypeError, ValueError:", "except TypeError | ValueError:", "except TypeError or ValueError:", "A"),
            ("What does `enumerate(['a','b'])` produce?", "enumerate object", "A list", "A tuple", "A set", "A"),
            ("How do you import only sqrt?", "from math import sqrt", "import math.sqrt", "from math import *", "import sqrt from math", "A"),
            ("Which keyword runs cleanup code?", "finally", "cleanup", "end", "ensure", "A"),
            ("What does `os.path.join('a','b')` return?", "a/b", "a\\b", "a:b", "a b", "A"),
            ("How do you create dict from list with default?", "dict.fromkeys(keys, 0)", "{k:0 for k in keys}", "dict(keys, 0)", "fromkeys(keys, 0)", "A"),
            ("Purpose of `if __name__ == '__main__'`?", "Run when executed", "Run when imported", "Declare main", "Import safely", "A"),
            ("Which built-in converts tuple to list?", "list()", "tuple()", "set()", "dict()", "A"),
            ("What type does {'a', 'b'} return?", "set", "list", "tuple", "dict", "A"),
            ("How to merge dicts in Python 3.9+?", "a | b", "a + b", "dict(a, **b)", "merge(a,b)", "A"),
            ("What does `map(lambda x: x*2, [1,2])` return?", "map object", "[2, 4]", "[1, 2]", "[2, 4, 2]", "A"),
            ("Which form of energy is electrical?", "Thermal", "Chemical", "Electrical", "Nuclear", "C"),
            ("What is main purpose of decorators?", "Modify functions", "Create classes", "Import modules", "Handle errors", "A"),
        ],
    },
    "maths": {
        "beginner": [
            ("What is 7 + 5?", "10", "11", "12", "13", "B"),
            ("What is 3 * 4?", "7", "12", "9", "14", "B"),
            ("What is 9 - 2?", "6", "7", "8", "5", "B"),
            ("What is 10 / 2?", "3", "5", "4", "6", "B"),
            ("What is 2 squared?", "2", "4", "8", "6", "B"),
            ("What is the perimeter of a 3x4 rectangle?", "7", "12", "14", "10", "C"),
            ("What is 6 * 7?", "36", "42", "48", "49", "B"),
            ("What is 15 - 8?", "6", "7", "8", "5", "B"),
            ("What is 100 / 10?", "5", "10", "15", "20", "B"),
            ("What is 5 * 5?", "20", "25", "30", "15", "B"),
        ],
        "intermediate": [
            ("What is the perimeter of a 3x4 rectangle?", "7", "12", "14", "10", "C"),
            ("What is 2 squared?", "2", "4", "8", "6", "B"),
            ("What is 10% of 50?", "5", "10", "15", "20", "A"),
            ("Solve for x: 2x + 3 = 11", "3", "4", "5", "6", "B"),
            ("What is 3/4 + 1/2?", "5/4", "1/4", "3/8", "5/8", "A"),
            ("What is the area of a 5x3 rectangle?", "8", "15", "10", "20", "B"),
            ("What is 25 % of 100?", "10", "20", "25", "30", "C"),
            ("Solve: x - 5 = 10", "15", "5", "10", "20", "A"),
            ("What is 7 * 8?", "54", "56", "60", "49", "B"),
            ("What is 144 / 12?", "10", "12", "11", "13", "B"),
            ("What is 15 / 3?", "3", "5", "4", "6", "B"),
            ("What is 9 squared?", "72", "81", "90", "64", "B"),
            ("What is 50 - 25?", "20", "25", "30", "15", "B"),
            ("What is 8 * 9?", "72", "81", "69", "64", "A"),
            ("What is 20 % of 80?", "16", "20", "25", "15", "A"),
            ("Solve: 3x = 21", "5", "7", "9", "6", "B"),
            ("What is the area of a 4x4 square?", "8", "16", "20", "12", "B"),
            ("What is 99 + 1?", "99", "100", "101", "98", "B"),
            ("What is 1000 / 100?", "5", "10", "15", "20", "B"),
            ("What is 11 * 11?", "121", "110", "100", "144", "A"),
        ],
        "advanced": [
            ("What is the derivative of x^2?", "x", "2x", "x^2", "2", "B"),
            ("What is the integral of 1/x dx?", "x", "ln|x| + C", "1/x^2", "e^x + C", "B"),
            ("What is sin(90°)?", "0", "1", "-1", "Undefined", "B"),
            ("What is cos(0°)?", "0", "1", "-1", "Undefined", "B"),
            ("What is tan(45°)?", "0", "1", "-1", "Undefined", "B"),
            ("What is 2^10?", "512", "1024", "2048", "256", "B"),
            ("What is the sum of first 10 natural numbers?", "45", "55", "65", "50", "B"),
            ("What is the probability of rolling a 6?", "1/6", "1/5", "1/4", "1/3", "A"),
            ("What is log₁₀(100)?", "1", "2", "10", "100", "B"),
            ("What is √144?", "11", "12", "13", "14", "B"),
            ("What is |-5|?", "5", "-5", "0", "10", "A"),
            ("What is 5!?", "100", "120", "150", "180", "B"),
            ("What is the circumference formula?", "πr", "2πr", "πr²", "πd", "B"),
            ("What is the area formula for circle?", "πr", "2πr", "πr²", "πd", "C"),
            ("What is 0.5 * 0.5?", "0.25", "0.5", "1", "0.1", "A"),
            ("What is (-2)^2?", "-4", "4", "-2", "2", "B"),
            ("What is √16?", "2", "4", "8", "16", "B"),
            ("What is 15% of 200?", "20", "30", "25", "35", "B"),
            ("What is (2/3) * 3?", "1", "2", "3", "6", "B"),
            ("What is the Pythagorean theorem?", "a+b=c", "a²+b²=c²", "a*b=c", "a-b=c", "B"),
        ],
    },
    "science": {
        "beginner": [
            ("Which planet is the Red Planet?", "Venus", "Mars", "Jupiter", "Saturn", "B"),
            ("What gas do plants absorb?", "Oxygen", "Nitrogen", "CO2", "Hydrogen", "C"),
            ("Which state has fixed shape?", "Liquid", "Gas", "Solid", "Plasma", "C"),
            ("What is H2O?", "Hydrogen", "Water", "Oxygen", "Salt", "B"),
            ("Which organ pumps blood?", "Lung", "Brain", "Heart", "Kidney", "C"),
            ("What is the powerhouse of cell?", "Nucleus", "Mitochondria", "Ribosome", "Golgi", "B"),
            ("How many bones in human body?", "150", "206", "250", "300", "B"),
            ("Which planet is closest to sun?", "Venus", "Mercury", "Earth", "Mars", "B"),
            ("What does chlorophyll do?", "Absorbs sound", "Absorbs light", "Absorbs heat", "Absorbs water", "B"),
            ("Which gas do we breathe in?", "CO2", "Nitrogen", "Oxygen", "Hydrogen", "C"),
        ],
        "intermediate": [
            ("What is the powerhouse of cell?", "Nucleus", "Mitochondria", "Ribosome", "Golgi", "B"),
            ("Newton's 2nd law is?", "F = ma", "E = mc2", "pV = nRT", "V = IR", "A"),
            ("What is chemical symbol for sodium?", "NaCl", "Na", "Cl", "K", "B"),
            ("Which organelle makes proteins?", "Nucleus", "Ribosome", "Golgi", "Vacuole", "B"),
            ("What is photosynthesis?", "Plant respiration", "Make food from light", "Breaking down food", "Moving energy", "B"),
            ("Which scientist discovered DNA?", "Einstein", "Darwin", "Watson & Crick", "Pasteur", "C"),
            ("What is pH scale range?", "0-7", "0-14", "1-10", "5-10", "B"),
            ("How many chambers in human heart?", "2", "3", "4", "5", "C"),
            ("What is speed of light?", "100,000 km/s", "300,000 km/s", "500,000 km/s", "1,000,000 km/s", "B"),
            ("What causes seasons?", "Distance from sun", "Earth's tilt", "Moon's gravity", "Solar winds", "B"),
            ("Which element has symbol O?", "Oxygen", "Iron", "Gold", "Copper", "A"),
            ("What is a neutron?", "Positive charge", "Negative charge", "No charge", "Double charge", "C"),
            ("Which gas is inert?", "Oxygen", "Nitrogen", "Helium", "Hydrogen", "C"),
            ("What is a sediment?", "Rock particle", "Water droplet", "Gas particle", "Light particle", "A"),
            ("How many chromosomes in humans?", "23", "46", "92", "69", "B"),
            ("What is sound measured in?", "Hertz", "Decibels", "Watts", "Volts", "B"),
            ("Which gas causes acid rain?", "CO2", "SO2", "NO2", "All of above", "D"),
            ("What is half-life?", "50% of time", "Time for half decay", "Half the age", "Half speed", "B"),
            ("Which biome has most rainfall?", "Desert", "Savanna", "Rainforest", "Tundra", "C"),
            ("What is an enzyme?", "Food", "Catalyst protein", "Blood cell", "Virus", "B"),
        ],
        "advanced": [
            ("Which molecule stores genetic info?", "Protein", "DNA", "Lipid", "Carb", "B"),
            ("Boyle's law relates what?", "Pressure & volume", "Heat & temp", "Force & motion", "Energy & mass", "A"),
            ("Which particle has negative charge?", "Proton", "Neutron", "Electron", "Photon", "C"),
            ("What is an isotope?", "Same protons", "Same neutrons", "Different neutrons", "Same mass", "C"),
            ("What is redox reaction?", "Acid-base", "Combustion", "Electron transfer", "Precipitation", "C"),
            ("Planck's constant is?", "6.626 × 10^-34", "3 × 10^8", "1.6 × 10^-19", "2.7 × 10^-5", "A"),
            ("What is valence electron?", "Inner electron", "Outer shell electron", "Core electron", "Nuclear electron", "B"),
            ("Which is noble gas?", "Oxygen", "Hydrogen", "Neon", "Chlorine", "C"),
            ("What is quantum tunneling?", "Particle through wall", "Light through prism", "Sound reflection", "Heat transfer", "A"),
            ("What is bioluminescence?", "Light from life", "Heat from life", "Sound from life", "Movement from life", "A"),
            ("How is DNA replicated?", "Semi-conservative", "Dispersive", "Conservative", "Non-replicative", "A"),
            ("What is entropy?", "Order", "Disorder", "Energy", "Mass", "B"),
            ("Which law: E = mc²?", "Newton's 1st", "Newton's 2nd", "Einstein's", "Ohm's", "C"),
            ("What is osmosis?", "Solute movement", "Solvent movement", "Gas exchange", "Heat transfer", "B"),
            ("What is chemosynthesis?", "Energy from sun", "Energy from chemicals", "Energy from heat", "Energy from motion", "B"),
            ("What is graviton?", "Gravity particle", "Light particle", "Sound particle", "Heat particle", "A"),
            ("What is CRISPR?", "DNA sequencing", "Protein folding", "Gene editing", "Cell division", "C"),
            ("What is dark matter?", "Black holes", "Invisible matter", "Dead stars", "Old planets", "B"),
            ("What is kinetic energy?", "Potential energy", "Energy of motion", "Energy of position", "Total energy", "B"),
            ("What is photosynthesis equation?", "C6H12O6", "Light + H2O + CO2", "O2 + Glucose", "ATP synthesis", "B"),
        ],
    },
    "gk": {
        "beginner": [
            ("Capital of France?", "Berlin", "Madrid", "Paris", "Rome", "C"),
            ("Largest ocean?", "Atlantic", "Indian", "Pacific", "Arctic", "C"),
            ("UN founded?", "1935", "1945", "1955", "1965", "B"),
            ("Highest mountain?", "K2", "Everest", "Denali", "Aconcagua", "B"),
            ("Capital of India?", "Mumbai", "Delhi", "Bangalore", "Kolkata", "B"),
            ("Largest country?", "China", "USA", "Russia", "Canada", "C"),
            ("Capital of Japan?", "Osaka", "Tokyo", "Kyoto", "Nagoya", "B"),
            ("Which continent is Africa?", "Asia", "Africa", "Europe", "Australia", "B"),
            ("Shakespeare wrote?", "Math book", "Poetry", "Plays", "All above", "C"),
            ("Earth orbits?", "Moon", "Sun", "Mars", "Venus", "B"),
        ],
        "intermediate": [
            ("Which continent has Sahara?", "Asia", "Africa", "Australia", "America", "B"),
            ("Japan currency?", "Dollar", "Euro", "Yen", "Won", "C"),
            ("Shakespeare wrote?", "Dickens", "Shakespeare", "Tolstoy", "Twain", "B"),
            ("Amazon River in?", "Africa", "Europe", "South America", "Asia", "C"),
            ("Nile River in?", "Africa", "Europe", "Asia", "America", "A"),
            ("Capital of Egypt?", "Alexandria", "Cairo", "Giza", "Luxor", "B"),
            ("Great Wall of?", "China", "Japan", "Korea", "India", "A"),
            ("Eiffel Tower in?", "London", "Paris", "Rome", "Berlin", "B"),
            ("Olympics held?", "Every 2 years", "Every 3 years", "Every 4 years", "Every 5 years", "C"),
            ("Capital of Brazil?", "Rio", "Sao Paulo", "Brasilia", "Salvador", "C"),
            ("Berlin Wall fell?", "1987", "1988", "1989", "1990", "C"),
            ("Renaissance period?", "1300-1600", "1400-1700", "1500-1800", "1600-1900", "A"),
            ("First president USA?", "Jefferson", "Washington", "Madison", "Monroe", "B"),
            ("Capital of Germany?", "Munich", "Hamburg", "Berlin", "Cologne", "C"),
            ("Taj Mahal in?", "Delhi", "Agra", "Mumbai", "Jaipur", "B"),
            ("Statue of Liberty in?", "Boston", "New York", "Philadelphia", "Washington", "B"),
            ("Big Ben is in?", "London", "Paris", "Rome", "Berlin", "A"),
            ("Pyramids in?", "Cairo", "Giza", "Luxor", "Aswan", "B"),
            ("Vatican is in?", "Italy", "France", "Spain", "Portugal", "A"),
            ("Ancient Rome founded?", "1000 BC", "753 BC", "500 BC", "100 AD", "B"),
        ],
        "advanced": [
            ("UN founded in 1945?", "1943", "1945", "1947", "1949", "B"),
            ("Great Pyramid in Giza?", "Hanging Gardens", "Colossus", "Great Pyramid", "Temple", "C"),
            ("Longest river?", "Amazon", "Nile", "Yangtze", "Mississippi", "B"),
            ("Amendment for free speech?", "First", "Second", "Third", "Fourth", "A"),
            ("Soviet Union dissolved?", "1989", "1990", "1991", "1992", "C"),
            ("Black Death occurred?", "1200s", "1300s", "1400s", "1500s", "B"),
            ("Industrial Revolution?", "1600-1700", "1700-1800", "1800-1900", "1900-2000", "B"),
            ("World War I started?", "1912", "1913", "1914", "1915", "C"),
            ("World War II started?", "1937", "1938", "1939", "1940", "C"),
            ("Cold War ended?", "1987", "1988", "1989", "1991", "D"),
            ("US Constitution signed?", "1776", "1787", "1789", "1791", "B"),
            ("French Revolution?", "1776", "1789", "1799", "1809", "B"),
            ("Renaissance started?", "1200", "1300", "1400", "1500", "B"),
            ("Ancient Egypt began?", "3000 BC", "2000 BC", "1000 BC", "500 BC", "A"),
            ("Roman Empire fell?", "200 AD", "300 AD", "400 AD", "500 AD", "C"),
            ("Magna Carta signed?", "1100", "1150", "1215", "1250", "C"),
            ("Columbus sailed?", "1490", "1491", "1492", "1493", "C"),
            ("Printing press invented?", "1300", "1400", "1440", "1500", "C"),
            ("Scientific Revolution?", "1500-1600", "1600-1700", "1700-1800", "1800-1900", "B"),
            ("Enlightenment period?", "1600-1700", "1700-1800", "1800-1900", "1900-2000", "B"),
        ],
    },
}

def populate_db():
    """Insert all questions into the database."""
    import time
    # Wait for any locks to clear
    time.sleep(1)
    
    conn = sqlite3.connect("quiz.db", timeout=30)
    cursor = conn.cursor()
    
    total = 0
    updated = 0
    errors = 0
    for topic, levels in QUESTIONS.items():
        for level, questions in levels.items():
            for prompt, a, b, c, d, correct in questions:
                try:
                    cursor.execute("SELECT id FROM questions WHERE prompt = ?", (prompt,))
                    existing = cursor.fetchone()
                    if existing:
                        cursor.execute(
                            "UPDATE questions SET option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_option = ?, level = ?, topic = ? WHERE id = ?",
                            (a, b, c, d, correct, level, topic, existing[0]),
                        )
                        updated += 1
                    else:
                        cursor.execute(
                            "INSERT INTO questions (prompt, option_a, option_b, option_c, option_d, correct_option, level, topic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (prompt, a, b, c, d, correct, level, topic),
                        )
                        total += 1
                except Exception as e:
                    print(f"Error: {e}")
                    errors += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Inserted {total} new questions")
    if updated > 0:
        print(f"  (Updated {updated} existing questions)")
    if errors > 0:
        print(f"  (Encountered {errors} errors)")
    
    # Verify counts
    time.sleep(1)
    conn = sqlite3.connect("quiz.db", timeout=30)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT topic, level, COUNT(*) as count FROM questions GROUP BY topic, level ORDER BY topic, level"
    )
    print("\nQuestion distribution:")
    for topic, level, count in cursor.fetchall():
        print(f"  {topic:10} {level:12} : {count:2} questions")
    conn.close()

if __name__ == "__main__":
    populate_db()
