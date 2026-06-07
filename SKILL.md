# Quiz Question Seeder Skill

## Purpose

This workspace skill helps generate and seed quiz questions for the Flask quiz app in `d:\quizapp`.

It focuses on creating:
- `python`
- `maths`
- `science`
- `gk`

for each difficulty level:
- `beginner`
- `intermediate`
- `advanced`

with target counts:
- 10 beginner questions per topic
- 20 intermediate questions per topic
- 30 advanced questions per topic

## When to use

Use this skill when you want to add structured quiz content for every topic/level combination and produce seed data that can be inserted into the app's `questions` table.

## Workflow

1. Confirm the topics and levels to seed.
2. For each topic-level pair, generate distinct multiple-choice questions.
3. Each question must include:
   - `prompt`
   - `option_a`
   - `option_b`
   - `option_c`
   - `option_d`
   - `correct_option` (`A`, `B`, `C`, or `D`)
4. Keep questions aligned with the app style: short, clear, knowledge-based, and suitable for beginner/intermediate/advanced.
5. Produce output in a format easy to insert into the app database, such as a JSON list or SQL insert statements.

## Expected output

- 10 questions for each topic at `beginner`
- 20 questions for each topic at `intermediate`
- 30 questions for each topic at `advanced`
- Total: 240 questions (4 topics x 60 questions)

Do not generate duplicates across the same topic and level.

## Example request

"Add 10 beginner, 20 intermediate, and 30 advanced questions for each of the topics: python, maths, science, and gk."

## Example response structure

- Topic: `python`
  - Level: `beginner`
    - Question 1: { prompt, option_a, option_b, option_c, option_d, correct_option }
    - ...
  - Level: `intermediate`
    - Question 1: ...
  - Level: `advanced`
    - Question 1: ...
- Topic: `maths`
  - ...

## Notes

- Prefer questions that fit the current app's quiz database schema.
- If the app already includes seeding logic, highlight that this skill is for generating additional content or examples to expand the database.
- If asked for code, return the questions as Python seeding data or SQL insert statements.
