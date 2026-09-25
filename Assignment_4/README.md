
```markdown
# FlyRank Backend Track – Auth, Login & Protect (FastAPI + Supabase)

A secure, production-ready REST API built with FastAPI and Supabase Auth. This application implements user registration, credential authentication, session revocation, and JWT token verification using custom FastAPI security dependencies.

---

## 📌 Project Overview

This API relies on **Supabase Auth** as a trusted Identity Provider to manage account storage and password hashing. The FastAPI server handles request routing, input validation via Pydantic, token extraction, and cryptographic token verification.

### Core Features
- **Stateless Authentication:** Uses JSON Web Tokens (JWT) issued by Supabase.
- **Dependency-Based Guards:** Reusable authorization middleware using FastAPI's `Depends` and `HTTPBearer`.
- **Automatic OpenAPI Documentation:** Swagger UI integration with Bearer Auth locks enabled.

---

## 🛠️ Environment Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/mennaahmed00/flyrank_assignmentss.git]
   cd flyrank_assignmentss

```

2. **activate the virtual environment:**
```bash
cd Assignment_4
virtual_env\Scripts\activate.bat  # On Windows cmd 

```

4. **Configure secrets:**
Copy the example environment file to create your local `.env`:
```bash
cp .env.example .env

```


Fill in your actual Supabase credentials in `.env`:
```env
SUPABASE_URL=[https://your-project-id.supabase.co](https://your-project-id.supabase.co)
SUPABASE_KEY=your_anon_public_key
PORT=8000

```



---

## 🚀 How to Run the Server

Start the server in development mode using `uv` or `fastapi`:

```bash
uv run fastapi dev main.py

```

The server will spin up locally at `http://localhost:8000`. You can inspect interactive API documentation by navigating to `http://localhost:8000/docs`.

---

## 📑 API Reference

| Method | Endpoint | Description | Auth Required | Expected Header |
| --- | --- | --- | --- | --- |
| `POST` | `/auth/signup` | Register a new user account | No | None |
| `POST` | `/auth/login` | Authenticate and retrieve JWT access token | No | None |
| `POST` | `/auth/logout` | Revoke user session | **Yes** | `Authorization: Bearer <token>` |
| `GET` | `/public/info` | Open informational route | No | None |
| `GET` | `/protected/profile` | Retrieve verified user profile metadata | **Yes** | `Authorization: Bearer <token>` |
| `GET` | `/protected/dashboard` | Secondary protected test route | **Yes** | `Authorization: Bearer <token>` |

---

## 🔒 Interactive API Docs (Swagger UI)

To test protected routes directly in the browser:

1. Navigate to `http://localhost:8000/docs`.
2. Authenticate via `POST /auth/login` to obtain an `access_token`.
3. Click the green **Authorize** button at the top right.
4. Paste the JWT into the **Value** field and click **Authorize**.
5. Execute requests against `/protected/profile` or `/protected/dashboard`.

---

## 💡 Key Architectural Takeaways

* **Never Roll Your Own Auth:** Cryptographic operations, password hashing, and user storage are delegated entirely to Supabase as the Identity Provider.
* **401 vs. 403 HTTP Statuses:**
* `401 Unauthorized`: Returned when a request is missing a token, presents a malformed header, or uses an expired/invalid JWT ("I don't know who you are").
* `403 Forbidden`: Reserved for cases where identity is verified, but the user lacks specific permissions to access a resource ("I know who you are, but you cannot enter").

Here are the screenshots from Swagger UI:

![alt text](<Screenshot 2026-09-25 070348.png>)
![alt text](<Screenshot 2026-09-25 070419.png>)


```






