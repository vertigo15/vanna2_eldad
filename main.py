import os
from dotenv import load_dotenv
from vanna import Agent, AgentConfig
from vanna.servers.fastapi import VannaFastAPIServer
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool
from vanna.integrations.postgres import PostgresRunner
import logging

# Load environment variables
load_dotenv()

# Custom Azure OpenAI integration
from azure_openai_llm import AzureOpenAILlmService
from knowledge_base import get_knowledge_base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User resolver
class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        user_id = request_context.get_cookie('user_id') or 'demo_user'
        role = request_context.get_cookie('role') or 'analyst'
        
        groups = ['read_sales'] if role == 'analyst' else ['admin']
        return User(id=user_id, group_memberships=groups)

# ============================================
# 1. AZURE OPENAI - For AI/LLM capabilities
# ============================================
azure_openai_config = {
    'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
    'azure_endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
    'api_version': os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
    'deployment_name': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
}

llm = AzureOpenAILlmService(
    api_key=azure_openai_config['api_key'],
    model=azure_openai_config['deployment_name'],
    azure_endpoint=azure_openai_config['azure_endpoint'],
    api_version=azure_openai_config['api_version']
)

logger.info(f"✓ Azure OpenAI configured: {azure_openai_config['deployment_name']}")

# ============================================
# 2. DATA SOURCE - Your business database that users will query
# ============================================
data_source_config = {
    'host': os.getenv('DATA_SOURCE_HOST'),          # Your data database
    'port': int(os.getenv('DATA_SOURCE_PORT', 5432)),
    'database': os.getenv('DATA_SOURCE_DB'),        # e.g., 'sales_db'
    'user': os.getenv('DATA_SOURCE_USER'),
    'password': os.getenv('DATA_SOURCE_PASSWORD'),
}

postgres_runner = PostgresRunner(**data_source_config)

logger.info(f"✓ Data source configured: {data_source_config['host']}/{data_source_config['database']}")

# ============================================
# 3. Register tools
# ============================================
tools = ToolRegistry()
run_sql_tool = RunSqlTool(sql_runner=postgres_runner)
tools.register_local_tool(run_sql_tool, access_groups=["read_sales", "admin"])

logger.info("✓ Tools registered")

# ============================================
# 4. OPTIONAL: Vanna storage for conversations
# (Uses in-memory by default, can use PostgreSQL for persistence)
# ============================================
use_persistent_storage = os.getenv('USE_PERSISTENT_STORAGE', 'false').lower() == 'true'

if use_persistent_storage:
    try:
        from vanna.integrations.postgres import PostgresConversationStore
        
        vanna_storage_config = {
            'host': os.getenv('VANNA_STORAGE_HOST'),
            'port': int(os.getenv('VANNA_STORAGE_PORT', 5432)),
            'database': os.getenv('VANNA_STORAGE_DB'),
            'user': os.getenv('VANNA_STORAGE_USER'),
            'password': os.getenv('VANNA_STORAGE_PASSWORD'),
        }
        
        conversation_store = PostgresConversationStore(**vanna_storage_config)
        logger.info(f"✓ Persistent storage configured: {vanna_storage_config['host']}")
    except ImportError:
        from vanna.integrations.local import MemoryConversationStore
        conversation_store = MemoryConversationStore()
        logger.warning("⚠ PostgresConversationStore not available, using in-memory storage")
else:
    from vanna.integrations.local import MemoryConversationStore
    conversation_store = MemoryConversationStore()
    logger.info("✓ Using in-memory conversation storage")

# ============================================
# 5. Create agent
# ============================================
config = AgentConfig(
    max_tool_iterations=10,
    stream_responses=True,
    temperature=0.7,
)

agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=SimpleUserResolver(),
    conversation_store=conversation_store,
    config=config
)

# ============================================
# 6. Load Knowledge Base (Training Data)
# ============================================
try:
    kb = get_knowledge_base()
    logger.info(f"✓ Knowledge base loaded and cached: {kb.get_stats()}")
    logger.info(f"✓ System context ready ({len(kb.get_system_context())} chars)")
except Exception as e:
    logger.warning(f"⚠ Could not load knowledge base: {e}")
    kb = None

# Create server
server = VannaFastAPIServer(agent)
app = server.create_app()

logger.info("✓ Vanna 2.0 application started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)