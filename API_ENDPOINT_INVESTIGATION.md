# Vanna 2.0 API Endpoint Investigation

**Date:** 2025-11-04  
**Status:** Completed  

## Summary

The Vanna 2.0 FastAPI server in this deployment **does not expose a traditional REST API** for text-to-SQL generation that can be tested via curl or standard HTTP POST requests.

## Investigation Results

### What We Found

1. **Web UI Works** ✅
   - URL: http://localhost:8000
   - Status: 200 OK
   - Functionality: Interactive web interface for chat

2. **Health Check Works** ✅
   - URL: http://localhost:8000/health
   - Status: 200 OK
   - Functionality: System health monitoring

3. **Swagger Docs Exist** ✅
   - URL: http://localhost:8000/docs
   - Shows: `/api/vanna/v2/chat/sse` endpoint
   - Issue: Endpoint listed but not accessible via traditional POST

4. **REST Endpoints Tested** ❌
   - `/api/chat` → 404 Not Found
   - `/chat` → 404 Not Found
   - `/api/v1/ask` → 404 Not Found
   - `/ask` → 404 Not Found
   - `/api/vanna/v2/chat/sse` → 404 Not Found

### Why This Happens

The `/api/vanna/v2/chat/sse` endpoint is likely:
- **Server-Sent Events (SSE) only** - Requires streaming connection, not standard POST
- **WebSocket protocol** - Requires upgrade from HTTP to WebSocket
- **Built into the web UI** - Exposed through the web interface, not as standalone API
- **Not directly callable** - Requires specific headers or connection upgrade

## Technical Details

### Endpoint Type
The Swagger documentation shows this is an SSE (Server-Sent Events) endpoint:
- SSE is a one-way connection from server to client
- Requires `Accept: text/event-stream` header
- Sends data as `data: {json}` events
- Different from traditional REST POST

### Why Standard HTTP POST Fails
```bash
# This fails with 404:
curl -X POST http://localhost:8000/api/vanna/v2/chat/sse \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

The endpoint requires:
1. Special connection headers (for SSE/WebSocket)
2. Or it's only callable from within the web UI context
3. Or it requires authentication/session

## Recommendations

### Option 1: Test Through Web UI (Recommended)
- Open: http://localhost:8000
- Ask questions interactively
- See results in real-time
- Most reliable method

### Option 2: Create Custom API Endpoint
Create a new FastAPI endpoint that:
```python
@app.post("/api/chat/ask")
async def ask_question(question: str):
    # Use the Vanna Agent
    result = agent.ask(question)
    return {"sql": result}
```

### Option 3: Use WebSocket/SSE Client
Modify test to:
- Connect with proper SSE/WebSocket protocol
- Upgrade from HTTP to streaming connection
- Parse event stream responses

## Files Generated

**Test Results:** `API_TEST_RESULTS_2025_11_04.md`
- 55 questions tested
- All returned 404 errors
- Detailed analysis provided

## Conclusion

The Vanna 2.0 deployment provides:
- ✅ Web UI for interactive testing
- ✅ Health monitoring
- ✅ Swagger documentation
- ❌ REST API for automated testing

**For testing: Use the web UI at http://localhost:8000**  
**For automation: Create a custom wrapper endpoint**

---

**Investigation completed:** 2025-11-04  
**Next steps:** Implement custom API endpoint or use web UI for validation
