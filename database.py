import sqlite3
from datetime import date
import pandas as pd

class DatabaseManager:
    def __init__(self, db_name="study_planner.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        # Create all tables
        conn = self.get_connection()
        cursor = conn.cursor()

        # Subjects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                difficulty INTEGER CHECK(difficulty >= 1 AND difficulty <= 10),
                hours REAL,
                priority INTEGER CHECK(priority >= 1 AND priority <= 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                due_date DATE,
                estimated_hours REAL,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            )
        """)

        # Study logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                date DATE,
                hours_studied REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            )
        """)

        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()


class SubjectCRUD:
    def __init__(self, db_manager):
        self.db = db_manager

    def create(self, name, difficulty, hours, priority):
        # Add new subject
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO subjects (name, difficulty, hours, priority) VALUES (?, ?, ?, ?)",
            (name, difficulty, hours, priority)
        )
        subject_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return subject_id

    def read(self, subject_id=None):
        # Get subjects
        conn = self.db.get_connection()
        if subject_id:
            query = "SELECT * FROM subjects WHERE id = ?"
            df = pd.read_sql_query(query, conn, params=(subject_id,))
        else:
            query = "SELECT * FROM subjects ORDER BY priority DESC, name ASC"
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def delete(self, subject_id):
        # Delete a subject
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success


class TaskCRUD:
    def __init__(self, db_manager):
        self.db = db_manager

    def create(self, subject_id, title, description, due_date, estimated_hours):
        # Add new task
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tasks (subject_id, title, description, due_date, estimated_hours) 
               VALUES (?, ?, ?, ?, ?)""",
            (subject_id, title, description, due_date, estimated_hours)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def read(self):
        # Get all tasks with subject names
        conn = self.db.get_connection()
        query = """
            SELECT t.*, s.name as subject_name 
            FROM tasks t 
            LEFT JOIN subjects s ON t.subject_id = s.id
            ORDER BY t.due_date ASC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_by_status(self, completed=False):
        # Get tasks by completion status
        conn = self.db.get_connection()
        query = """
            SELECT t.*, s.name as subject_name 
            FROM tasks t 
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE t.completed = ?
            ORDER BY t.due_date ASC
        """
        df = pd.read_sql_query(query, conn, params=(int(completed),))
        conn.close()
        return df

    def mark_complete(self, task_id):
        # Mark task as done
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()


class StudyLogCRUD:
    def __init__(self, db_manager):
        self.db = db_manager

    def create(self, subject_id, date, hours_studied, notes=""):
        # Add study session
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO study_logs (subject_id, date, hours_studied, notes) 
               VALUES (?, ?, ?, ?)""",
            (subject_id, date, hours_studied, notes)
        )
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def read(self):
        # Get all study logs
        conn = self.db.get_connection()
        query = """
            SELECT sl.*, s.name as subject_name 
            FROM study_logs sl 
            LEFT JOIN subjects s ON sl.subject_id = s.id
            ORDER BY sl.date DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df


class ChatHistoryCRUD:
    def __init__(self, db_manager):
        self.db = db_manager

    def create(self, message, response):
        # Save chat message
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (message, response) VALUES (?, ?)",
            (message, response)
        )
        chat_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return chat_id

    def read(self, limit=None):
        # Get chat history
        conn = self.db.get_connection()
        query = "SELECT * FROM chat_history ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df


class AnalyticsDB:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_total_study_hours(self):
        # Sum of all study hours
        conn = self.db.get_connection()
        query = "SELECT COALESCE(SUM(hours_studied), 0) as total FROM study_logs"
        result = pd.read_sql_query(query, conn)
        conn.close()
        return float(result['total'][0])

    def get_task_stats(self):
        # Count completed and pending tasks
        conn = self.db.get_connection()
        completed = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM tasks WHERE completed = 1", conn
        )['count'][0]
        pending = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM tasks WHERE completed = 0", conn
        )['count'][0]
        conn.close()
        return {'completed': completed, 'pending': pending}

    def get_hours_by_subject(self):
        # Study hours grouped by subject
        conn = self.db.get_connection()
        query = """
            SELECT s.name, COALESCE(SUM(sl.hours_studied), 0) as hours
            FROM subjects s
            LEFT JOIN study_logs sl ON s.id = sl.subject_id
            GROUP BY s.id, s.name
            ORDER BY hours DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_average_difficulty(self):
        # Average difficulty of all subjects
        conn = self.db.get_connection()
        query = "SELECT COALESCE(AVG(difficulty), 0) as avg FROM subjects"
        result = pd.read_sql_query(query, conn)
        conn.close()
        return float(result['avg'][0])


# Initialize all database managers
def get_db_managers(db_name="study_planner.db"):
    # Create and return all database managers
    db = DatabaseManager(db_name)
    return {
        'db': db,
        'subjects': SubjectCRUD(db),
        'tasks': TaskCRUD(db),
        'logs': StudyLogCRUD(db),
        'chat': ChatHistoryCRUD(db),
        'analytics': AnalyticsDB(db)
    }