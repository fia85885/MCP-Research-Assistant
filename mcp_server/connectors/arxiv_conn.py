from typing import List, Dict
import arxiv

def arxiv_search(query: str, max_results: int = 10) -> List[Dict]:
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    results = []
    for r in search.results():
        results.append({
            "title": r.title,
            "authors": [a.name for a in r.authors],
            "published": r.published.isoformat() if r.published else None,
            "summary": r.summary,
            "pdf_url": r.pdf_url,
            "entry_id": r.entry_id,
        })
    return results
