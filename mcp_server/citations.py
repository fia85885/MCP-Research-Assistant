from typing import List
import requests

def _crossref_lookup(identifier: str):
    doi = identifier
    if "doi.org/" in identifier:
        doi = identifier.split("doi.org/")[-1]
    url = f"https://api.crossref.org/works/{doi}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json().get("message", {})

def _to_bibtex(message: dict) -> str:
    authors = message.get("author", [])
    author_str = " and ".join([f"{a.get('family','')}, {a.get('given','')}" for a in authors])
    title = message.get("title", [""])[0]
    year = message.get("issued", {}).get("date-parts", [[None]])[0][0]
    doi = message.get("DOI", "")
    entry_key = (authors[0].get('family','') if authors else "paper") + (str(year) if year else "")
    return f"""@article{{{entry_key},
  title={{ {title} }},
  author={{ {author_str} }},
  year={{ {year or ''} }},
  doi={{ {doi} }}
}}"""

def build_citations(identifiers: List[str], style: str = "bibtex") -> str:
    messages = [_crossref_lookup(x) for x in identifiers]
    if style.lower() == "bibtex":
        return "\n\n".join(_to_bibtex(m) for m in messages)
    else:
        import json
        return json.dumps(messages, indent=2)
