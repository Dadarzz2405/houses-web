# House Website System — Minimal File Structure (Rohis Style)

This structure follows a **minimal Flask setup**, similar to the Rohis app, using:

* One main application file (`app.py`)
* One database file (`models.py`)
* Jinja for management
* React (later) for public display

Designed for **simplicity first**, scalability later.

---

## Root Directory

```
house-website/
├── app.py
├── models.py
├── requirements.txt
├── .env
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── captain_dashboard.html
│   └── public_home.html
│
├── static/
│   ├── css/
│   └── images/
│
└── react-frontend/        # added later
```

---

## Core Files (Very Important)

### `app.py`

The **heart of the application**.

Contains:

* Flask app setup
* Database initialization
* Login & session handling
* All routes (admin, captain, public, API)
* Basic business logic (for now)

Responsibilities:

* Handle HTTP requests
* Enforce permissions
* Call database models
* Return Jinja templates or JSON

This is similar to how Rohis worked — one file, everything wired.

---

### `models.py`

The **entire database layer**.

Contains:

* SQLAlchemy setup
* All models in one file

Models inside:

* User (admin, captain)
* House
* Event
* Achievement
* ScoreSubmission

Rules:

* No routes
* No templates
* Only database definitions and relationships

---

## Templates (`templates/`)

```
templates/
├── base.html
├── login.html
├── admin_dashboard.html
├── captain_dashboard.html
└── public_home.html
```

Purpose:

* Render UI for admins & captains
* Display public homepage (temporary before React)

Rules:

* No database queries
* No business logic
* Only display data passed from `app.py`

---

## Static Files (`static/`)

```
static/
├── css/
└── images/
```

Purpose:

* Styling
* Icons and assets

JavaScript is optional and minimal.

---

## React Frontend (Later Phase)

```
react-frontend/
├── src/
├── public/
└── package.json
```

Purpose:

* Student-facing UI
* Fetches data from:

  * `/api/scores`
  * `/api/events`
  * `/api/achievements`

Rules:

* Read-only
* No login
* No data modification

Backend (`app.py`) stays the same.

---

## API Routes (Inside `app.py`)

Even in a minimal setup, separate **conceptually**:

* `/` → public_home.html (temporary)
* `/login` → login.html
* `/admin` → admin_dashboard.html
* `/captain` → captain_dashboard.html

API (JSON):

* `/api/scores`
* `/api/events`
* `/api/achievements`

---

## Why This Structure Works

* Matches your Rohis project mindset
* Easy to understand
* Fast to develop
* No overengineering
* Can be refactored later if needed

When the project grows:

* You can split `app.py` into services/routes
* You can split `models.py` into multiple files
* Nothing breaks if done carefully

---

## Golden Rule

**Start simple. Ship early. Refactor only when needed.**

This structure is intentionally boring — and that’s a good thing.
