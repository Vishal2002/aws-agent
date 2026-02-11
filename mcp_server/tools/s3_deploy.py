"""S3 Frontend Deployment Tool"""
import secrets
from typing import Dict, Any
from ..deployers.s3 import S3Deployer
from ..deployers.utils import clone_repo, cleanup_temp_dir
from ..models.deployment import save_deployment, load_deployment
from ..config import settings


async def deploy_frontend_to_s3(
    repo_url: str,
    name: str,
    build_command: str = "npm run build",
    region: str = None,
    backend_url: str = None
) -> Dict[str, Any]:
    """Deploy frontend application to S3"""
    
    if region is None:
        region = settings.aws_default_region
    
    print(f"\n🚀 Deploying frontend '{name}' to S3...")
    print(f"   Repository: {repo_url}")
    print(f"   Build command: {build_command}")
    
    deployer = S3Deployer(region=region)
    
    # Clone repository
    print(f"\n📦 Cloning repository...")
    repo_path = clone_repo(repo_url)
    
    # If backend_url provided, create .env file for build
    if backend_url:
        print(f"\n🔗 Configuring backend URL: {backend_url}")
        env_file = repo_path / ".env"
        with open(env_file, 'w') as f:
            f.write(f"REACT_APP_API_URL={backend_url}\n")
            f.write(f"VITE_API_URL={backend_url}\n")
            f.write(f"NEXT_PUBLIC_API_URL={backend_url}\n")
    
    # Build the application
    build_dir = deployer.build_app(repo_path, build_command)
    
    # Create unique bucket name
    bucket_name = f"{name}-{secrets.token_hex(6)}".lower()
    print(f"\n☁️  Creating S3 bucket: {bucket_name}")
    
    deployer.create_bucket(bucket_name)
    
    # Upload files
    print(f"\n📤 Uploading files...")
    file_count = deployer.upload_directory(build_dir, bucket_name)
    
    # Clean up
    cleanup_temp_dir(repo_path)
    
    # Get website URL
    website_url = deployer.get_website_url(bucket_name)
    
    # Save deployment info
    deployment_info = {
        "name": name,
        "type": "frontend",
        "bucket_name": bucket_name,
        "url": website_url,
        "region": region,
        "file_count": file_count,
        "status": "deployed",
        "repo_url": repo_url,
        "build_command": build_command
    }
    
    if backend_url:
        deployment_info["backend_url"] = backend_url
    
    save_deployment(name, deployment_info)
    
    cost = deployer.estimate_cost()
    
    print(f"\n✅ Frontend deployment complete!")
    print(f"   URL: {website_url}")
    print(f"   Files: {file_count}")
    print(f"   Cost: ${cost:.2f}/month")
    
    return {
        "success": True,
        "message": f"✓ Frontend '{name}' deployed successfully!",
        "bucket_name": bucket_name,
        "url": website_url,
        "file_count": file_count,
        "cost_per_month": cost,
        "deployment_info": deployment_info
    }