"""
AWS Deployment Agent - MCP Server for Claude Desktop
"""

import asyncio
import sys
import json
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Log startup to stderr (stdout is reserved for MCP protocol)
print("=" * 60, file=sys.stderr)
print("🚀 AWS DEPLOYMENT AGENT - MCP SERVER", file=sys.stderr)
print("=" * 60, file=sys.stderr)

from .tools import (
    deploy_backend_to_ec2,
    deploy_frontend_to_s3,
    connect_services,
    setup_nginx_proxy,
    create_autoscaling_group,
    estimate_deployment_cost,
    get_deployment_status,
)

print("✅ Tools imported successfully", file=sys.stderr)

# Initialize MCP server
app = Server("aws-deployment-agent")
print("✅ MCP Server initialized", file=sys.stderr)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available AWS deployment tools"""
    
    print("📋 Listing tools...", file=sys.stderr)
    
    tools = [
        Tool(
            name="deploy_backend_to_ec2",
            description="""Deploy a backend application to AWS EC2.

Supports Node.js and Python applications.

Instance types:
- t2.micro ($8/mo) - FREE TIER eligible, good for small apps
- t2.small ($17/mo) - Medium traffic
- t3.medium ($30/mo) - Production apps

Automatically handles:
- EC2 instance provisioning
- Security group configuration  
- Application deployment
- Auto-start on boot

Example: "Deploy my Express API at github.com/user/repo to EC2"
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_url": {
                        "type": "string",
                        "description": "GitHub repository URL (e.g., https://github.com/user/repo)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Deployment name for tracking (e.g., 'my-backend')"
                    },
                    "instance_type": {
                        "type": "string",
                        "default": "t2.micro",
                        "description": "EC2 instance type"
                    },
                    "port": {
                        "type": "integer",
                        "default": 3000,
                        "description": "Application port"
                    },
                },
                "required": ["repo_url", "name"]
            }
        ),
        Tool(
            name="deploy_frontend_to_s3",
            description="""Deploy a frontend application to AWS S3 with static website hosting.

Supports React, Vue, Angular, Next.js, and any static site.

Automatically handles:
- S3 bucket creation
- Building your app (npm run build)
- Uploading files
- Public website configuration
- Backend URL injection

Cost: ~$0.50/month

Example: "Deploy my React app at github.com/user/repo to S3"
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_url": {
                        "type": "string",
                        "description": "GitHub repository URL"
                    },
                    "name": {
                        "type": "string",
                        "description": "Deployment name"
                    },
                    "build_command": {
                        "type": "string",
                        "default": "npm run build",
                        "description": "Build command"
                    },
                    "backend_url": {
                        "type": "string",
                        "description": "Backend API URL to inject into environment"
                    },
                },
                "required": ["repo_url", "name"]
            }
        ),
        Tool(
            name="connect_services",
            description="""Connect backend and frontend deployments.

Updates CORS configuration and links the services.

Use after deploying both frontend and backend.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "backend_name": {
                        "type": "string",
                        "description": "Backend deployment name"
                    },
                    "frontend_name": {
                        "type": "string",
                        "description": "Frontend deployment name"
                    },
                },
                "required": ["backend_name", "frontend_name"]
            }
        ),
        Tool(
            name="get_deployment_status",
            description="""Check the status and details of a deployment.

Returns current state, URLs, and resource information.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_name": {
                        "type": "string",
                        "description": "Name of deployment to check"
                    },
                },
                "required": ["deployment_name"]
            }
        ),
        Tool(
            name="estimate_deployment_cost",
            description="""Estimate monthly AWS costs for a deployment.

Shows breakdown of EC2, S3, and data transfer costs.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_name": {
                        "type": "string",
                        "description": "Deployment name"
                    },
                },
                "required": ["deployment_name"]
            }
        ),
    ]
    
    print(f"✅ Returning {len(tools)} tools", file=sys.stderr)
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Execute a tool with given arguments"""
    
    try:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"🔧 TOOL CALLED: {name}", file=sys.stderr)
        print(f"📝 Arguments:", file=sys.stderr)
        print(json.dumps(arguments, indent=2), file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        
        result = None
        
        if name == "deploy_backend_to_ec2":
            result = await deploy_backend_to_ec2(**arguments)
            
        elif name == "deploy_frontend_to_s3":
            result = await deploy_frontend_to_s3(**arguments)
            
        elif name == "connect_services":
            result = await connect_services(**arguments)
            
        elif name == "setup_nginx_proxy":
            result = await setup_nginx_proxy(**arguments)
            
        elif name == "create_autoscaling_group":
            result = await create_autoscaling_group(**arguments)
            
        elif name == "estimate_deployment_cost":
            result = await estimate_deployment_cost(**arguments)
            
        elif name == "get_deployment_status":
            result = await get_deployment_status(**arguments)
            
        else:
            result = {"error": f"Unknown tool: {name}", "success": False}
        
        print(f"\n✅ TOOL COMPLETED: {name}", file=sys.stderr)
        print(f"Result preview: {str(result)[:200]}...", file=sys.stderr)
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        print(f"\n❌ ERROR: {error_msg}", file=sys.stderr)
        
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def main():
    """Run the MCP server using stdio transport"""
    
    print("\n🎯 Starting MCP server with stdio transport...", file=sys.stderr)
    print("📡 Waiting for connections from Claude Desktop...\n", file=sys.stderr)
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            print("✅ Connected! Processing requests...\n", file=sys.stderr)
            
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"\n\n❌ Server error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!", file=sys.stderr)