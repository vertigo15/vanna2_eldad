"""
Enhanced Azure OpenAI LLM Service that uses the knowledge base
"""
from typing import List, Dict, Any, Optional
from vanna.core.llm import LlmService
from openai import AzureOpenAI
import logging

logger = logging.getLogger(__name__)


class EnhancedAzureOpenAILlmService(LlmService):
    """
    Azure OpenAI LLM Service that injects knowledge base context
    """
    
    def __init__(
        self,
        api_key: str,
        model: str,
        azure_endpoint: str,
        api_version: str,
        knowledge_base=None
    ):
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
        self.model = model
        self.knowledge_base = knowledge_base
        
        # Build enhanced system context
        self.system_context = self._build_system_context()
        
    def _build_system_context(self) -> str:
        """Build system context from knowledge base"""
        context_parts = [
            "You are a SQL expert assistant for AdventureWorksDW database.",
            "You help users write SQL queries to answer their business questions."
        ]
        
        if self.knowledge_base:
            # Add schema information
            context_parts.append("\n\n=== DATABASE SCHEMA ===")
            schema_ddls = self.knowledge_base.get_schema_ddl()
            if schema_ddls:
                # Include first 10 tables to avoid token limits
                for ddl in schema_ddls[:10]:
                    context_parts.append(ddl)
            
            # Add business context
            business_context = self.knowledge_base.get_business_context()
            if business_context:
                context_parts.append("\n\n=== BUSINESS CONTEXT ===")
                context_parts.append(business_context)
            
            # Add example queries
            examples = self.knowledge_base.get_example_queries()
            if examples:
                context_parts.append("\n\n=== EXAMPLE QUERIES ===")
                # Include first 5 examples
                for ex in examples[:5]:
                    context_parts.append(f"\nQuestion: {ex['question']}")
                    context_parts.append(f"SQL: {ex['sql']}\n")
        
        return "\n".join(context_parts)
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion with knowledge base context injected
        """
        # Inject system context as first message if not present
        enhanced_messages = []
        
        # Add system context
        if not any(msg.get("role") == "system" for msg in messages):
            enhanced_messages.append({
                "role": "system",
                "content": self.system_context
            })
        
        # Add original messages
        enhanced_messages.extend(messages)
        
        # Check if user is asking about example queries
        if self.knowledge_base and enhanced_messages:
            last_message = enhanced_messages[-1].get("content", "")
            if last_message:
                similar = self.knowledge_base.find_similar_question(last_message)
                if similar:
                    logger.info(f"Found similar question: {similar['question']}")
                    # Add hint about similar example
                    enhanced_messages.append({
                        "role": "system",
                        "content": f"Hint: Similar question example:\nQ: {similar['question']}\nSQL: {similar['sql']}"
                    })
        
        try:
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=enhanced_messages,
                tools=tools if tools else None,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000)
            )
            
            message = response.choices[0].message
            
            result = {
                "role": message.role,
                "content": message.content if message.content else None
            }
            
            # Handle tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            
            return result
            
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI: {e}")
            raise
