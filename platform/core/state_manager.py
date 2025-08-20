"""Platform state management with transactions."""

import json
import fcntl
import time
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, Any, Optional
from datetime import datetime
from .logger import logger

class StateManager:
    """Manages platform state with atomic operations."""
    
    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = state_dir or Path.home() / ".platform"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.state_dir / "state.json"
        self.lock_file = self.state_dir / "state.lock"
        self.backup_dir = self.state_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Initialize state if it doesn't exist
        if not self.state_file.exists():
            self._initialize_state()
    
    def _initialize_state(self):
        """Initialize empty state."""
        initial_state = {
            "version": "2.0.0",
            "created_at": datetime.now().isoformat(),
            "platform": {
                "status": "not_initialized",
                "environment": None,
                "last_updated": datetime.now().isoformat()
            },
            "services": {},
            "checkpoints": []
        }
        self._write_state(initial_state)
        logger.info("Initialized platform state")
    
    def _read_state(self) -> Dict[str, Any]:
        """Read current state."""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("State file corrupted or missing, reinitializing")
            self._initialize_state()
            return self._read_state()
    
    def _write_state(self, state: Dict[str, Any]):
        """Write state to file."""
        state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    @contextmanager
    def transaction(self):
        """Atomic state transaction with file locking."""
        lock_acquired = False
        lock_file = open(self.lock_file, 'w')
        
        try:
            # Acquire exclusive lock with timeout
            timeout = 5
            start_time = time.time()
            
            while True:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    lock_acquired = True
                    break
                except IOError:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Could not acquire state lock")
                    time.sleep(0.1)
            
            # Read current state
            state = self._read_state()
            
            # Create checkpoint before modifications
            checkpoint_id = self.create_checkpoint(state)
            
            # Yield state for modifications
            yield state
            
            # Write modified state
            self._write_state(state)
            logger.debug(f"State transaction completed (checkpoint: {checkpoint_id})")
            
        except Exception as e:
            logger.error(f"State transaction failed: {e}")
            # Attempt to restore from latest checkpoint
            if 'checkpoint_id' in locals():
                self.restore_checkpoint(checkpoint_id)
            raise
        finally:
            if lock_acquired:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
    
    def create_checkpoint(self, state: Dict[str, Any]) -> str:
        """Create a state checkpoint."""
        checkpoint_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.backup_dir / f"checkpoint_{checkpoint_id}.json"
        
        with open(checkpoint_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        # Keep only last 10 checkpoints
        checkpoints = sorted(self.backup_dir.glob("checkpoint_*.json"))
        if len(checkpoints) > 10:
            for old_checkpoint in checkpoints[:-10]:
                old_checkpoint.unlink()
        
        return checkpoint_id
    
    def restore_checkpoint(self, checkpoint_id: str):
        """Restore state from checkpoint."""
        checkpoint_file = self.backup_dir / f"checkpoint_{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found")
        
        with open(checkpoint_file, 'r') as f:
            state = json.load(f)
        
        self._write_state(state)
        logger.success(f"Restored state from checkpoint {checkpoint_id}")
    
    def get_service_state(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get state for a specific service."""
        state = self._read_state()
        return state.get("services", {}).get(service_name)
    
    def update_service_state(self, service_name: str, service_state: Dict[str, Any]):
        """Update state for a specific service."""
        with self.transaction() as state:
            if "services" not in state:
                state["services"] = {}
            state["services"][service_name] = {
                **service_state,
                "last_updated": datetime.now().isoformat()
            }
    
    def get_platform_status(self) -> str:
        """Get current platform status."""
        state = self._read_state()
        return state.get("platform", {}).get("status", "unknown")
    
    def set_platform_status(self, status: str):
        """Set platform status."""
        with self.transaction() as state:
            if "platform" not in state:
                state["platform"] = {}
            state["platform"]["status"] = status
            state["platform"]["last_updated"] = datetime.now().isoformat()
