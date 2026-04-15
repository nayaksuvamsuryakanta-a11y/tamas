#!/usr/bin/env python3
"""
TAMAS CLI - Terminal Academic Management & Assessment System
Aligned with Dr. Harisingh Gour Vishwavidyalaya BCA NEP-2020 Syllabus
"""

import os
import sqlite3
import json
import hashlib
import sys
from datetime import datetime
from getpass import getpass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.text import Text

console = Console()
DB_PATH = "tamas_nep2020.db"


# ================= DATABASE ENGINE =================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()
        self._seed_syllabus()

    def _init_schema(self):
        """Create all tables with correct syntax."""
        self.conn.executescript("""
                                CREATE TABLE IF NOT EXISTS users
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    username
                                    TEXT
                                    UNIQUE
                                    NOT
                                    NULL,
                                    email
                                    TEXT
                                    UNIQUE
                                    NOT
                                    NULL,
                                    password_hash
                                    TEXT
                                    NOT
                                    NULL,
                                    role
                                    TEXT
                                    DEFAULT
                                    'student',
                                    sem_id
                                    INTEGER
                                    NOT
                                    NULL,
                                    created_at
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP
                                );

                                CREATE TABLE IF NOT EXISTS courses
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    sem_id
                                    INTEGER
                                    NOT
                                    NULL,
                                    code
                                    TEXT
                                    UNIQUE
                                    NOT
                                    NULL,
                                    title
                                    TEXT
                                    NOT
                                    NULL,
                                    theory_credits
                                    INTEGER
                                    DEFAULT
                                    0,
                                    practical_credits
                                    INTEGER
                                    DEFAULT
                                    0,
                                    total_credits
                                    INTEGER
                                    GENERATED
                                    ALWAYS AS
                                (
                                    theory_credits
                                    +
                                    practical_credits
                                ) STORED
                                    );

                                CREATE TABLE IF NOT EXISTS units
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    course_id
                                    INTEGER
                                    NOT
                                    NULL,
                                    num
                                    INTEGER
                                    NOT
                                    NULL,
                                    title
                                    TEXT,
                                    FOREIGN
                                    KEY
                                (
                                    course_id
                                ) REFERENCES courses
                                (
                                    id
                                ) ON DELETE CASCADE
                                    );

                                CREATE TABLE IF NOT EXISTS library
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    title
                                    TEXT
                                    NOT
                                    NULL,
                                    author
                                    TEXT
                                    DEFAULT
                                    'Unknown',
                                    type
                                    TEXT
                                    CHECK (
                                    type
                                    IN
                                (
                                    'syllabus',
                                    'book',
                                    'paper',
                                    'notes'
                                )),
                                    unit_id INTEGER NOT NULL,
                                    file_path TEXT NOT NULL,
                                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY
                                (
                                    unit_id
                                ) REFERENCES units
                                (
                                    id
                                ) ON DELETE CASCADE
                                    );

                                CREATE TABLE IF NOT EXISTS attendance
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    student_id
                                    INTEGER
                                    NOT
                                    NULL,
                                    course_id
                                    INTEGER
                                    NOT
                                    NULL,
                                    attended
                                    INTEGER
                                    DEFAULT
                                    0,
                                    total_classes
                                    INTEGER
                                    DEFAULT
                                    0,
                                    UNIQUE
                                (
                                    student_id,
                                    course_id
                                ),
                                    FOREIGN KEY
                                (
                                    student_id
                                ) REFERENCES users
                                (
                                    id
                                ) ON DELETE CASCADE,
                                    FOREIGN KEY
                                (
                                    course_id
                                ) REF
                                R
                                    ENCES 
                                    course
                                    s
    
                                                            (
                                    id
                                )
                                  ON DELETE CASCADE
                                    );

                                CREATE TABLE IF NOT EXISTS exam_papers
                                (
                                    id
                                    INTEGER
     
                                 
                                              
                                                  
                                 
                                    PR
                                IMARY
                                    KEY
                                    AUTOINCREMENT,
           
                                 
                                      
                                           
                                           
                                       
                                               NOT
                                           exa
                                    _type
 
                                       
                                         
                                    (
      
                                           
                                       
                                         
                                    ','qu
                                    z'))
                                    
  
                                         
                                             
                                        
                                       
                                    sem_i
                                    T NOT NULL,

                                             
                                           
                                                     c
                                    at TIME
                                    TAM
                                 
                                    DEFAULT CU
                                RRENT_TIMESTAMP,
 
                                 
                                      
                                                                FOREIGN KEY (created_by) REFERENCES 
                                s
                                    ers(id)

                                                        
                                 
                                      
                                 
                                         );

                                CREATE TABLE IF NOT EXISTS results (
                                                                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                       student_id INTEGER NOT NULL,
                                                                       paper_id INTEGER NOT NULL,
                                                                       score REAL NOT NULL,
                                                                       max_marks REAL NOT NULL,
                                                                       submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                                       FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                                    FOREIGN KEY (paper_id) REFERENCES exam_papers(id) ON DELETE CASCADE
                                    );
                                """)
        self.conn.commit()

    def _seed_syllabus(self):
        """Insert exact NEP-2020 BCA syllabus data."""
        if self.conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0] > 0:
            return

        sem_courses = {
            1: [
                ('CSA-DSM-111', 'Programming using C', 4, 0),
                ('CSA-DSM-112', 'Lab based on C programming', 0, 2),
                ('CSA-DSM-113', 'PC Software', 4, 0),
                ('CSA-DSM-114', 'Lab based on PC Software', 0, 2),
                ('CSA-MDM-111', 'Mathematics for Computer Science', 6, 0),
                ('CSA-AEC-111', 'Fundamental of Computer Science', 2, 0),
                ('CSA-SEC-111', 'Lab Based ICT-I', 0, 2)
            ],
            2: [
                ('CSA-DSM-211', 'Data Structures', 4, 0),
                ('CSA-DSM-212', 'Lab based on Data Structures using C', 0, 2),
                ('CSA-DSM-213', 'OOPs using C++', 4, 0),
                ('CSA-DSM-214', 'Lab based on C++ Programming', 0, 2),
                ('CSA-MDM-211', 'Computer Organization', 6, 0),
                ('CSA-AEC-211', 'Lab based on Web Designing', 0, 2),
                ('CSA-SEC-211', 'Lab based ICT-II', 0, 2)
            ],
            3: [
                ('CSA-DSM-311', 'PHP Programming', 4, 0),
                ('CSA-DSM-312', 'Lab based on PHP', 0, 2),
                ('CSA-DSM-313', 'Database Management System', 4, 0),
                ('CSA-DSM-314', 'Lab Based on SQL', 0, 2),
                ('CSA-DSM-315', 'Fundamental of Computer Algorithms', 6, 0),
                ('CSA-AEC-311', 'Lab Based on Web Designing using JavaScript', 0, 2),
                ('CSA-SEC-311', 'Seminar/Poster presentation/Group Discussion', 0, 2)
            ],
            4: [
                ('CSA-DSM-411', 'Java Programming', 4, 0),
                ('CSA-DSM-412', 'Lab Based on Java Programming', 0, 2),
                ('CSA-DSM-413', 'Python Programming', 4, 0),
                ('CSA-DSM-414', 'Lab Based on Python Programming', 0, 2),
                ('CSA-DSM-415', 'Operating System', 6, 0),
                ('CSA-AEC-411', 'Fundamental of Cyber Security', 2, 0),
                ('CSA-SEC-411', 'Seminar/Poster presentation/Group Discussion', 0, 2)
            ],
            5: [
                ('CSA-DSM-511', 'R Programming', 4, 0),
                ('CSA-DSM-512', 'Lab Based on R programming', 0, 2),
                ('CSA-DSM-513', 'Computer Networks', 4, 0),
                ('CSA-DSM-514', 'Computer Graphics', 4, 0),
                ('CSA-DSM-515', 'Data Analytics', 4, 0),
                ('CSA-SEC-511', 'Internship', 0, 2)
            ],
            6: [
                ('CSA-DSM-611', 'Artificial Intelligence', 4, 0),
                ('CSA-DSM-612', 'Lab Based on Artificial Intelligence', 0, 2),
                ('CSA-DSM-613', 'Theory of Computation', 4, 0),
                ('CSA-DSM-614', 'Software Engineering', 4, 0),
                ('CSA-DSM-615', 'Major Project', 0, 4),
                ('CSA-SEC-611', 'Seminar/Poster/Presentation/Group Discussion', 0, 2)
            ]
        }

        cur = self.conn.cursor()
        for sem, courses in sem_courses.items():
            for code, title, theory, practical in courses:
                cur.execute(
                    'INSERT INTO courses (sem_id, code, title, theory_credits, practical_credits) VALUES (?,?,?,?,?)',
                    (sem, code, title, theory, practical))
                cid = cur.lastrowid
                if theory > 0:
                    for u in range(1, 6):
                        cur.execute('INSERT INTO units (course_id, num, title) VALUES (?,?,?)',
                                    (cid, u, f'Unit {u}: {title} Core Concepts'))
        self.conn.commit()

    def register_user(self, username, email, password, sem_id, role='student'):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.conn.execute(
                'INSERT INTO users (username, email, password_hash, sem_id, role) VALUES (?,?,?,?,?)',
                (username, email.lower(), pw_hash, int(sem_id), role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, email, password):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        row = self.conn.execute('SELECT * FROM users WHERE email=?', (email.lower(),)).fetchone()
        return dict(row) if row and row['password_hash'] == pw_hash else None

    def get_courses_by_sem(self, sem_id):
        return [dict(r) for r in self.conn.execute(
            'SELECT id, code, title, theory_credits, practical_credits, total_credits FROM courses WHERE sem_id=? ORDER BY code',
            (sem_id,)).fetchall()]

    def get_units_by_course(self, course_id):
        return [dict(r) for r in self.conn.execute(
            'SELECT id, num, title FROM units WHERE course_id=? ORDER BY num', (course_id,)).fetchall()]

    def add_library_item(self, title, author, item_type, unit_id, path):
        self.conn.execute(
            'INSERT INTO library (title, author, type, unit_id, file_path) VALUES (?,?,?,?,?)',
            (title, author, item_type, unit_id, path))
        self.conn.commit()

    def get_library_items(self, unit_id=None):
        query = '''SELECT l.*, u.title as unit_title, c.code as course_code
                   FROM library l
                            JOIN units u ON l.unit_id = u.id
                            JOIN courses c ON u.course_id = c.id'''
        if unit_id:
            query += ' WHERE l.unit_id = ?'
            return [dict(r) for r in self.conn.execute(query, (unit_id,)).fetchall()]
        return [dict(r) for r in self.conn.execute(query).fetchall()]

    def remove_library_item(self, item_id):
        self.conn.execute('DELETE FROM library WHERE id=?', (item_id,))
        self.conn.commit()

    def update_attendance(self, student_id, course_id, attended_delta, total_delta):
        self.conn.execute('''
                          INSERT INTO attendance (student_id, course_id, attended, total_classes)
                          VALUES (?, ?, ?, ?) ON CONFLICT(student_id, course_id) DO
                          UPDATE SET
                              attended = attended + excluded.attended,
                              total_classes = total_classes + excluded.total_classes
                          ''', (student_id, course_id, attended_delta, total_delta))
        self.conn.commit()

    def get_attendance(self, student_id):
        rows = self.conn.execute('''
                                 SELECT c.code, c.title, a.attended, a.total_classes
                                 FROM attendance a
                                          JOIN courses c ON a.course_id = c.id
                                 WHERE a.student_id = ?
                                 ''', (student_id,)).fetchall()
        return [dict(r) for r in rows]

    def save_exam_paper(self, title, exam_type, fmt, sem_id, content, creator_id):
        self.conn.execute(
            'INSERT INTO exam_papers (title, exam_type, format, sem_id, content_json, created_by) VALUES (?,?,?,?,?,?)',
            (title, exam_type, fmt, sem_id, json.dumps(content), creator_id))
        self.conn.commit()

    def get_exam_papers(self, sem_id=None):
        if sem_id:
            rows = self.conn.execute('SELECT * FROM exam_papers WHERE sem_id=? ORDER BY created_at DESC',
                                     (sem_id,)).fetchall()
        else:
            rows = self.conn.execute('SELECT * FROM exam_papers ORDER BY created_at DESC').fetchall()
        return [dict(r) for r in rows]

    def save_result(self, student_id, paper_id, score, max_marks):
        self.conn.execute('INSERT INTO results (student_id, paper_id, score, max_marks) VALUES (?,?,?,?)',
                          (student_id, paper_id, score, max_marks))
        self.conn.commit()

    def get_results_by_sem(self, sem_id):
        return [dict(r) for r in self.conn.execute('''
                                                   SELECT u.username,
                                                          u.email,
                                                          ep.title AS paper_title,
                                                          ep.exam_type,
                                                          r.score,
                                                          r.max_marks,
                                                          r.submitted_at
                                                   FROM results r
                                                            JOIN users u ON r.student_id = u.id
                                                            JOIN exam_papers ep ON r.paper_id = ep.id
                                                   WHERE u.sem_id = ?
                                                   ORDER BY u.username, ep.title
                                                   ''', (sem_id,)).fetchall()]

    def get_results_by_student(self, student_id):
        return [dict(r) for r in self.conn.execute('''
                                                   SELECT ep.title, ep.exam_type, r.score, r.max_marks, r.submitted_at
                                                   FROM results r
                                                            JOIN exam_papers ep ON r.paper_id = ep.id
                                                   WHERE r.student_id = ?
                                                   ORDER BY r.submitted_at DESC
                                                   ''', (student_id,)).fetchall()]

    def get_students_by_sem(self, sem_id):
        return [dict(r) for r in self.conn.execute(
            "SELECT id, username, email FROM users WHERE role='student' AND sem_id=? ORDER BY username",
            (sem_id,)).fetchall()]

    def close(self):
        self.conn.close()


# ================= CLI UI HELPERS =================
def display_header(title):
    console.print(Panel(Text(title, style="bold white on blue"), expand=False))


def display_courses_table(courses):
    table = Table(title="BCA NEP-2020 Courses", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Code")
    table.add_column("Title")
    table.add_column("Credits (T+P)")
    for c in courses:
        table.add_row(str(c['id']), c['code'], c['title'], f"{c['theory_credits']}+{c['practical_credits']}")
    console.print(table)


def display_attendance_table(attendance_records):
    table = Table(title="Attendance Summary", show_header=True, header_style="bold yellow")
    table.add_column("Course")
    table.add_column("Attended/Total", justify="center")
    table.add_column("Percentage", justify="right")
    for rec in attendance_records:
        perc = (rec['attended'] / rec['total_classes'] * 100) if rec['total_classes'] > 0 else 0.0
        color = "green" if perc >= 75 else "red"
        table.add_row(f"{rec['code']}", f"{rec['attended']}/{rec['total_classes']}", f"[{color}]{perc:.1f}%[/]")
    console.print(table)


# ================= MENUS =================
def student_menu(db, user):
    while True:
        console.clear()
        display_header(f"Student Portal: {user['username']} | Sem {user['sem_id']}")
        console.print("\n[1] View Courses\n[2] My Attendance\n[3] My Results\n[0] Logout")
        choice = Prompt.ask("Action", choices=["0", "1", "2", "3"])

        if choice == "0":
            break
        elif choice == "1":
            display_courses_table(db.get_courses_by_sem(user['sem_id']))
            Prompt.ask("\nPress Enter")
        elif choice == "2":
            att = db.get_attendance(user['id'])
            if att:
                display_attendance_table(att)
            else:
                console.print("[yellow]No records.[/]")
            Prompt.ask("\nPress Enter")
        elif choice == "3":
            res = db.get_results_by_student(user['id'])
            if res:
                table = Table(title="Examination Results")
                table.add_column("Paper")
                table.add_column("Score")
                for r in res: table.add_row(r['title'], f"{r['score']}/{r['max_marks']}")
                console.print(table)
            else:
                console.print("[yellow]No results posted.[/]")
            Prompt.ask("\nPress Enter")


def teacher_menu(db, user):
    while True:
        console.clear()
        display_header(f"Teacher Panel: {user['username']}")
        console.print("\n[1] Mark Attendance\n[2] Upload Result\n[3] Library Manager\n[0] Logout")
        choice = Prompt.ask("Action", choices=["0", "1", "2", "3"])

        if choice == "0":
            break
        elif choice == "1":
            sem = IntPrompt.ask("Semester")
            courses = db.get_courses_by_sem(sem)
            display_courses_table(courses)
            course_id = IntPrompt.ask("Select Course ID")
            students = db.get_students_by_sem(sem)
            for s in students:
                is_present = Confirm.ask(f"Is {s['username']} present?")
                db.update_attendance(s['id'], course_id, 1 if is_present else 0, 1)
            console.print("[green]Attendance updated.[/]")
            Prompt.ask("Press Enter")
        elif choice == "2":
            sem = IntPrompt.ask("Semester")
            papers = db.get_exam_papers(sem)
            if not papers:
                console.print("[red]No papers found. Create one first.[/]")
            else:
                for p in papers: console.print(f"ID: {p['id']} | {p['title']}")
                p_id = IntPrompt.ask("Paper ID")
                max_m = IntPrompt.ask("Max Marks")
                students = db.get_students_by_sem(sem)
                for s in students:
                    score = IntPrompt.ask(f"Score for {s['username']}")
                    db.save_result(s['id'], p_id, score, max_m)
                console.print("[green]Results saved.[/]")
            Prompt.ask("Press Enter")
        elif choice == "3":
            console.print("[blue]Library Management (Simulated)[/]")
            # Add library logic here similar to your snippet
            Prompt.ask("Press Enter")


def main():
    db = Database()
    try:
        while True:
            console.clear()
            display_header("TAMAS: Academic Management (NEP-2020)")
            console.print("\n[1] Login\n[2] Register\n[0] Exit")
            choice = Prompt.ask("Action", choices=["0", "1", "2"])

            if choice == "0":
                break
            elif choice == "1":
                email = Prompt.ask("Email")
                console.print("Password: ", end="")
                pw = getpass("")
                user = db.verify_user(email, pw)
                if user:
                    if user['role'] == 'teacher':
                        teacher_menu(db, user)
                    else:
                        student_menu(db, user)
                else:
                    console.print("[red]Login Failed.[/]")
                    Prompt.ask("Retry")
            elif choice == "2":
                u = Prompt.ask("Name")
                e = Prompt.ask("Email")
                console.print("Password: ", end="")
                p = getpass("")
                s = IntPrompt.ask("Semester (1-6)")
                r = Prompt.ask("Role", choices=["student", "teacher"], default="student")
                if db.register_user(u, e, p, s, r):
                    console.print("[green]Success! Please login.[/]")
                else:
                    console.print("[red]Registration failed (Email taken).[/]")
                Prompt.ask("Continue")
    finally:
        db.close()


if __name__ == "__main__":
    main()