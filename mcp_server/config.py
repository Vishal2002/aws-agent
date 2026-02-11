"""Configuration management"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file BEFORE creating Settings
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # AWS Configuration
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_default_region: str = "us-east-1"
    print(aws_access_key_id)
    
    # Application
    state_dir: Path = Path("./deployments")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Create state directory
settings.state_dir.mkdir(exist_ok=True)

# Configure boto3 to use our credentials
if settings.aws_access_key_id and settings.aws_secret_access_key:
    import boto3
    boto3.setup_default_session(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_default_region
    )