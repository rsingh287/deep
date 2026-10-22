import threading
import time
import requests
import json
import logging
from typing import List, Dict

# Synthetic Autonomous Micro-Enterprise / Swarm Simulator
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SwarmSimulator")

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"

PERSONAS = {
    "DevOps Lead ('Alex')": "You are Alex, a senior DevOps engineer. Your job is to analyze the user's idea or code for scalability, uptime, Docker containerization, and PostgreSQL database bottlenecks. Be harsh and focus on infrastructure.",
    "Frontend Designer ('Maya')": "You are Maya, an expert UX/UI frontend designer. You specialize in Three.js, Tailwind, and Apple-like aesthetics. Review the user's idea or code strictly for user experience, accessibility, and visual wow-factor.",
    "Security Red-Teamer ('Cipher')": "You are Cipher, an elite penetration tester. Your single goal is to break the system. Look for SQL injection, XSS, insecure endpoints, and data leaks. Be paranoid and ruthless.",
    "Product Manager ('Marcus')": "You are Marcus, a ruthless Product Manager. Your focus is on MVP timeline, business value, user acquisition, and whether this feature actually matters. Cut the fluff.",
    "Novice User ('Dave')": "You are Dave, a confused, non-technical novice user. You click the wrong buttons and get easily frustrated by technical jargon. Explain how this idea would confuse you."
}

def invoke_persona(persona_name: str, system_prompt: str, task: str) -> Dict[str, str]:
    prompt = f"System: {system_prompt}\n\nTask: {task}\n\nProvide your analysis:"
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=120)
        
        if response.status_code == 200:
            return {"persona": persona_name, "response": response.json().get("response", "").strip()}
        else:
            return {"persona": persona_name, "response": f"Error: {response.text}"}
    except Exception as e:
        return {"persona": persona_name, "response": f"Exception: {str(e)}"}

def run_swarm_simulation(task: str) -> List[Dict[str, str]]:
    logger.info(f"Starting swarm simulation for task: {task[:50]}...")
    
    results = []
    threads = []
    
    def worker(name, sys_prompt):
        res = invoke_persona(name, sys_prompt, task)
        results.append(res)
    
    for name, sys_prompt in PERSONAS.items():
        t = threading.Thread(target=worker, args=(name, sys_prompt))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    logger.info("Swarm simulation complete.")
    return results

if __name__ == "__main__":
    task = "I want to build a local python flask server that takes a user's picture via webcam and stores it in an unencrypted sqlite database, then emails them a link to view it using smtplib."
    print("--- INITIATING SYNTHETIC SWARM SIMULATION ---")
    print(f"Task: {task}")
    print("---------------------------------------------")
    
    results = run_swarm_simulation(task)
    for r in results:
        print(f"\n[{r['persona']}]")
        print(r['response'])
