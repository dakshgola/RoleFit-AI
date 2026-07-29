import os
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from langchain_core.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

from datetime import datetime
from rich import print as rprint

# Load environment variables
load_dotenv()

def get_tavily_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set. Please add it to your .env file.")
    return TavilyClient(api_key=api_key)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def _tavily_search_with_retry(query: str) -> dict:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    rprint(f"[bold yellow][{timestamp}] Tavily Search API Call Initiated[/bold yellow] - Query: {query}")
    client = get_tavily_client()
    return client.search(query=query, max_results=5)

@tool
def web_search(query: str) -> str:
    """Search the web using Tavily for the given query and return top 5 results formatted as Title / URL / Snippet blocks."""
    try:
        response = _tavily_search_with_retry(query)
        results = []
        for result in response.get("results", []):
            title = result.get('title', 'N/A')
            url = result.get('url', 'N/A')
            content = result.get('content', 'N/A')
            results.append(f"Title: {title} / URL: {url} / Snippet: {content}")
        if not results:
            return "Limited data found for this query — proceeding with best available information"
        return "\n\n".join(results)
    except Exception as e:
        print(f"web_search tool failed after retries: {str(e)}")
        return "Limited data found for this query — proceeding with best available information"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def _scrape_request_with_retry(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text

@tool
def scrape_url(url: str) -> str:
    """Fetch content from a URL using requests and BeautifulSoup, strip script/style/nav/footer tags, and return clean text limited to 3000 characters."""
    try:
        html_content = _scrape_request_with_retry(url)
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Strip script, style, nav, and footer tags
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()
            
        text = soup.get_text(separator="\n")
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = "\n".join(chunk for chunk in chunks if chunk)
        
        # Return max 3000 characters
        if not cleaned_text.strip():
            return "Could not retrieve detailed page content — proceeding with search snippets alone."
        return cleaned_text[:3000]
    except Exception as e:
        print(f"scrape_url tool failed after retries: {str(e)}")
        return "Could not retrieve detailed page content — proceeding with search snippets alone."

@tool
def parse_resume(file_path: str) -> str:
    """Use PdfReader to extract all text from a PDF resume file path, joining pages with newlines."""
    try:
        reader = PdfReader(file_path)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text)
    except Exception as e:
        return f"Error parsing PDF resume: {str(e)}"

