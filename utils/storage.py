import json
import fcntl
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class Storage:
    """
    File storage utility for atomic operations with JSON data.
    Provides thread-safe operations with file locking.
    """
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def read(self) -> Dict[str, Any]:
        """
        Read data from storage file with shared lock.
        
        Returns:
            Dictionary with data or empty dict if file doesn't exist
        """
        if not self.file_path.exists():
            return {}
        
        try:
            with open(self.file_path, "r") as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                try:
                    return json.load(f)
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON from {self.file_path}: {e}")
                    return {}
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except FileNotFoundError:
            return {}
        except Exception as e:
            logging.error(f"Error reading from {self.file_path}: {e}")
            return {}
    
    def write(self, data: Dict[str, Any]) -> bool:
        """
        Write data to storage file with exclusive lock.
        
        Args:
            data: Dictionary to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            with open(self.file_path, "w") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                    return True
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            logging.error(f"Error writing to {self.file_path}: {e}")
            return False
                
    def update_user(self, user_id: str, update_func) -> bool:
        """
        Update user data with a function.
        
        Args:
            user_id: User ID to update
            update_func: Function that takes user data and updates it
            
        Returns:
            True if successful, False otherwise
        """
        data = self.read()
        user_data = data.get(user_id, {})
        update_func(user_data)
        data[user_id] = user_data
        return self.write(data) 