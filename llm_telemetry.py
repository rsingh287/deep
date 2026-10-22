import os
import functools

try:
    from langfuse import Langfuse
    from langfuse.decorators import observe
except ImportError:
    Langfuse = None
    observe = None

class DEEPTelemetry:
    def __init__(self):
        print("[LLM Telemetry] Initializing Langfuse tracing...")
        # Expecting LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY in environment
        if Langfuse:
            try:
                self.langfuse = Langfuse()
                self.active = True
            except Exception as e:
                print(f"[LLM Telemetry] Could not initialize Langfuse: {e}")
                self.active = False
        else:
            self.active = False

    def trace_execution(self, name, **kwargs):
        if not self.active:
            return None
        return self.langfuse.trace(name=name, **kwargs)

    def flush(self):
        if self.active:
            self.langfuse.flush()

telemetry_engine = None

def get_telemetry():
    global telemetry_engine
    if telemetry_engine is None:
        telemetry_engine = DEEPTelemetry()
    return telemetry_engine

# Decorator for easy wrapping of LLM calls
def trace_llm(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if observe:
                return observe(name=name)(func)(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator
