# Weekly Report Generator — FastAPI Backend

A real **\*\*FastAPI + Python\*\*** backend for the Weekly Report Generator and Team Dashboard. It provides authentication, role-based access, project management, weekly report workflow, report version history, dashboards, analytics, and the Gemini-backed AI assistant.

**## Stack**

\- Python 3.12

\- FastAPI

\- SQLAlchemy Async

\- asyncmy

\- MySQL 8

\- Alembic

\- Pydantic

\- JWT Authentication

\- Argon2 password hashing

\- Gemini AI

\- pytest

**## Local setup**

Requirements: Python 3.12+, MySQL 8, and Git.

Create and activate a virtual environment.

\`\`\`bash

python3.12 -m venv .venv

source .venv/bin/activate

\`\`\`

Install all backend dependencies directly from \`requirements.txt\`.

\`\`\`bash

pip install -r requirements.txt

\`\`\`

Create the environment file.

\`\`\`bash

cp .env.example .env

\`\`\`

Update \`.env\` with your local configuration.

\`\`\`env

DATABASE\_URL=mysql+asyncmy://root\@127.0.0.1:3306/weekly\_report

JWT\_SECRET\_KEY=CHANGE\_THIS\_TO\_A\_SECURE\_SECRET

JWT\_ALGORITHM=HS256

ACCESS\_TOKEN\_EXPIRE\_MINUTES=60

CORS\_ORIGINS=[http://127.0.0.1:3000](http://127.0.0.1:3000)

GEMINI\_API\_KEY=YOUR\_GEMINI\_API\_KEY

GEMINI\_MODEL=gemini-3.7-flash

AI\_CONTEXT\_WEEKS=12

\`\`\`

Never commit database passwords, JWT signing secrets, Gemini API keys, or the \`.env\` file.

**## Gemini API Key Setup**

The Gemini AI assistant requires a Gemini API key. Follow these steps to create a key and add it to your local environment.

### 1. Open Google AI Studio

Open the Google AI Studio API Keys page using the following link:

[Google AI Studio — API Keys](https://aistudio.google.com/app/api-keys?project=gen-lang-client-0644397669)

You must be signed in to the Google account that you want to use for the Gemini API.

### 2. Open the API Keys page

After opening Google AI Studio, go to the **API Keys** section.

You should see the API keys page similar to the following:

![Google AI Studio API Keys](docs/images/gemini-api-keys.png)

### 3. Create a new API key

Click the **Create API key** button in the top-right corner.

![Create Gemini API Key](docs/images/gemini-create-api-key.png)

### 4. Select the project

In the **Create a new key** dialog:

1. Enter a descriptive name for the API key, for example:
   `Weekly Report AI Assistant`
2. Select the required Google AI Studio project.
3. Click **Create key**.

### 5. Copy the API key

After the key is created, copy the generated API key.

**Do not share the API key publicly or commit it to Git.**

### 6. Add the API key to `.env`

Open the backend `.env` file and replace the placeholder value:

\`\`\`env

GEMINI\_API\_KEY=YOUR\_GEMINI\_API\_KEY

\`\`\`

with your actual Gemini API key:

\`\`\`env

GEMINI\_API\_KEY=your_actual_gemini_api_key

\`\`\`

Keep the key only in the FastAPI backend environment.

### 7. Restart the backend

After updating `.env`, restart the FastAPI server so the new environment variable is loaded.

\`\`\`bash

uvicorn app.main --reload

\`\`\`

**Important:** Never add the Gemini API key to frontend environment variables such as `NEXT_PUBLIC_*`, commit it to Git, or include it directly in source code.

**## Database setup**

Start MySQL.

\`\`\`bash

sudo systemctl start mysql

\`\`\`

Login to MySQL.

\`\`\`bash

mysql -u root -p

\`\`\`

Create the database.

\`\`\`sql

CREATE DATABASE weekly\_report

CHARACTER SET utf8mb4

COLLATE utf8mb4\_unicode\_ci;

\`\`\`

Exit MySQL.

\`\`\`sql

EXIT;

\`\`\`

Run database migrations.

\`\`\`bash

alembic upgrade head

\`\`\`

Seed the demo users and project after running the migrations.

\`\`\`bash

uv run python -m app.db.seeders.demo\_data

\`\`\`

**## Run backend**

Start the FastAPI development server.

\`\`\`bash

uvicorn app.main --reload

\`\`\`

Open **\*\*http\://127.0.0.1:8000\*\***.

Swagger API documentation is available at:

\`\`\`text

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

\`\`\`

**## Commands**

\`\`\`bash

pip install -r requirements.txt

alembic upgrade head

uv run python -m app.db.seeders.demo\_data

uvicorn app.main --reload

pytest -q

\`\`\`

**## Architecture**

\`\`\`text

Router

↓

Service

↓

Repository

↓

SQLAlchemy

↓

MySQL

\`\`\`

The router handles HTTP requests and authentication. The service layer contains business rules and workflow logic. The repository layer handles database queries and persistence.

**## Main features**

\- JWT authentication

\- Team Member, Manager, and Admin roles

\- User management

\- Project management and member assignment

\- Weekly report creation and submission

\- Report review and correction workflow

\- Report version history

\- Draft privacy

\- Dashboard and analytics

\- Gemini AI assistant

**## Report workflow**

\`\`\`text

DRAFT

↓

SUBMITTED

↓

MANAGER REVIEW

├── APPROVED

└── NEEDS\_CORRECTION

     ↓

EDIT NEW VERSION

     ↓

  SUBMITTED

     ↓

  APPROVED

\`\`\`

Old submitted versions remain unchanged. Manager reviews are linked to the exact report version being reviewed.

**## Role access**

\| Feature | Team Member | Manager | Admin |

\|---|---:|---:|---:|

\| Create/edit own reports | Yes | No | No |

\| Submit own reports | Yes | No | No |

\| View team reports | No | Yes | Yes |

\| Request corrections | No | Yes | Yes |

\| Approve reports | No | Yes | Yes |

\| Dashboard and analytics | No | Yes | Yes |

\| Manage projects | No | Yes | Yes |

\| Manage users | No | No | Yes |

\| AI assistant | No | Yes | Yes |

The backend remains the final authorization boundary. Role and active status are checked on protected requests.

**## AI assistant**

The backend exposes:

\`\`\`text

POST /api/v1/ai/chat

\`\`\`

The backend first loads relevant submitted report data, creates structured context, and then sends that context to Gemini.

The Gemini API key remains only in the FastAPI backend.

**## Verification**

After installing dependencies and configuring the database, run:

\`\`\`bash

pytest -q

\`\`\`

Then start the backend:

\`\`\`bash

uvicorn app.main --reload

\`\`\`