import os
from typing import Dict, List

import streamlit as st


def chat_with_zhipu(messages: List[Dict[str, str]]) -> str:
    api_key = os.environ.get("ZHIPU_API_KEY", "")
    if not api_key:
        return "未配置 ZHIPU_API_KEY，请在 Streamlit Cloud Secrets 中添加。"
    try:
        from zhipuai import ZhipuAI

        client = ZhipuAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.environ.get("ZHIPU_MODEL", "glm-4"),
            messages=messages,
            temperature=0.7,
        )
        return (resp.choices[0].message.content or "").strip() or "模型未返回内容"
    except Exception as e:
        return f"调用失败: {e}"


st.set_page_config(page_title="langchain-ai助手", page_icon="🤖", layout="wide")
st.title("langchain-ai助手（Streamlit Cloud）")
st.caption("纯云端部署版本：直接调用智谱 API，无需 Docker 后端。")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是 langchain-ai助手。"}
    ]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

query = st.chat_input("请输入问题...")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            reply = chat_with_zhipu(st.session_state.messages)
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

with st.sidebar:
    st.subheader("Secrets 配置")
    st.code('ZHIPU_API_KEY = "你的真实key"\nZHIPU_MODEL = "glm-4"')
import json
import os
from typing import Optional

import requests
import streamlit as st


st.set_page_config(page_title="langchain-ai助手", page_icon="🤖", layout="wide")

API_BASE = os.environ.get("API_BASE", "").rstrip("/")


def parse_sse_payload(raw_text: str) -> Optional[dict]:
    last = None
    for line in raw_text.splitlines():
        if line.startswith("data: "):
            try:
                last = json.loads(line[6:])
            except Exception:
                pass
    return last


def api_login(base: str, username: str, password: str) -> tuple[bool, str]:
    try:
        resp = requests.post(
            f"{base}/auth/login",
            json={"username": username, "password": password},
            timeout=30,
        )
        if not resp.ok:
            return False, f"登录失败: {resp.text}"
        data = resp.json()
        return True, data.get("token", "")
    except Exception as e:
        return False, f"网络错误: {e}"


def api_chat(base: str, token: str, query: str) -> tuple[bool, str]:
    try:
        resp = requests.post(
            f"{base}/chat/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": query, "stream": False},
            timeout=90,
        )
        if not resp.ok:
            return False, f"请求失败: {resp.status_code} {resp.text}"
        data = parse_sse_payload(resp.text) or {}
        return True, data.get("text") or data.get("answer") or "未收到回复"
    except Exception as e:
        return False, f"网络错误: {e}"


st.title("langchain-ai助手（Streamlit Cloud）")
st.caption("此页面是云端轻量入口，调用你已部署的后端 API。")

if not API_BASE:
    st.error("未设置环境变量 API_BASE。请在 Streamlit Cloud Secrets 中配置 API_BASE。")
    st.stop()

with st.sidebar:
    st.subheader("后端连接")
    st.code(API_BASE)
    st.write("请在 Secrets 中设置：")
    st.code('API_BASE = "http://<server-ip>:7861"')

if "token" not in st.session_state:
    st.session_state.token = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.token:
    st.subheader("登录")
    u = st.text_input("用户名")
    p = st.text_input("密码", type="password")
    if st.button("登录", type="primary", use_container_width=True):
        ok, result = api_login(API_BASE, u, p)
        if ok:
            st.session_state.token = result
            st.success("登录成功")
            st.rerun()
        else:
            st.error(result)
    st.stop()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("输入你的问题...")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            ok, result = api_chat(API_BASE, st.session_state.token, query)
        st.markdown(result)
    st.session_state.messages.append({"role": "assistant", "content": result})
