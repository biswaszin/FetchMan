<h1 align="center">FetchMan</h1>
<p align="center">A modern API client</p>
<img width="2720" height="920" alt="fetchman_logo" src="https://github.com/user-attachments/assets/67441b61-068e-400f-a052-1ba0f17c4564" />

---

## What is Postman?

Postman is one of the most widely used tools for API development and testing. It lets developers send HTTP requests to servers, inspect responses, organize requests into collections, and collaborate with teammates — all through a graphical interface. It's essentially a Swiss Army knife for anyone working with APIs.

---

## What We're Building

We're building a lightweight, open, and developer-friendly alternative to Postman that addresses the pain points that have crept in over the years — bloat, paywalls, and forced cloud dependency. The goal is a fast, intuitive API client that gets out of your way.

---

## Core Features

- **Request Builder** — Support for all standard HTTP methods (GET, POST, PUT, PATCH, DELETE) with headers, query params, and body (JSON, form-data, raw)
- **Response Viewer** — Clean, readable display of response body, status code, headers, and response time
- **Collections** — Group and organize related requests into named collections, with folder support
- **Environments & Variables** — Define variables like `{{base_url}}` or `{{token}}` and switch between environments (dev, staging, prod)
- **Authentication Support** — Built-in helpers for API Key, Bearer Token, and Basic Auth
- **Request History** — Automatic log of past requests so nothing is lost
- **Import / Export** — Support importing Postman collections (JSON) so teams can migrate easily

---

## Shortcomings of Postman We're Fixing

- **It's gotten really heavy** — Postman used to be simple. Now it opens slowly and uses a lot of memory even for basic tasks. We're keeping our app lean and fast.
- **Too many features locked behind a paid plan** — Things like syncing across devices, certain collaboration features, and mock servers require a subscription. Our version will keep core features free and open.
- **Forced account login** — Postman now requires you to sign in just to use it. We're making our tool fully usable offline, no account needed.
- **Cluttered UI** — The interface has become overwhelming for new users. We're designing a cleaner UI that's easier for beginners to pick up.
- **No true local-first storage** — Postman pushes data to their cloud by default. We store everything locally on your machine, so you're always in control of your data.

---

## Setup

**1. Create and activate a virtual environment**

```bash
python -m venv .venv
```

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the demo server**

```bash
python server.py
```

The server starts at `http://localhost:5000`.

---

## Project Structure

```
FetchMan/
├── server.py
├── requirements.txt
├── fetchman/
│   └── tests/
│       ├── conftest.py
│       └── test_endpoints.py
└── .github/
    └── workflows/
        └── test.yml
```
