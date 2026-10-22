import os
from dotenv import load_dotenv

load_dotenv()

try:
    from mem0 import Memory
except ImportError:
    Memory = None


class DEEPEpisodicMemory:
    def __init__(self):
        self.memory = None

        # PostgreSQL connection string from .env
        db_url = os.environ.get(
            "DATABASE_URL",
            f"postgresql://postgres:{os.getenv('DB_PASSWORD', '')}@localhost:5432/deep_db"
        )

        config = {
            "vector_store": {
                "provider": "pgvector",
                "config": {
                    "connection_string": db_url,
                    "collection_name": "mem0_episodic_vectors",
                    "embedding_model_dims": 768,  # nomic-embed-text output dim
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "nomic-embed-text",
                    "ollama_base_url": "http://localhost:11434"
                }
            },
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "qwen2.5:3b",
                    "ollama_base_url": "http://localhost:11434"
                }
            }
        }

        print("[Episodic Memory] Initializing mem0 with local Ollama + pgvector on deep_db...")
        if Memory:
            try:
                self.memory = Memory.from_config(config)
                print("[Episodic Memory] Episodic Memory Core ONLINE — vectors stored in deep_db.")
            except Exception as e:
                print(f"[Episodic Memory] Initialization error: {e}")
                self.memory = None
        else:
            print("[Episodic Memory] mem0 not installed — episodic memory disabled.")

    def store_interaction(self, user_id, message, metadata=None):
        if not self.memory:
            return False
        try:
            self.memory.add(message, user_id=user_id, metadata=metadata)
            return True
        except Exception as e:
            print(f"[Episodic Memory] Store error: {e}")
            return False

    def recall_context(self, user_id, query):
        if not self.memory:
            return []
        try:
            results = self.memory.search(query, user_id=user_id)
            return results
        except Exception as e:
            print(f"[Episodic Memory] Search error: {e}")
            return []


episodic_core = None


def init_episodic_memory():
    global episodic_core
    if episodic_core is None:
        episodic_core = DEEPEpisodicMemory()
    return episodic_core
