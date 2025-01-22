from typing import Dict
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_website(url: str) -> Dict:
    """
    Scrapes basic information from a given URL.
    
    Args:
        url: The website URL to scrape
        
    Returns:
        Dict containing scraped information:
        - title: page title
        - description: meta description
        - text: main content text
        - domain: website domain
    """
    print(f"Scraping website: {url}")
    try:
        # Send request with headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)
        # Extract basic information
        title = soup.title.string if soup.title else ""
        description = soup.find("meta", {"name": "description"})
        description = description["content"] if description else ""
        
        # Get main text content
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = " ".join(soup.stripped_strings)
        
        domain = urlparse(url).netloc
        
        return {
            "url": url,
            "title": title,
            "description": description, 
            "text": text,  # Truncate text to first 1000 chars
            "domain": domain
        }
        
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "domain": urlparse(url).netloc
        }
