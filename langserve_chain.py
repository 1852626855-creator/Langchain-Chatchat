"""LangServe 服务部署

使用官方 LangServe 库创建标准的 LangChain 服务
支持 REST API 和 Playground 界面
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langserve import add_routes
import uvicorn
import requests

try:
    from configs.model_config import ONLINE_LLM_MODEL
except ImportError:
    ONLINE_LLM_MODEL = {}


class SimpleZhipuAIChat(BaseChatModel):
    """简单的智谱 AI 聊天模型"""

    api_key: str
    model: str = "glm-4"
    temperature: float = 0.7

    def _generate(self, messages: list[BaseMessage], *args, **kwargs) -> ChatResult:
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted_messages.append({"role": "assistant", "content": msg.content})

        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.temperature,
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            ai_message = result["choices"][0]["message"]["content"]
            return ChatResult(
                generations=[ChatGeneration(message=AIMessage(content=ai_message))]
            )
        except Exception as e:
            raise RuntimeError(f"调用智谱 AI API 失败: {str(e)}")

    @property
    def _llm_type(self) -> str:
        return "simple_zhipuai_chat"


def create_llm():
    """创建 LLM 实例"""
    zhipu_config = ONLINE_LLM_MODEL.get("zhipu-api", {})
    api_key = zhipu_config.get("api_key", "") or os.environ.get("ZHIPU_API_KEY", "")

    if not api_key:
        raise ValueError(
            "未配置智谱 API Key，请设置环境变量 ZHIPU_API_KEY 或在 configs/model_config.py 中配置"
        )

    print(f"Using Zhipu AI API Key: {api_key[:10]}...")
    return SimpleZhipuAIChat(api_key=api_key, model="glm-4", temperature=0.7)


def create_chat_chain():
    """创建 LangServe 可部署的对话 Chain"""
    llm = create_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个友好的AI助手，使用中文回答问题。"),
        ("human", "{input}"),
    ])
    return prompt | llm | (lambda x: x.content)


def create_app():
    """创建 LangServe 应用"""
    app = FastAPI(
        title="LangChain-Chatchat LangServe",
        version="1.0",
        description="基于官方 LangServe 的对话服务",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    chain = create_chat_chain()
    add_routes(
        app,
        chain,
        path="/chat",
        enable_feedback_endpoint=False,
        playground_type="default",
    )

    llm = create_llm()

    @app.post("/api/chat")
    async def chat_endpoint(request: Request):
        """兼容旧版前端的聊天端点"""
        data = await request.json()
        user_input = data.get("input", "")
        if not user_input:
            return {"error": "请提供输入内容"}
        try:
            messages = [
                HumanMessage(content="你是一个友好的AI助手，使用中文回答问题。"),
                HumanMessage(content=user_input),
            ]
            result = llm._generate(messages)
            return {"output": result.generations[0].text}
        except Exception as e:
            return {"error": str(e)}

    @app.get("/")
    async def root():
        return {
            "service": "LangChain-Chatchat LangServe",
            "version": "1.0",
            "docs_url": "/docs",
            "playground_url": "/chat/playground",
            "invoke_url": "/chat/invoke",
            "stream_url": "/chat/stream",
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "LangServe"}

    return app


if __name__ == "__main__":
    try:
        app = create_app()
        print("=" * 60)
        print("LangServe 服务初始化成功")
        print("使用模型: Zhipu GLM-4")
        print("=" * 60)
        print("服务端点:")
        print("  - 主页面: http://localhost:8000")
        print("  - 文档页面: http://localhost:8000/docs")
        print("  - Playground: http://localhost:8000/chat/playground")
        print("  - Invoke API: http://localhost:8000/chat/invoke")
        print("  - Stream API: http://localhost:8000/chat/stream")
        print("=" * 60)

        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"服务启动失败: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
