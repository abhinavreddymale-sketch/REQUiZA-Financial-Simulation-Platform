import sqlite3
import bcrypt
from itsdangerous import URLSafeTimedSerializer
from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])

DB_PATH = "requiza.db"
SECRET_KEY = "requiza-local-development-secret"

serializer = URLSafeTimedSerializer(SECRET_KEY)


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def get_user(email):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute(
        "SELECT id, name, email, password_hash FROM users WHERE email = ?",
        (email.lower(),)
    ).fetchone()
    conn.close()
    return user


init_db()


@router.post("/signup")
def signup(data: SignupRequest, response: Response):
    if len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters."
        )

    if get_user(data.email):
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    password_hash = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (data.name.strip(), data.email.lower(), password_hash)
    )

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    token = serializer.dumps({"user_id": user_id})

    response.set_cookie(
        key="requiza_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400
    )

    return {
        "message": "Account created successfully.",
        "user": {
            "id": user_id,
            "name": data.name.strip(),
            "email": data.email.lower()
        }
    }


@router.post("/login")
def login(data: LoginRequest, response: Response):
    user = get_user(data.email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not bcrypt.checkpw(
        data.password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    token = serializer.dumps({"user_id": user["id"]})

    response.set_cookie(
        key="requiza_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400
    )

    return {
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }


@router.get("/me")
def get_current_user(request: Request):
    token = request.cookies.get("requiza_session")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not signed in."
        )

    try:
        data = serializer.loads(token, max_age=86400)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid."
        )

    user = get_user_by_id(data["user_id"])

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }


def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    user = conn.execute(
        "SELECT id, name, email FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    conn.close()
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("requiza_session")

    return {
        "message": "Logged out successfully."
    }
