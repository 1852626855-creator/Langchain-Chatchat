from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import jwt
import hashlib
import sqlite3
import os

app = FastAPI(title="Langchain-Chatchat API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    token: str
    username: str

class ChatMessage(BaseModel):
    message: str
    username: str = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str

def init_db():
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(username: str) -> str:
    payload = {"username": username, "exp": datetime.utcnow().timestamp() + 3600}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["username"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

init_db()

@app.post("/auth/register", response_model=Token)
async def register(user: User):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
            (user.username, hash_password(user.password), str(datetime.now()))
        )
        conn.commit()
        return {"token": create_token(user.username), "username": user.username}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()

@app.post("/auth/login", response_model=Token)
async def login(user: User):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (user.username,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0] == hash_password(user.password):
        return {"token": create_token(user.username), "username": user.username}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/auth/verify")
async def verify(token: str = Depends(verify_token)):
    return {"username": token}

@app.post("/chat/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, token: str = Depends(verify_token)):
    response = f"收到消息: {message.message}\n\n这是一个演示响应。在实际部署中，这里会调用 LLM 模型生成回答。"
    
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO conversations (username, message, response, timestamp) VALUES (?, ?, ?, ?)',
        (token, message.message, response, str(datetime.now()))
    )
    conn.commit()
    conn.close()
    
    return {"response": response, "timestamp": str(datetime.now())}

@app.get("/auth/history")
async def get_history(token: str = Depends(verify_token)):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('SELECT message, response, timestamp FROM conversations WHERE username = ? ORDER BY timestamp DESC', (token,))
    results = cursor.fetchall()
    conn.close()
    return [{"message": r[0], "response": r[1], "timestamp": r[2]} for r in results]

@app.get("/")
async def root():
    return {"message": "Langchain-Chatchat API Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7861)