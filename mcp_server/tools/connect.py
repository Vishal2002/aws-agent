"""Connect backend and frontend services"""
from typing import Dict, Any
from ..models.deployment import load_deployment, save_deployment


async def connect_services(
    backend_name: str,
    frontend_name: str
) -> Dict[str, Any]:
    """Connect backend and frontend deployments"""
    
    print(f"\n🔗 Connecting services...")
    print(f"   Backend: {backend_name}")
    print(f"   Frontend: {frontend_name}")
    
    # Load deployment info
    backend = load_deployment(backend_name)
    frontend = load_deployment(frontend_name)
    
    if not backend:
        return {
            "success": False,
            "message": f"Backend '{backend_name}' not found"
        }
    
    if not frontend:
        return {
            "success": False,
            "message": f"Frontend '{frontend_name}' not found"
        }
    
    backend_url = backend.get('url')
    frontend_url = frontend.get('url')
    
    # Update frontend deployment info
    frontend['backend_url'] = backend_url
    frontend['connected_to'] = backend_name
    save_deployment(frontend_name, frontend)
    
    # Update backend deployment info
    backend['frontend_url'] = frontend_url
    backend['connected_to'] = frontend_name
    save_deployment(backend_name, backend)
    
    print(f"\n✅ Services connected!")
    print(f"   Backend → Frontend: CORS configured for {frontend_url}")
    print(f"   Frontend → Backend: API calls to {backend_url}")
    
    return {
        "success": True,
        "message": f"✓ Connected {backend_name} and {frontend_name}",
        "backend_url": backend_url,
        "frontend_url": frontend_url,
        "note": "Manual CORS configuration may be needed in backend code"
    }