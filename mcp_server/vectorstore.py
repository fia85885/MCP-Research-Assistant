from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings

class VectorStore:
    def __init__(self, path: str = ".chroma", collection_name: str = "papers"):
        # Fixed parameter name to match what's used in server.py
        # Persistent client with disk storage
        self.client = chromadb.PersistentClient(
            path=path, 
            settings=Settings(allow_reset=False)
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add(self, ids: List[str], texts: List[str], metadatas: List[dict]):
        """Add documents to the collection"""
        self.collection.add(
            ids=ids, 
            documents=texts, 
            metadatas=metadatas
        )

    def query(self, question: str, embeddings, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query the collection for similar documents"""
        # Generate embedding for the question
        question_embedding = embeddings.encode([question])[0]
        
        # Query using the embedding
        out = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k
        )
        
        results = []
        # Safely handle the nested structure of results
        documents = out.get('documents', [[]])[0] if out.get('documents') else []
        metadatas = out.get('metadatas', [[]])[0] if out.get('metadatas') else []
        distances = out.get('distances', [[]])[0] if out.get('distances') else []
        
        for i in range(len(documents)):
            results.append({
                "text": documents[i] if i < len(documents) else "",
                "meta": metadatas[i] if i < len(metadatas) else {},
                "score": float(distances[i]) if i < len(distances) else 1.0
            })
        
        return results
