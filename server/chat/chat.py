from fastapi import Body, Header
from sse_starlette.sse import EventSourceResponse
from configs import LLM_MODELS, TEMPERATURE
from server.utils import wrap_done, get_ChatOpenAI
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
import json
from langchain.prompts.chat import ChatPromptTemplate
from typing import List, Optional, Union
from server.chat.utils import History
from langchain.prompts import PromptTemplate
from server.utils import get_prompt_template
from server.memory.conversation_db_buffer_memory import ConversationBufferDBMemory
from server.db.repository import add_message_to_db
from server.callback_handler.conversation_callback_handler import ConversationCallbackHandler
from server.user_auth import verify_token, add_chat_history

ASSISTANT_NAME = "langchain-ai助手"


def _name_intent_reply(user_query: str) -> str:
    text = (user_query or "").strip()
    if any(k in text for k in ["你叫什么", "你叫啥", "你是谁", "你的名字", "叫什么名字", "名字是", "名字叫"]):
        return f"我的名字是 {ASSISTANT_NAME}。"
    return ""


def _direct_zhipu_reply(user_query: str, temperature: float = 0.7) -> str:
    """Direct call to Zhipu API when local model gateway is unavailable."""
    try:
        import os
        from zhipuai import ZhipuAI
        from configs.model_config import ONLINE_LLM_MODEL

        zhipu_cfg = ONLINE_LLM_MODEL.get("zhipu-api", {})
        api_key = zhipu_cfg.get("api_key") or os.environ.get("ZHIPU_API_KEY", "")
        if not api_key:
            return ""

        client = ZhipuAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=zhipu_cfg.get("version", "glm-4"),
            messages=[
                {"role": "system", "content": "你是一个友好的AI助手，请使用中文回答。"},
                {"role": "user", "content": user_query},
            ],
            temperature=temperature,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        return ""


def _fallback_reply(user_query: str) -> str:
    name_reply = _name_intent_reply(user_query)
    if name_reply:
        return name_reply
    return "模型服务暂时不可用，请稍后重试。"


async def chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
               conversation_id: str = Body("", description="对话框ID"),
               history_len: int = Body(-1, description="从数据库中取历史消息的数量"),
               history: Union[int, List[History]] = Body([],
                                                         description="历史对话，设为一个整数可以从数据库中读取历史消息",
                                                         examples=[[
                                                             {"role": "user",
                                                              "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                             {"role": "assistant", "content": "虎头虎脑"}]]
                                                         ),
               stream: bool = Body(False, description="流式输出"),
               model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
               temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=2.0),
               max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
               # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
               prompt_name: str = Body("default", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
               authorization: Optional[str] = Header(None, description="Bearer token"),
               ):
    # 从 Authorization header 获取用户 token
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        user_id = verify_token(token)

    name_reply = _name_intent_reply(query)
    if name_reply:
        if user_id:
            add_chat_history(user_id, "user", query)
            add_chat_history(user_id, "assistant", name_reply)

        async def name_reply_iterator() -> AsyncIterable[str]:
            yield json.dumps({"text": name_reply}, ensure_ascii=False)

        return EventSourceResponse(name_reply_iterator())
    
    async def chat_iterator() -> AsyncIterable[str]:
        nonlocal history, max_tokens
        callback = AsyncIteratorCallbackHandler()
        callbacks = [callback]
        memory = None

        # 负责保存llm response到message db
        message_id = add_message_to_db(chat_type="llm_chat", query=query, conversation_id=conversation_id)
        conversation_callback = ConversationCallbackHandler(conversation_id=conversation_id, message_id=message_id,
                                                            chat_type="llm_chat",
                                                            query=query)
        callbacks.append(conversation_callback)

        if isinstance(max_tokens, int) and max_tokens <= 0:
            max_tokens = None

        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=callbacks,
        )

        if history: # 优先使用前端传入的历史消息
            history = [History.from_data(h) for h in history]
            prompt_template = get_prompt_template("llm_chat", prompt_name)
            input_msg = History(role="user", content=prompt_template).to_msg_template(False)
            chat_prompt = ChatPromptTemplate.from_messages(
                [i.to_msg_template() for i in history] + [input_msg])
        elif conversation_id and history_len > 0: # 前端要求从数据库取历史消息
            # 使用memory 时必须 prompt 必须含有memory.memory_key 对应的变量
            prompt = get_prompt_template("llm_chat", "with_history")
            chat_prompt = PromptTemplate.from_template(prompt)
            # 根据conversation_id 获取message 列表进而拼凑 memory
            memory = ConversationBufferDBMemory(conversation_id=conversation_id,
                                                llm=model,
                                                message_limit=history_len)
        else:
            prompt_template = get_prompt_template("llm_chat", prompt_name)
            input_msg = History(role="user", content=prompt_template).to_msg_template(False)
            chat_prompt = ChatPromptTemplate.from_messages([input_msg])

        chain = LLMChain(prompt=chat_prompt, llm=model, memory=memory)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"input": query}),
            callback.done),
        )

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield json.dumps(
                    {"text": token, "message_id": message_id},
                    ensure_ascii=False)
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token

            if not answer.strip():
                # If model gateway returns empty output, try direct provider API once.
                answer = _direct_zhipu_reply(query, temperature=temperature) or _fallback_reply(query)
            
            # 如果有用户认证，保存对话历史
            if user_id:
                add_chat_history(user_id, "user", query)
                add_chat_history(user_id, "assistant", answer)
            
            yield json.dumps(
                {"text": answer, "message_id": message_id},
                ensure_ascii=False)

        await task

    return EventSourceResponse(chat_iterator())
