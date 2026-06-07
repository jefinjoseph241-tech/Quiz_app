import json
import random
from datetime import datetime

random.seed(42)

topics = ["python", "maths", "science", "gk"]
targets = {"beginner": 10, "intermediate": 20, "advanced": 30}

# Templates per topic/level
python_templates = {
    "beginner": [
        ("Which keyword starts a function definition in Python?", ["func", "def", "function", "begin"]),
        ("Which symbol starts a single-line comment in Python?", ["//", "/*", "#", "--"]),
        ("What does `len([1,2,3])` return?", ["2", "3", "1", "0"]),
        ("Which of these is a mutable sequence?", ["tuple", "string", "list", "int"]),
        ("Which operator is used for exponentiation?", ["^", "**", "pow", "%%"]),
    ],
    "intermediate": [
        ("What does `dict.get(key, default)` do?", ["Raises KeyError", "Returns value or default", "Deletes key", "Returns a list"]),
        ("Which statement exits a loop immediately?", ["continue", "break", "pass", "return"]),
        ("Which built-in creates an immutable sequence?", ["list()", "set()", "tuple()", "dict()"]),
        ("What is the output type of `range(5)` in Python 3?", ["list", "range", "tuple", "iterator"]),
    ],
    "advanced": [
        ("Which keyword defines a generator expression?", ["yield", "gen", "lambda", "async"]),
        ("What does `with open(..., 'r') as f:` ensure?", ["File deleted", "File closed automatically", "File opened in binary", "File encoded"]),
        ("Which module provides regular expressions?", ["regex", "re", "regexp", "pyre"]),
        ("What is the purpose of `__init__` in a class?", ["Module init", "Constructor for instances", "Static init", "Class decorator"]),
    ],
}

maths_templates = {
    "beginner": [
        ("What is 7 + 5?", ["10", "11", "12", "13"]),
        ("What is 3 * 4?", ["7", "12", "9", "14"]),
        ("What is 9 - 2?", ["6", "7", "8", "5"]),
    ],
    "intermediate": [
        ("What is the perimeter of a rectangle with sides 3 and 4?", ["7", "12", "14", "10"]),
        ("What is 2 squared?", ["2", "4", "8", "6"]),
        ("What is 10% of 50?", ["5", "10", "15", "20"]),
    ],
    "advanced": [
        ("What is the derivative of x^2?", ["x", "2x", "x^2", "2"]),
        ("What is the integral of 1/x dx?", ["x", "ln|x| + C", "1/x^2", "e^x + C"]),
        ("What is sin(90°)?", ["0", "1", "-1", "Undefined"]),
    ],
}

science_templates = {
    "beginner": [
        ("Which planet is known as the Red Planet?", ["Venus", "Mars", "Jupiter", "Saturn"]),
        ("What gas do plants absorb for photosynthesis?", ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"]),
        ("Which state of matter has a fixed shape?", ["Liquid", "Gas", "Solid", "Plasma"]),
    ],
    "intermediate": [
        ("What is the powerhouse of the cell?", ["Nucleus", "Mitochondria", "Ribosome", "Golgi apparatus"]),
        ("Which law is F = ma?", ["Hooke's law", "Newton's second law", "Ohm's law", "Kepler's law"]),
        ("What is H2O commonly called?", ["Hydrogen peroxide", "Water", "Hydrogen oxide", "Hydroxide"]),
    ],
    "advanced": [
        ("Which molecule stores genetic information?", ["Protein", "DNA", "Lipid", "Carbohydrate"]),
        ("Which law relates pressure and volume at constant temperature?", ["Boyle's law", "Charles's law", "Avogadro's law", "Ohm's law"]),
        ("Which particle has a negative charge?", ["Proton", "Neutron", "Electron", "Photon"]),
    ],
}

gk_templates = {
    "beginner": [
        ("What is the capital of France?", ["Berlin", "Madrid", "Paris", "Rome"]),
        ("Which ocean is largest?", ["Atlantic", "Indian", "Pacific", "Arctic"]),
        ("Who wrote 'Romeo and Juliet'?", ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"]),
    ],
    "intermediate": [
        ("Which continent is the Sahara Desert in?", ["Asia", "Africa", "Australia", "South America"]),
        ("What currency is used in Japan?", ["Dollar", "Euro", "Yen", "Won"]),
        ("Which river is often considered the longest?", ["Amazon", "Nile", "Yangtze", "Mississippi"]),
    ],
    "advanced": [
        ("Which organization was founded in 1945 to promote international cooperation?", ["NATO", "UN", "EU", "WHO"]),
        ("Which ancient wonder was in Giza?", ["Hanging Gardens", "Colossus", "Great Pyramid", "Temple of Artemis"]),
        ("Which amendment commonly protects freedom of speech?", ["First", "Second", "Third", "Fourth"]),
    ],
}

all_templates = {
    "python": python_templates,
    "maths": maths_templates,
    "science": science_templates,
    "gk": gk_templates,
}

questions = []

for topic in topics:
    for level, count in targets.items():
        pool = all_templates[topic].get(level, [])
        for i in range(1, count + 1):
            # Reuse templates cyclically and produce small variations
            tpl = pool[(i - 1) % len(pool)] if pool else (f"{topic} {level} question {i}", ["A", "B", "C", "D"])
            base_prompt, opts = tpl
            prompt = f"{base_prompt} (Q{ i })"
            # Rotate options deterministically
            shift = (i + len(topic)) % len(opts)
            opts_rotated = opts[shift:] + opts[:shift]
            # Select correct index deterministically
            correct_index = (i * 3 + len(topic)) % 4
            correct_option = "ABCD"[correct_index]
            option_a, option_b, option_c, option_d = opts_rotated[0], opts_rotated[1], opts_rotated[2], opts_rotated[3]
            questions.append({
                "prompt": prompt,
                "option_a": option_a,
                "option_b": option_b,
                "option_c": option_c,
                "option_d": option_d,
                "correct_option": correct_option,
                "level": level,
                "topic": topic,
            })

# Basic deduplication based on prompt
seen = set()
unique_questions = []
for q in questions:
    if q["prompt"] not in seen:
        seen.add(q["prompt"])
        unique_questions.append(q)

# Write to JSON file
out_path = "generated_questions.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"generated_at": datetime.utcnow().isoformat(), "count": len(unique_questions), "questions": unique_questions}, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(unique_questions)} questions to {out_path}")
