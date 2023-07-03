from docdeid import Document
from langchain.text_splitter import TokenTextSplitter
from pydantic import BaseModel


class TokenHandler(BaseModel):
    """
        A class that handles token related operations
    """
    max_token_len = 4096
    llm_name: str

    def split_by_token(self, text, chunk_size=1200):
        text_splitter = TokenTextSplitter(model_name=self.llm_name, chunk_size=chunk_size)
        split_text = text_splitter.split_text(text)
        return [Document(page_content=t) for t in split_text]
