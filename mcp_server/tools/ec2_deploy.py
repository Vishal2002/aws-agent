"""EC2 Backend Deployment Tool"""
import asyncio
import secrets
from typing import Dict, Any
from ..deployers.ec2 import EC2Deployer
from ..deployers.utils import clone_repo, detect_app_type, cleanup_temp_dir
from ..models.deployment import save_deployment
from ..config import settings


async def deploy_backend_to_ec2(
    repo_url: str,
    name: str,
    instance_type: str = "t2.micro",
    region: str = None,
    port: int = 3000,
) -> Dict[str, Any]:
    """Deploy backend application to EC2"""
    
    if region is None:
        region = settings.aws_default_region
    
    print(f"\n🚀 Deploying backend '{name}' to EC2...")
    print(f"   Repository: {repo_url}")
    print(f"   Instance: {instance_type} in {region}")
    print(f"   Port: {port}")
    
    deployer = EC2Deployer(region=region)
    
    # Clone and detect app type
    print(f"\n📦 Analyzing repository...")
    repo_path = clone_repo(repo_url)
    app_type = detect_app_type(repo_path)
    print(f"   Detected: {app_type} application")
    cleanup_temp_dir(repo_path)
    
    # Create security group
    print(f"\n🔒 Creating security group...")
    sg_name = f"{name}-sg-{secrets.token_hex(4)}"
    security_group_id = deployer.create_security_group(
        name=sg_name,
        ports=[port, 22]  # App port + SSH
    )
    print(f"   Security group: {security_group_id}")
    
    # Generate user data script
    print(f"\n📝 Generating deployment script...")
    if app_type == "nodejs":
        user_data = deployer.generate_user_data_nodejs(repo_url, port)
    elif app_type == "python":
        user_data = deployer.generate_user_data_python(repo_url, port)
    else:
        raise ValueError(f"Unsupported app type: {app_type}. Supported: nodejs, python")
    
    # Launch EC2 instance
    print(f"\n☁️  Launching EC2 instance...")
    instance = deployer.launch_instance(
        name=name,
        instance_type=instance_type,
        security_group_id=security_group_id,
        user_data=user_data
    )
    
    instance_id = instance['InstanceId']
    print(f"   Instance ID: {instance_id}")
    
    # Wait for instance to be running
    public_ip = await deployer.wait_for_instance(instance_id)
    
    # Save deployment info
    deployment_info = {
        "name": name,
        "type": "backend",
        "instance_id": instance_id,
        "public_ip": public_ip,
        "port": port,
        "url": f"http://{public_ip}:{port}",
        "security_group_id": security_group_id,
        "instance_type": instance_type,
        "region": region,
        "app_type": app_type,
        "status": "running",
        "repo_url": repo_url
    }
    
    save_deployment(name, deployment_info)
    
    cost = deployer.estimate_cost(instance_type)
    
    print(f"\n✅ Backend deployment complete!")
    print(f"   URL: {deployment_info['url']}")
    print(f"   Cost: ${cost:.2f}/month")
    
    return {
        "success": True,
        "message": f"✓ Backend '{name}' deployed successfully!",
        "instance_id": instance_id,
        "url": deployment_info["url"],
        "public_ip": public_ip,
        "port": port,
        "cost_per_month": cost,
        "deployment_info": deployment_info
    }