#!/usr/bin/env python3
"""
Update the question generator functions with curated questions for specific ranges.
"""

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Find and replace the generate_gk_question function
old_gk_func = """def generate_gk_question(level, index):
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
    bank = gk_bank.get(level, gk_bank['beginner'])
    return bank[(index - 1) % len(bank)]"""

new_gk_func = """def generate_gk_question(level, index):
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
    return bank[(index - 1) % len(bank)]"""

if old_gk_func in content:
    content = content.replace(old_gk_func, new_gk_func)
    print("✓ Updated generate_gk_question function")
else:
    print("✗ Could not find generate_gk_question function to update")
    
# Write back the updated content
with open('app.py', 'w') as f:
    f.write(content)

print("✓ app.py updated successfully")

# Now reseed the database
print("\nReseeding database...")
from app import app, init_db

with app.app_context():
    init_db()
    print("✓ Database reseeded")

print("\nDone!")
