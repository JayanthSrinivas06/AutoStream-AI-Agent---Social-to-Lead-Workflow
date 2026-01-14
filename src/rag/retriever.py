import json
import os
from typing import List, Dict
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class KnowledgeBaseRetriever:
    
    def __init__(self, knowledge_base_path: str = None):    #type:ignore
        if knowledge_base_path is None:
            # Default to knowledge_base.json in same directory
            current_dir = Path(__file__).parent
            knowledge_base_path = current_dir / "knowledge_base.json"
        
        self.knowledge_base_path = knowledge_base_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None
        self._load_knowledge_base()
    

    def _load_knowledge_base(self):
        # Load JSON data
        with open(self.knowledge_base_path, 'r') as f:
            kb_data = json.load(f)
        
        # Convert to documents
        documents = self._create_documents(kb_data)
        
        # Split documents for better retrieval (optimized for token efficiency)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=30,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        split_docs = text_splitter.split_documents(documents)
        
        # Create vector store
        self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
    

    def _create_documents(self, data: Dict, prefix: str = "") -> List[Document]:
        documents = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_prefix = f"{prefix} > {key}" if prefix else key
                
                if isinstance(value, (dict, list)):
                    # Recursively process nested structures
                    documents.extend(self._create_documents(value, current_prefix)) #type:ignore
                else:
                    # Create document for leaf values
                    content = f"{current_prefix}: {value}"
                    documents.append(Document(
                        page_content=content,
                        metadata={"category": prefix, "key": key}
                    ))
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    documents.extend(self._create_documents(item, prefix))
                else:
                    content = f"{prefix}: {item}"
                    documents.append(Document(
                        page_content=content,
                        metadata={"category": prefix, "index": i}
                    ))
        
        return documents
    

    def retrieve(self, query: str, k: int = 2) -> List[str]:
        if self.vector_store is None:
            return []
        
        # Perform similarity search
        results = self.vector_store.similarity_search(query, k=k)
        
        # Extract content
        return [doc.page_content for doc in results]
    

    def get_context(self, query: str) -> str:
        relevant_docs = self.retrieve(query, k=2)
        
        if not relevant_docs:
            return "No info found."
        
        context = "AutoStream info:\n"
        for i, doc in enumerate(relevant_docs, 1):
            context += f"{i}. {doc}\n"
        
        return context


# Singleton instance for reuse
_retriever_instance = None

def get_retriever() -> KnowledgeBaseRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeBaseRetriever()
    return _retriever_instance
