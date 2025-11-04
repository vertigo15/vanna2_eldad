# Vanna 2.0 with Azure OpenAI & PostgreSQL

This project implements [Vanna 2.0](https://github.com/vanna-ai/vanna) - an AI-powered text-to-SQL system using Azure OpenAI and PostgreSQL.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  VANNA 2.0 APP                      │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │  1. Azure OpenAI (LLM)                      │  │
│  │     - Generates SQL from natural language   │  │
│  │     - gpt-4o deployment                     │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │  2. Data Source (PostgreSQL) ⭐ MAIN        │  │
│  │     - Your business database                │  │
│  │     - AdventureWorksDW                      │  │
│  │     - Vanna executes SQL queries here       │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │  3. Vanna Storage (Optional)                │  │
│  │     - In-memory (default) OR                │  │
│  │     - PostgreSQL for persistence            │  │
│  │     - Stores: conversations, metadata       │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Azure OpenAI subscription
- PostgreSQL database access

## 🚀 Quick Start

### 1. Environment Setup

Copy the `.env.template` file (if available) or create `.env`:

```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-06-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Data Source (Your business database)
DATA_SOURCE_HOST=your-pg-host.postgres.database.azure.com
DATA_SOURCE_PORT=5432
DATA_SOURCE_DB=AdventureWorksDW
DATA_SOURCE_USER=your_user
DATA_SOURCE_PASSWORD=your_password

# Vanna Storage (Optional)
USE_PERSISTENT_STORAGE=false

# App Config
PORT=8000
LOG_LEVEL=info
```

### 2. Test Connections (Optional)

```bash
pip install psycopg2-binary openai python-dotenv
python test_connections.py
```

### 3. Run with Docker

```bash
docker-compose up -d
```

The app will be available at: `http://localhost:8000`

### 4. Run Locally (Development)

```bash
pip install -r requirements.txt
python main.py
```

## 🔍 Key Components

### `main.py`
- FastAPI application
- Vanna 2.0 Agent configuration
- Azure OpenAI integration
- PostgreSQL runner setup
- User authentication resolver

### `docker-compose.yml`
- Docker service configuration
- Environment variable mapping
- Network and volume setup

### `Dockerfile`
- Python 3.11 slim base
- PostgreSQL client libraries
- Security: non-root user
- Health checks

### `test_connections.py`
- PostgreSQL connection test
- Azure OpenAI deployment test

## 🔧 Configuration

### Azure OpenAI
- Uses Azure OpenAI service for LLM capabilities
- Configured for `gpt-4o` deployment
- API version: `2024-06-01`

### PostgreSQL
- **Data Source**: Main database for user queries
- **Vanna Storage**: Optional persistent conversation storage
- Default: In-memory storage (no additional DB needed)

### Vanna 2.0 Features
- **Agent-based architecture**: Uses tools and LLM for text-to-SQL
- **Tool Registry**: `RunSqlTool` for executing SQL queries
- **User Resolver**: Simple cookie-based user authentication
- **Conversation Store**: Memory or PostgreSQL-backed
- **FastAPI Server**: Built-in web interface

## 🔐 Security Notes

- `.env` file is gitignored (contains sensitive credentials)
- Docker runs as non-root user (`vanna`)
- Azure OpenAI keys should be rotated regularly
- Use managed identities in production

## 🐛 Troubleshooting

### PostgreSQL Connection Failed
- Verify `DATA_SOURCE_*` environment variables
- Check firewall rules for Azure PostgreSQL
- Ensure IP address is whitelisted

### Azure OpenAI DeploymentNotFound
- Verify `AZURE_OPENAI_DEPLOYMENT_NAME` matches your Azure deployment
- Check deployment is in the correct region
- Confirm API key has access to the deployment

### Docker Build Issues
- Ensure Docker daemon is running
- Check network connectivity for `pip install`
- Try `docker-compose build --no-cache`

## 📚 Resources

- [Vanna 2.0 Documentation](https://vanna.ai/docs/)
- [Vanna GitHub](https://github.com/vanna-ai/vanna)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

## 📝 License

MIT (follows Vanna's license)
