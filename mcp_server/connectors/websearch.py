
import os
from typing import List, Dict
import requests
from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 10) -> List[Dict]:
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if tavily_key:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": tavily_key, "query": query, "max_results": max_results},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        out = [{"title": r.get("title"), "url": r.get("url"), "content": r.get("content")} for r in data.get("results", [])][:max_results]
        return out
    else:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            out = [{"title": r.get("title"), "url": r.get("href"), "content": r.get("body")} for r in results]
            return out
