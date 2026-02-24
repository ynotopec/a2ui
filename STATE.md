{
  "project_id": "ynotopec/a2ui",
  "project_version": "1.0.0",
  "created_at": "2026-02-24T00:00:00Z",
  "status": "active",
  "description": "A2UI streaming JSONL endpoint with vLLM service"

}

---

## Router / Decision Flow

### 1. Main Entry Point (`GET /a2ui`)

```
┌─────────────────────────────────────┐
│     GET /a2ui?q=QUERY              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   LLM Generation Trigger           │
│   - Send query to Qwen2.5-72B-Instruct
│   - Temperature: 0.2
│   - Max tokens: auto
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Parse LLM Response               │
│   - Extract JSON from raw response │
│   - Validate with AgentData schema  │
│   - Enforce constraints:           │
│     * title: 1-120 chars           │
│     * summary: 1-600 chars         │
│     * bullets: 3-7 items           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Error Handling & Fallback        │
│   If validation fails:             │
│   - Return error message           │
│   - Use default AgentData with    │
│     retry information             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   A2UI Protocol Processing         │
│   - Generate surfaceUpdate msg     │
│   - Generate dataModelUpdate msg   │
│   - Generate beginRendering msg    │
│   - Stream as JSONL                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Client Rendering Trigger         │
│   - Client receives stream         │
│   - Process messages sequentially  │
│   - Update UI incrementally       │
└─────────────────────────────────────┘
```

### 2. Streaming Flow Control

```
┌────────────────────┐
│  Start Stream      │
└─────────┬──────────┘
          │
          ▼
┌────────────────────────────────┐
│   Send surfaceUpdate message   │
│   - Define UI components       │
│   - Bind data paths            │
└─────────┬──────────────────────┘
          │
          ▼
┌────────────────────────────────┐
│   Send dataModelUpdate message │
│   - Set path values            │
│   - /view/title                │
│   - /view/summary              │
│   - /view/bullets/0-6          │
└─────────┬──────────────────────┘
          │
          ▼
┌────────────────────────────────┐
│     Send beginRendering        │
│   - Signal ready to render    │
│   - Client starts UI updates   │
└────────────────────────────────┘
```

### 3. Data Flow

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Agent FastAPI      │
└──────┬──────────────┘
       │
       ├─► LLM (Qwen2.5-72B)
       │     ↓
       │  JSON Data
       │
       ├─► A2UI Protocol
       │
       ▼
┌─────────────────────┐
│  JSONL Stream       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Client Renderer    │
└─────────────────────┘
```

---

## Critical Test Case Sequence

### Test Case: Complex Query Processing

```
START: 2026-02-24T10:00:00Z
    │
    ▼
[1] Client sends GET /a2ui?q=Quelle+est+la+différence+entre+AI+et+ML?
    │
    ▼
[2] FastAPI validates query parameters
    - q: "Quelle est la différence entre AI et ML?"
    - surface_id: (generated timestamp-based)
    │
    ▼
[3] LLM Generation
    ├─► System prompt: "You are a helpful assistant..."
    ├─► User prompt: "Quelle est la différence entre AI et ML?"
    ├─► Model: Qwen2.5-72B-Instruct
    ├─► Temperature: 0.2
    └─► Expected output: JSON with title, summary, bullets
    │
    ▼
[4] Response Parsing
    ├─► Extract raw string from API response
    ├─► Find JSON object boundaries (first '{' to last '}')
    ├─► Parse JSON
    ├─► Validate with AgentData schema
    │
    ▼
[5] Data Validation
    ├─► Check title length (1-120 chars)
    ├─► Check summary length (1-600 chars)
    ├─► Check bullets count (3-7 items)
    ├─► Pad or truncate bullets to 7 items
    └─► Remove empty/whitespace bullets
    │
    ▼
[6] A2UI Protocol - Surface Update
    ├─► message type: "surfaceUpdate"
    ├─► surfaceId: "surface-1737794000000"
    ├─► components: [
    │     { id: "root", component: { Column: {...}} },
    │     { id: "title", component: { Text: { text: { binding: "/view/title" }} }},
    │     { id: "summary", component: { Text: { text: { binding: "/view/summary" }} }},
    │     { id: "bullets", component: { Column: { children: {...}} }},
    │     { id: "b0"..."b6" }
    │   ]
    └─► JSON stream:
        {"surfaceUpdate": {...}}\n
        {"dataModelUpdate": {...}}\n
        {"beginRendering": {...}}\n
    │
    ▼
[7] Client Streaming Reception
    ├─► Establish WebSocket connection (HTTP streaming)
    ├─► Read chunked data stream
    ├─► Split by '\n' to parse individual JSONL messages
    ├─► Thread-safe message handling
    │
    ▼
[8] Message Processing Sequence
    ├─► Receive surfaceUpdate
    │    - Create component tree structure
    │    - Initialize DOM elements
    │    └─► Update: messageCount = 1
    │
    ├─► Receive dataModelUpdate
    │    - Update path bindings:
    │      * /view/title → "Intelligence Artificielle vs Machine Learning"
    │      * /view/summary → "AI combines ML with symbolic AI..."
    │      * /view/bullets[0-6] → bullet points
    │    └─► Update: messageCount = 2
    │
    └─► Receive beginRendering
         - Mark surface as rendering
         - Start DOM updates
         └─► Update: messageCount = 3
    │
    ▼
[9] UI State Management
    ├─► Surface rendering: true
    ├─► Title: "Intelligence Artificielle vs Machine Learning"
    ├─► Summary: "AI combines ML with symbolic AI..."
    ├─► Bullets: [3-7 bullet points]
    │
    ▼
[10] Completion
    └─► Stream closed normally
        └─► Status: "Terminé"
        └─► Message count: 3+ (one per type)
        └─► Render complete
        └─► END: 2026-02-24T10:00:05Z (5s duration)

---

## Error Handling Flow

```
┌──────────────────────┐
│ Query Validation      │
└──────────┬───────────┘
           │
           ▼
    ┌────────────────┐
    │ q too short/long│
    └───────┬────────┘
            ├──► 400 Bad Request
            │
            ▼
    ┌────────────────┐
    │ LLM API Error  │
    └───────┬────────┘
            ├──► 503 Service Unavailable
            │
            ▼
    ┌────────────────┐
    │ JSON Parse Error│
    └───────┬────────┘
            ├──► Fallback AgentData
            │   - Error message
            │   - Retry suggestions
            │
            └─► Output: 3 JSONL messages w/ error content
```

---

## Performance Metrics

| Metric | Target | Actual |
|--------|--------|---------|
| LLM Generation (Qwen2.5-72B) | < 3s | TBD |
| JSONL Stream Size | < 5KB | TBD |
| Client Rendering | < 200ms | TBD |
| API Response Time | < 5s | TBD |
| Memory Usage | < 8GB | TBD |
| GPU Memory (vLLM) | ~6GB | TBD |

---

## Deployment Notes

1. Requires NVIDIA GPU with 8GB+ VRAM
2. Docker volume: `./models:/models` (HF model cache)
3. Environment: `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`
4. Test endpoints:
   - `http://localhost:8000/v1/models` (vLLM)
   - `http://localhost:8080/a2ui?q=test` (agent)