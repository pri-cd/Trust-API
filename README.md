# Trust-API 🛡️

A lightweight **fraud detection / trust scoring API** built with **FastAPI**.  
It ingests session and device events, applies real-time fraud rules backed by **Redis**, and persists every event in **SQLite** — returning structured reason codes whenever suspicious activity is detected.

---

## ✨ Features

- **Event Ingestion** — REST endpoint (`POST /events`) that validates and stores user session events.
- **Real-Time Fraud Rules** — Pluggable rule engine with reason codes returned per request.
  - `NEW_DEVICE_001` — flags events coming from a device never seen before.
  - `HIGH_VELOCITY_002` — flags users performing more than **3 events in a 60-second sliding window**.
- **Redis-backed Velocity Tracking** — Atomic `INCR` + `EXPIRE` counters for fast, low-latency abuse detection.
- **SQLite Persistence** — Zero-config local storage with parameterized queries (no SQL injection risk).
- **Strict Input Validation** — Pydantic models enforce the event schema and reject malformed payloads with `422`.
- **Test Suite** — Pytest coverage for the happy path, validation failures, and the velocity boundary case.

---

## 🧱 Tech Stack

| Layer            | Technology              |
|------------------|-------------------------|
| API Framework    | FastAPI                 |
| Validation       | Pydantic v2             |
| Persistence      | SQLite (`sqlite3`)      |
| Rate/Velocity    | Redis                   |
| Testing          | Pytest + TestClient     |
| Server           | Uvicorn                 |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+**
- A running **Redis** instance (default: `localhost:6379`)

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd Trust-API

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Redis

```
# For now, locally
redis-server
```

### 3. Run the API

```
uvicorn main:app --reload
```

The API will be available at **http://127.0.0.1:8000**.
Interactive docs: **http://127.0.0.1:8000/docs** (As of Now (Without frontend for now))

---

## 📡 API Reference

### `POST /events`

Records a session event and returns any fraud reason codes.

**Request body**

| Field | Type | Required | Description |
|---|---|---|---|
| `device_id` | string | ✅ | Unique device identifier |
| `user_id` | string | ✅ | Unique user identifier |
| `session_id` | string | ✅ | Session identifier |
| `event_type` | string | ✅ | e.g. `login`, `transaction`, `page_view` |
| `ip_address` | string | ❌ | Optional IP address |
| `timestamp` | string | ❌ | Optional ISO timestamp |

**Example**

```
curl -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -d '{
        "device_id": "dev_abc123",
        "user_id": "user_42",
        "session_id": "sess_001",
        "event_type": "login"
      }'
```

**Response — `201 Created`**

```
{
  "status": "success",
  "message": "Event recorded successfully",
  "event_id": 1,
  "reason_codes": ["NEW_DEVICE_001"]
}
```

**Reason codes**

| Code | Meaning |
|---|---|
| `NEW_DEVICE_001` | Device has never been seen before in the event store |
| `HIGH_VELOCITY_002` | User exceeded 3 events within the 60-second velocity window |

**Errors**

| Status ↕▾ | When ↕▾ |
|---|---|
| −`422` | Missing/invalid required fields |
| −`500` | Database or internal failure |
⚙

---

## 🧠 How the Fraud Engine Works

```
      POST /events
           │
           ▼
┌──────────────────────┐
│  Pydantic Validation │  → rejects malformed payloads (422)
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Fraud Rule Engine   │
│  ┌────────────────┐  │
│  │ NEW_DEVICE rule│──┼──▶ SQLite lookup: device_id seen before?
│  ├────────────────┤  │
│  │ VELOCITY rule  │──┼──▶ Redis INCR velocity:{user_id}, EXPIRE 60s
│  └────────────────┘  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│   Persist Event      │  → SQLite (parameterized INSERT)
└──────────┬───────────┘
           ▼
     JSON Response with reason_codes
```

> **Note:** the velocity counter is a fixed 60-second window keyed on `user_id`. This is a deliberate simple design; a sliding-window implementation (sorted sets or Redis `TTL`-based buckets) is a natural next step.

---

## 🧪 Running Tests

```
pytest -v
```

- Valid event → `201` + `NEW_DEVICE_001`
- Missing required field → `422`
- Velocity boundary → the **4th** event in the window returns `HIGH_VELOCITY_002`

> **Tip:** tests reset Redis (`FLUSHDB`) before running. Ensure Redis is up.

---

## 🔮 Roadmap

- Sliding-window velocity tracking (Redis sorted sets)
- IP reputation / geolocation signals
- Configurable rule thresholds via env vars
- Async DB driver (e.g. `aiosqlite`) for non-blocking I/O
- Structured logging + request tracing
- Docker Compose bundle (API + Redis)

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-rule`)
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

MIT — do whatever, just don't blame me.

