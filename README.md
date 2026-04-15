# 🎓 TAMAS - Academic Management System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3%2B-black?logo=flask)](https://flask.palletsprojects.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)](#)

> **TAMAS** (Teaching & Academic Management Automation System) is a lightweight, modular Flask web application designed to streamline academic workflows — from exam generation and library management to student tracking and quiz assessments.

---

## ✨ Features

### 🔐 Authentication & User Management
- Secure login/logout with session management
- User registration with form validation
- Flash messaging for user feedback
- Protected routes via `@login_required` decorator

### 📚 Library Management
- Upload & categorize academic resources (PDF, DOCX, TXT)
- Filter by semester (1-6) and category (Textbook, Syllabus, Notes, Research Paper)
- Secure file handling with `werkzeug.security`

### 📝 AI-Powered Exam Generator *(Ready for Integration)*
- Configure exam type (Mid/End Semester), difficulty, subject & units
- Optional reference material upload for context-aware generation
- Structured form handling for future AI/LLM integration

### 👥 Student Management
- View registered students (UI ready)
- Track attendance & semester records (backend extensible)

### 🧠 Quiz & Assessment Module
- Interactive quiz interface
- Answer submission & result display workflow
- Score tracking via session (mock implementation)

### 🎨 Modern UI/UX
- Responsive Bootstrap 5.3 design with dark/light mode support
- Clean card-based dashboard with intuitive navigation
- Accessible forms with validation hints

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.8+, Flask, Werkzeug |
| **Frontend** | HTML5, Jinja2, Bootstrap 5.3, Bootstrap Icons |
| **Styling** | Custom CSS, CSS Variables, Utility Classes |
| **File Handling** | `secure_filename()`, MIME type validation |
| **Session Mgmt** | Flask Sessions (cookie-based) |
| **Deployment Ready** | Gunicorn, WSGI, Environment Variables |

---

## 📁 Project Structure

```
TAMAS_WEB/
├── app.py                      # Main Flask application & routes
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
│
├── static/
│   ├── css/
│   │   └── custom.css          # Custom styles & overrides
│   └── uploads/                # [Auto-created] Uploaded resources
│
└── templates/
    ├── base.html               # Master template with nav/footer
    ├── login.html              # User login form
    ├── register.html           # User registration form
    ├── dashboard.html          # Main dashboard with quick actions
    ├── library.html            # Resource upload & management
    ├── exam_generate.html      # AI exam configuration form
    ├── students.html           # Student records view (UI)
    ├── quiz.html               # Quiz interface (UI)
    └── result.html             # Exam/quiz results display
```

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/your-username/tamas-web.git
cd tamas-web
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure (Optional)
```bash
cp .env.example .env
# Edit .env with your SECRET_KEY and other settings
```

### 3. Run the App
```bash
python app.py
```
✅ Visit: `http://127.0.0.1:5000`

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `'tamassupersecretkey'` | Session encryption key (**change in production!**) |
| `UPLOAD_FOLDER` | `'static/uploads'` | Directory for uploaded files |
| `MAX_CONTENT_LENGTH` | `16MB` | Max file upload size |
| `ALLOWED_EXTENSIONS` | `{'pdf','docx','txt','png','jpg'}` | Permitted upload file types |

> 🔐 **Production Tip**: Generate a strong secret key:
> ```python
> import secrets; print(secrets.token_hex(32))
> ```

---

## 🧭 User Guide

1. **Register** → Create account with email & password (min 8 chars)
2. **Login** → Access dashboard with session persistence
3. **Dashboard** → Navigate to Library, Exams, Students, or Quiz
4. **Library** → Upload resources with metadata (title, semester, category)
5. **Exam Generator** → Configure parameters → Generate → View result
6. **Quiz** → Take assessment → Submit → View score

---

## 🌐 API Routes

| Route | Method | Access | Description |
|-------|--------|--------|-------------|
| `/` | GET | Public | Redirect to login or dashboard |
| `/login` | GET/POST | Public | User authentication |
| `/register` | GET/POST | Public | New user registration |
| `/logout` | GET | Auth | End session |
| `/dashboard` | GET | Auth | Main user dashboard |
| `/library` | GET/POST | Auth | Resource management & upload |
| `/exam/generate` | GET/POST | Auth | AI exam configuration |
| `/students` | GET | Auth | Student records view |
| `/quiz` | GET | Auth | Quiz interface |
| `/quiz/submit` | POST | Auth | Process quiz answers |
| `/result` | GET | Auth | Display exam/quiz results |

> 🔹 **Auth** = Requires login via `@login_required`

---

## 🔒 Security Checklist

✅ **Implemented**
- Input sanitization with `.strip()` and `secure_filename()`
- Basic password length validation
- File extension whitelisting
- Session-based access control

⚠️ **Before Production**
- [ ] Add Flask-WTF for CSRF protection
- [ ] Hash passwords with `werkzeug.security`
- [ ] Add rate limiting (`Flask-Limiter`)
- [ ] Enable HTTPS & secure cookies
- [ ] Integrate proper database (SQLite/PostgreSQL)
- [ ] Add email verification & password reset

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add some AmazingFeature'`
4. Push: `git push origin feature/AmazingFeature`
5. Open a Pull Request 🎉

**Guidelines**: Follow [PEP 8](https://peps.python.org/pep-0008/), use semantic commits, update docs for new features.

---

## 📄 License

MIT License • See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap 5](https://getbootstrap.com) & [Bootstrap Icons](https://icons.getbootstrap.com)
- [Werkzeug](https://werkzeug.palletsprojects.com/)

---

## 📬 Support

- 🐛 Bugs: [Open an Issue](https://github.com/your-username/tamas-web/issues)
- 💡 Ideas: [GitHub Discussions](https://github.com/your-username/tamas-web/discussions)

> ⭐ **Found TAMAS useful? Star the repo!** It helps others discover the project.

---

*Built with ❤️ for educators, students, and academic administrators.*  
**v1.0.0** • 2024
```
