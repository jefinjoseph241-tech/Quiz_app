#!/usr/bin/env python3
"""
Standalone database seeding script to avoid Flask debug mode locking issues.
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

DATABASE = "quiz.db"

def get_db():
    db = sqlite3.connect(DATABASE, timeout=30.0)
    db.row_factory = sqlite3.Row
    return db

def init_db_schema():
    """Initialize the database schema"""
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
    db.close()
    print("✓ Database schema created")

def seed_database():
    """Seed the database with questions and admin user"""
    db = get_db()
    
    # Create admin user
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
        print("✓ Admin user created")
    
    # Import the app to get access to question generators
    from app import (
        generate_topic_question,
        generate_python_question,
        generate_science_question,
        generate_gk_question,
        generate_maths_question,
    )
    
    # Seed topic-specific questions
    desired_counts = {"beginner": 10, "intermediate": 20, "advanced": 30}
    topics = ["python", "maths", "science", "gk"]
    
    for topic in topics:
        for level, target in desired_counts.items():
            # Check how many questions we already have for this topic/level
            cnt = db.execute(
                "SELECT COUNT(*) AS c FROM questions WHERE COALESCE(topic, 'python') = ? AND COALESCE(level, 'beginner') = ?",
                (topic, level),
            ).fetchone()["c"]
            
            next_index = cnt + 1
            inserted = 0
            
            while cnt < target:
                try:
                    prompt, option_a, option_b, option_c, option_d, correct = generate_topic_question(
                        topic, level, next_index
                    )
                    
                    # Check if question already exists
                    existing = db.execute(
                        "SELECT id FROM questions WHERE prompt = ?", (prompt,)
                    ).fetchone()
                    
                    if existing is None:
                        db.execute(
                            "INSERT INTO questions (prompt, option_a, option_b, option_c, option_d, correct_option, level, topic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (prompt, option_a, option_b, option_c, option_d, correct, level, topic),
                        )
                        cnt += 1
                        inserted += 1
                    
                    next_index += 1
                except Exception as e:
                    print(f"Error generating question for {topic}/{level}/{next_index}: {e}")
                    next_index += 1
                    continue
            
            if inserted > 0:
                print(f"✓ Inserted {inserted} {topic}/{level} questions")
    
    db.commit()
    print("\n✓ Database seeding completed!")
    
    # Verify counts
    for topic in topics:
        for level in ["beginner", "intermediate", "advanced"]:
            cnt = db.execute(
                "SELECT COUNT(*) AS c FROM questions WHERE COALESCE(topic, 'python') = ? AND COALESCE(level, 'beginner') = ?",
                (topic, level),
            ).fetchone()["c"]
            print(f"  {topic:8} {level:12}: {cnt:3} questions")
    
    db.close()

if __name__ == "__main__":
    init_db_schema()
    seed_database()
