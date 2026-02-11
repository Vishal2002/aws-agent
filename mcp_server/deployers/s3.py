"""S3 Deployment Engine"""

import os
import subprocess
import mimetypes
import json
from pathlib import Path
from typing import Dict, Optional
import boto3
from botocore.exceptions import ClientError
from .utils import clone_repo, cleanup_temp_dir


class S3Deployer:
    """Handles S3 static website deployment"""

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.s3 = boto3.client("s3", region_name=region)

    def create_bucket(self, bucket_name: str) -> str:
        """Create S3 bucket with static website hosting"""

        try:
            if self.region == "us-east-1":
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": self.region},
                )

            # Enable static website hosting
            self.s3.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    "IndexDocument": {"Suffix": "index.html"},
                    "ErrorDocument": {"Key": "index.html"},
                },
            )

            # Set bucket ownership
            self.s3.put_bucket_ownership_controls(
                Bucket=bucket_name,
                OwnershipControls={
                    "Rules": [{"ObjectOwnership": "BucketOwnerEnforced"}]
                },
            )

            # Disable public access block
            self.s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": False,
                    "IgnorePublicAcls": False,
                    "BlockPublicPolicy": False,
                    "RestrictPublicBuckets": False,
                },
            )

            # Add bucket policy for public read
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    }
                ],
            }

            self.s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(policy),
            )

            # Add tags
            self.s3.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={
                    "TagSet": [
                        {"Key": "ManagedBy", "Value": "aws-agent"}
                    ]
                },
            )

            return bucket_name

        except ClientError as e:
            if "BucketAlreadyOwnedByYou" in str(e):
                return bucket_name
            raise

    def build_app(self, repo_path: Path, build_command: str) -> Path:
        """Build the frontend application"""

        print("📦 Installing dependencies...")

        if (repo_path / "package.json").exists():
            package_json_path = repo_path / "package.json"

            with open(package_json_path, "r") as f:
                package_data = json.load(f)

            # Remove homepage field if exists
            if "homepage" in package_data:
                old_homepage = package_data["homepage"]
                print(f"   ⚠️  Found homepage: {old_homepage}")
                print("   Removing it for S3 deployment...")
                del package_data["homepage"]

                with open(package_json_path, "w") as f:
                    json.dump(package_data, f, indent=2)

            # Install dependencies
            result = subprocess.run(
                ["npm", "install"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"⚠️  npm install warnings: {result.stderr}")

        print("🔨 Building application...")

        env = os.environ.copy()
        env["PUBLIC_URL"] = "/"
        env["GENERATE_SOURCEMAP"] = "false"

        result = subprocess.run(
            build_command.split(),
            cwd=repo_path,
            capture_output=True,
            text=True,
            env=env,
        )

        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            raise subprocess.CalledProcessError(
                result.returncode, build_command, result.stderr
            )

        possible_build_dirs = ["build", "dist", "out", ".next/out", "public"]
        build_dir = None

        for dir_name in possible_build_dirs:
            potential_dir = repo_path / dir_name
            if potential_dir.exists() and (potential_dir / "index.html").exists():
                build_dir = potential_dir
                print(f"✓ Found build output: {dir_name}/")
                break

        if not build_dir:
            dirs = [d.name for d in repo_path.iterdir() if d.is_dir()]
            print(f"⚠️  Available directories: {dirs}")
            raise ValueError(
                f"Could not find build directory with index.html. "
                f"Looked in: {possible_build_dirs}"
            )

        # Fix incorrect paths if needed
        index_html = build_dir / "index.html"
        with open(index_html, "r") as f:
            html_content = f.read()

        if "/simple-reactjs-app/" in html_content:
            print("⚠️  Fixing paths in index.html...")
            html_content = html_content.replace(
                "/simple-reactjs-app/", "/"
            )
            with open(index_html, "w") as f:
                f.write(html_content)
            print("✓ Paths fixed!")

        file_count = sum(
            1 for _ in build_dir.rglob("*") if _.is_file()
        )
        print(f"✓ Build contains {file_count} files")

        print("\n📂 What will be uploaded:")
        items = sorted(build_dir.iterdir())[:8]

        for item in items:
            if item.is_dir():
                print(f"   📁 {item.name}/")
            else:
                size_kb = item.stat().st_size / 1024
                print(f"   📄 {item.name} ({size_kb:.1f}KB)")

        if len(list(build_dir.iterdir())) > 8:
            print(
                f"   ... and {len(list(build_dir.iterdir())) - 8} more items"
            )

        return build_dir

    def upload_directory(self, local_path: Path, bucket_name: str) -> int:
        """Upload directory contents to S3 root (no nested folder)"""

        file_count = 0
        print("\n📤 Uploading to S3...")

        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file = Path(root) / file
                relative_path = local_file.relative_to(local_path)
                s3_key = str(relative_path).replace("\\", "/")

                content_type, _ = mimetypes.guess_type(str(local_file))
                if content_type is None:
                    content_type = "application/octet-stream"

                self.s3.upload_file(
                    str(local_file),
                    bucket_name,
                    s3_key,
                    ExtraArgs={"ContentType": content_type},
                )

                file_count += 1

                if file_count <= 5:
                    print(f"   ✓ {s3_key}")

        if file_count > 5:
            print(f"   ✓ ... and {file_count - 5} more files")

        print(f"\n✓ Uploaded {file_count} files to bucket root")

        return file_count

    def get_website_url(self, bucket_name: str) -> str:
        """Get the website URL for a bucket"""

        if self.region == "us-east-1":
            return (
                f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com"
            )

        return (
            f"http://{bucket_name}.s3-website-{self.region}.amazonaws.com"
        )

    def estimate_cost(self, storage_gb: float = 1.0) -> float:
        """Estimate monthly S3 costs"""

        storage_cost = storage_gb * 0.023
        request_cost = 0.01
        return storage_cost + request_cost
