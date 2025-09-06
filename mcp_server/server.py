import json
import os
import sys
import traceback
from typing import List
from pydantic import BaseModel, Field
import shutil, os


# MCP server
from mcp.server.fastmcp import FastMCP

# Import your modules - handle both package and direct execution
try:
    # Try relative imports first (when run as module)
    from .connectors.arxiv_conn import arxiv_search as arxiv_search_func
    from .connectors.websearch import web_search as web_search_func
    from .ingest.pdf_ingest import fetch_pdf_file, ingest_folder as ingest_folder_func
    from .vectorstore import VectorStore
    from .embeddings import Embeddings
    from .citations import build_citations
    
except ImportError:
    # Fall back to absolute imports (when run directly)
    from connectors.arxiv_conn import arxiv_search as arxiv_search_func
    from connectors.websearch import web_search as web_search_func
    from ingest.pdf_ingest import fetch_pdf_file, ingest_folder as ingest_folder_func
    from vectorstore import VectorStore
    from embeddings import Embeddings
    from citations import build_citations

# Initial Configurations
CFG_PATH = os.environ.get("MCP_CONFIG_PATH", "config.json")
DEFAULTS = {
    "chromadb_path": "chroma",
    "embedding_model": "text-embedding-3-small",
    "embedding_backend": "openai",
    "openai_api_key": "OPENAI_API_KEY",
    "collection_name": "papers",
    "download_dir": "data/papers",
}

try:
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        CONFIG = {**DEFAULTS, **json.load(f)}
except FileNotFoundError:
    CONFIG = DEFAULTS

# Initialize MCP server
mcp = FastMCP("MCP Research Assistant")

# Pydantic models for input validation
class SearchInput(BaseModel):
    query: str = Field(..., description="The search query")
    max_results: int = Field(5, description="Maximum number of results")

class WebSearchInput(BaseModel):
    query: str = Field(..., description="The search query")
    max_results: int = Field(5, description="Maximum number of results")

class FetchInput(BaseModel):
    url: str = Field(..., description="PDF URL to fetch")

class IngestFolderInput(BaseModel):
    path: str = Field(..., description="Path to folder containing PDFs")

class QueryInput(BaseModel):
    question: str = Field(..., description="Question to query")
    top_k: int = Field(5, description="Number of top results")

class CiteInput(BaseModel):
    doi_or_url_list: List[str] = Field(..., description="List of DOIs or URLs")
    style: str = Field("bibtex", description="Citation style")

class ResetDbInput(BaseModel):
    chroma_path: str = Field(None)

# Lazy singleton pattern for embeddings and store
_embeddings = None
_store = None

def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = Embeddings(
            backend=CONFIG["embedding_backend"],
            model_name=CONFIG["embedding_model"],
        )
    return _embeddings

def _get_store():
    global _store
    if _store is None:
        _store = VectorStore(
            path=CONFIG["chromadb_path"],
            collection_name=CONFIG["collection_name"],
        )
    return _store

# MCP Tools
@mcp.tool()
async def search_arxiv(input: SearchInput) -> dict:
    """Search arXiv for papers matching the query"""
    try:
        return arxiv_search_func(input.query, input.max_results)
    except Exception as e:
        return {"error": f"Failed to search arXiv: {str(e)}"}

@mcp.tool()
async def search_web(input: WebSearchInput) -> dict:
    """Search the web, prioritizing Tavily else will go with DuckDuckGo"""
    try:
        return web_search_func(input.query, input.max_results)
    except Exception as e:
        return {"error": f"Failed to search web: {str(e)}"}

@mcp.tool()
async def fetch_pdf(input: FetchInput) -> dict:
    """Download and parse a PDF from a URL"""
    try:
        saved = fetch_pdf_file(input.url, CONFIG["download_dir"])
        return {"status": "success", "file": saved}
    except Exception as e:
        return {"error": f"Failed to fetch PDF: {str(e)}"}

@mcp.tool()
async def ingest_folder(input: IngestFolderInput) -> dict:
    """Ingest a folder of PDFs into the vector store"""
    try:
        embeddings = _get_embeddings()
        store = _get_store()
        
        # Simple progress callback
        def progress_cb(msg: str):
            print(f"Progress: {msg}", file=sys.stderr)
        
        n = ingest_folder_func(input.path, embeddings, store, progress_cb=progress_cb)
        return {
            "status": "success",
            "ingested_chunks": n,
            "collection": CONFIG['collection_name']
        }
    except Exception as e:
        return {"error": f"Failed to ingest folder: {str(e)}"}

@mcp.tool()
async def query_memory(input: QueryInput) -> dict:
    """Query the vector store for top-k supporting chunks"""
    try:
        embeddings = _get_embeddings()
        store = _get_store()
        results = store.query(input.question, embeddings, top_k=input.top_k)
        return {"status": "success", "results": results}
    except Exception as e:
        return {"error": f"Failed to query memory: {str(e)}"}

@mcp.tool()
async def make_citations(input: CiteInput) -> dict:
    """Return citations (bibtex by default) for a list of DOIs or URLs"""
    try:
        citations = build_citations(input.doi_or_url_list, style=input.style)
        return {"status": "success", "citations": citations}
    except Exception as e:
        return {"error": f"Failed to generate citations: {str(e)}"}

@mcp.tool()
def reset_chroma_tool(input: ResetDbInput = None):
    path = CONFIG.get("chromadb_path", "chroma")
    if input and input.chroma_path:
        path = input.chroma_path
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        return {"status":"ok","message":"No chroma folder found"}
    try:
        shutil.rmtree(abs_path)
    except Exception as e:
        return {"status":"error","message":str(e)}
    # reset in-memory singletons if you use them
    global _store
    _store = None
    return {"status":"ok","message":f"Removed {abs_path}. Re-run ingest to rebuild."}

@mcp.tool()
async def ping() -> str:
    """Simple test tool to confirm the server responds"""
    return "pong"

def log_err(msg: str, err: Exception = None):
    """Log error messages to stderr"""
    print(f"❌ {msg}", file=sys.stderr)
    if err:
        traceback.print_exc(file=sys.stderr)

def main():
    """Main entry point for the MCP server"""
    try:
        # Check if we should run in stdio mode (this is what Claude uses)
        if len(sys.argv) >= 2 and sys.argv[1] == "stdio":
            print("🔌 Running MCP Research Assistant in stdio mode", file=sys.stderr)
            # Run the MCP server in stdio mode - FastMCP handles stdio by default
            mcp.run()
        else:
            # For standalone mode (optional, for testing)
            print("ℹ️ To use with Claude, run with 'stdio' argument", file=sys.stderr)
            print("Example: python -m mcp_server.server stdio", file=sys.stderr)
            mcp.run()
            
    except KeyboardInterrupt:
        print("\n👋 Server shutting down gracefully", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        log_err("Server crashed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()