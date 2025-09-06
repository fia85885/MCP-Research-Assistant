Got it ✅ I’ll create a **complete README.md (Markdown) for your GitHub repo** based on the project files you uploaded. This will look professional and explain the purpose, setup, and usage clearly.

Here’s the draft:

---

# 📚 MCP Research Assistant

An AI-powered **research assistant** built on the **Model Context Protocol (MCP)**.
It can:

* 🔎 Search academic papers from **arXiv**
* 🌍 Perform web searches (Tavily / DuckDuckGo fallback)
* 📄 Fetch & parse PDFs
* 📥 Ingest documents into a **ChromaDB vector store**
* ❓ Answer queries with semantic search over ingested papers
* 📑 Generate citations (BibTeX, JSON)

This project integrates **OpenAI embeddings**, **ChromaDB**, and **MCP tooling** to create a research pipeline.

---

## ⚡ Features

* **arXiv Search** → Find papers by query
* **Web Search** → Uses Tavily API if available, otherwise DuckDuckGo
* **PDF Ingestion** → Chunk & embed PDFs for semantic search
* **Vector Store** → Store and query embeddings via ChromaDB
* **Citation Builder** → Generate BibTeX citations from DOIs/URLs
* **MCP Server** → Tools exposed for MCP-compatible clients (e.g., Claude Desktop)

---

## 📂 Project Structure

```
├── server.py          # Main MCP server (FastMCP)
├── embeddings.py      # Embeddings wrapper (OpenAI API)
├── vectorstore.py     # ChromaDB vector store wrapper
├── pdf_ingest.py      # PDF fetching, text extraction, chunking & ingestion
├── arxiv_conn.py      # arXiv API connector
├── websearch.py       # Tavily / DuckDuckGo web search connector
├── citations.py       # Crossref citation builder
└── requirements.txt   # Dependencies
```

---

## 🔧 Installation

### 1. Clone the repo

```bash
git clone https://github.com/your-username/mcp-research-assistant.git
cd mcp-research-assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # On Linux/Mac
.venv\Scripts\activate      # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

```bash
# Required
export OPENAI_API_KEY="your_openai_api_key"

# Optional (if you want Tavily web search)
export TAVILY_API_KEY="your_tavily_api_key"
```

---

## ▶️ Usage

### Run MCP server

```bash
python server.py stdio
```

This runs in **stdio mode**, ready for MCP-compatible clients like **Claude Desktop**.

---

## 🛠️ Tools Exposed

| Tool                | Description                                 |
| ------------------- | ------------------------------------------- |
| `search_arxiv`      | Search arXiv for research papers            |
| `search_web`        | Search the web (Tavily/DuckDuckGo)          |
| `fetch_pdf`         | Download and parse a PDF                    |
| `ingest_folder`     | Ingest all PDFs from a folder               |
| `query_memory`      | Query stored documents with semantic search |
| `make_citations`    | Generate citations in BibTeX/JSON           |
| `reset_chroma_tool` | Reset the ChromaDB database                 |
| `ping`              | Test server response                        |

---

## 📑 Example Workflows

### Search arXiv

```json
{
  "tool": "search_arxiv",
  "input": { "query": "machine learning", "max_results": 3 }
}
```

### Ingest PDFs

```json
{
  "tool": "ingest_folder",
  "input": { "path": "data/papers" }
}
```

### Query Knowledge Base

```json
{
  "tool": "query_memory",
  "input": { "question": "What is attention mechanism?", "top_k": 5 }
}
```

### Generate Citations

```json
{
  "tool": "make_citations",
  "input": { "doi_or_url_list": ["https://doi.org/10.48550/arXiv.1706.03762"], "style": "bibtex" }
}
```

---

## 📦 Dependencies

* [OpenAI](https://pypi.org/project/openai/) – embeddings
* [ChromaDB](https://www.trychroma.com/) – vector database
* [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) – PDF parsing
* [arxiv](https://pypi.org/project/arxiv/) – arXiv API client
* [duckduckgo-search](https://pypi.org/project/duckduckgo-search/) – fallback web search
* [requests](https://docs.python-requests.org/) – HTTP requests
* [pydantic](https://docs.pydantic.dev/) – schema validation
* [fastmcp](https://github.com/modelcontextprotocol/fastmcp) – MCP server

---

## 📌 Roadmap

* [ ] Add support for more citation styles
* [ ] Improve query relevance with RAG pipeline
* [ ] Support embeddings backends beyond OpenAI

---

## 🤝 Contributing

Pull requests are welcome!
For major changes, please open an issue first to discuss what you’d like to change.

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

Would you like me to also **generate a `requirements.txt`** for this project so your repo is fully ready to run?

