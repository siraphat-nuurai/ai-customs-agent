import os
import shutil
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

UPLOAD_DIR = "/tmp/customs_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IngestionService:
    def __init__(self):
        self.db_dir = os.getenv("CHROMA_DB_DIR", "/app/data/chroma_store")
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " "]
        )

    async def ingest_file(self, file: UploadFile) -> dict:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            ext = file.filename.rsplit(".", 1)[-1].lower()
            if ext == "pdf":
                loader = PyPDFLoader(file_path)
            elif ext == "txt":
                loader = TextLoader(file_path)
            else:
                return {"status": "error", "message": "Unsupported file format."}
                
            raw_documents = loader.load()
            for doc in raw_documents:
                doc.metadata["source"] = file.filename
                
            chunked_documents = self.text_splitter.split_documents(raw_documents)
            
            vector_store = Chroma(
                persist_directory=self.db_dir, 
                embedding_function=self.embeddings, 
                collection_name="customs_tariffs"
            )
            vector_store.add_documents(chunked_documents)
            
            return {
                "status": "success",
                "filename": file.filename,
                "chunks_processed": len(chunked_documents)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)