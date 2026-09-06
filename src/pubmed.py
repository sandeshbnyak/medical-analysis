import xml.etree.ElementTree as ET
from urllib.parse import quote

import requests

ENTREZ_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def search_pubmed(query, max_results=5):
    """Search PubMed and return a list of summary records."""
    if not query or not query.strip():
        return []

    query_text = query.strip()
    params = {
        "db": "pubmed",
        "term": query_text,
        "retmode": "json",
        "retmax": str(max_results),
        "sort": "relevance",
    }

    esearch = requests.get(f"{ENTREZ_BASE_URL}esearch.fcgi", params=params, timeout=30)
    esearch.raise_for_status()
    data = esearch.json()

    ids = data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    efetch = requests.get(f"{ENTREZ_BASE_URL}efetch.fcgi", params=fetch_params, timeout=30)
    efetch.raise_for_status()

    root = ET.fromstring(efetch.content)
    results = []

    for article in root.findall("./PubmedArticle"):
        med_article = article.find("MedlineCitation/Article")
        if med_article is None:
            continue

        article_id = article.findtext("MedlineCitation/PMID") or ""
        title = med_article.findtext("ArticleTitle") or "Untitled"
        abstract_elem = med_article.find("Abstract")
        abstract_parts = []
        if abstract_elem is not None:
            for text in abstract_elem.findall("AbstractText"):
                if text.text:
                    abstract_parts.append(text.text)
        abstract = " ".join(abstract_parts).strip()

        journal = med_article.findtext("Journal/Title") or "Unknown journal"
        pub_date = med_article.find("Journal/JournalIssue/PubDate")
        year = "Unknown"
        if pub_date is not None:
            year_elem = pub_date.find("Year")
            if year_elem is not None and year_elem.text:
                year = year_elem.text

        results.append({
            "pmid": article_id,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "year": year,
        })

    return results


def fetch_pubmed_abstract(pmid):
    """Fetch a single PubMed abstract by PMID."""
    params = {
        "db": "pubmed",
        "id": str(pmid),
        "retmode": "xml",
        "rettype": "abstract",
    }
    response = requests.get(f"{ENTREZ_BASE_URL}efetch.fcgi", params=params, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    article = root.find("./PubmedArticle/MedlineCitation/Article")
    if article is None:
        return None

    abstract_parts = []
    for text in article.findall("Abstract/AbstractText"):
        if text.text:
            abstract_parts.append(text.text)

    return {
        "pmid": article.findtext("../PMID") or str(pmid),
        "title": article.findtext("ArticleTitle") or "Untitled",
        "abstract": " ".join(abstract_parts).strip(),
        "journal": article.findtext("Journal/Title") or "Unknown journal",
        "year": article.findtext("Journal/JournalIssue/PubDate/Year") or "Unknown",
    }
