"""EC2 Deployment Engine"""
import time
import asyncio
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError


class EC2Deployer:
    """Handles EC2 instance deployment and management"""
    
    # Cost estimates (USD/month) - accurate as of 2024
    INSTANCE_COSTS = {
        "t2.nano": 4.25,
        "t2.micro": 8.47,
        "t2.small": 16.79,
        "t2.medium": 33.58,
        "t3.nano": 3.80,
        "t3.micro": 7.59,
        "t3.small": 15.18,
        "t3.medium": 30.37,
        "t3.large": 60.74,
    }
    
    # Ubuntu 24.04 LTS AMIs by region (update these!)
    AMIS = {
        "us-east-1": "ami-0c7217cdde317cfec",
        "us-east-2": "ami-0ea3c35c5c3284d82",
        "us-west-1": "ami-0d5ae304a0b933620",
        "us-west-2": "ami-0aff18ec83b712f05",
        "eu-west-1": "ami-0d64bb532e0502c46",
        "eu-central-1": "ami-0084a47cc718c111a",
    }
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.ec2 = boto3.client('ec2', region_name=region)
        self.ec2_resource = boto3.resource('ec2', region_name=region)
    
    def create_security_group(self, name: str, ports: List[int]) -> str:
        """Create security group with specified ports open"""
        
        try:
            # Get default VPC
            vpcs = self.ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
            vpc_id = vpcs['Vpcs'][0]['VpcId']
            
            response = self.ec2.create_security_group(
                GroupName=name,
                Description=f'Security group for {name}',
                VpcId=vpc_id,
                TagSpecifications=[{
                    'ResourceType': 'security-group',
                    'Tags': [
                        {'Key': 'Name', 'Value': name},
                        {'Key': 'ManagedBy', 'Value': 'aws-agent'}
                    ]
                }]
            )
            
            sg_id = response['GroupId']
            
            # Wait a bit for the security group to be available
            time.sleep(2)
            
            # Add ingress rules
            ip_permissions = []
            for port in ports:
                ip_permissions.append({
                    'IpProtocol': 'tcp',
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': f'Allow port {port}'}]
                })
            
            if ip_permissions:
                self.ec2.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=ip_permissions
                )
            
            return sg_id
            
        except ClientError as e:
            if 'already exists' in str(e):
                # Security group exists, get its ID
                groups = self.ec2.describe_security_groups(
                    Filters=[{'Name': 'group-name', 'Values': [name]}]
                )
                return groups['SecurityGroups'][0]['GroupId']
            raise
    
    def generate_user_data_nodejs(self, repo_url: str, port: int) -> str:
        """Generate user data script for Node.js application"""
        
        return f"""#!/bin/bash
set -e

# Logging
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "Starting deployment at $(date)"

# Update system
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs git build-essential

# Verify installation
node --version
npm --version

# Clone repository
cd /home/ubuntu
rm -rf app
git clone {repo_url} app
cd app

# Install dependencies
npm install --production

# Create environment file
cat > .env <<EOF
PORT={port}
NODE_ENV=production
EOF

# Create systemd service
cat > /etc/systemd/system/app.service <<EOF
[Unit]
Description=Backend Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/app
Environment=PORT={port}
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
chown -R ubuntu:ubuntu /home/ubuntu/app

# Start service
systemctl daemon-reload
systemctl enable app
systemctl start app

# Wait and check status
sleep 10
systemctl status app --no-pager

echo "Deployment completed at $(date)"
"""
    
    def generate_user_data_python(self, repo_url: str, port: int) -> str:
        """Generate user data script for Python application"""
        
        return f"""#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "Starting Python deployment at $(date)"

# Update and install Python
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
apt-get install -y python3 python3-pip python3-venv git

# Clone repository
cd /home/ubuntu
rm -rf app
git clone {repo_url} app
cd app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/app.service <<EOF
[Unit]
Description=Python Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/app
Environment=PORT={port}
ExecStart=/home/ubuntu/app/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

chown -R ubuntu:ubuntu /home/ubuntu/app

systemctl daemon-reload
systemctl enable app
systemctl start app

sleep 10
systemctl status app --no-pager

echo "Python deployment completed at $(date)"
"""
    
    def launch_instance(
        self,
        name: str,
        instance_type: str,
        security_group_id: str,
        user_data: str
    ) -> Dict:
        """Launch EC2 instance"""
        
        ami_id = self.AMIS.get(self.region)
        if not ami_id:
            raise ValueError(f"No AMI configured for region {self.region}")
        
        response = self.ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[security_group_id],
            UserData=user_data,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': name},
                    {'Key': 'ManagedBy', 'Value': 'aws-agent'}
                ]
            }],
            # Enable detailed monitoring for better metrics
            Monitoring={'Enabled': True}
        )
        
        return response['Instances'][0]
    
    async def wait_for_instance(self, instance_id: str, timeout: int = 600) -> str:
        """Wait for instance to be running and return public IP"""
        
        print(f"⏳ Waiting for instance {instance_id} to start...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            instance = response['Reservations'][0]['Instances'][0]
            
            state = instance['State']['Name']
            print(f"   Instance state: {state}")
            
            if state == 'running':
                public_ip = instance.get('PublicIpAddress')
                if public_ip:
                    print(f"✓ Instance running at {public_ip}")
                    print(f"⏳ Waiting 60s for application to start...")
                    # Give user data script time to run
                    await asyncio.sleep(60)
                    return public_ip
            
            await asyncio.sleep(10)
        
        raise TimeoutError(f"Instance {instance_id} did not start within {timeout}s")
    
    def estimate_cost(self, instance_type: str) -> float:
        """Estimate monthly cost for instance type"""
        return self.INSTANCE_COSTS.get(instance_type, 0.0)
    
    def get_instance_info(self, instance_id: str) -> Dict:
        """Get current instance information"""
        
        response = self.ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        
        return {
            'instance_id': instance_id,
            'state': instance['State']['Name'],
            'public_ip': instance.get('PublicIpAddress'),
            'instance_type': instance['InstanceType'],
            'launch_time': instance['LaunchTime'].isoformat()
        }