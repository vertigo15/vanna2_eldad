# Vanna 2.0 Training Data

## Important Note About Vanna 2.0

**Vanna 2.0 uses an Agent-based architecture and does NOT require traditional "training" like Vanna 1.0.**

### How Vanna 2.0 Works:

1. **Dynamic Schema Introspection**: The agent can query your database schema automatically
2. **LLM-Powered**: Uses Azure OpenAI to generate SQL on-the-fly
3. **No Training Needed**: The agent learns from the database structure in real-time

### Why These JSON Files?

These JSON files are prepared for **future use** if you want to:
- Add context to improve SQL generation quality
- Provide business terminology
- Give examples of complex queries
- Document special business rules

## Current Status

The Vanna 2.0 Agent in this project:
- ✅ Can introspect your PostgreSQL database schema
- ✅ Generates SQL using Azure OpenAI (GPT-4)
- ✅ Works out-of-the-box without training data
- ✅ Improves over time through conversation history

## Future Enhancement

If Vanna 2.0 adds a training API or knowledge base feature in the future, these JSON files can be used to:
1. Pre-load domain knowledge
2. Provide SQL generation hints
3. Define business terms and metrics

## Usage

For now, the agent works without these files. The database schema from `AdventureWorksDW` will be discovered automatically when users ask questions.

### Example Queries You Can Ask:

- "What are the total sales by product category?"
- "Show me the top 10 customers by revenue"
- "What was our revenue last month?"

The agent will:
1. Understand your question
2. Inspect the database schema
3. Generate appropriate SQL
4. Execute and return results
