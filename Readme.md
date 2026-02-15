# 🤖 AWS Deployment Agent

> Deploy AWS infrastructure with natural language using AI-powered MCP agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Built with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for the Archestra Hackathon 2026.

---

## ✨ What It Does

Transform this:
```
You: "Deploy my React + Express app to AWS"
```

Into this:
```
✓ Backend deployed to EC2 (http://54.123.45.67:3000)
✓ Frontend deployed to S3 (http://my-app.s3-website.amazonaws.com)
✓ Services connected
✓ Auto-scaling configured
💰 Total cost: $8.50/month
```

**No YAML. No Terraform. No clicking through 47 AWS console pages.**

---

## 🎯 Features

- 🗣️ **Natural Language Interface** - Describe what you want, get infrastructure
- 🔧 **MCP-Based Architecture** - Protocol-compliant, works with any MCP client
- ☁️ **Multi-Service Support** - EC2, S3, VPC, Auto-Scaling
- 💰 **Cost Aware** - Estimates costs before deploying
- 🐳 **Docker Ready** - One-command setup
- 🔒 **Secure** - Credentials never leave your machine
- 📊 **Observable** - Track all deployments

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- AWS Account with credentials
- [Claude Desktop](https://claude.ai/download) (or Archestra)

### 1. Clone & Configure
```bash
git clone https://github.com/yourusername/aws-agent.git
cd aws-agent

# Copy environment template
cp .env.example .env

# Edit .env with your AWS credentials
nano .env
```

### 2. Build Docker Image
```bash
# Using Make (easiest)
make build

# Or using Docker directly
docker build -t aws-deployment-agent .
```

### 3. Test the Setup
```bash
make test
```

Should output:
```
✅ Config loaded
Region: us-east-1
```

### 4. Configure Claude Desktop

**Mac/Linux:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
notepad %APPDATA%\Claude\claude_desktop_config.json
```

**Add this configuration:**
```json
{
  "mcpServers": {
    "aws-deployment-agent": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/FULL/PATH/TO/YOUR/aws-agent/.env",
        "aws-deployment-agent"
      ]
    }
  }
}
```

⚠️ **IMPORTANT:** Replace `/FULL/PATH/TO/YOUR/aws-agent/` with your actual path!

Get your full path:
```bash
cd /path/to/aws-agent
pwd
```

### 5. Start Using!

1. **Restart Claude Desktop** completely (Cmd+Q or Alt+F4)
2. **Look for 🔌 icon** in bottom-right corner
3. **Start deploying!**
```
You: "Deploy my Express backend at github.com/user/backend"

Claude: I'll deploy your Express backend to AWS EC2...
[Deploys in 2 minutes]
Your backend is live at http://3.21.45.67:3000
```

---

## 📖 Usage Examples

### Deploy Backend Only
```
Deploy my Node.js API at github.com/myuser/backend to AWS
```

### Deploy Full-Stack App
```
I have a React frontend at github.com/user/frontend and 
Express backend at github.com/user/backend. 
Deploy both and connect them.
```

### Check Deployment Status
```
What's the status of my backend deployment?
```

### Estimate Costs
```
How much is my deployment costing per month?
```

### Cost-Optimized Deployment
```
Deploy my side project as cheaply as possible
```

---

## 🏗️ Architecture
```
┌─────────────────────────────────────┐
│   User (Natural Language)           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Claude Desktop / Archestra        │
│   (MCP Client)                      │
└──────────────┬──────────────────────┘
               │ MCP Protocol
┌──────────────▼──────────────────────┐
│   MCP Server (Docker)               │
│   • deploy_backend_to_ec2()         │
│   • deploy_frontend_to_s3()         │
│   • connect_services()              │
│   • estimate_costs()                │
└──────────────┬──────────────────────┘
               │ boto3 (AWS SDK)
┌──────────────▼──────────────────────┐
│   AWS Cloud                         │
│   EC2 • S3 • VPC • Auto-Scaling     │
└─────────────────────────────────────┘
```

---

## 🛠️ Available Tools

| Tool | Description | Cost |
|------|-------------|------|
| `deploy_backend_to_ec2` | Deploy Node.js/Python backends | ~$8/mo |
| `deploy_frontend_to_s3` | Deploy React/Vue/Angular apps | ~$0.50/mo |
| `connect_services` | Link frontend & backend | Free |
| `estimate_deployment_cost` | Calculate AWS costs | Free |
| `get_deployment_status` | Check deployment health | Free |

---

## 💰 Cost Estimates

| Resource | Configuration | Monthly Cost |
|----------|---------------|--------------|
| **t2.micro** | 1 vCPU, 1GB RAM | $8.47 (FREE TIER) |
| **t2.small** | 1 vCPU, 2GB RAM | $16.79 |
| **t3.medium** | 2 vCPU, 4GB RAM | $30.37 |
| **S3 Static** | 1GB storage | $0.50 |

**Typical full-stack app:** $8-15/month

---

## 🔑 AWS Credentials Setup

### Option 1: Environment Variables (Recommended)

Edit `.env`:
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
```

### Option 2: AWS CLI Credentials

If you have AWS CLI configured, Docker can use those:
```bash
# Check if AWS CLI is configured
aws configure list

# Docker will automatically use ~/.aws/credentials
```

### Getting AWS Credentials

1. **Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)**
2. **Create a new user** → Attach `AdministratorAccess` policy
3. **Create access key** → Download credentials
4. **Add to `.env` file**

### Minimum Required Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:DescribeInstances",
        "ec2:CreateSecurityGroup",
        "s3:CreateBucket",
        "s3:PutObject",
        "s3:PutBucketWebsite"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🐳 Docker Commands
```bash
# Build image
make build

# Start server
make run

# View logs
make logs

# Stop server
make stop

# Clean up everything
make clean

# Run tests
make test

# Get shell access
make shell
```

---

## 🔧 Troubleshooting

### MCP Server Not Connecting

**Check Docker is running:**
```bash
docker ps
```

**Check credentials are loaded:**
```bash
make test
```

**View logs:**
```bash
make logs
```

### "Operation not permitted" Error

This is a macOS security issue. Solutions:

1. **Use Docker** (recommended - bypasses the issue)
2. **Grant Full Disk Access** to Claude Desktop in System Settings

### Python Module Not Found

Make sure you're using the Docker setup:
```bash
make build
make run
```

### AWS Credentials Invalid

Test your credentials:
```bash
docker run --rm --env-file .env aws-deployment-agent \
  python -c "import boto3; print(boto3.client('sts').get_caller_identity())"
```

---

## 📚 Documentation

- [Detailed Setup Guide](docs/SETUP.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Creating Custom Tools](docs/CUSTOM_TOOLS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

## 🎥 Demo Video

[Watch the 3-minute demo](https://youtube.com/your-video)

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

### Add New Tools

1. Create tool in `mcp_server/tools/`
2. Add to `__init__.py`
3. Register in `server.py`
4. Test with Docker

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - The standard for AI tool integration
- [Anthropic](https://www.anthropic.com/) - For Claude AI
- [Archestra](https://archestra.ai/) - For the hackathon
- [AWS](https://aws.amazon.com/) - For cloud infrastructure

---

## 🏆 Built For

**Archestra Hackathon 2026** - Hack All February Series

---

## 📬 Contact

- **GitHub:** [@yourusername](https://github.com/yourusername)
- **Twitter:** [@yourusername](https://twitter.com/yourusername)
- **Email:** your.email@example.com

---

## ⭐ Star This Repo

If this helped you, give it a star! It helps others discover the project.

[⬆ Back to top](#-aws-deployment-agent)