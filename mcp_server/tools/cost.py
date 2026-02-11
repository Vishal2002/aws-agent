"""Cost estimation"""
from typing import Dict, Any
from ..models.deployment import load_deployment
from ..deployers.ec2 import EC2Deployer
from ..deployers.s3 import S3Deployer


async def estimate_deployment_cost(deployment_name: str) -> Dict[str, Any]:
    """Estimate cost for a deployment"""
    
    deployment = load_deployment(deployment_name)
    
    if not deployment:
        return {
            "success": False,
            "message": f"Deployment '{deployment_name}' not found"
        }
    
    deployment_type = deployment.get('type')
    total_cost = 0.0
    breakdown = {}
    
    if deployment_type == 'backend':
        instance_type = deployment.get('instance_type', 't2.micro')
        deployer = EC2Deployer()
        cost = deployer.estimate_cost(instance_type)
        total_cost += cost
        breakdown['ec2'] = cost
    
    elif deployment_type == 'frontend':
        deployer = S3Deployer()
        cost = deployer.estimate_cost()
        total_cost += cost
        breakdown['s3'] = cost
    
    return {
        "success": True,
        "deployment_name": deployment_name,
        "total_cost_per_month": round(total_cost, 2),
        "breakdown": breakdown,
        "currency": "USD"
    }