import os
from typing import List, Dict

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
    st.subheader("部署说明")
    st.markdown(
        "在 Streamlit Cloud 的 **Secrets** 里添加:\n\n"
        "```toml\n"
        'ZHIPU_API_KEY = "你的真实Key"\n'
        'ZHIPU_MODEL = "glm-4"\n'
        "```"
    )
