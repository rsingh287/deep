import json
import os
import re
from datetime import datetime

DATASET_FILE = "dataset_fine_tune.jsonl"

def log_correction(user_prompt: str, previous_ai_response: str):
    """
    If the user's prompt contains a correction, save the interaction as a DPO/SFT training triplet.
    """
    correction_triggers = [
        "that didn't work",
        "that did not work",
        "wrong",
        "incorrect",
        "do this instead",
        "fix it",
        "no, use",
        "not quite",
        "you forgot",
    ]
    
    prompt_low = user_prompt.lower()
    is_correction = any(t in prompt_low for t in correction_triggers)
    
    if is_correction and previous_ai_response:
        triplet = {
            "timestamp": datetime.now().isoformat(),
            "instruction": "Original instruction context", # We would need the full history for this ideally
            "rejected_response": previous_ai_response,
            "correction_prompt": user_prompt,
            "status": "pending_fine_tune"
        }
        
        with open(DATASET_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(triplet) + '\n')
            
        print(f"[LoRA Self-Learning] Saved correction to {DATASET_FILE} for future fine-tuning.")
        return True
    return False

def trigger_weekly_lora_finetune():
    """
    Placeholder for the actual LoRA finetuning job.
    In a real scenario, this would use PEFT/transformers to train an adapter on dataset_fine_tune.jsonl.
    """
    if not os.path.exists(DATASET_FILE):
        return
        
    print("[LoRA Self-Learning] Triggering weekly LoRA adaptation...")
    # Simulated fine-tuning process
    pass

