#!/usr/bin/env python3
"""
TAMAS CLI - Terminal Academic Management & Assessment System
Aligned with Dr. Harisingh Gour Vishwavidyalaya BCA NEP-2020 Syllabus

Complete corrected version with full CLI functionality.
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
from rich.layout import Layout
from rich.columns import Columns

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
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                sem_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sem_id INTEGER NOT NULL,
                code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                theory_credits INTEGER DEFAULT 0,
                practical_credits INTEGER DEFAULT 0,
                total_credits INTEGER GENERATED ALWAYS AS (theory_credits + practical_credits) STORED
            );

            CREATE TABLE IF NOT EXISTS units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                num INTEGER NOT NULL,
                title TEXT,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT DEFAULT 'Unknown',
                type TEXT CHECK (type IN ('syllabus','book','paper','notes')),
                unit_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                attended INTEGER DEFAULT 0,
                total_classes INTEGER DEFAULT 0,
                UNIQUE(student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS exam_papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                exam_type TEXT CHECK (exam_type IN ('mid','end','quiz')),
                format TEXT DEFAULT 'pdf',
                sem_id INTEGER NOT NULL,
                content_json TEXT NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
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
                cid = cur.execute('SELECT id FROM courses WHERE code=?', (code,)).fetchone()['id']
                # Add 5 standard units for each theory course
                if theory > 0:
                    for u in range(1, 6):
                        cur.execute('INSERT INTO units (course_id, num, title) VALUES (?,?,?)',
                                    (cid, u, f'Unit {u}: {title} Core Concepts'))
        self.conn.commit()

    # ------------------- Authentication -------------------
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

    # ------------------- Courses & Units -------------------
    def get_courses_by_sem(self, sem_id):
        return [dict(r) for r in self.conn.execute(
            'SELECT id, code, title, theory_credits, practical_credits, total_credits FROM courses WHERE sem_id=? ORDER BY code',
            (sem_id,)).fetchall()]

    def get_units_by_course(self, course_id):
        return [dict(r) for r in self.conn.execute(
            'SELECT id, num, title FROM units WHERE course_id=? ORDER BY num', (course_id,)).fetchall()]

    # ------------------- Library -------------------
    def add_library_item(self, title, author, item_type, unit_id, path):
        cur = self.conn.execute(
            'INSERT INTO library (title, author, type, unit_id, file_path) VALUES (?,?,?,?,?)',
            (title, author, item_type, unit_id, path))
        self.conn.commit()
        return cur.lastrowid

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

    # ------------------- Attendance -------------------
    def update_attendance(self, student_id, course_id, attended_delta, total_delta):
        self.conn.execute('''
            INSERT INTO attendance (student_id, course_id, attended, total_classes)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, course_id) DO UPDATE SET
                attended = attended + excluded.attended,
                total_classes = total_classes + excluded.total_classes
        ''', (student_id, course_id, attended_delta, total_delta))
        self.conn.commit()

    def get_attendance(self, student_id, course_id=None):
        if course_id:
            row = self.conn.execute(
                'SELECT attended, total_classes FROM attendance WHERE student_id=? AND course_id=?',
                (student_id, course_id)).fetchone()
            return dict(row) if row else {'attended': 0, 'total_classes': 0}
        else:
            rows = self.conn.execute('''
                SELECT c.code, c.title, a.attended, a.total_classes
                FROM attendance a
                JOIN courses c ON a.course_id = c.id
                WHERE a.student_id = ?
            ''', (student_id,)).fetchall()
            return [dict(r) for r in rows]

    def check_attendance_eligibility(self, student_id, course_id):
        row = self.conn.execute(
            'SELECT attended, total_classes FROM attendance WHERE student_id=? AND course_id=?',
            (student_id, course_id)).fetchone()
        if not row or row['total_classes'] == 0:
            return 100.0
        return (row['attended'] / row['total_classes']) * 100

    def get_students_by_sem(self, sem_id):
        return [dict(r) for r in self.conn.execute(
            "SELECT id, username, email FROM users WHERE role='student' AND sem_id=? ORDER BY username",
            (sem_id,)).fetchall()]

    # ------------------- Exam Papers -------------------
    def save_exam_paper(self, title, exam_type, fmt, sem_id, content, creator_id):
        cur = self.conn.execute(
            'INSERT INTO exam_papers (title, exam_type, format, sem_id, content_json, created_by) VALUES (?,?,?,?,?,?)',
            (title, exam_type, fmt, sem_id, json.dumps(content), creator_id))
        self.conn.commit()
        return cur.lastrowid

    def get_exam_papers(self, sem_id=None):
        if sem_id:
            rows = self.conn.execute(
                'SELECT * FROM exam_papers WHERE sem_id=? ORDER BY created_at DESC', (sem_id,)).fetchall()
        else:
            rows = self.conn.execute('SELECT * FROM exam_papers ORDER BY created_at DESC').fetchall()
        return [dict(r) for r in rows]

    # ------------------- Results -------------------
    def save_result(self, student_id, paper_id, score, max_marks):
        self.conn.execute('INSERT INTO results (student_id, paper_id, score, max_marks) VALUES (?,?,?,?)',
                          (student_id, paper_id, score, max_marks))
        self.conn.commit()

    def get_results_by_sem(self, sem_id):
        return [dict(r) for r in self.conn.execute('''
            SELECT u.username, u.email, ep.title AS paper_title, ep.exam_type,
                   r.score, r.max_marks, r.submitted_at
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
            ORDER BY ep.title
        ''', (student_id,)).fetchall()]


# ================= CLI INTERFACE =================
def display_header(title):
    console.print(Panel(Text(title, style="bold white on blue"), expand=False))

def display_courses_table(courses):
    table = Table(title="Courses", show_header=True, header_style="bold cyan")
    table.add_column("Code", style="dim")
    table.add_column("Title")
    table.add_column("Theory")
    table.add_column("Prac")
    table.add_column("Total Credits", justify="center")
    for c in courses:
        table.add_row(c['code'], c['title'], str(c['theory_credits']),
                      str(c['practical_credits']), str(c['total_credits']))
    console.print(table)

def display_units_table(units):
    table = Table(title="Course Units", show_header=True, header_style="bold green")
    table.add_column("Unit #", style="dim")
    table.add_column("Title")
    for u in units:
        table.add_row(str(u['num']), u['title'])
    console.print(table)

def display_library_items(items):
    if not items:
        console.print("[yellow]No library items found.[/]")
        return
    table = Table(title="Library Resources", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Type")
    table.add_column("Course Code")
    table.add_column("Unit")
    for item in items:
        table.add_row(str(item['id']), item['title'], item['author'],
                      item['type'], item['course_code'], item['unit_title'])
    console.print(table)

def display_attendance_table(attendance_records):
    table = Table(title="Attendance Summary", show_header=True, header_style="bold yellow")
    table.add_column("Course Code")
    table.add_column("Course Title")
    table.add_column("Attended", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Percentage", justify="right")
    for rec in attendance_records:
        perc = (rec['attended'] / rec['total_classes'] * 100) if rec['total_classes'] > 0 else 0.0
        color = "green" if perc >= 75 else "red"
        table.add_row(rec['code'], rec['title'], str(rec['attended']), str(rec['total_classes']),
                      f"[{color}]{perc:.1f}%[/]")
    console.print(table)

def display_results_table(results, title="Results"):
    table = Table(title=title, show_header=True, header_style="bold blue")
    if results and 'username' in results[0]:
        table.add_column("Student")
        table.add_column("Email")
    table.add_column("Paper")
    table.add_column("Type")
    table.add_column("Score", justify="right")
    table.add_column("Max", justify="right")
    table.add_column("%", justify="right")
    for r in results:
        perc = (r['score'] / r['max_marks'] * 100) if r['max_marks'] > 0 else 0.0
        if 'username' in r:
            table.add_row(r['username'], r['email'], r['paper_title'], r['exam_type'],
                          f"{r['score']:.1f}", f"{r['max_marks']:.1f}", f"{perc:.1f}%")
        else:
            table.add_row(r['title'], r['exam_type'], f"{r['score']:.1f}",
                          f"{r['max_marks']:.1f}", f"{perc:.1f}%")
    console.print(table)

def student_menu(db, user):
    while True:
        console.clear()
        display_header(f"Student Dashboard - {user['username']} (Semester {user['sem_id']})")
        console.print("\n[1] View My Courses")
        console.print("[2] View Course Units & Library")
        console.print("[3] Check My Attendance")
        console.print("[4] View My Results")
        console.print("[5] Change Password (coming soon)")
        console.print("[0] Logout")

        choice = Prompt.ask("Choose an option", choices=["0","1","2","3","4","5"])

        if choice == "0":
            break
        elif choice == "1":
            courses = db.get_courses_by_sem(user['sem_id'])
            display_courses_table(courses)
            Prompt.ask("\nPress Enter to continue")
        elif choice == "2":
            courses = db.get_courses_by_sem(user['sem_id'])
            display_courses_table(courses)
            course_id = IntPrompt.ask("Enter course ID to view units (0 to cancel)")
            if course_id == 0:
                continue
            units = db.get_units_by_course(course_id)
            display_units_table(units)
            view_lib = Confirm.ask("View library items for this course?")
            if view_lib:
                items = []
                for unit in units:
                    items.extend(db.get_library_items(unit['id']))
                display_library_items(items)
            Prompt.ask("\nPress Enter to continue")
        elif choice == "3":
            attendance = db.get_attendance(user['id'])
            if attendance:
                display_attendance_table(attendance)
                # Show eligibility warnings
                console.print("\n[bold]Eligibility Status (75% rule):[/]")
                for rec in attendance:
                    perc = (rec['attended'] / rec['total_classes'] * 100) if rec['total_classes'] > 0 else 0.0
                    status = "[green]Eligible[/]" if perc >= 75 else "[red]Detained[/]"
                    console.print(f"{rec['code']}: {status}")
            else:
                console.print("[yellow]No attendance records yet.[/]")
            Prompt.ask("\nPress Enter to continue")
        elif choice == "4":
            results = db.get_results_by_student(user['id'])
            if results:
                display_results_table(results, f"Your Results - Semester {user['sem_id']}")
            else:
                console.print("[yellow]No results available.[/]")
            Prompt.ask("\nPress Enter to continue")
        elif choice == "5":
            console.print("[yellow]Feature under development.[/]")
            Prompt.ask("Press Enter to continue")

def teacher_menu(db, user):
    while True:
        console.clear()
        display_header(f"Teacher Dashboard - {user['username']}")
        console.print("\n[1] Manage Syllabus & Courses")
        console.print("[2] Manage Library Resources")
        console.print("[3] Attendance Management")
        console.print("[4] Exam Papers")
        console.print("[5] Results Entry")
        console.print("[6] View Student Reports")
        console.print("[0] Logout")

        choice = Prompt.ask("Choose an option", choices=["0","1","2","3","4","5","6"])

        if choice == "0":
            break
        elif choice == "1":
            sem = IntPrompt.ask("Enter semester number (1-6)")
            courses = db.get_courses_by_sem(sem)
            display_courses_table(courses)
            Prompt.ask("\nPress Enter to continue")
        elif choice == "2":
            lib_menu(db, user)
        elif choice == "3":
            attendance_menu(db, user)
        elif choice == "4":
            exam_menu(db, user)
        elif choice == "5":
            results_entry_menu(db, user)
        elif choice == "6":
            sem = IntPrompt.ask("Enter semester to view results")
            results = db.get_results_by_sem(sem)
            if results:
                display_results_table(results, f"Semester {sem} Results")
            else:
                console.print("[yellow]No results found.[/]")
            Prompt.ask("\nPress Enter to continue")

def lib_menu(db, user):
    while True:
        console.clear()
        display_header("Library Management")
        console.print("\n[1] Add Resource")
        console.print("[2] View All Resources")
        console.print("[3] Remove Resource")
        console.print("[0] Back")

        choice = Prompt.ask("Choose", choices=["0","1","2","3"])
        if choice == "0":
            break
        elif choice == "1":
            sem = IntPrompt.ask("Semester")
            courses = db.get_courses_by_sem(sem)
            display_courses_table(courses)
            course_id = IntPrompt.ask("Course ID")
            units = db.get_units_by_course(course_id)
            display_units_table(units)
            unit_id = IntPrompt.ask("Unit ID")
            title = Prompt.ask("Resource title")
            author = Prompt.ask("Author", default="Unknown")
            rtype = Prompt.ask("Type", choices=["syllabus","book","paper","notes"])
            path = Prompt.ask("File path (or URL)")
            db.add_library_item(title, author, rtype, unit_id, path)
            console.print("[green]Resource added![/]")
            Prompt.ask("Press Enter")
        elif choice == "2":
            items = db.get_library_items()
            display_library_items(items)
            Prompt.ask("Press Enter")
        elif choice == "3":
            items = db.get_library_items()
            display_library_items(items)
            item_id = IntPrompt.ask("Enter ID to delete (0 to cancel)")
            if item_id != 0:
                db.remove_library_item(item_id)
                console.print("[green]Deleted.[/]")
            Prompt.ask("Press Enter")

def attendance_menu(db, user):
    while True:
        console.clear()
        display_header("Attendance Management")
        console.print("\n[1] Mark Attendance for a Class")
        console.print("[2] View Student Attendance")
        console.print("[0] Back")

        choice = Prompt.ask("Choose", choices=["0","1","2"])
        if choice == "0":
            break
        elif choice == "1":
            sem = IntPrompt.ask("Semester")
            students = db.get_students_by_sem(sem)
            if not students:
                console.print("[yellow]No students in this semester.[/]")
                Prompt.ask("Press Enter")
                continue
            courses = db.get_courses_by_sem(sem)
            display_courses_table(courses)
            course_id = IntPrompt.ask("Course ID")
            console.print("\nMark attendance for each student (1 = present, 0 = absent):")
            for s in students:
                status = Confirm.ask(f"{s['username']} ({s['email']}) present?")
                db.update_attendance(s['id'], course_id, 1 if status else 0, 1)
            console.print("[green]Attendance recorded.[/]")
            Prompt.ask("Press Enter")
        elif choice == "2":
            sem = IntPrompt.ask("Semester")
            students = db.get_students_by_sem(sem)
            if not students:
                console.print("[yellow]No students found.[/]")
                Prompt.ask("Press Enter")
                continue
            student_id = IntPrompt.ask("Student ID (or 0 to see list)")
            if student_id == 0:
                for s in students:
                    console.print(f"ID: {s['id']} - {s['username']} ({s['email']})")
                student_id = IntPrompt.ask("Student ID")
            attendance = db.get_attendance(student_id)
            if attendance:
                display_attendance_table(attendance)
            else:
                console.print("[yellow]No attendance records.[/]")
            Prompt.ask("Press Enter")

def exam_menu(db, user):
    while True:
        console.clear()
        display_header("Exam Paper Management")
        console.print("\n[1] Create New Exam Paper")
        console.print("[2] View Existing Papers")
        console.print("[0] Back")

        choice = Prompt.ask("Choose", choices=["0","1","2"])
        if choice == "0":
            break
        elif choice == "1":
            title = Prompt.ask("Paper title")
            exam_type = Prompt.ask("Type", choices=["mid","end","quiz"])
            sem = IntPrompt.ask("Semester")
            fmt = Prompt.ask("Format (pdf/doc)", default="pdf")
            console.print("Enter questions (JSON format) - for demo we'll create a simple structure.")
            # In real app, you'd have a nice editor; here we'll just prompt for a dummy.
            content = {"questions": []}
            if Confirm.ask("Add a sample question?"):
                q = Prompt.ask("Question text")
                content["questions"].append({"q": q, "marks": 5})
            db.save_exam_paper(title, exam_type, fmt, sem, content, user['id'])
            console.print("[green]Exam paper saved![/]")
            Prompt.ask("Press Enter")
        elif choice == "2":
            sem = IntPrompt.ask("Semester (0 for all)")
            papers = db.get_exam_papers(sem if sem > 0 else None)
            if papers:
                table = Table(title="Exam Papers")
                table.add_column("ID")
                table.add_column("Title")
                table.add_column("Type")
                table.add_column("Semester")
                for p in papers:
                    table.add_row(str(p['id']), p['title'], p['exam_type'], str(p['sem_id']))
                console.print(table)
            else:
                console.print("[yellow]No papers found.[/]")
            Prompt.ask("Press Enter")

def results_entry_menu(db, user):
    console.clear()
    display_header("Results Entry")
    sem = IntPrompt.ask("Semester")
    papers = db.get_exam_papers(sem)
    if not papers:
        console.print("[red]No exam papers for this semester.[/]")
        Prompt.ask("Press Enter")
        return

    table = Table(title="Select Paper")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Type")
    for p in papers:
        table.add_row(str(p['id']), p['title'], p['exam_type'])
    console.print(table)
    paper_id = IntPrompt.ask("Paper ID")
    max_marks = IntPrompt.ask("Maximum marks")

    students = db.get_students_by_sem(sem)
    console.print(f"\nEnter marks for {len(students)} students:")
    for s in students:
        score = IntPrompt.ask(f"{s['username']} ({s['email']})", default=0)
        db.save_result(s['id'], paper_id, score, max_marks)
    console.print("[green]Results saved![/]")
    Prompt.ask("Press Enter")

def login_register(db):
    while True:
        console.clear()
        display_header("TAMAS - Academic Management System")
        console.print("\n[1] Login")
        console.print("[2] Register")
        console.print("[0] Exit")

        choice = Prompt.ask("Choose", choices=["0","1","2"])
        if choice == "0":
            sys.exit(0)
        elif choice == "1":
            email = Prompt.ask("Email")
            password = getpass("Password: ")
            user = db.verify_user(email, password)
            if user:
                console.print(f"[green]Welcome, {user['username']}![/]")
                if user['role'] == 'teacher':
                    teacher_menu(db, user)
                else:
                    student_menu(db, user)
            else:
                console.print("[red]Invalid credentials.[/]")
                Prompt.ask("Press Enter to try again")
        elif choice == "2":
            username = Prompt.ask("Username")
            email = Prompt.ask("Email")
            password = getpass("Password: ")
            sem = IntPrompt.ask("Semester (1-6)")
            role = Prompt.ask("Role", choices=["student","teacher"], default="student")
            if db.register_user(username, email, password, sem, role):
                console.print("[green]Registration successful! Please login.[/]")
            else:
                console.print("[red]Username or email already exists.[/]")
            Prompt.ask("Press Enter to continue")

def main():
    # Ensure DB exists
    if not os.path.exists(DB_PATH):
        console.print("[yellow]Initializing database...[/]")
    db = Database()
    login_register(db)

if __name__ == "__main__":
    main()