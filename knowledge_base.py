import os
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """
    Loads and caches training data to provide context to the Vanna agent.
    Since Vanna 2.0 doesn't have a .train() method, we provide this data
    as system context that can be injected into prompts.
    """
    
    def __init__(self, training_data_dir: str = "training_data"):
        self.training_data_dir = Path(training_data_dir)
        self._cache = {}
        self._system_context = None
        
    def load_all(self) -> Dict[str, Any]:
        """Load all training data files into cache"""
        logger.info("Loading knowledge base...")
        
        # Load each file
        self._cache['schema'] = self._load_json('schema.json')
        self._cache['queries'] = self._load_json('queries.json')
        self._cache['documentation'] = self._load_json('documentation.json')
        self._cache['sql_patterns'] = self._load_json('sql_patterns.json')
        self._cache['samples'] = self._load_json('samples.json')
        
        # Build system context
        self._system_context = self._build_system_context()
        
        logger.info(f"✓ Knowledge base loaded: {self.get_stats()}")
        return self._cache
    
    def _load_json(self, filename: str) -> Any:
        """Load a JSON file"""
        filepath = self.training_data_dir / filename
        if not filepath.exists():
            logger.warning(f"⚠ File not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"  ✓ Loaded {filename}")
                return data
        except Exception as e:
            logger.error(f"  ✗ Error loading {filename}: {e}")
            return None
    
    def _build_system_context(self) -> str:
        """Build a comprehensive system context string from all training data"""
        context_parts = []
        
        # Add schema information
        if self._cache.get('schema'):
            context_parts.append("=== DATABASE SCHEMA ===")
            for table in self._cache['schema'].get('tables', []):
                context_parts.append(f"\n{table['name']}: {table['description']}")
                context_parts.append(table['ddl'])
        
        # Add business documentation
        if self._cache.get('documentation'):
            context_parts.append("\n\n=== BUSINESS TERMINOLOGY ===")
            for term in self._cache['documentation'].get('business_terms', []):
                context_parts.append(f"\n{term['term']}: {term['definition']}")
            
            context_parts.append("\n\n=== BUSINESS RULES ===")
            for rule in self._cache['documentation'].get('business_rules', []):
                context_parts.append(f"\n{rule['rule']}: {rule['description']}")
        
        # Add query examples
        if self._cache.get('queries'):
            context_parts.append("\n\n=== EXAMPLE QUERIES ===")
            for q in self._cache['queries'].get('question_sql_pairs', [])[:5]:  # Top 5 examples
                context_parts.append(f"\nQ: {q['question']}")
                context_parts.append(f"SQL: {q['sql']}")
        
        return "\n".join(context_parts)
    
    def get_system_context(self) -> str:
        """Get the cached system context string"""
        if self._system_context is None:
            self.load_all()
        return self._system_context
    
    def get_schema_ddl(self) -> List[str]:
        """Get all DDL statements"""
        if not self._cache.get('schema'):
            return []
        return [table['ddl'] for table in self._cache['schema'].get('tables', [])]
    
    def get_example_queries(self) -> List[Dict[str, str]]:
        """Get question-SQL pairs"""
        if not self._cache.get('queries'):
            return []
        return self._cache['queries'].get('question_sql_pairs', [])
    
    def find_similar_question(self, question: str) -> Dict[str, str]:
        """Find a similar question in the examples (simple keyword matching)"""
        question_lower = question.lower()
        examples = self.get_example_queries()
        
        for example in examples:
            example_q = example['question'].lower()
            # Simple keyword matching
            keywords = [word for word in question_lower.split() if len(word) > 3]
            matches = sum(1 for kw in keywords if kw in example_q)
            
            if matches >= 2:  # If at least 2 keywords match
                return example
        
        return None
    
    def get_business_context(self) -> str:
        """Get business terms and rules as formatted text"""
        if not self._cache.get('documentation'):
            return ""
        
        parts = []
        doc = self._cache['documentation']
        
        for term in doc.get('business_terms', []):
            parts.append(f"{term['term']}: {term['definition']}")
        
        for rule in doc.get('business_rules', []):
            parts.append(f"{rule['rule']}: {rule['description']}")
        
        return "\n".join(parts)
    
    def get_stats(self) -> str:
        """Get statistics about loaded data"""
        stats = []
        
        if self._cache.get('schema'):
            table_count = len(self._cache['schema'].get('tables', []))
            stats.append(f"{table_count} tables")
        
        if self._cache.get('queries'):
            query_count = len(self._cache['queries'].get('question_sql_pairs', []))
            stats.append(f"{query_count} example queries")
        
        if self._cache.get('documentation'):
            term_count = len(self._cache['documentation'].get('business_terms', []))
            stats.append(f"{term_count} business terms")
        
        return ", ".join(stats) if stats else "no data"
    
    def get_cache(self) -> Dict[str, Any]:
        """Get the entire cache"""
        if not self._cache:
            self.load_all()
        return self._cache


# Global instance
_kb_instance = None

def get_knowledge_base() -> KnowledgeBase:
    """Get or create the global knowledge base instance (singleton)"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
        _kb_instance.load_all()
    return _kb_instance
