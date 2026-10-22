import re

def route_query_complexity(prompt):
    print(f"[SemanticGate] Analyzing complexity for dynamic model routing...")
    
    # 5ms local classifier heuristics
    simple_patterns = [
        r'what is the time', r'current date', r'convert .* to .*',
        r'what port', r'hello', r'ping'
    ]
    
    prompt_lower = prompt.lower()
    is_simple = any(re.search(p, prompt_lower) for p in simple_patterns)
    word_count = len(prompt.split())
    
    if is_simple or word_count < 8:
        return {
            "status": "success",
            "complexity": "low",
            "routed_model": "1B_Fast_Model",
            "estimated_latency": "100ms",
            "message": "Simple query detected. Routed to ultra-fast 1B parameter model."
        }
    else:
        return {
            "status": "success",
            "complexity": "high",
            "routed_model": "14B_Reasoning_Engine",
            "estimated_latency": "2000ms+",
            "message": "Complex reasoning detected. Routed to heavy 14B reasoning engine."
        }
