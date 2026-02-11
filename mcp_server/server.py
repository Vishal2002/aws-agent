"""
AWS Deployment Agent - MCP Server
"""

import asyncio
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

from .tools import (
    deploy_backend_to_ec2,
    deploy_frontend_to_s3,
    connect_services,
    setup_nginx_proxy,
    create_autoscaling_group,
    estimate_deployment_cost,
    get_deployment_status,
)

# Initialize MCP server
app = Server("aws-deployment-agent")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return [
        Tool(
            name="deploy_backend_to_ec2",
            description="""Deploy backend to EC2. Supports Node.js and Python apps. Instance types: t2.micro ($8/mo, FREE TIER), t2.small ($17/mo), t3.medium ($30/mo).""",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_url": {"type": "string", "description": "GitHub repository URL"},
                    "name": {"type": "string", "description": "Deployment name"},
                    "instance_type": {"type": "string", "default": "t2.micro"},
                    "port": {"type": "integer", "default": 3000},
                },
                "required": ["repo_url", "name"]
            }
        ),
        Tool(
            name="deploy_frontend_to_s3",
            description="""Deploy frontend to S3 static hosting. Supports React, Vue, Next.js. Auto-builds and uploads.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_url": {"type": "string"},
                    "name": {"type": "string"},
                    "build_command": {"type": "string", "default": "npm run build"},
                    "backend_url": {"type": "string", "description": "Optional backend API URL"},
                },
                "required": ["repo_url", "name"]
            }
        ),
        Tool(
            name="connect_services",
            description="""Connect backend and frontend deployments. Updates CORS and environment variables.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "backend_name": {"type": "string"},
                    "frontend_name": {"type": "string"},
                },
                "required": ["backend_name", "frontend_name"]
            }
        ),
        Tool(
            name="get_deployment_status",
            description="""Check status and details of a deployment.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_name": {"type": "string"},
                },
                "required": ["deployment_name"]
            }
        ),
        Tool(
            name="estimate_deployment_cost",
            description="""Estimate monthly AWS costs for a deployment.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_name": {"type": "string"},
                },
                "required": ["deployment_name"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Execute tool"""
    
    try:
        print(f"\n🔧 Calling tool: {name}")
        print(f"   Arguments: {json.dumps(arguments, indent=2)}")
        
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
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        error_msg = f"❌ Error in {name}: {str(e)}"
        print(error_msg)
        return [TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}))]


async def main():
    """Run MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())