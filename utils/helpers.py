import time
from typing import Dict, Any, Optional
from datetime import datetime

def update_last_active(user_data: Dict[str, Any], context: str, phase: Optional[str] = None) -> None:
    """
    Update user's last active status with context and timestamp.
    
    Args:
        user_data: User data dictionary
        context: Context of the activity (e.g., "quest", "reflection")
        phase: Current user phase, or None to use the existing phase
    """
    user_data["last_active"] = {
        "timestamp": time.time(),
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "context": context,
        "phase": phase or user_data.get("phase") or "-"
    }
