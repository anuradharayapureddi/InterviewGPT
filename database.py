
import sqlite3


def create_database():
    conn = sqlite3.connect("interview_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            feedback TEXT,
            technical_score INTEGER,
            communication_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add score columns to an existing database safely.
    cursor.execute("PRAGMA table_info(interview_history)")
    columns = [column[1] for column in cursor.fetchall()]

    if "technical_score" not in columns:
        cursor.execute(
            "ALTER TABLE interview_history ADD COLUMN technical_score INTEGER"
        )

    if "communication_score" not in columns:
        cursor.execute(
            "ALTER TABLE interview_history ADD COLUMN communication_score INTEGER"
        )

    conn.commit()
    conn.close()


def save_interview(
    question,
    answer,
    feedback,
    technical_score=None,
    communication_score=None
):
    conn = sqlite3.connect("interview_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interview_history (
            question,
            answer,
            feedback,
            technical_score,
            communication_score
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        question,
        answer,
        feedback,
        technical_score,
        communication_score
    ))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("Interview database created successfully!")
