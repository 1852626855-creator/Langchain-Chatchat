"""用户认证模块

提供用户注册、登录、token验证和对话历史记录功能
使用 SQLite 数据库存储用户信息和对话记录
"""

import hashlib
import uuid
import sqlite3
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List, Dict

# 创建 FastAPI 路由
router = APIRouter(prefix="/auth", tags=["用户认证"])

# 数据库文件路径
DB_PATH = "auth.db"

# Token 过期时间（小时）
TOKEN_EXPIRE_HOURS = 24

class UserRegister(BaseModel):
    """用户注册请求模型"""
    username: str
    password: str

class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Token 响应模型"""
    token: str
    username: str

class HistoryResponse(BaseModel):
    """历史记录响应模型"""
    id: int
    user_id: int
    role: str
    content: str
    created_at: str

def init_db():
    """初始化 SQLite 数据库，创建 users、sessions 和 chat_history 表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建 users 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建 sessions 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 创建 chat_history 表（存储用户对话历史）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,  -- 'user' 或 'assistant'
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """使用 SHA256 哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    """生成随机 token"""
    return str(uuid.uuid4())

def get_user_by_username(username: str) -> Optional[dict]:
    """根据用户名查询用户"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'password_hash': row[2],
            'created_at': row[3]
        }
    return None

def create_user(username: str, password: str) -> int:
    """创建新用户"""
    password_hash = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="用户名已存在")

def create_session(user_id: int) -> str:
    """创建用户会话（生成 token）"""
    token = generate_token()
    expires_at = datetime.now() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
        (user_id, token, expires_at.isoformat())
    )
    conn.commit()
    conn.close()
    return token

def verify_token(token: str) -> Optional[int]:
    """验证 token 是否有效，返回用户 ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id, expires_at FROM sessions WHERE token = ?',
        (token,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    user_id, expires_at = row
    if datetime.fromisoformat(expires_at) < datetime.now():
        return None
    
    return user_id

def add_chat_history(user_id: int, role: str, content: str):
    """添加对话历史记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)',
        (user_id, role, content)
    )
    conn.commit()
    conn.close()

def get_chat_history(user_id: int) -> List[Dict]:
    """获取用户对话历史"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, role, content, created_at FROM chat_history WHERE user_id = ? ORDER BY created_at ASC',
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        'id': row[0],
        'role': row[1],
        'content': row[2],
        'created_at': row[3]
    } for row in rows]

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """用户注册接口
    
    注册新用户并返回 token
    - username: 用户名（唯一）
    - password: 密码（将被 SHA256 哈希存储）
    
    返回：token 和 username
    """
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    
    user_id = create_user(user.username, user.password)
    token = create_session(user_id)
    
    return {"token": token, "username": user.username}

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    """用户登录接口
    
    验证用户名和密码，返回 token
    - username: 用户名
    - password: 密码
    
    返回：token 和 username
    """
    db_user = get_user_by_username(user.username)
    
    if not db_user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if db_user['password_hash'] != hash_password(user.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    token = create_session(db_user['id'])
    
    return {"token": token, "username": user.username}

@router.get("/verify")
async def verify(token: str):
    """验证 token 接口
    
    检查 token 是否有效
    - token: 用户登录时获取的 token
    
    返回：用户信息或错误信息
    """
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="无效的 token")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"user_id": user_id, "username": row[0]}
    else:
        raise HTTPException(status_code=401, detail="用户不存在")

@router.get("/history")
async def history(token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """获取用户对话历史接口
    
    获取当前用户的所有对话记录
    - token: 用户登录时获取的 token
    
    返回：对话历史列表
    """
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token:
        raise HTTPException(status_code=401, detail="缺少 token")

    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="无效的 token")
    
    history = get_chat_history(user_id)
    return {"history": history, "count": len(history)}

# 初始化数据库
init_db()