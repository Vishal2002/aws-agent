"""Deployment state management"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from ..config import settings


def save_deployment(name: str, info: Dict[str, Any]) -> None:
    """Save deployment information to disk"""
    
    state_file = settings.state_dir / f"{name}.json"
    
    # Add timestamp
    info['updated_at'] = datetime.utcnow().isoformat()
    if 'created_at' not in info:
        info['created_at'] = info['updated_at']
    
    with open(state_file, 'w') as f:
        json.dump(info, f, indent=2)


def load_deployment(name: str) -> Optional[Dict[str, Any]]:
    """Load deployment information from disk"""
    
    state_file = settings.state_dir / f"{name}.json"
    
    if not state_file.exists():
        return None
    
    with open(state_file, 'r') as f:
        return json.load(f)


def list_deployments() -> Dict[str, Dict[str, Any]]:
    """List all deployments"""
    
    deployments = {}
    
    for state_file in settings.state_dir.glob("*.json"):
        name = state_file.stem
        with open(state_file, 'r') as f:
            deployments[name] = json.load(f)
    
    return deployments


def delete_deployment(name: str) -> bool:
    """Delete deployment information"""
    
    state_file = settings.state_dir / f"{name}.json"
    
    if state_file.exists():
        state_file.unlink()
        return True
    
    return False