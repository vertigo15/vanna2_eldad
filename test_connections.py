import os
import psycopg2
from openai import AzureOpenAI

def test_postgres():
    """Test PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATA_SOURCE_HOST'),
            port=os.getenv('DATA_SOURCE_PORT'),
            database=os.getenv('DATA_SOURCE_DB'),
            user=os.getenv('DATA_SOURCE_USER'),
            password=os.getenv('DATA_SOURCE_PASSWORD')
        )
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        print(f"✓ PostgreSQL connected: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False

def test_azure_openai():
    """Test Azure OpenAI connection"""
    try:
        client = AzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        )
        
        response = client.chat.completions.create(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print(f"✓ Azure OpenAI connected: {response.model}")
        return True
    except Exception as e:
        print(f"✗ Azure OpenAI connection failed: {e}")
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing connections...")
    test_postgres()
    test_azure_openai()