import threading
import time
import requests
import json
import logging
from typing import List, Dict

# Synthetic Autonomous Micro-Enterprise / Swarm Simulator
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SwarmSimulator")

import os

OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/generate"
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

PERSONAS = {
    "DevOps Lead ('Alex')": "You are Alex, a senior DevOps engineer. Your job is to analyze the user's idea or code for scalability, uptime, Docker containerization, and PostgreSQL database bottlenecks. Be harsh and focus on infrastructure.",
    "Frontend Designer ('Maya')": "You are Maya, an expert UX/UI frontend designer. You specialize in Three.js, Tailwind, and Apple-like aesthetics. Review the user's idea or code strictly for user experience, accessibility, and visual wow-factor.",
    "Security Red-Teamer ('Cipher')": "You are Cipher, an elite penetration tester. Your single goal is to break the system. Look for SQL injection, XSS, insecure endpoints, and data leaks. Be paranoid and ruthless.",
    "Product Manager ('Marcus')": "You are Marcus, a ruthless Product Manager. Your focus is on MVP timeline, business value, user acquisition, and whether this feature actually matters. Cut the fluff.",
    "Novice User ('Dave')": "You are Dave, a confused, non-technical novice user. You click the wrong buttons and get easily frustrated by technical jargon. Explain how this idea would confuse you."
}

# Concurrency semaphore to avoid overwhelming local GPU VRAM
CONCURRENCY_SEMAPHORE = threading.Semaphore(2)

def invoke_persona(persona_name: str, system_prompt: str, task: str, model: str = None) -> Dict[str, str]:
    if not model:
        model = DEFAULT_MODEL
    prompt = f"System: {system_prompt}\n\nTask: {task}\n\nProvide your analysis:"

    with CONCURRENCY_SEMAPHORE:
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }, timeout=120)
            
            if response.status_code == 200:
                return {"persona": persona_name, "response": response.json().get("response", "").strip()}
            else:
                return {"persona": persona_name, "response": f"Ollama Error (HTTP {response.status_code}): {response.text[:200]}"}
        except Exception as e:
            return {"persona": persona_name, "response": f"Exception connecting to model service: {str(e)}"}

def run_swarm_simulation(task: str, model: str = None) -> List[Dict[str, str]]:
    logger.info(f"Starting swarm simulation for task: {task[:50]}...")
    
    persona_keys = list(PERSONAS.keys())
    results = [None] * len(persona_keys)
    threads = []
    
    def worker(index, name, sys_prompt):
        res = invoke_persona(name, sys_prompt, task, model=model)
        results[index] = res
    
    for i, (name, sys_prompt) in enumerate(PERSONAS.items()):
        t = threading.Thread(target=worker, args=(i, name, sys_prompt))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    logger.info("Swarm simulation complete.")
    return [r for r in results if r is not None]

if __name__ == "__main__":
    task = "I want to build a local python flask server that takes a user's picture via webcam and stores it in an unencrypted sqlite database, then emails them a link to view it using smtplib."
    print("--- INITIATING SYNTHETIC SWARM SIMULATION ---")
    print(f"Task: {task}")
    print("---------------------------------------------")
    
    results = run_swarm_simulation(task)
    for r in results:
        print(f"\n[{r['persona']}]")
        print(r['response'])
