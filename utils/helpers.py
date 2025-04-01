import time

def update_last_active(user_data: dict, context: str, phase: str = None):
    user_data["last_active"] = {
        "timestamp": time.time(),
        "context": context,
        "phase": (phase or user_data.get("phase") or "-")
    }
