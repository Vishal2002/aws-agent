# Complete Setup Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- Docker Desktop 4.0+ ([Download](https://docs.docker.com/get-docker/))
- AWS Account ([Sign up](https://aws.amazon.com/free/))
- Claude Desktop ([Download](https://claude.ai/download))

### Optional
- Make (for convenience commands)
- Git (for cloning)

---

## Installation Methods

### Method 1: Docker (Recommended)

**Step 1: Clone Repository**
```bash
git clone https://github.com/Vishal2002/aws-agent.git
cd aws-agent
```

**Step 2: Configure Credentials**
```bash
cp .env.example .env
nano .env  # or use any text editor
```

Add your AWS credentials:
```
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_DEFAULT_REGION=us-east-1
```

**Step 3: Build & Test**
```bash
make build
make test
```

**Step 4: Configure Claude Desktop**

Find your full project path:
```bash
pwd
# Output: /Users/yourname/projects/aws-agent
```

Edit Claude config:
```bash
# Mac
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux  
nano ~/.config/Claude/claude_desktop_config.json

# Windows
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Add:
```json
{
  "mcpServers": {
    "aws-deployment-agent": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--env-file", "/FULL/PATH/FROM/STEP/ABOVE/.env",
        "aws-deployment-agent"
      ]
    }
  }
}
```

**Step 5: Restart Claude Desktop**

Completely quit and reopen. Look for 🔌 icon.

---

### Method 2: Manual (Without Docker)

**Step 1: Clone & Setup**
```bash
git clone https://github.com/Vishal2002/aws-agent.git
cd aws-agent
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Step 2: Configure**
```bash
cp .env.example .env
# Edit .env with your credentials
```

**Step 3: Test**
```bash
python -m mcp_server.server
# Should start without errors, press Ctrl+C
```

**Step 4: Configure Claude**
```json
{
  "mcpServers": {
    "aws-deployment-agent": {
      "command": "/FULL/PATH/TO/venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/FULL/PATH/TO/aws-agent",
      "env": {
        "PYTHONPATH": "/FULL/PATH/TO/aws-agent",
        "AWS_ACCESS_KEY_ID": "your_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret",
        "AWS_DEFAULT_REGION": "us-east-1"
      }
    }
  }
}
```

---

## Configuration

### AWS Credentials

#### Getting Credentials

1. Log into [AWS Console](https://console.aws.amazon.com/)
2. Navigate to IAM → Users
3. Create new user or select existing
4. Security Credentials tab → Create Access Key
5. Download and save securely

#### Free Tier Eligible

New AWS accounts get:
- 750 hours/month of t2.micro EC2 (first 12 months)
- 5GB S3 storage
- Perfect for this project!

### MCP Server Configuration

Default settings in `mcp_server/config.py`:
```python
aws_default_region = "us-east-1"
state_dir = "./deployments"
```

Override with environment variables:
```bash
AWS_DEFAULT_REGION=us-west-2
STATE_DIR=/custom/path
```

---

## Verification

### Test 1: Docker Build
```bash
make build
# Should complete without errors
```

### Test 2: Credentials
```bash
make test
# Should show: ✅ Config loaded
```

### Test 3: MCP Connection

1. Open Claude Desktop
2. Look for 🔌 icon (bottom-right)
3. Ask: "What tools do you have?"
4. Should list AWS deployment tools

### Test 4: Actual Deployment
```
You: "Deploy a test backend at github.com/frankhokevinho/simple-express-app"

Claude: [Should call deploy_backend_to_ec2 tool]
```

---

## Troubleshooting

### Docker Not Starting
```bash
# Check Docker is running
docker ps

# Check Docker version
docker --version  # Need 20.10+

# Restart Docker Desktop
```

### Credentials Not Loading
```bash
# Verify .env file
cat .env

# Test credentials directly
docker run --rm --env-file .env aws-deployment-agent \
  python -c "from mcp_server.config import settings; print(settings.aws_access_key_id)"
```

### Claude Desktop Not Connecting
```bash
# Check config file exists
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check path is correct (common mistake!)
# Path must be absolute: /Users/name/... not ~/...

# View Claude logs
tail -f ~/Library/Logs/Claude/mcp*.log
```

### Port Already in Use
```bash
# Find and kill process
lsof -i :3000
kill -9 <PID>
```

---

---

## Getting Help

- **GitHub Issues:** [Report a bug](https://github.com/Vishal2002/aws-agent/issues)
- **Email:** vishalsharma05052002@gmail.com