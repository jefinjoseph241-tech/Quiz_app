import sqlite3
import os
import random
import re
from datetime import datetime
from flask import Flask, g, render_template, request, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES, timeout=30.0)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA busy_timeout = 30000")  # 30 seconds timeout for locked database
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    try:
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                password TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS questions (
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

            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                level TEXT,
                topic TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        db.commit()
        
        # Ensure schema migrations only if not already done
        ensure_user_full_name_column(db)
        ensure_question_level_column(db)
        ensure_question_topic_column(db)
        ensure_feedback_table(db)
    except Exception as e:
        print(f"Error initializing database: {e}")


def ensure_question_level_column(db):
    # Add a `level` column to questions if it doesn't exist
    cols = [r[1] for r in db.execute("PRAGMA table_info(questions)").fetchall()]
    if "level" not in cols:
        try:
            db.execute("ALTER TABLE questions ADD COLUMN level TEXT DEFAULT 'beginner'")
            db.commit()
        except Exception:
            # ignore if cannot alter (older SQLite versions) - fallback handled by default values on insert
            pass

def ensure_question_topic_column(db):
    # Add a `topic` column to questions if it doesn't exist
    cols = [r[1] for r in db.execute("PRAGMA table_info(questions)").fetchall()]
    if "topic" not in cols:
        try:
            db.execute("ALTER TABLE questions ADD COLUMN topic TEXT DEFAULT 'python'")
            db.commit()
        except Exception:
            pass

def ensure_user_full_name_column(db):
    cols = [r[1] for r in db.execute("PRAGMA table_info(users)").fetchall()]
    if "full_name" not in cols:
        try:
            db.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
            db.commit()
        except Exception:
            pass


def ensure_feedback_table(db):
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            rating INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    db.commit()


def generate_topic_question(topic, level, index):
    if topic == "maths":
        return generate_maths_question(level, index)
    if topic == "science":
        return generate_science_question(level, index)
    if topic == "gk":
        return generate_gk_question(level, index)
    return generate_python_question(level, index)


def generate_maths_question(level, index):
    a = (index * 3) % 12 + 1
    b = (index * 5) % 9 + 1
    c = (index * 7) % 8 + 1
    if level == "beginner":
        kind = index % 4
        if kind == 0:
            prompt = f"What is {a} + {b}?"
            option_a = str(a + b)
            option_b = str(a + b + 1)
            option_c = str(abs(a - b) + 1)
            option_d = str(a * b)
        elif kind == 1:
            prompt = f"What is {a + c} - {b}?"
            option_a = str(a + c - b)
            option_b = str(a + c - b + 1)
            option_c = str(a + c + b)
            option_d = str(a * c)
        elif kind == 2:
            prompt = f"What is {a} * {b}?"
            option_a = str(a * b)
            option_b = str(a * b + 1)
            option_c = str(a + b)
            option_d = str(a * b - 1)
        else:
            divisor = b if b != 0 else 1
            dividend = a * divisor
            prompt = f"What is {dividend} // {divisor}?"
            option_a = str(dividend // divisor)
            option_b = str(dividend // divisor + 1)
            option_c = str(dividend)
            option_d = str(divisor)
    elif level == "intermediate":
        kind = index % 5
        if kind == 0:
            prompt = f"What is the perimeter of a rectangle with sides {a} and {b}?"
            option_a = str(2 * (a + b))
            option_b = str(a + b)
            option_c = str(a * b)
            option_d = str(a + b + 2)
        elif kind == 1:
            prompt = f"What is {a} squared?"
            option_a = str(a * a)
            option_b = str(a * a + 1)
            option_c = str(a * a - 1)
            option_d = str(a + a)
        elif kind == 2:
            percent = 10 + (index % 5) * 5
            amount = 20 + (index % 4) * 5
            correct_value = amount * percent // 100
            prompt = f"What is {percent}% of {amount}?"
            option_a = str(correct_value)
            option_b = str(correct_value + 1)
            option_c = str(correct_value - 1)
            option_d = str(amount)
        elif kind == 3:
            x = (index % 5) + 2
            b_val = (index % 8) + 1
            c_val = x * a + b_val
            prompt = f"Solve for x: {x}x + {b_val} = {c_val}."
            option_a = str((c_val - b_val) // x)
            option_b = str((c_val - b_val) // x + 1)
            option_c = str((c_val - b_val) // x - 1)
            option_d = str(x)
        else:
            prompt = f"What is the value of 2**{c}?"
            option_a = str(2 ** c)
            option_b = str(2 ** c + 1)
            option_c = str(2 ** c - 1)
            option_d = str(c * c)
    else:
        kind = index % 6
        if kind == 0:
            prompt = f"What is 2**{a}?"
            option_a = str(2 ** a)
            option_b = str(2 ** a + 1)
            option_c = str(a ** 2)
            option_d = str(a * 2)
        elif kind == 1:
            n = a + 2
            prompt = f"What is the sum of the first {n} natural numbers?"
            option_a = str(n * (n + 1) // 2)
            option_b = str(n * (n + 1))
            option_c = str(n * n)
            option_d = str(n + 1)
        elif kind == 2:
            prompt = f"What is the next prime after {5 + index % 10}?"
            prime = [7, 11, 13, 17, 19, 23, 29, 31, 37, 41][index % 10]
            option_a = str(prime)
            option_b = str(prime + 1)
            option_c = str(prime + 2)
            option_d = str(prime + 3)
        elif kind == 3:
            radius = (index % 5) + 2
            prompt = f"What is the area of a circle with radius {radius} (use 3.14)?"
            area = round(3.14 * radius * radius)
            option_a = str(area)
            option_b = str(area + 1)
            option_c = str(area - 1)
            option_d = str(radius * radius)
        elif kind == 4:
            prompt = f"What is the probability of rolling a 6 on a fair six-sided die?"
            option_a = "1/6"
            option_b = "1/5"
            option_c = "1/4"
            option_d = "1/3"
        else:
            prompt = f"What is the value of the expression {a}*{b} - {c}?"
            option_a = str(a * b - c)
            option_b = str(a * b)
            option_c = str(a + b - c)
            option_d = str(a * b + c)
    return prompt, option_a, option_b, option_c, option_d, "A"


def generate_python_question(level, index):
    # New curated questions for specific index ranges
    intermediate_curated = {
        1: ("What is the difference between == and is?", "== checks value, is checks identity", "Both check value", "Both check identity", "No difference", "A"),
        2: ("Which method adds items to the end of a list?", "append()", "add()", "extend()", "push()", "A"),
        3: ("What does sorted() return?", "A new sorted list", "None after sorting", "The original list", "An iterator", "A"),
        4: ("How do you create a tuple with one element?", "(1,)", "(1)", "[1]", "{1}", "A"),
        5: ("What does enumerate() do?", "Returns indices and values", "Returns only indices", "Returns only values", "Returns nothing", "A"),
        6: ("Which method removes and returns the last list item?", "pop()", "remove()", "del", "clear()", "A"),
        7: ("What is the output of 'hello'.split('l')?", "['he', '', 'o']", "['h','e','l','l','o']", "'he', 'o'", "['hello']", "A"),
        8: ("How do you check if a key exists in a dict d?", "'key' in d", "d.has_key('key')", "d.contains('key')", "d.includes('key')", "A"),
        9: ("What is the result of list(range(5))?", "[0, 1, 2, 3, 4]", "[1, 2, 3, 4, 5]", "[0, 1, 2, 3, 4, 5]", "[5]", "A"),
        10: ("Which function applies a function to every item?", "map()", "apply()", "execute()", "call()", "A"),
    }
    advanced_curated = {
        1: ("What does zip() do with multiple iterables?", "Pairs elements from each iterable", "Compresses data", "Merges lists", "Flattens lists", "A"),
        2: ("What is the purpose of *args in a function?", "Accept variable number of arguments", "Multiply arguments", "Access arguments", "Create tuples", "A"),
        3: ("How do **kwargs work?", "Accept keyword arguments as dict", "Multiply keyword values", "Create lists", "Return keyword values", "A"),
        4: ("What does filter() return?", "An iterator of filtered elements", "A list", "A tuple", "A boolean", "A"),
        5: ("Which method is called when an object is created?", "__init__", "__new__", "__create__", "__setup__", "A"),
        6: ("What is a lambda function?", "An anonymous function", "A class", "A module", "A variable", "A"),
        7: ("What does isinstance(x, int) check?", "If x is an int instance", "If x equals int", "If x is named int", "If x is callable", "A"),
        8: ("What is the @property decorator used for?", "Create a property getter", "Decorate a function", "Set a property", "Check a property", "A"),
        9: ("What does super() return in a class?", "A proxy to parent class methods", "The parent class itself", "The instance", "The class definition", "A"),
        10: ("What is the purpose of __str__?", "Return string representation", "Store a string", "Compare strings", "Print a string", "A"),
        11: ("What does hasattr(obj, 'attr') do?", "Check if object has attribute", "Get attribute value", "Set an attribute", "Delete an attribute", "A"),
        12: ("What is getattr(obj, 'attr', default)?", "Get attribute or return default", "Get attribute safely", "Get default value", "Get all attributes", "A"),
        13: ("What does setattr(obj, 'attr', val) do?", "Set attribute to value", "Get attribute value", "Check attribute exists", "Delete attribute", "A"),
        14: ("What is globals() used for?", "Access global namespace dict", "Define global variables", "Access local variables", "Delete global variables", "A"),
        15: ("What does locals() return?", "Local namespace as dict", "Global namespace dict", "List of variables", "Variable names", "A"),
        16: ("What is eval() used for?", "Evaluate expression string", "Evaluate code blocks", "Evaluate conditionals", "Evaluate loops", "A"),
        17: ("What is exec() used for?", "Execute string as code", "Execute expressions", "Execute functions", "Execute imports", "A"),
        18: ("What is __name__ set to when running directly?", "'__main__'", "'__file__'", "'__module__'", "'__self__'", "A"),
        19: ("What does dir(obj) show?", "All attributes of object", "All methods only", "All variables only", "All properties only", "A"),
        20: ("What is the purpose of @staticmethod?", "Method that doesn't need self", "A static variable", "A class method", "A constant", "A"),
    }
    
    python_bank = {
        'beginner': [
            ("What keyword defines a function?", "def", "function", "func", "define", "A"),
            ("Which literal creates a list?", "[1,2]", "(1,2)", "{'a':1}", "<1,2>", "A"),
            ("What does print('Hi') output?", "Hi", "'Hi'", "None", "Error", "A"),
            ("How do you write a single-line comment?", "#", "//", "/*", "--", "A"),
            ("What does len('abc') return?", "3", "'3'", "2", "Error", "A"),
            ("What does int('5') return?", "5", "'5'", "5.0", "None", "A"),
            ("What is the result of True and False?", "False", "True", "1", "0", "A"),
            ("Which operator is used for addition?", "+", "-", "*", "/", "A"),
            ("Which data type is immutable?", "tuple", "list", "dict", "set", "A"),
            ("How do you access the first element of list a?", "a[0]", "a(0)", "a{0}", "a.first", "A"),
        ],
        'intermediate': [
            ("What does list.reverse() do?", "Reverses list in place", "Returns reversed list", "Sorts list", "Removes last item", "A"),
            ("Which keyword enables generator behavior in a function?", "yield", "iter", "next", "generator", "A"),
            ("How do you handle exceptions in Python?", "try/except", "try/catch", "begin/rescue", "handle/except", "A"),
            ("What does dict.items() return?", "Pairs of key and value", "Keys only", "Values only", "A list of keys", "A"),
            ("What is a list comprehension?", "A concise way to create lists", "A loop that prints", "A function", "A module", "A"),
            ("Which method removes an element by index?", "pop()", "remove()", "discard()", "delete()", "A"),
            ("How do you get the length of an iterable?", "len()", "size()", "count()", "length()", "A"),
            ("Which statement creates an empty set?", "set()", "{}", "[]", "()", "A"),
            ("How to convert string '3.14' to float?", "float('3.14')", "int('3.14')", "str(3.14)", "decimal('3.14')", "A"),
            ("Which built-in sorts a list in-place and returns None?", "list.sort()", "sorted()", "order()", "sortlist()", "A"),
        ],
        'advanced': [
            ("What is a coroutine in Python?", "A function that can pause and resume", "A class", "A module", "A variable", "A"),
            ("Which module supports asynchronous IO?", "asyncio", "threading", "multiprocessing", "concurrent", "A"),
            ("What does the 'with' statement ensure?", "Resource cleanup", "Faster execution", "Type checking", "Global variables", "A"),
            ("How do you create a descriptor in Python?", "Define __get__/__set__", "Define __init__", "Use property()", "Use decorator", "A"),
            ("What does functools.lru_cache do?", "Caches function results", "Logs calls", "Locks threads", "Runs functions in parallel", "A"),
            ("Which library is commonly used for HTTP requests?", "requests", "http", "urllib3", "httplib", "A"),
            ("How do you define a dataclass?", "@dataclass above class", "class Data:", "def dataclass():", "use struct", "A"),
            ("What is monkey patching?", "Modifying code at runtime", "A security feature", "A testing tool", "A static analysis", "A"),
            ("Which built-in module helps with introspection?", "inspect", "introspect", "reflect", "meta", "A"),
            ("What is pickling in Python?", "Serializing objects", "Encrypting data", "Compressing data", "Parsing strings", "A"),
        ],
    }
    
    # Use curated questions for specified ranges
    if level == 'intermediate' and index in intermediate_curated:
        return intermediate_curated[index]
    elif level == 'advanced' and index in advanced_curated:
        return advanced_curated[index]
    
    bank = python_bank.get(level, python_bank['beginner'])
    return bank[(index - 1) % len(bank)]


def generate_science_question(level, index):
    # New curated questions for specific index ranges
    beginner_curated = {
        4: ("What is the main function of the heart?", "Pump blood throughout the body", "Filter blood", "Produce hormones", "Store oxygen", "A"),
        5: ("Which gas do animals breathe in?", "Oxygen", "Carbon dioxide", "Nitrogen", "Helium", "A"),
        6: ("What do we call the study of living things?", "Biology", "Geology", "Chemistry", "Physics", "A"),
        7: ("What is the largest organ in the human body?", "Skin", "Liver", "Heart", "Brain", "A"),
        8: ("Which of these is a renewable energy source?", "Solar", "Coal", "Oil", "Natural gas", "A"),
        9: ("What is the process by which water changes to steam?", "Evaporation", "Condensation", "Freezing", "Melting", "A"),
        10: ("What type of animal has feathers and lays eggs?", "Bird", "Fish", "Reptile", "Amphibian", "A"),
    }
    intermediate_curated = {
        4: ("What is the powerhouse of the cell?", "Mitochondria", "Nucleus", "Ribosome", "Endoplasmic reticulum", "A"),
        5: ("Which element has atomic number 6?", "Carbon", "Oxygen", "Nitrogen", "Hydrogen", "A"),
        6: ("What is the speed of sound in air approximately?", "343 m/s", "3 x 10^8 m/s", "100 m/s", "500 m/s", "A"),
        7: ("What is the SI unit of electric current?", "Ampere", "Volt", "Ohm", "Watt", "A"),
        8: ("Which type of reaction releases energy?", "Exothermic", "Endothermic", "Catalytic", "Reversible", "A"),
        9: ("What is the name of the outermost layer of the Sun?", "Photosphere", "Corona", "Chromosphere", "Core", "A"),
        10: ("How many bones are in the adult human body?", "206", "256", "186", "226", "A"),
        11: ("What is the process of converting starch to glucose called?", "Digestion", "Respiration", "Photosynthesis", "Fermentation", "A"),
        12: ("Which component of blood carries oxygen?", "Red blood cells", "White blood cells", "Platelets", "Plasma", "A"),
        13: ("What is the name of the tubes that carry urine from kidneys?", "Ureters", "Urethra", "Nephrons", "Tubules", "A"),
        14: ("What does ATP stand for?", "Adenosine Triphosphate", "Adenosine Trioxide", "Amino Trioxide", "Atom Transfer Protein", "A"),
        15: ("What is the process of breaking down glucose for energy?", "Cellular respiration", "Photosynthesis", "Fermentation", "Glycogenesis", "A"),
        16: ("What is the name of the protective outer layer of a cell?", "Cell membrane", "Cell wall", "Nucleus", "Chloroplast", "A"),
        17: ("Which organ produces insulin?", "Pancreas", "Liver", "Kidney", "Thyroid", "A"),
        18: ("What is the smallest unit of life?", "Cell", "Atom", "Molecule", "Organism", "A"),
        19: ("What is the name of the protein that carries oxygen in blood?", "Hemoglobin", "Myoglobin", "Albumin", "Collagen", "A"),
        20: ("What type of blood vessel carries blood away from the heart?", "Artery", "Vein", "Capillary", "Vessel", "A"),
    }
    advanced_curated = {
        4: ("What is the Heisenberg Uncertainty Principle about?", "Cannot simultaneously know position and momentum precisely", "Energy and mass are equivalent", "Particles move in straight lines", "Light has wave properties", "A"),
        5: ("What is the name of the reaction between an acid and base?", "Neutralization", "Combustion", "Oxidation", "Reduction", "A"),
        6: ("What is the energy required to remove an electron from an atom?", "Ionization energy", "Kinetic energy", "Binding energy", "Activation energy", "A"),
        7: ("Which organelle synthesizes proteins?", "Ribosome", "Mitochondria", "Golgi apparatus", "Nucleolus", "A"),
        8: ("What is the name of the protein in muscle fibers?", "Myosin and actin", "Hemoglobin", "Collagen", "Elastin", "A"),
        9: ("What is the process of producing glucose from non-carbohydrate sources?", "Gluconeogenesis", "Glycogenesis", "Glycolysis", "Photosynthesis", "A"),
        10: ("What is the name of the proteins that speed up reactions?", "Enzymes", "Antibodies", "Hormones", "Antigens", "A"),
        11: ("What is the pH where most enzymes work optimally?", "7", "1", "14", "9", "A"),
        12: ("What is the name of the process of ATP production?", "Cellular respiration", "Anaerobic respiration", "Fermentation", "Photosynthesis", "A"),
        13: ("What is the Krebs cycle also known as?", "Citric acid cycle", "Glycolysis", "Electron transport chain", "Pentose phosphate pathway", "A"),
        14: ("How many ATP molecules are produced per glucose in aerobic respiration?", "30-32", "2", "10", "100", "A"),
        15: ("What is the name of the organic molecules that store genetic info?", "Nucleic acids", "Proteins", "Lipids", "Carbohydrates", "A"),
        16: ("What are the four bases found in DNA?", "A, T, G, C", "A, U, G, C", "A, T, G, U", "A, T, C, U", "A"),
        17: ("What is the process of making mRNA from DNA?", "Transcription", "Translation", "Replication", "Mutation", "A"),
        18: ("What is the process of making proteins from mRNA?", "Translation", "Transcription", "Replication", "Mutation", "A"),
        19: ("What is the name of the region where mRNA is read by ribosome?", "Ribosome binding site", "Promoter", "Enhancer", "Silencer", "A"),
        20: ("What is the name of the protective caps on chromosome ends?", "Telomeres", "Centromeres", "Histones", "Nucleosomes", "A"),
        21: ("What is the process by which cells divide to form sex cells?", "Meiosis", "Mitosis", "Amitosis", "Cytokinesis", "A"),
        22: ("What is the name of the threadlike structures in nucleus?", "Chromosomes", "Centrosomes", "Ribosomes", "Nucleoles", "A"),
        23: ("What percentage of the human body is water?", "60-70%", "40-50%", "80-90%", "20-30%", "A"),
        24: ("What is the name of the circulation between heart and lungs?", "Pulmonary circulation", "Systemic circulation", "Portal circulation", "Coronary circulation", "A"),
        25: ("What is the name of the substance that prevents blood clotting?", "Heparin", "Thrombin", "Fibrin", "Prothrombin", "A"),
        26: ("What is the name of the hormone that regulates blood sugar?", "Insulin", "Glucagon", "Epinephrine", "Thyroid hormone", "A"),
        27: ("What is the name of the structure that filters blood in kidney?", "Nephron", "Glomerulus", "Loop of Henle", "Collecting duct", "A"),
        28: ("What is the name of the wave-like muscle contraction in digestive system?", "Peristalsis", "Chewing", "Swallowing", "Secretion", "A"),
        29: ("What is the name of the junction between neurons?", "Synapse", "Dendrite", "Axon", "Soma", "A"),
        30: ("What is the name of the chemical messengers in nervous system?", "Neurotransmitters", "Hormones", "Antibodies", "Enzymes", "A"),
    }
    
    science_bank = {
        'beginner': [
            ("Which state of matter has a definite shape and volume?", "Solid", "Liquid", "Gas", "Plasma", "A"),
            ("What planet is known as the Red Planet?", "Mars", "Venus", "Jupiter", "Saturn", "A"),
            ("What gas do plants primarily absorb?", "Carbon Dioxide", "Oxygen", "Nitrogen", "Hydrogen", "A"),
            ("What is the powerhouse of the cell?", "Mitochondria", "Nucleus", "Ribosome", "Golgi apparatus", "A"),
            ("Which organ pumps blood?", "Heart", "Lungs", "Liver", "Kidneys", "A"),
            ("What do bees make from nectar?", "Honey", "Wax", "Milk", "Sap", "A"),
            ("Which senses detect sound?", "Ears", "Eyes", "Nose", "Tongue", "A"),
            ("Water boils at 100°C on which temperature scale?", "Celsius", "Fahrenheit", "Kelvin", "Rankine", "A"),
            ("What force pulls objects toward Earth?", "Gravity", "Magnetism", "Friction", "Buoyancy", "A"),
            ("What does H2O represent?", "Water", "Oxygen", "Hydrogen peroxide", "Salt", "A"),
        ],
        'intermediate': [
            ("Which law states F = ma?", "Newton's second law", "Newton's first law", "Newton's third law", "Law of conservation", "A"),
            ("What is the chemical symbol for sodium?", "Na", "S", "Sn", "So", "A"),
            ("Which gas is produced by plants during photosynthesis?", "Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen", "A"),
            ("What is the main gas in Earth's atmosphere?", "Nitrogen", "Oxygen", "Carbon dioxide", "Argon", "A"),
        ],
        'advanced': [
            ("Which principle states energy cannot be created or destroyed?", "Conservation of energy", "Newton's law", "Ohm's law", "Bernoulli's principle", "A"),
            ("What is the pH of pure water?", "7", "0", "14", "1", "A"),
            ("What does mitochondria produce?", "ATP", "DNA", "RNA", "Oxygen", "A"),
            ("Which organelle contains chlorophyll?", "Chloroplast", "Mitochondria", "Nucleus", "Ribosome", "A"),
            ("Which bases are paired in DNA?", "A and T", "A and C", "C and G", "G and T", "A"),
            ("What type of bond shares electrons?", "Covalent bond", "Ionic bond", "Hydrogen bond", "Metallic bond", "A"),
            ("Which gas is most abundant in the Sun?", "Hydrogen", "Helium", "Oxygen", "Nitrogen", "A"),
            ("What is the unit of electrical resistance?", "Ohm", "Volt", "Ampere", "Watt", "A"),
            ("What is the acceleration due to gravity near Earth?", "9.8 m/s^2", "9.8 km/s^2", "10 m/s^2", "8.9 m/s^2", "A"),
            ("Which process converts glucose into pyruvate?", "Glycolysis", "Photosynthesis", "Fermentation", "Respiration", "A"),
            ("What is the speed of light in vacuum approximately?", "3 x 10^8 m/s", "3 x 10^6 m/s", "1.5 x 10^8 m/s", "3 x 10^5 m/s", "A"),
            ("Which law states for every action there is an equal opposite reaction?", "Newton's third law", "Newton's first law", "Newton's second law", "Law of conservation of mass", "A"),
            ("Which element has atomic number 6?", "Carbon", "Oxygen", "Nitrogen", "Hydrogen", "A"),
            ("What is the chemical formula for methane?", "CH4", "CO2", "H2O", "C2H6", "A"),
            ("What is the SI unit of pressure?", "Pascal", "Newton", "Joule", "Watt", "A"),
            ("Which organ system includes the brain and nerves?", "Nervous system", "Digestive system", "Respiratory system", "Circulatory system", "A"),
            ("Which layer of Earth is liquid iron and nickel?", "Outer core", "Inner core", "Mantle", "Crust", "A"),
            ("What term describes traits passed from parents to offspring?", "Heredity", "Evolution", "Mutation", "Adaptation", "A"),
            ("What is the bending of light called?", "Refraction", "Reflection", "Diffraction", "Absorption", "A"),
            ("Which process breaks down food in the stomach?", "Digestion", "Absorption", "Circulation", "Excretion", "A"),
            ("What is the boiling point of liquid nitrogen?", "-196°C", "-100°C", "0°C", "100°C", "A"),
            ("Which particle in the atomic nucleus has no charge?", "Neutron", "Proton", "Electron", "Photon", "A"),
            ("What is the formula for density?", "mass/volume", "mass*volume", "volume/mass", "mass+volume", "A"),
            ("Which gas do plants use in photosynthesis?", "Carbon dioxide", "Oxygen", "Nitrogen", "Hydrogen", "A"),
            ("What is the main function of red blood cells?", "Transport oxygen", "Fight infection", "Digest food", "Store energy", "A"),
            ("Which organ creates insulin?", "Pancreas", "Liver", "Kidney", "Gallbladder", "A"),
            ("What does kinetic energy depend on?", "Mass and speed", "Mass only", "Speed only", "Volume", "A"),
            ("Which device measures atmospheric pressure?", "Barometer", "Thermometer", "Ammeter", "Voltmeter", "A"),
            ("What is the main pigment in green plants?", "Chlorophyll", "Melanin", "Hemoglobin", "Carotene", "A"),
            ("What causes an echo?", "Sound reflection", "Sound absorption", "Sound distortion", "Sound creation", "A"),
        ],
    }
    bank = science_bank.get(level, science_bank['beginner'])
    return bank[(index - 1) % len(bank)]


def generate_gk_question(level, index):
    # Curated questions for specific ranges
    beginner_curated = {
        4: ("What currency is used in Japan?", "Yen", "Dollar", "Euro", "Pound", "A"),
        5: ("What is the capital of India?", "New Delhi", "Mumbai", "Bangalore", "Kolkata", "A"),
        6: ("Which planet is nearest to the Sun?", "Mercury", "Venus", "Earth", "Mars", "A"),
        7: ("What is the tallest mountain in the world?", "Mount Everest", "K2", "Kangchenjunga", "Lhotse", "A"),
        8: ("Which country built the Great Wall?", "China", "India", "Egypt", "Greece", "A"),
        9: ("How many continents are there?", "7", "5", "6", "8", "A"),
        10: ("Which is the largest country by area?", "Russia", "Canada", "USA", "Australia", "A"),
    }
    intermediate_curated = {
        4: ("Which city hosts the Statue of Liberty?", "New York", "London", "Paris", "Sydney", "A"),
        5: ("What is the capital of Canada?", "Ottawa", "Toronto", "Vancouver", "Montreal", "A"),
        6: ("Which country is famous for the Eiffel Tower?", "France", "Italy", "Spain", "Germany", "A"),
        7: ("Which country hosted the 2016 Olympics?", "Brazil", "China", "Russia", "UK", "A"),
        8: ("What is the capital of Australia?", "Canberra", "Sydney", "Melbourne", "Brisbane", "A"),
        9: ("Which U.S. document begins with 'We the People'?", "The Constitution", "The Declaration", "The Bill of Rights", "The Federalist Papers", "A"),
        10: ("Which continent has the most countries?", "Africa", "Europe", "Asia", "South America", "A"),
        11: ("Which city is known as the City of Love?", "Paris", "Rome", "Venice", "New York", "A"),
        12: ("What is the largest island in the world?", "Greenland", "Madagascar", "Borneo", "New Guinea", "A"),
        13: ("Which country is famous for tulips and windmills?", "Netherlands", "Denmark", "Belgium", "Switzerland", "A"),
        14: ("Which language is spoken in Spain?", "Spanish", "Portuguese", "French", "Italian", "A"),
        15: ("What is the tallest waterfall in the world?", "Angel Falls", "Niagara Falls", "Victoria Falls", "Iguazu Falls", "A"),
        16: ("Which river flows through Egypt?", "Nile", "Tigris", "Euphrates", "Amazon", "A"),
        17: ("Which country uses the rupee as currency?", "India", "Pakistan", "Nepal", "Sri Lanka", "A"),
        18: ("Which mountain range includes Mount Everest?", "Himalayas", "Andes", "Rockies", "Alps", "A"),
        19: ("Which ocean is east of Africa?", "Indian Ocean", "Atlantic Ocean", "Pacific Ocean", "Arctic Ocean", "A"),
        20: ("Which country is called the Land of the Rising Sun?", "Japan", "China", "Korea", "Thailand", "A"),
    }
    advanced_curated = {
        4: ("Who flew solo across the Atlantic first?", "Amelia Earhart", "Valentina Tereshkova", "Harriet Quimby", "Sally Ride", "A"),
        5: ("Which country has the most UNESCO World Heritage sites?", "Italy", "China", "Spain", "France", "A"),
        6: ("Which city hosted the 2008 Summer Olympics?", "Beijing", "London", "Athens", "Sydney", "A"),
        7: ("What is the currency of South Africa?", "Rand", "Dollar", "Euro", "Pound", "A"),
        8: ("Which country is known as the Land of the Midnight Sun?", "Norway", "Sweden", "Finland", "Iceland", "A"),
        9: ("Where is the European Union headquartered?", "Brussels", "Strasbourg", "Berlin", "Paris", "A"),
        10: ("Who invented the telephone?", "Alexander Graham Bell", "Thomas Edison", "Nikola Tesla", "Guglielmo Marconi", "A"),
        11: ("What is the smallest country by land area?", "Vatican City", "Monaco", "Nauru", "Tuvalu", "A"),
        12: ("Which mountain range runs along western South America?", "Andes", "Rockies", "Alps", "Himalayas", "A"),
        13: ("What is the main legislative body of the UK?", "Parliament", "Congress", "Duma", "National Assembly", "A"),
        14: ("Which country has the largest population?", "China", "India", "USA", "Indonesia", "A"),
        15: ("Which sea lies between Saudi Arabia and Africa?", "Red Sea", "Mediterranean Sea", "Arabian Sea", "Black Sea", "A"),
        16: ("What is Earth's longest underwater mountain range?", "Mid-Ocean Ridge", "The Alps", "Andes", "Himalayas", "A"),
        17: ("Which organization oversees the Olympic Games?", "IOC", "FIFA", "UN", "NATO", "A"),
        18: ("What is the capital of Italy?", "Rome", "Milan", "Venice", "Naples", "A"),
        19: ("In what year did the Berlin Wall fall?", "1989", "1991", "1987", "1995", "A"),
        20: ("Which country is home to Petra?", "Jordan", "Egypt", "Greece", "Turkey", "A"),
        21: ("What is the official language of Egypt?", "Arabic", "English", "French", "Spanish", "A"),
        22: ("Which revolution began in Russia in 1917?", "Russian Revolution", "French Revolution", "Industrial Revolution", "Chinese Revolution", "A"),
        23: ("Which lake is the largest freshwater lake by surface area?", "Lake Superior", "Lake Victoria", "Lake Baikal", "Lake Michigan", "A"),
        24: ("What is the busiest airport by passenger traffic?", "Hartsfield-Jackson Atlanta", "Beijing Capital", "Dubai", "Tokyo Haneda", "A"),
        25: ("Which country contains most of the Amazon rainforest?", "Brazil", "Peru", "Colombia", "Venezuela", "A"),
        26: ("What is the capital of South Korea?", "Seoul", "Busan", "Pyongyang", "Tokyo", "A"),
        27: ("Which ocean is the smallest?", "Arctic Ocean", "Indian Ocean", "Atlantic Ocean", "Southern Ocean", "A"),
        28: ("Which country gifted the Statue of Liberty to the United States?", "France", "England", "Spain", "Germany", "A"),
        29: ("Which river passes through Paris?", "Seine", "Thames", "Danube", "Rhine", "A"),
        30: ("What is the largest desert in the world?", "Sahara", "Arctic", "Gobi", "Kalahari", "A"),
    }
    
    gk_bank = {
        'beginner': [
            ("What is the capital of France?", "Paris", "Berlin", "Madrid", "Rome", "A"),
            ("Which ocean is the largest?", "Pacific", "Atlantic", "Indian", "Arctic", "A"),
            ("Which organization was founded in 1945 to promote peace?", "UN", "EU", "NATO", "WHO", "A"),
            ("Who wrote 'Hamlet'?", "William Shakespeare", "Charles Dickens", "Jane Austen", "Mark Twain", "A"),
            ("Which continent is the Sahara Desert in?", "Africa", "Asia", "South America", "Australia", "A"),
            ("What currency is used in Japan?", "Yen", "Dollar", "Euro", "Pound", "A"),
            ("What is the capital of India?", "New Delhi", "Mumbai", "Bangalore", "Kolkata", "A"),
            ("Which planet is nearest to the Sun?", "Mercury", "Venus", "Earth", "Mars", "A"),
            ("What is the tallest mountain in the world?", "Mount Everest", "K2", "Kangchenjunga", "Lhotse", "A"),
            ("Which country built the Great Wall?", "China", "India", "Egypt", "Greece", "A"),
        ],
        'intermediate': [
            ("What currency is used in the United Kingdom?", "Pound sterling", "Euro", "Dollar", "Franc", "A"),
            ("Which river is the longest in the world?", "Nile", "Amazon", "Yangtze", "Mississippi", "A"),
            ("Who is the author of '1984'?", "George Orwell", "Aldous Huxley", "J.K. Rowling", "Ernest Hemingway", "A"),
            ("Which city hosts the Statue of Liberty?", "New York", "London", "Paris", "Sydney", "A"),
            ("What is the capital of Canada?", "Ottawa", "Toronto", "Vancouver", "Montreal", "A"),
            ("Which country is famous for the Eiffel Tower?", "France", "Italy", "Spain", "Germany", "A"),
            ("Which country hosted the 2016 Olympics?", "Brazil", "China", "Russia", "UK", "A"),
            ("What is the capital of Australia?", "Canberra", "Sydney", "Melbourne", "Brisbane", "A"),
            ("Which U.S. document begins with 'We the People'?", "The Constitution", "The Declaration", "The Bill of Rights", "The Federalist Papers", "A"),
            ("Which continent has the most countries?", "Africa", "Europe", "Asia", "South America", "A"),
            ("Which city is known as the City of Love?", "Paris", "Rome", "Venice", "New York", "A"),
            ("What is the largest island in the world?", "Greenland", "Madagascar", "Borneo", "New Guinea", "A"),
            ("Which country is famous for tulips and windmills?", "Netherlands", "Denmark", "Belgium", "Switzerland", "A"),
            ("Which language is spoken in Spain?", "Spanish", "Portuguese", "French", "Italian", "A"),
            ("What is the tallest waterfall in the world?", "Angel Falls", "Niagara Falls", "Victoria Falls", "Iguazu Falls", "A"),
            ("Which river flows through Egypt?", "Nile", "Tigris", "Euphrates", "Amazon", "A"),
            ("Which country uses the rupee as currency?", "India", "Pakistan", "Nepal", "Sri Lanka", "A"),
            ("Which mountain range includes Mount Everest?", "Himalayas", "Andes", "Rockies", "Alps", "A"),
            ("Which ocean is east of Africa?", "Indian Ocean", "Atlantic Ocean", "Pacific Ocean", "Arctic Ocean", "A"),
            ("Which country is called the Land of the Rising Sun?", "Japan", "China", "Korea", "Thailand", "A"),
        ],
        'advanced': [
            ("Which amendment protects freedom of speech in the U.S.?", "First", "Second", "Third", "Fourth", "A"),
            ("What is the capital of Canada?", "Ottawa", "Toronto", "Vancouver", "Montreal", "A"),
            ("Which body regulates international air travel?", "ICAO", "WHO", "UNESCO", "IMF", "A"),
            ("Which country has the largest nominal GDP?", "United States", "China", "Japan", "Germany", "A"),
            ("Who flew solo across the Atlantic first?", "Amelia Earhart", "Valentina Tereshkova", "Harriet Quimby", "Sally Ride", "A"),
            ("Which country has the most UNESCO World Heritage sites?", "Italy", "China", "Spain", "France", "A"),
            ("Which city hosted the 2008 Summer Olympics?", "Beijing", "London", "Athens", "Sydney", "A"),
            ("What is the currency of South Africa?", "Rand", "Dollar", "Euro", "Pound", "A"),
            ("Which country is known as the Land of the Midnight Sun?", "Norway", "Sweden", "Finland", "Iceland", "A"),
            ("Where is the European Union headquartered?", "Brussels", "Strasbourg", "Berlin", "Paris", "A"),
            ("Who invented the telephone?", "Alexander Graham Bell", "Thomas Edison", "Nikola Tesla", "Guglielmo Marconi", "A"),
            ("What is the smallest country by land area?", "Vatican City", "Monaco", "Nauru", "Tuvalu", "A"),
            ("Which mountain range runs along western South America?", "Andes", "Rockies", "Alps", "Himalayas", "A"),
            ("What is the main legislative body of the UK?", "Parliament", "Congress", "Duma", "National Assembly", "A"),
            ("Which country has the largest population?", "China", "India", "USA", "Indonesia", "A"),
            ("Which sea lies between Saudi Arabia and Africa?", "Red Sea", "Mediterranean Sea", "Arabian Sea", "Black Sea", "A"),
            ("What is Earth's longest underwater mountain range?", "Mid-Ocean Ridge", "The Alps", "Andes", "Himalayas", "A"),
            ("Which organization oversees the Olympic Games?", "IOC", "FIFA", "UN", "NATO", "A"),
            ("What is the capital of Italy?", "Rome", "Milan", "Venice", "Naples", "A"),
            ("In what year did the Berlin Wall fall?", "1989", "1991", "1987", "1995", "A"),
            ("Which country is home to Petra?", "Jordan", "Egypt", "Greece", "Turkey", "A"),
            ("What is the official language of Egypt?", "Arabic", "English", "French", "Spanish", "A"),
            ("Which revolution began in Russia in 1917?", "Russian Revolution", "French Revolution", "Industrial Revolution", "Chinese Revolution", "A"),
            ("Which lake is the largest freshwater lake by surface area?", "Lake Superior", "Lake Victoria", "Lake Baikal", "Lake Michigan", "A"),
            ("What is the busiest airport by passenger traffic?", "Hartsfield-Jackson Atlanta", "Beijing Capital", "Dubai", "Tokyo Haneda", "A"),
            ("Which country contains most of the Amazon rainforest?", "Brazil", "Peru", "Colombia", "Venezuela", "A"),
            ("What is the capital of South Korea?", "Seoul", "Busan", "Pyongyang", "Tokyo", "A"),
            ("Which ocean is the smallest?", "Arctic Ocean", "Indian Ocean", "Atlantic Ocean", "Southern Ocean", "A"),
            ("Which country gifted the Statue of Liberty to the United States?", "France", "England", "Spain", "Germany", "A"),
            ("Which river passes through Paris?", "Seine", "Thames", "Danube", "Rhine", "A"),
        ],
    }
    
    # Check curated questions first
    if level == 'beginner' and index in beginner_curated:
        return beginner_curated[index]
    elif level == 'intermediate' and index in intermediate_curated:
        return intermediate_curated[index]
    elif level == 'advanced' and index in advanced_curated:
        return advanced_curated[index]
    
    bank = gk_bank.get(level, gk_bank['beginner'])
    return bank[(index - 1) % len(bank)]


def seed_data(db):
    # Check if database already has enough questions - if so, skip seeding to avoid lock issues
    total_questions = db.execute("SELECT COUNT(*) AS count FROM questions").fetchone()["count"]
    if total_questions > 100:
        # Database already has enough questions, just ensure admin exists
        admin = db.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
        if admin is None:
            db.execute(
                "INSERT INTO users (username, password, is_admin, created_at) VALUES (?, ?, ?, ?)",
                (
                    "admin",
                    generate_password_hash("admin123"),
                    1,
                    datetime.utcnow().isoformat(),
                ),
            )
            db.commit()
        return
    
    admin = db.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
    if admin is None:
        db.execute(
            "INSERT INTO users (username, password, is_admin, created_at) VALUES (?, ?, ?, ?)",
            (
                "admin",
                generate_password_hash("admin123"),
                1,
                datetime.utcnow().isoformat(),
            ),
        )

    sample_questions = db.execute("SELECT COUNT(*) AS count FROM questions").fetchone()["count"]
    examples = [
        ("What keyword begins a function definition in Python?", "func", "def", "function", "begin", "B", "beginner"),
        ("Which symbol is used for single-line comments in Python?", "//", "/*", "#", "--", "C", "beginner"),
        ("Which of these is a valid Python variable name?", "2name", "first-name", "username", "user name", "C", "beginner"),
        ("What type does the expression `5 / 2` return in Python 3?", "int", "float", "str", "bool", "B", "beginner"),
        ("Which method adds an item to the end of a list?", "append()", "add()", "push()", "insert()", "A", "beginner"),
        ("How do you start a block of code that should run if a condition is true?", "if x == 1:", "if (x == 1) then", "if x = 1", "while x == 1", "A", "beginner"),
        ("Which built-in function returns the length of a string or list?", "size()", "count()", "length()", "len()", "D", "beginner"),
        ("How do you create a dictionary in Python?", "{ 'a': 1 }", "[ 'a', 1 ]", "( 'a', 1 )", "< 'a', 1 >", "A", "beginner"),
        ("Which data type is immutable in Python?", "list", "set", "tuple", "dictionary", "C", "beginner"),
        ("What does `==` compare in Python?", "Value equality", "Identity", "Type only", "Assignment", "A", "beginner"),
        ("Which keyword is used to loop over items in a sequence?", "for", "loop", "iterate", "repeat", "A", "intermediate"),
        ("How do you import the `math` module?", "import math", "include math", "using math", "require math", "A", "intermediate"),
        ("What is the output type of `range(5)` in Python 3?", "list", "range", "tuple", "iterator", "B", "intermediate"),
        ("Which statement is used to stop a loop early?", "break", "stop", "exit", "end", "A", "intermediate"),
        ("How do you open a file named `data.txt` for reading?", "open('data.txt', 'r')", "open('data.txt', 'w')", "open('data.txt', 'a')", "open('data.txt', 'x')", "A", "intermediate"),
        ("What is the correct way to create a set?", "{1, 2, 3}", "[1, 2, 3]", "(1, 2, 3)", "{'1', '2', '3'}", "A", "intermediate"),
        ("Which keyword creates an anonymous function?", "function", "lambda", "anon", "def", "B", "intermediate"),
        ("How do you write a multi-line string?", "'''text'''", '"""text"""', "Both A and B", "None of the above", "C", "intermediate"),
        ("What does `str(10)` do?", "Converts to string", "Converts to integer", "Creates a list", "Creates a tuple", "A", "intermediate"),
        ("How many districts are in Kerala?", "10", "12", "14", "16", "C", "intermediate"),
        ("Which operator is used for exponentiation?", "^", "**", "pow", "%%", "B", "intermediate"),
        ("How do you add comments to a line of code?", "# comment", "/* comment */", "// comment", "-- comment", "A", "intermediate"),
        ("Which keyword skips the rest of the current loop iteration?", "break", "continue", "pass", "return", "B", "intermediate"),
        ("How do you create a list comprehension for squares of numbers 0 to 4?", "[x**2 for x in range(5)]", "[x^2 for x in range(5)]", "{x**2 for x in range(5)}", "list(range(5**2))", "A", "intermediate"),
        ("Which method returns a shallow copy of a list?", "copy()", "clone()", "duplicate()", "copy_list()", "A", "intermediate"),
        ("What is the value of `bool('False')` in Python?", "False", "True", "None", "0", "B", "intermediate"),
        ("Which built-in function returns the largest item in an iterable?", "max()", "largest()", "top()", "highest()", "A", "intermediate"),
        ("How do you check whether key 'name' exists in dictionary d?", "'name' in d", "d.has('name')", "d.exists('name')", "d.contains('name')", "A", "intermediate"),
        ("Which string method converts all letters to uppercase?", "upper()", "uppercase()", "capitalize()", "toUpperCase()", "A", "intermediate"),
        ("What does `zip([1,2],[3,4])` return?", "A zip object", "A list of tuples", "A dictionary", "An iterator of lists", "A", "intermediate"),
        ("Which method removes and returns the last item from a list?", "pop()", "remove()", "delete()", "discard()", "A", "advanced"),
        ("What is the correct syntax for an if/else block?", "if x > 0:\n    print(x)\nelse:\n    print(-x)", "if x > 0 then print(x) else print(-x)", "if (x > 0) { print(x) } else { print(-x) }", "if x > 0\nprint(x)\nelse\nprint(-x)", "A", "advanced"),
        ("What keyword is used to create a class?", "class", "struct", "object", "type", "A", "advanced"),
        ("Which of these is a valid string literal?", "Hello", "'Hello'", "Hello'", '"Hello"', "B", "advanced"),
        ("How do you convert a string `'123'` to an integer?", "int('123')", "str('123')", "float('123')", "bool('123')", "A", "advanced"),
        ("What does the expression `3 * 'ab'` return?", "'ababab'", "'ab3'", "'ab ab ab'", "Error", "A", "advanced"),
        ("Which statement is used to handle exceptions?", "try/except", "catch/throw", "if/error", "handle/except", "A", "advanced"),
        ("What is the output of `print(type(True))`?", "<class 'int'>", "<class 'bool'>", "<class 'str'>", "<class 'NoneType'>", "B", "advanced"),
        ("Which loop will execute at least once?", "for", "while", "do-while", "None of the above", "D", "advanced"),
        ("How do you access the value associated with key 'name' in a dictionary `user`?", "user['name']", "user.name", "user{name}", "user.get(name)", "A", "advanced"),
        ("What does the @staticmethod decorator do?", "Allows a method to be called on a class without self", "Creates a private method", "Defines a class method", "Marks a method as abstract", "A", "advanced"),
        ("Which expression creates a generator?", "(x*x for x in range(5))", "[x*x for x in range(5)]", "{x*x for x in range(5)}", "<x*x for x in range(5)>", "A", "advanced"),
        ("How do you catch multiple exception types in one except block?", "except (TypeError, ValueError):", "except TypeError, ValueError:", "except TypeError | ValueError:", "except TypeError or ValueError:", "A", "advanced"),
        ("What is the output of list(map(lambda x: x*2, [1,2,3]))?", "[2, 4, 6]", "[1, 2, 3]", "[3, 6, 9]", "[2, 4, 6, 8]", "A", "advanced"),
        ("Which library is used for regular expressions in Python?", "re", "regex", "pyregex", "regexp", "A", "advanced"),
        ("How do you open a file safely for reading?", "with open('file.txt') as f:", "open('file.txt')", "file = open('file.txt', 'r')", "open.read('file.txt')", "A", "advanced"),
        ("What does __init__ define in a class?", "An initializer for new instances", "A static method", "A class variable", "A module import", "A", "advanced"),
        ("What is the result of 'abc'.split('b')?", "['a', 'c']", "['ab', 'c']", "['a', 'b', 'c']", "['a b c']", "A", "advanced"),
        ("Which function shows the documentation for an object?", "help()", "doc()", "info()", "describe()", "A", "advanced"),
        ("How do you create a set of unique items from a list items?", "set(items)", "list(items)", "tuple(items)", "dict(items)", "A", "advanced"),
        ("Which module provides JSON encoding and decoding?", "json", "pickle", "yaml", "csv", "A", "advanced"),
        ("What does enumerate(['a','b']) produce?", "An enumerate object", "A list", "A tuple", "A set", "A", "advanced"),
        ("How do you import only sqrt from math?", "from math import sqrt", "import math.sqrt", "from math import *", "import sqrt from math", "A", "advanced"),
        ("Which keyword runs cleanup code regardless of exceptions?", "finally", "cleanup", "end", "ensure", "A", "advanced"),
        ("What does os.path.join('a','b') return on Unix?", "a/b", "a\\b", "a:b", "a b", "A", "advanced"),
        ("How do you create a dictionary with keys from a list and default value 0?", "dict.fromkeys(keys, 0)", "{k:0 for k in keys}", "dict(keys, 0)", "fromkeys(keys, 0)", "A", "advanced"),
        ("What is the purpose of if __name__ == '__main__'?", "Run code only when script is executed directly", "Always run code when imported", "Declare the main function", "Import modules safely", "A", "advanced"),
        ("Which built-in function converts a tuple to a list?", "list()", "tuple()", "set()", "dict()", "A", "advanced"),
        ("What type does {'a', 'b'} return?", "set", "list", "tuple", "dict", "A", "advanced"),
        ("How do you merge two dictionaries a and b in Python 3.9+?", "a | b", "a + b", "dict(a, **b)", "merge(a,b)", "A", "advanced"),
    ]
    if sample_questions == 0:
        for question in examples:
            db.execute(
                "INSERT INTO questions (prompt, option_a, option_b, option_c, option_d, correct_option, level) VALUES (?, ?, ?, ?, ?, ?, ?)",
                question,
            )
    else:
        for question in examples:
            prompt = question[0]
            existing = db.execute("SELECT id FROM questions WHERE prompt = ?", (prompt,)).fetchone()
            if existing is None:
                db.execute(
                    "INSERT INTO questions (prompt, option_a, option_b, option_c, option_d, correct_option, level) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    question,
                )
    # Seed topic-specific questions (maths, science, gk) if missing
    topic_examples = [
        # Maths
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
    for tq in topic_examples:
        prompt = tq[0]
        existing = db.execute("SELECT id FROM questions WHERE prompt = ?", (prompt,)).fetchone()
        if existing is None:
            db.execute(
                "INSERT INTO questions (prompt, option_a, option_b, option_c, option_d, correct_option, level, topic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                tq,
            )
    # Ensure each topic has the desired number of questions per level
    desired_counts = {"beginner": 10, "intermediate": 20, "advanced": 30}
    topics = ["python", "maths", "science", "gk"]
    for topic in topics:
        for level, target in desired_counts.items():
            cnt = db.execute(
                "SELECT COUNT(*) AS c FROM questions WHERE COALESCE(topic, 'python') = ? AND COALESCE(level, 'beginner') = ?",
                (topic, level),
            ).fetchone()[0]
            next_index = cnt + 1
            while cnt < target:
                prompt, option_a, option_b, option_c, option_d, correct = generate_topic_question(topic, level, next_index)

                existing = db.execute("SELECT id FROM questions WHERE prompt = ?", (prompt,)).fetchone()
                if existing is None:
                    db.execute(
                        "INSERT INTO questions (prompt, option_a, option_b, option_c, option_d, correct_option, level, topic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (prompt, option_a, option_b, option_c, option_d, correct, level, topic),
                    )
                    cnt += 1
                    next_index += 1
                else:
                    next_index += 1
                    cnt = db.execute(
                        "SELECT COUNT(*) AS c FROM questions WHERE COALESCE(topic, 'python') = ? AND COALESCE(level, 'beginner') = ?",
                        (topic, level),
                    ).fetchone()[0]
    db.commit()


def ensure_balanced_correct_options(db):
    # Randomize stored option positions so correct answers are not always in the same slot
    rows = db.execute("SELECT id, option_a, option_b, option_c, option_d, correct_option FROM questions").fetchall()
    for r in rows:
        qid = r[0]
        opts = [r[1], r[2], r[3], r[4]]
        # find the text of the current correct option
        label = r[5]
        try:
            idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}[label]
        except Exception:
            idx = 0
        correct_text = opts[idx]
        # shuffle until correct_text moves to a different index sometimes
        new_opts = opts[:]
        random.shuffle(new_opts)
        # find new index of the correct text
        try:
            new_idx = new_opts.index(correct_text)
        except ValueError:
            # fallback: if texts are duplicated or not found, skip updating
            continue
        new_label = ['A', 'B', 'C', 'D'][new_idx]
        # Update DB only if ordering changed
        if new_opts != opts:
            db.execute(
                "UPDATE questions SET option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_option = ? WHERE id = ?",
                (new_opts[0], new_opts[1], new_opts[2], new_opts[3], new_label, qid),
            )
    db.commit()


@app.before_request
def setup_database():
    if not os.path.exists(app.config["DATABASE"]):
        open(app.config["DATABASE"], "a").close()
    if not getattr(app, "_db_initialized", False):
        init_db()
        app._db_initialized = True


def get_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    db = get_db()
    user = db.execute("SELECT id, username, full_name, is_admin FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(user) if user is not None else None


@app.route("/")
def home():
    user = get_user()
    return render_template("home.html", user=user)


@app.route("/select", methods=["GET"])
def select_level():
    user = get_user()
    db = get_db()
    rows = db.execute("SELECT DISTINCT COALESCE(topic, 'python') AS topic FROM questions").fetchall()
    topics = [r[0] for r in rows if r[0]]
    # ensure common topics exist
    for t in ("python", "maths", "science", "gk"):
        if t not in topics:
            topics.append(t)
    return render_template("select_level.html", user=user, topics=sorted(set(topics)))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])
            display_name = user["full_name"] or user["username"]
            flash(f"Welcome back, {display_name}!", "success")
            return redirect(url_for("home"))
        flash("Username or password is incorrect.", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        if not full_name:
            flash("Full name is required.", "danger")
        elif not username or not password:
            flash("Username and password are required.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        else:
            db = get_db()
            existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if existing:
                flash("A user with that name already exists.", "danger")
            else:
                db.execute(
                    "INSERT INTO users (username, full_name, password, is_admin, created_at) VALUES (?, ?, ?, ?, ?)",
                    (username, full_name, generate_password_hash(password), 0, datetime.utcnow().isoformat()),
                )
                db.commit()
                flash("Registration successful. Please log in.", "success")
                return redirect(url_for("login"))
    return render_template("register.html")


ALLOWED_ADMIN_EMAILS = {
    "jefinjoseph2005@gmail.com",
    "aswinaiswaria@gmail.com",
}


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Email and password are required.", "danger")
        elif email not in ALLOWED_ADMIN_EMAILS:
            flash("This email is not authorized for admin access.", "danger")
        elif password != "98765":
            flash("Incorrect admin password.", "danger")
        else:
            db = get_db()
            display_name = None
            if email == "jefinjoseph2005@gmail.com":
                display_name = "Jefin Joseph"
            elif email == "aswinaiswaria@gmail.com":
                display_name = "Aswin S"

            user = db.execute("SELECT * FROM users WHERE username = ?", (email,)).fetchone()
            if user is None:
                db.execute(
                    "INSERT INTO users (username, full_name, password, is_admin, created_at) VALUES (?, ?, ?, ?, ?)",
                    (email, display_name, generate_password_hash("98765"), 1, datetime.utcnow().isoformat()),
                )
                db.commit()
                user = db.execute("SELECT * FROM users WHERE username = ?", (email,)).fetchone()
            else:
                if not user["is_admin"]:
                    db.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user["id"],))
                if display_name and user["full_name"] != display_name:
                    db.execute("UPDATE users SET full_name = ? WHERE id = ?", (display_name, user["id"]))
                db.commit()
                user = db.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = True
            flash("Admin login successful.", "success")
            return redirect(url_for("admin"))
    return render_template("admin_login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    user = get_user()

    db = get_db()

    # POST: grade the quiz
    if request.method == "POST":
        question_ids = session.get("quiz_question_ids")
        if not question_ids:
            flash("Your quiz session expired. Please try again.", "warning")
            return redirect(url_for("quiz"))

        correct_map = session.get("quiz_correct_options", {})
        score = 0
        for qid in question_ids:
            ans = request.form.get(str(qid))
            if ans and correct_map.get(str(qid)) == ans:
                score += 1

        total = len(question_ids)
        # save result only for logged in users
        if user is not None:
            db.execute(
                "INSERT INTO results (user_id, score, total, created_at) VALUES (?, ?, ?, ?)",
                (user["id"], score, total, datetime.utcnow().isoformat()),
            )
            db.commit()
        session["quiz_result"] = {"score": score, "total": total}
        return redirect(url_for("result"))

    # GET: prepare a new quiz
    selection = request.args.get("selection")
    level = "beginner"
    topic = request.args.get("topic")
    if selection and ":" in selection:
        selected_level, selected_count = selection.split(":", 1)
        level = selected_level.lower()
        try:
            num_questions = max(1, int(selected_count))
        except ValueError:
            num_questions = None
    else:
        level = request.args.get("level") or session.get("quiz_level", "beginner")
        level = level.lower()
        try:
            num_questions = int(request.args.get("count"))
        except (TypeError, ValueError):
            num_questions = None

    default_counts = {"beginner": 10, "intermediate": 20, "advanced": 30}
    if num_questions is None:
        num_questions = default_counts.get(level, 5)

    if topic:
        topic = topic.lower()
        rows = db.execute(
            "SELECT id, prompt, option_a, option_b, option_c, option_d, correct_option FROM questions WHERE COALESCE(topic, 'python') = ? AND COALESCE(level, 'beginner') = ? ORDER BY RANDOM() LIMIT ?",
            (topic, level, num_questions),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT id, prompt, option_a, option_b, option_c, option_d, correct_option FROM questions WHERE COALESCE(level, 'beginner') = ? ORDER BY RANDOM() LIMIT ?",
            (level, num_questions),
        ).fetchall()
    if not rows:
        rows = db.execute(
            "SELECT id, prompt, option_a, option_b, option_c, option_d, correct_option FROM questions ORDER BY RANDOM() LIMIT ?",
            (num_questions,),
        ).fetchall()

    questions = []
    shuffled_correct = {}
    for r in rows:
        q = dict(r)
        opts = [
            {"label": "A", "text": q["option_a"]},
            {"label": "B", "text": q["option_b"]},
            {"label": "C", "text": q["option_c"]},
            {"label": "D", "text": q["option_d"]},
        ]
        random.shuffle(opts)
        for idx, opt in enumerate(opts):
            opt["display_label"] = chr(ord("A") + idx)
            if opt["label"] == q["correct_option"]:
                shuffled_correct[str(q["id"])] = opt["display_label"]
        q["options"] = opts
        questions.append(q)

    timer_seconds = max(60, num_questions * 30)
    session["quiz_question_ids"] = [q["id"] for q in questions]
    session["quiz_correct_options"] = shuffled_correct
    session["quiz_level"] = level

    return render_template(
        "quiz.html",
        user=user,
        questions=questions,
        timer_seconds=timer_seconds,
        level=level.capitalize(),
        num_questions=num_questions,
    )


@app.route("/result")
def result():
    user = get_user()
    result_data = session.pop("quiz_result", None)
    if result_data is None:
        flash("No quiz result available. Please take the quiz first.", "info")
        return redirect(url_for("quiz"))
    return render_template("result.html", user=user, result=result_data)


@app.route("/feedback", methods=["POST"])
def submit_feedback():
    username = request.form.get("username", "").strip() or None
    email = request.form.get("email", "").strip() or None
    rating = request.form.get("rating")
    message = request.form.get("message", "").strip()

    if not rating or not message:
        flash("Please provide a rating and feedback message.", "danger")
        return redirect(url_for("home"))

    try:
        rating_value = int(rating)
    except ValueError:
        flash("Invalid rating value.", "danger")
        return redirect(url_for("home"))

    db = get_db()
    db.execute(
        "INSERT INTO feedback (username, email, rating, message, created_at) VALUES (?, ?, ?, ?, ?)",
        (username, email, rating_value, message, datetime.utcnow().isoformat()),
    )
    db.commit()
    flash("Thank you for your feedback!", "success")
    return redirect(url_for("home"))


def admin_required():
    user = get_user()
    if user is None or not user.get("is_admin"):
        flash("Administrator access required.", "danger")
        return redirect(url_for("home"))
    if user.get("username", "").lower() not in ALLOWED_ADMIN_EMAILS:
        flash("Administrator access is restricted.", "danger")
        return redirect(url_for("home"))
    return user


@app.route("/admin")
def admin():
    user = admin_required()
    if isinstance(user, Response):
        return user
    db = get_db()
    questions = db.execute(
        "SELECT id, prompt, option_a, option_b, option_c, option_d, correct_option, COALESCE(level, 'beginner') AS level, COALESCE(topic, 'python') AS topic "
        "FROM questions ORDER BY level, topic, id ASC"
    ).fetchall()
    return render_template("admin.html", user=user, questions=questions)


@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    user = admin_required()
    if isinstance(user, Response):
        return user
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        option_a = request.form.get("option_a", "").strip()
        option_b = request.form.get("option_b", "").strip()
        option_c = request.form.get("option_c", "").strip()
        option_d = request.form.get("option_d", "").strip()
        correct = request.form.get("correct_option", "")
        level = request.form.get("level", "beginner")
        topic = request.form.get("topic", "python")
        if not (prompt and option_a and option_b and option_c and option_d and correct):
            flash("All fields are required.", "danger")
        else:
            db = get_db()
            db.execute(
                "INSERT INTO questions (prompt, option_a, option_b, option_c, option_d, correct_option, level, topic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (prompt, option_a, option_b, option_c, option_d, correct, level, topic),
            )
            db.commit()
            flash("Question added successfully.", "success")
            return redirect(url_for("admin"))
    TOPICS = ["python", "maths", "science", "gk"]
    return render_template("add_question.html", user=user, topics=TOPICS)


@app.route("/admin/edit/<int:question_id>", methods=["GET", "POST"])
def admin_edit(question_id):
    user = admin_required()
    if isinstance(user, Response):
        return user
    db = get_db()
    q = db.execute("SELECT id, prompt, option_a, option_b, option_c, option_d, correct_option, COALESCE(level, 'beginner') AS level, COALESCE(topic, 'python') AS topic FROM questions WHERE id = ?", (question_id,)).fetchone()
    if not q:
        flash("Question not found.", "danger")
        return redirect(url_for("admin"))

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        option_a = request.form.get("option_a", "").strip()
        option_b = request.form.get("option_b", "").strip()
        option_c = request.form.get("option_c", "").strip()
        option_d = request.form.get("option_d", "").strip()
        correct = request.form.get("correct_option", "")
        level = request.form.get("level", "beginner")
        topic = request.form.get("topic", "python")
        if not (prompt and option_a and option_b and option_c and option_d and correct):
            flash("All fields are required.", "danger")
        else:
            db.execute(
                "UPDATE questions SET prompt = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_option = ?, level = ?, topic = ? WHERE id = ?",
                (prompt, option_a, option_b, option_c, option_d, correct, level, topic, question_id),
            )
            db.commit()
            flash("Question updated successfully.", "success")
            return redirect(url_for("admin"))

    TOPICS = ["python", "maths", "science", "gk"]
    return render_template("add_question.html", user=user, topics=TOPICS, question=dict(q))


@app.route("/admin/users")
def admin_users():
    user = admin_required()
    if isinstance(user, Response):
        return user
    db = get_db()
    users = db.execute("SELECT id, username, is_admin, created_at FROM users ORDER BY id DESC").fetchall()
    return render_template("admin_users.html", user=user, users=users)


@app.route("/admin/results")
def admin_results():
    user = admin_required()
    if isinstance(user, Response):
        return user
    db = get_db()
    rows = db.execute(
        "SELECT r.id, u.username, r.score, r.total, r.created_at FROM results r JOIN users u ON r.user_id = u.id ORDER BY r.created_at DESC"
    ).fetchall()
    return render_template("admin_results.html", user=user, results=rows)


@app.route("/admin/feedback")
def admin_feedback():
    user = admin_required()
    if isinstance(user, Response):
        return user
    db = get_db()
    feedback = db.execute(
        "SELECT id, username, email, rating, message, created_at FROM feedback ORDER BY created_at DESC"
    ).fetchall()
    return render_template("admin_feedback.html", user=user, feedback=feedback)


@app.route("/admin/reset-password/<int:user_id>")
def admin_reset_password(user_id):
    user = admin_required()
    if isinstance(user, Response):
        return user
    db = get_db()
    # generate a temporary password (for demo only)
    temp = "temp" + str(random.randint(1000, 9999))
    db.execute("UPDATE users SET password = ? WHERE id = ?", (generate_password_hash(temp), user_id))
    db.commit()
    flash(f"Password for user id {user_id} reset to '{temp}' (displayed for admin).", "info")
    return redirect(url_for("admin_users"))


@app.route("/admin/delete-user/<int:user_id>")
def admin_delete_user(user_id):
    user = admin_required()
    if isinstance(user, Response):
        return user
    if user_id == user["id"]:
        flash("You cannot delete your own admin account while logged in.", "danger")
        return redirect(url_for("admin_users"))
    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for("admin_users"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        temp_password = request.form.get("temp_password", "")
        new_password = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        if not (username and temp_password and new_password and confirm):
            flash("All fields are required.", "danger")
            return render_template("forgot_password.html")
        if new_password != confirm:
            flash("New passwords do not match.", "danger")
            return render_template("forgot_password.html")
        db = get_db()
        user = db.execute("SELECT id, password FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            flash("No user found with that username.", "danger")
            return render_template("forgot_password.html")
        # verify temporary password matches the stored (hashed) password
        if not check_password_hash(user[1], temp_password):
            flash("Temporary password is incorrect.", "danger")
            return render_template("forgot_password.html")
        # update to new password
        db.execute("UPDATE users SET password = ? WHERE id = ?", (generate_password_hash(new_password), user[0]))
        db.commit()
        flash("Password updated successfully. You can now log in with your new password.", "success")
        return redirect(url_for("login"))
    return render_template("forgot_password.html")


@app.route("/admin/delete/<int:question_id>")
def admin_delete(question_id):
    user = admin_required()
    if isinstance(user, Response):
        return user
    db = get_db()
    db.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    db.commit()
    flash("Question deleted.", "info")
    return redirect(url_for("admin"))


@app.route("/admin/import-topic-questions", methods=["POST"])
def admin_import_topic_questions():
    user = admin_required()
    if isinstance(user, Response):
        return user
    db = get_db()
    desired_counts = {"beginner": 10, "intermediate": 20, "advanced": 30}
    topics = ["python", "maths", "science", "gk"]
    inserted = 0
    batch_size = 10  # Commit after every 10 inserts to avoid long locks
    
    for topic in topics:
        for level, target in desired_counts.items():
            try:
                cnt = db.execute(
                    "SELECT COUNT(*) AS c FROM questions WHERE COALESCE(topic, 'python') = ? AND COALESCE(level, 'beginner') = ?",
                    (topic, level),
                ).fetchone()[0]
                next_index = cnt + 1
                batch_count = 0
                
                while cnt < target:
                    try:
                        prompt, option_a, option_b, option_c, option_d, correct = generate_topic_question(topic, level, next_index)
                        existing = db.execute(
                            "SELECT id FROM questions WHERE prompt = ? AND COALESCE(topic, 'python') = ?",
                            (prompt, topic),
                        ).fetchone()
                        if existing:
                            next_index += 1
                            continue
                        db.execute(
                            "INSERT INTO questions (prompt, option_a, option_b, option_c, option_d, correct_option, level, topic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (prompt, option_a, option_b, option_c, option_d, correct, level, topic),
                        )
                        inserted += 1
                        batch_count += 1
                        cnt += 1
                        next_index += 1
                        
                        # Commit after batch_size inserts to release locks
                        if batch_count >= batch_size:
                            db.commit()
                            batch_count = 0
                    except sqlite3.OperationalError as e:
                        if "database is locked" in str(e):
                            db.rollback()
                            flash(f"Database temporarily locked. Imported {inserted} question(s) so far.", "warning")
                            return redirect(url_for("admin"))
                        raise
            except Exception as e:
                db.rollback()
                flash(f"Error importing {topic} questions: {str(e)}", "danger")
                return redirect(url_for("admin"))
    
    db.commit()
    flash(f"Imported {inserted} topic-relevant question(s).", "success")
    return redirect(url_for("admin"))


@app.route("/admin/clean-prompts", methods=["POST"])
def admin_clean_prompts():
    user = admin_required()
    if isinstance(user, Response):
        return user
    db = get_db()
    rows = db.execute("SELECT id, prompt FROM questions").fetchall()
    updated = 0
    for r in rows:
        qid = r[0]
        prompt = r[1]
        cleaned = prompt
        # Remove trailing parenthetical that contains #number
        cleaned = re.sub(r"\s*\([^)]*#\d+\)\s*$", "", cleaned)
        # Remove trailing '(... question placeholder ...)' patterns
        cleaned = re.sub(r"\s*\([^)]*question placeholder[^)]*\)\s*$", "", cleaned, flags=re.I)
        # Remove trailing '(level topic)' patterns like '(intermediate maths)'
        cleaned = re.sub(r"\s*\((?:beginner|intermediate|advanced)\s+\w+\)\s*$", "", cleaned, flags=re.I)
        cleaned = cleaned.strip()
        if cleaned != prompt:
            db.execute("UPDATE questions SET prompt = ? WHERE id = ?", (cleaned, qid))
            updated += 1
    db.commit()
    flash(f"Cleaned {updated} question prompt(s).", "success")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
