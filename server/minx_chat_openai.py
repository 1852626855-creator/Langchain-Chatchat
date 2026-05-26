try:
    from langchain.chat_models import ChatOpenAI
except ImportError:
    try:
        from langchain_community.chat_models import ChatOpenAI
    except ImportError:
        from langchain_openai import ChatOpenAI


class MinxChatOpenAI(ChatOpenAI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)