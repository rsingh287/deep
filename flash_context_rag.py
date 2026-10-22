import os
import time
import threading
import psycopg2

# Flash Context RAG Engine - Zero Latency Local Vector DB (PostgreSQL Full-Text Search based)
# Automatically indexes files in 'flash_knowledge' folder to inject instantly into LLM context.

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "flash_knowledge")
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

PG_URL = os.getenv("DATABASE_URL", f"postgresql://postgres:{os.getenv('DB_PASSWORD', '')}@localhost:5432/deep_db")

class FlashContextRAG:
    def __init__(self):
        self.lock = threading.Lock()
        self.last_files_state = {}
        
        self._init_db()
        
        # Run initial index synchronously
        self._index_directory()
        
        self._start_background_indexer()

    def _init_db(self):
        try:
            conn = psycopg2.connect(PG_URL)
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS flash_context (
                    id SERIAL PRIMARY KEY,
                    source TEXT,
                    chunk_idx INTEGER,
                    content TEXT,
                    content_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED,
                    UNIQUE (source, chunk_idx)
                );
            ''')
            cur.execute('''
                CREATE INDEX IF NOT EXISTS flash_context_vector_idx ON flash_context USING GIN (content_vector);
            ''')
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"[FlashContextRAG] DB Init Error: {e}")

    def _start_background_indexer(self):
        """Starts a daemon thread that watches the flash_knowledge directory and indexes new files."""
        def indexer():
            while True:
                try:
                    self._index_directory()
                except Exception as e:
                    print(f"[FlashContextRAG] Indexer Error: {e}")
                time.sleep(10) # Check every 10 seconds

        t = threading.Thread(target=indexer, daemon=True)
        t.start()

    def _index_directory(self):
        """Scans the directory for text-based files and indexes them to PostgreSQL."""
        new_docs = []
        
        # Check if any files changed based on mtime
        current_state = {}
        changed = False
        
        for root, _, files in os.walk(KNOWLEDGE_DIR):
            for file in files:
                if file.endswith((".txt", ".md", ".csv", ".json", ".py", ".js")):
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        current_state[file_path] = mtime
                        if self.last_files_state.get(file_path) != mtime:
                            changed = True
                            
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read().replace("\x00", " ")
                        
                        # Simple chunking (e.g., 1000 characters)
                        chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                        
                        for idx, chunk in enumerate(chunks):
                            new_docs.append((file_path, idx, chunk))
                    except Exception as e:
                        print(f"[FlashContextRAG] Failed to read {file}: {e}")
                        
        with self.lock:
            # Rebuild index if files changed or first run
            if changed or not self.last_files_state:
                try:
                    conn = psycopg2.connect(PG_URL)
                    cur = conn.cursor()
                    
                    # We just TRUNCATE and bulk insert for simplicity on local datasets
                    cur.execute("TRUNCATE TABLE flash_context RESTART IDENTITY;")
                    
                    if new_docs:
                        from psycopg2.extras import execute_values
                        execute_values(
                            cur,
                            "INSERT INTO flash_context (source, chunk_idx, content) VALUES %s",
                            new_docs
                        )
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    self.last_files_state = current_state
                    print(f"[FlashContextRAG] Re-indexed {len(new_docs)} document chunks to PostgreSQL.")
                except Exception as e:
                    print(f"[FlashContextRAG] DB Insert Error: {e}")

    def get_flash_context(self, user_prompt, limit=2):
        """Instantly fetches the most relevant context from PostgreSQL Full-Text Search."""
        try:
            conn = psycopg2.connect(PG_URL)
            cur = conn.cursor()
            
            # Use OR logic for the text search to ensure we get matches even if not all words are present
            query = '''
                SELECT content, ts_rank(content_vector, query) as rank 
                FROM flash_context, 
                     to_tsquery('english', replace(plainto_tsquery('english', %s)::text, '&', '|')) query
                WHERE content_vector @@ query 
                ORDER BY rank DESC 
                LIMIT %s
            '''
            
            cur.execute(query, (user_prompt, limit))
            results = cur.fetchall()
            
            cur.close()
            conn.close()
            
            context_str = ""
            for row in results:
                content, rank = row
                if rank > 0.01: # Small threshold
                    context_str += f"\n- {content}\n"
            
            if context_str:
                return f"\n\n[FLASH CONTEXT RAG (PostgreSQL)]\n{context_str}\n"
            return ""
        except Exception as e:
            print(f"[FlashContextRAG] Query Error: {e}")
            return ""

_global_rag_engine = None

def get_engine():
    global _global_rag_engine
    if _global_rag_engine is None:
        _global_rag_engine = FlashContextRAG()
    return _global_rag_engine
