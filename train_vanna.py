import os
import json
from pathlib import Path
from dotenv import load_dotenv
from vanna import Agent, AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool
from vanna.integrations.postgres import PostgresRunner
try:
    from vanna.integrations.postgres import PostgresConversationStore
except ImportError:
    PostgresConversationStore = None
import logging

# Load environment variables
load_dotenv()

# Custom Azure OpenAI integration
from azure_openai_llm import AzureOpenAILlmService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User resolver for training
class TrainingUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(id='training_user', group_memberships=['admin'])

# ============================================
# Initialize Agent (same as main.py)
# ============================================

# Setup Azure OpenAI
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

# Setup data source
data_source_config = {
    'host': os.getenv('DATA_SOURCE_HOST'),
    'port': int(os.getenv('DATA_SOURCE_PORT', 5432)),
    'database': os.getenv('DATA_SOURCE_DB'),
    'user': os.getenv('DATA_SOURCE_USER'),
    'password': os.getenv('DATA_SOURCE_PASSWORD'),
}

postgres_runner = PostgresRunner(**data_source_config)
logger.info(f"✓ Data source configured: {data_source_config['host']}/{data_source_config['database']}")

# Register tools
tools = ToolRegistry()
run_sql_tool = RunSqlTool(sql_runner=postgres_runner)
tools.register_local_tool(run_sql_tool, access_groups=["admin"])

# Setup persistent storage (recommended for training)
use_persistent_storage = os.getenv('USE_PERSISTENT_STORAGE', 'false').lower() == 'true'

if use_persistent_storage and PostgresConversationStore is not None:
    vanna_storage_config = {
        'host': os.getenv('VANNA_STORAGE_HOST'),
        'port': int(os.getenv('VANNA_STORAGE_PORT', 5432)),
        'database': os.getenv('VANNA_STORAGE_DB'),
        'user': os.getenv('VANNA_STORAGE_USER'),
        'password': os.getenv('VANNA_STORAGE_PASSWORD'),
    }
    conversation_store = PostgresConversationStore(**vanna_storage_config)
    logger.info(f"✓ Persistent storage configured: {vanna_storage_config['host']}/{vanna_storage_config['database']}")
else:
    from vanna.integrations.local import MemoryConversationStore
    conversation_store = MemoryConversationStore()
    if use_persistent_storage:
        logger.warning("⚠ PostgresConversationStore not available, using in-memory storage")
    else:
        logger.warning("⚠ Using in-memory storage - training data will be lost on restart!")

# Create agent
config = AgentConfig(
    max_tool_iterations=10,
    stream_responses=False,
    temperature=0.7,
)

agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=TrainingUserResolver(),
    conversation_store=conversation_store,
    config=config
)

logger.info("✓ Agent initialized for training")

# ============================================
# Training Functions
# ============================================

TRAINING_DATA_DIR = Path(__file__).parent / "training_data"

def load_json_file(filename):
    """Load JSON file from training_data directory"""
    filepath = TRAINING_DATA_DIR / filename
    if not filepath.exists():
        logger.warning(f"⚠ File not found: {filepath}")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def train_database_schema():
    """Train with database schema (DDL)"""
    logger.info("📊 Training database schema...")
    data = load_json_file("schema.json")
    
    if not data:
        logger.warning("⚠ Skipping schema training - file not found")
        return
    
    count = 0
    for table in data.get('tables', []):
        agent.train(ddl=table['ddl'])
        logger.info(f"  ✓ Trained table: {table['name']}")
        count += 1
    
    logger.info(f"✓ Schema training complete: {count} tables\n")

def train_example_queries():
    """Train with question-SQL pairs"""
    logger.info("💬 Training question-SQL pairs...")
    data = load_json_file("queries.json")
    
    if not data:
        logger.warning("⚠ Skipping queries training - file not found")
        return
    
    count = 0
    for item in data.get('question_sql_pairs', []):
        agent.train(
            question=item['question'],
            sql=item['sql']
        )
        logger.info(f"  ✓ Trained: {item['question'][:60]}...")
        count += 1
    
    logger.info(f"✓ Queries training complete: {count} examples\n")

def train_business_context():
    """Train with business documentation"""
    logger.info("📚 Training business context...")
    data = load_json_file("documentation.json")
    
    if not data:
        logger.warning("⚠ Skipping documentation training - file not found")
        return
    
    count = 0
    # Train business terms
    for item in data.get('business_terms', []):
        doc = f"{item['term']}: {item['definition']}"
        agent.train(documentation=doc)
        logger.info(f"  ✓ Trained term: {item['term']}")
        count += 1
    
    # Train business rules
    for item in data.get('business_rules', []):
        doc = f"{item['rule']}: {item['description']}"
        agent.train(documentation=doc)
        logger.info(f"  ✓ Trained rule: {item['rule']}")
        count += 1
    
    logger.info(f"✓ Documentation training complete: {count} items\n")

def train_sql_patterns():
    """Train with common SQL patterns"""
    logger.info("🔧 Training SQL patterns...")
    data = load_json_file("sql_patterns.json")
    
    if not data:
        logger.warning("⚠ Skipping SQL patterns training - file not found")
        return
    
    count = 0
    for item in data.get('common_queries', []):
        agent.train(sql=item['sql'])
        logger.info(f"  ✓ Trained pattern: {item['description']}")
        count += 1
    
    logger.info(f"✓ SQL patterns training complete: {count} patterns\n")

def train_data_samples():
    """Train with data samples"""
    logger.info("📋 Training data samples...")
    data = load_json_file("samples.json")
    
    if not data:
        logger.warning("⚠ Skipping samples training - file not found")
        return
    
    count = 0
    for item in data.get('data_samples', []):
        # Format examples as documentation
        examples_text = f"Sample data from {item['table']}:\n"
        examples_text += json.dumps(item['examples'], indent=2)
        agent.train(documentation=examples_text)
        logger.info(f"  ✓ Trained samples: {item['table']}")
        count += 1
    
    logger.info(f"✓ Data samples training complete: {count} tables\n")

def run_all_training():
    """Run all training steps"""
    print("\n" + "="*60)
    print("🚀 VANNA 2.0 TRAINING STARTED")
    print("="*60 + "\n")
    
    # Train in priority order
    train_database_schema()      # CRITICAL
    train_example_queries()       # CRITICAL
    train_business_context()      # IMPORTANT
    train_sql_patterns()          # OPTIONAL
    train_data_samples()          # OPTIONAL
    
    print("="*60)
    print("✅ ALL TRAINING COMPLETE!")
    print("="*60)
    
    if use_persistent_storage:
        print(f"\n📦 Training data saved to: {vanna_storage_config['host']}/{vanna_storage_config['database']}")
    else:
        print("\n⚠ WARNING: In-memory storage - restart app to lose training data")
    
    print("\n🎯 Next step: python main.py")

if __name__ == "__main__":
    run_all_training()
