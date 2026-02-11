"""Quick test script"""
import asyncio
from mcp_server.tools import deploy_backend_to_ec2, deploy_frontend_to_s3, connect_services

async def test():
    # Deploy backend
    print("=" * 60)
    print("DEPLOYING BACKEND")
    print("=" * 60)
    
    backend_result = await deploy_backend_to_ec2(
        repo_url="https://github.com/frankhokevinho/simple-express-app",
        name="test-backend",
        instance_type="t2.micro"
    )
    
    print(f"\n✅ Backend deployed: {backend_result['url']}")
    
    # Deploy frontend
    print("\n" + "=" * 60)
    print("DEPLOYING FRONTEND")
    print("=" * 60)
    
    frontend_result = await deploy_frontend_to_s3(
        repo_url="https://github.com/aditya-sridhar/simple-reactjs-app",
        name="test-frontend",
        backend_url=backend_result['url']
    )
    
    print(f"\n✅ Frontend deployed: {frontend_result['url']}")
    
    # Connect them
    print("\n" + "=" * 60)
    print("CONNECTING SERVICES")
    print("=" * 60)
    
    connect_result = await connect_services(
        backend_name="test-backend",
        frontend_name="test-frontend"
    )
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"Backend:  {backend_result['url']}")
    print(f"Frontend: {frontend_result['url']}")
    print(f"Total cost: ${backend_result['cost_per_month'] + frontend_result['cost_per_month']:.2f}/month")

if __name__ == "__main__":
    asyncio.run(test()) 