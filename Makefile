.PHONY: build run stop clean help test

# Variables
IMAGE_NAME := aws-deployment-agent
CONTAINER_NAME := aws-deployment-agent

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker image
	@echo "🔨 Building Docker image..."
	docker build -t $(IMAGE_NAME) .
	@echo "✅ Build complete!"

run: ## Run the MCP server
	@echo "🚀 Starting MCP server..."
	docker-compose up -d
	@echo "✅ Server running! Use 'make logs' to view output."

stop: ## Stop the MCP server
	@echo "🛑 Stopping MCP server..."
	docker-compose down
	@echo "✅ Server stopped."

restart: stop run ## Restart the MCP server

logs: ## View server logs
	docker-compose logs -f

test: ## Test the Docker setup
	@echo "🧪 Testing Docker setup..."
	docker run --rm --env-file .env $(IMAGE_NAME) python -c "from mcp_server.config import settings; print('✅ Config loaded'); print(f'Region: {settings.aws_default_region}')"

clean: ## Remove Docker images and containers
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker rmi $(IMAGE_NAME) || true
	@echo "✅ Cleanup complete!"

shell: ## Open shell in container
	docker-compose exec aws-deployment-agent bash

setup: ## Initial setup (copy .env.example)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "📝 Created .env file. Please edit it with your AWS credentials."; \
	else \
		echo "⚠️  .env file already exists."; \
	fi