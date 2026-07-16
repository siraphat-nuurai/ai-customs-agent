import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

class RetrieverService:
    def __init__(self):
        self.db_dir = os.getenv("CHROMA_DB_DIR", "/app/data/chroma_store")
        self.collection_name = "customs_tariffs"
        self.embeddings = OpenAIEmbeddings()
        
        os.makedirs(self.db_dir, exist_ok=True)
        
        self.vectorstore = Chroma(
            persist_directory=self.db_dir,
            embedding_function=self.embeddings,
            collection_name=self.collection_name
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})

    def get_retriever(self):
        return self.retriever