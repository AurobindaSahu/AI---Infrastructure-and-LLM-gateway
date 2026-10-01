# 🚀 Gateway Studio: Multi-LLM Gateway & Prompt Management Dashboard

A full-stack **LLMOps Microservice & Developer Playground** built using **FastAPI**, **LiteLLM**, **SQLite**, and **Vanilla HTML/CSS/JS**. 

This system acts as a unified AI gateway that automatically classifies incoming user intent, routes requests through primary LLM models, provides automatic fallback execution, tracks dynamic prompt versions (`v1`, `v2`, `v3`...), and logs real-time operational telemetry.

---

## 📌 Architecture & Features

### 1. Multi-LLM Routing & Fallback Gateway
- **Intent Classification:** Automatically categorizes user queries (`chat`, `summary`, `general`) using lightweight routing models.
- **Dynamic Model Selection:** Routes traffic across multiple providers (Google Gemini, Groq Llama, OpenAI).
- **Automated Fallback:** If a primary model API fails, hits rate limits, or times out, LiteLLM catches the exception and routes to backup models automatically.

### 2. Prompt Registry & Auto-Versioning
- **Automated Versioning:** Whenever a `Prompt Name` is reused, the backend automatically calculates and increments its version (`v1` → `v2` → `v3`...).
- **Prompt Lookup:** Allows querying specific prompt versions or retrieving the latest active prompt.

### 3. Telemetry & Execution Analytics
- Tracks execution metrics for every API call, including **Latency (ms)**, **Prompt Tokens**, **Completion Tokens**, **Actual Model Used**, and **HTTP Status Codes**.

---

## 📁 Project Directory Structure

```text
├── main.py        # Core FastAPI application endpoints and CORS middleware
├── generate.py    # LiteLLM client, intent routing, and fallback handler
├── curd.py        # SQLite database operations for Prompts and API Logs
├── data.py        # Database schema initialization script
├── index.html     # Dark-mode developer dashboard UI
└── .env           # Environment variables for API keys
