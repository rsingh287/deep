def predict_next_action(recent_events):
    print("[MarkovAnticipator] Calculating probabilistic next-intent vector...")
    
    # Mocking a lightweight Markov Chain decision
    prediction = "python app.py"
    probability = 0.85
    
    if "modified routes/system.py" in recent_events:
        prediction = "curl -X POST http://127.0.0.1:8000/api/system/test"
        probability = 0.92
    elif "git add" in recent_events:
        prediction = "git commit -m 'Update system'"
        probability = 0.88
        
    return {
        "status": "success",
        "predicted_command": prediction,
        "confidence": probability,
        "message": f"Glowing HUD autocomplete pill armed: '{prediction}'."
    }
