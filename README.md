Weekly Report Generator - Backend

FastAPI backend for the Weekly Report Generator & Team Dashboard.

Technology Stack

Python 3.12

FastAPI

SQLAlchemy Async

asyncmy

MySQL 8

Alembic

Pydantic

JWT Authentication

pwdlib / Argon2

Google Gemini API

pytest

uv

Backend Architecture

Router
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy
  ↓
MySQL

Prerequisites

Python 3.12

uv

MySQL 8

Git

Check versions:

python --version
uv --version
mysql --version
git --version

Installation

git clone <BACKEND_REPOSITORY_URL>
cd <BACKEND_REPOSITORY_FOLDER>
uv sync

Database Setup

Start MySQL:

sudo systemctl start mysql

Login:

mysql -u root -p

Create database:

CREATE DATABASE weekly_report
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

Exit:

EXIT;

Environment Configuration

Create .env in the backend root.

DATABASE_URL=mysql+asyncmy://root:YOUR_MYSQL_PASSWORD@localhost:3306/weekly_report

JWT_SECRET_KEY=CHANGE_THIS_TO_A_SECURE_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ORIGINS=http://localhost:3000

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.7-flash
AI_CONTEXT_WEEKS=12

Use the exact variable names from your repository's .env.example if they differ.

Never commit .env, database passwords, JWT secrets, or API keys.

Run Database Migrations

uv run alembic upgrade head

Verify:

mysql -u root -p

USE weekly_report;
SHOW TABLES;

Main tables:

users
projects
project_user
reports
report_versions
report_tasks
report_blockers
report_achievements
report_reviews
alembic_version

Run the Backend

uv run uvicorn app.main:app --reload

Backend:

http://localhost:8000

Swagger:

http://localhost:8000/docs

Run Tests

uv run pytest -q

Roles

TEAM_MEMBER

Create/edit own reports

Save drafts

Submit/resubmit

View correction comments

View version history

MANAGER

View team reports

Review submitted reports

Request corrections

Approve

Dashboard and analytics

Project/member management

AI Assistant

Managers cannot read unpublished draft content.

ADMIN

Manager capabilities

Create users

Change roles

Deactivate users

Manage users/projects

Report Workflow

DRAFT
  ↓
SUBMITTED
  ├── APPROVED
  └── NEEDS_CORRECTION
          ↓
      EDIT NEW VERSION
          ↓
       SUBMITTED
          ↓
       APPROVED

Important:

manager never edits Team Member report content

corrections create a new editable version

old submitted versions remain unchanged

reviews are linked to exact report versions

drafts remain private

AI Assistant

The AI Assistant is available to Manager/Admin.

Manager Question
      ↓
FastAPI AI Service
      ↓
Load submitted report data
      ↓
Build structured context
      ↓
Gemini
      ↓
Grounded answer

The AI does not directly access MySQL and does not receive private draft content.

Security

Passwords are hashed with Argon2.

JWT is used for protected APIs.

Backend loads the current user from the database.

Role and active status are checked on protected requests.

Frontend visibility is not authorization.

Draft privacy is enforced by the backend.

Future Improvements

Project-scoped Manager role

Notifications/reminders

PDF/Excel export

Audit logging

Profile/password management

CI/CD

End-to-end browser tests

Persistent AI history

RAG/semantic search for larger report volume