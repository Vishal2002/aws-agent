"""Utility functions for deployers"""
import tempfile
import shutil
from pathlib import Path
from typing import Optional
import git


def clone_repo(repo_url: str, target_dir: Optional[Path] = None) -> Path:
    """Clone a git repository"""
    
    if target_dir is None:
        target_dir = Path(tempfile.mkdtemp())
    
    git.Repo.clone_from(repo_url, target_dir)
    
    return target_dir


def detect_app_type(repo_path: Path) -> str:
    """Detect application type from repository contents"""
    
    if (repo_path / "package.json").exists():
        return "nodejs"
    elif (repo_path / "requirements.txt").exists():
        return "python"
    elif (repo_path / "go.mod").exists():
        return "go"
    elif (repo_path / "Gemfile").exists():
        return "ruby"
    else:
        return "unknown"


def cleanup_temp_dir(path: Path) -> None:
    """Clean up temporary directory"""
    if path.exists() and path.is_dir():
        shutil.rmtree(path)