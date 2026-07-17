# AI Customs & Import Duty Agent: A Multi-Tool LLM Assessor for Trade Compliance

---

## Overview

This is a comprehensive decoupled prototype demonstrating:

- RAG (Retrieval Augmented Generation) with customs tariff document search

- Multi-tool Agent with a duty calculator, web search, and HS code retrieval

- Decoupled execution with a FastAPI backend and Streamlit frontend

- Conversational memory for context retention across complex assessments

---

## Features

🤖 Agent Tools
- Duty Calculator - Safe, deterministic mathematical calculations for CIF (Cost, Insurance, Freight), Import Duty, and VAT.

- Web Search - Real-time web search for current FX rates and trade restrictions using DuckDuckGo.

- HS Code Search - RAG-based search on Harmonized System (HS) tariffs and import regulations.

📊 Sample Vector Store (ChromaDB)
The prototype creates a sample ChromaDB vector store with:

- HS Code classifications (e.g., electronics, leather goods, textiles)

- Associated import duty rates and VAT percentages

- Regulatory guidelines (Prohibited, Restricted, or Allowed statuses)

🔍 RAG System
- Loads and indexes Customs Tariff documentation (PDFs/TXT)

- Uses embedding models for high-dimensional semantic search

- Retrieves relevant regulatory context to ground the LLM's assessments

---

## Setup

1. Install dependencies:

```bash
# For local execution without Docker
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

2. Get API Key:
- Visit the OpenAI Platform (or Google AI Studio)
- Create a new API key
- Copy .env.example to .env and add your key

3. Run the prototype:

```bash
# Using Docker Compose (Recommended)
docker-compose up --build
```

---

## Example Queries

### Customs Duty Calculations
- "Calculate the import duty for a $500 laptop with $50 shipping and $20 insurance. The duty rate is 0%."

- "What is the total tax payable for a CIF value of 10,000 THB with a 5% duty rate and 7% VAT?"

- "Compute VAT and Duty for importing 500 units of leather shoes if FOB is $2000."

### Classification & Status Queries
- "Is it allowed to import e-cigarettes for personal use?"

- "Do I need a license to import agricultural drones?"

- "What is the customs status for importing medical devices?"

### Document Search (RAG)
- "What is the HS code for running shoes?"

- "Explain the import regulations for lithium batteries."

- "What are the duty exemptions for personal effects?"

### Web Search
- "What is the current USD to THB exchange rate?"

- "Search for recent import bans in Thailand."

- "Find recent news about cross-border e-commerce tax rules."

---

## Architecture

![Architecture Diagram](images\ai-customs-agent-arch.png)

---

### Agent Flow
1. Question Analysis - Agent analyzes the user query and assesses risk intent.

2. Tool Selection - Chooses appropriate tool(s) based on the strict hierarchy (Prohibited > Restricted > Allowed).

3. Tool Execution - Executes selected tool (e.g., calculating CIF or fetching live FX rates).

4. Result Processing - Processes and formats results to map against regulatory guidelines.

5. Response Generation - Provides a final assessment to the user, appending mandatory disclaimers.

---

## Customization

### Adding Real Web Search API
Replace the mock/DuckDuckGo web search with premium APIs like Tavily or SerpAPI:

```python
# Example with Tavily
from langchain_community.tools.tavily_search import TavilySearchResults

def web_search_fn(query: str) -> str:
    search = TavilySearchResults(max_results=3)
    return search.run(query)
```

### Adding More Customs Documents
Extend the ingestion.py pipeline to ingest bulk tariff files:

```python
vector_store.add_documents(chunked_customs_pdfs)
```

### Custom Document Sources
Modify the loaders to load from different government sources:

```python
# Load from URL, PDF, etc.
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
```

---

## Security Notes
- Input Guardrails: Queries are intercepted and blocked if they contain keywords relating to smuggling, tax evasion, or bribery.

- Output Guardrails: The agent is hardcoded to append a mandatory disclaimer ("This is an estimated assessment...") to prevent legally binding assumptions.

- Calculator Strictness: The calculator relies on deterministic Python math, preventing the LLM from hallucinating tax percentages or arithmetic.

In production, implement proper input validation, API authentication, and rate limiting for the FastAPI backend.

---

## Troubleshooting

### Common Issues
1. Missing API Key: Ensure OPENAI_API_KEY (or GOOGLE_API_KEY) is set in the .env file.

2. Import Errors: Ensure all requirements are installed and virtual environments are activated.

3. Database Errors: Check file permissions for the ChromaDB local directory creation (./data/chroma_store).

### Debug Mode
Set verbose=True in the AgentExecutor initialization (inside backend/app/services/agent.py) to see detailed step-by-step execution, tool selections, and intermediate LLM thoughts in your terminal.