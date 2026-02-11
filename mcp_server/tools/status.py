"""Get deployment status"""
from typing import Dict, Any
from ..models.deployment import load_deployment
from ..deployers.ec2 import EC2Deployer


async def get_deployment_status(deployment_name: str) -> Dict[str, Any]:
    """Get status of a deployment"""
    
    deployment = load_deployment(deployment_name)
    
    if not deployment:
        return {
            "success": False,
            "message": f"Deployment '{deployment_name}' not found"
        }
    
    deployment_type = deployment.get('type')
    
    if deployment_type == 'backend':
        # Get live instance info
        instance_id = deployment.get('instance_id')
        region = deployment.get('region', 'us-east-1')
        
        deployer = EC2Deployer(region=region)
        try:
            instance_info = deployer.get_instance_info(instance_id)
            deployment.update(instance_info)
        except Exception as e:
            deployment['status'] = 'error'
            deployment['error'] = str(e)
    
    return {
        "success": True,
        "deployment": deployment
    }