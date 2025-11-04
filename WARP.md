# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Vanna 2.0 implementation - an AI-powered text-to-SQL system using Azure OpenAI and PostgreSQL. The app translates natural language queries into SQL, executes them against a PostgreSQL database (AdventureWorksDW), and returns results.

## Architecture

**Three-Component System:**
1. **Azure OpenAI (LLM)**: Generates SQL from natural language using gpt-4o deployment
2. **Data Source (PostgreSQL)**: Your business database where Vanna executes queries (AdventureWorksDW)
3. **Vanna Storage**: Optional persistent conversation storage (defaults to in-memory)

**Key Design:**
- Agent-based architecture using Vanna 2.0 framework
- Custom Azure OpenAI integration (`AzureOpenAILlmService`) that extends Vanna's base `LlmService`
- Tool Registry pattern with `RunSqlTool` for SQL execution
- FastAPI server with built-in web interface
- Cookie-based user authentication with role-based access control

## Common Commands

### Development
```powershell
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Test database and Azure OpenAI connections
python test_connections.py
```

### Docker
```powershell
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after code changes
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Execute commands inside container
docker-compose exec vanna-app bash
```

### Access
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Environment Configuration

Required environment variables in `.env`:

**Azure OpenAI:**
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION` (default: 2024-06-01)
- `AZURE_OPENAI_DEPLOYMENT_NAME` (default: gpt-4o)

**Data Source (PostgreSQL):**
- `DATA_SOURCE_HOST`
- `DATA_SOURCE_PORT` (default: 5432)
- `DATA_SOURCE_DB`
- `DATA_SOURCE_USER`
- `DATA_SOURCE_PASSWORD`

**Optional Persistent Storage:**
- `USE_PERSISTENT_STORAGE` (true/false, default: false)
- If true, also set: `VANNA_STORAGE_HOST`, `VANNA_STORAGE_PORT`, `VANNA_STORAGE_DB`, `VANNA_STORAGE_USER`, `VANNA_STORAGE_PASSWORD`

## Code Structure

### `main.py`
FastAPI application entry point that:
- Initializes Azure OpenAI LLM service
- Configures PostgreSQL runner for data source
- Registers tools (RunSqlTool) with access control
- Sets up conversation store (memory or persistent)
- Creates Vanna Agent with all components
- Starts FastAPI server

### `azure_openai_llm.py`
Custom LLM service implementation:
- Extends `vanna.core.llm.LlmService`
- Implements `send_request()` for non-streaming requests
- Implements `stream_request()` for streaming responses
- Handles tool call extraction and formatting for Azure OpenAI API
- Manages message formatting and payload building

### `test_connections.py`
Diagnostic script to verify:
- PostgreSQL database connectivity
- Azure OpenAI deployment access

## Important Notes

### Custom Azure OpenAI Integration
Vanna 2.0 doesn't natively support Azure OpenAI, so this project uses a custom `AzureOpenAILlmService` that implements the Vanna `LlmService` interface. When modifying LLM behavior, edit `azure_openai_llm.py`.

### Database Roles
- **Data Source**: The PostgreSQL database that users query (contains business data)
- **Vanna Storage**: Optional separate database for storing conversations and metadata (defaults to in-memory)

### User Authentication
Uses `SimpleUserResolver` that extracts user_id and role from cookies. Roles map to access groups:
- `analyst` role → `read_sales` group
- Other roles → `admin` group

### Tool Access Control
`RunSqlTool` is registered with access groups `["read_sales", "admin"]`. Only users in these groups can execute SQL queries.

### Vanna 2.0 Installation
Requirements install Vanna 2.0 directly from GitHub (`git+https://github.com/vanna-ai/vanna.git@v2`), not from PyPI, as v2 is not yet released.
