def toggle_neuro_soundscape(enable=True, state="deep_flow"):
    print(f"[NeuroSoundscape] Toggling adaptive 40Hz binaural acoustics: {enable} (State: {state})")
    
    if enable:
        if state == "deep_flow":
            msg = "40Hz Gamma binaural beats + heavy procedural brown noise engaged."
        elif state == "pause":
            msg = "Acoustics softened to ambient rain and light alpha frequencies."
        else:
            msg = "Soundscape initiated."
    else:
        msg = "Neuro-acoustic generator silenced."
        
    return {
        "status": "success",
        "enabled": enable,
        "current_state": state,
        "message": msg
    }
