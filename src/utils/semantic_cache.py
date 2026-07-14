import os
import json
import numpy as np
import faiss
from langchain_openai import OpenAIEmbeddings
from config.settings import OPENAI_API_KEY
from src.models.visualization import VisualizationSchema
from src.models.answer import AnswerSchema

class SemanticCache:
    def __init__(self, threshold=0.99, index_file="tests/semantic_cache.index", data_file="tests/semantic_cache.json"):
        self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        self.threshold = threshold
        self.index_file = index_file
        self.data_file = data_file
        self.dim = 1536 # OpenAI text-embedding-ada-002 dimension
        
        self.texts = []
        self.schemas = []
        
        # Inisialisasi FAISS index (Inner Product untuk cosine similarity)
        self.index = faiss.IndexFlatIP(self.dim)
        
        if os.path.exists(self.index_file) and os.path.exists(self.data_file):
            try:
                self.index = faiss.read_index(self.index_file)
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.texts = data.get("texts", [])
                    self.schemas = data.get("schemas", [])
            except Exception as e:
                print(f"Gagal memuat cache: {e}")
            
    def check_cache(self, query: str):
        if self.index.ntotal == 0:
            return None
            
        try:
            query_emb = np.array([self.embeddings.embed_query(query)], dtype=np.float32)
            faiss.normalize_L2(query_emb)
            
            distances, indices = self.index.search(query_emb, 1)
            best_dist = distances[0][0]
            best_idx = indices[0][0]
            
            if best_dist >= self.threshold and best_idx != -1:
                cached_data = self.schemas[best_idx]
                
                # Reconstruct Pydantic Model
                intent = cached_data["intent"]
                schema_dict = cached_data["dsl_schema"]
                
                if intent == "visualization":
                    schema_obj = VisualizationSchema(**schema_dict)
                else:
                    schema_obj = AnswerSchema(**schema_dict)
                    
                return {
                    "intent": intent,
                    "dsl_schema": schema_obj
                }
        except Exception as e:
            print(f"Error checking cache: {e}")
            
        return None
        
    def add_to_cache(self, query: str, intent: str, dsl_schema_dict: dict):
        try:
            query_emb = np.array([self.embeddings.embed_query(query)], dtype=np.float32)
            faiss.normalize_L2(query_emb)
            
            self.index.add(query_emb)
            self.texts.append(query)
            self.schemas.append({"intent": intent, "dsl_schema": dsl_schema_dict})
            
            # Buat direktori tests jika belum ada
            os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
            
            # Save ke disk
            faiss.write_index(self.index, self.index_file)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump({"texts": self.texts, "schemas": self.schemas}, f, indent=4)
        except Exception as e:
            print(f"Error saving to cache: {e}")

# Singleton instance
semantic_cache = SemanticCache()
