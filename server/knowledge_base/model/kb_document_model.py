
try:
    from langchain.docstore.document import Document
except ImportError:
    try:
        from langchain_community.docstore.document import Document
    except ImportError:
        from langchain_core.documents.base import Document


class DocumentWithVSId(Document):
    """
    矢量化后的文档
    """
    id: str = None
    score: float = 3.0
