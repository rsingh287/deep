import urllib.request
import json
import urllib.parse
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import threading

def fetch_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        text = soup.get_text(separator=" ", strip=True)
        return text[:3000] # keep it brief per site
    except Exception as e:
        return ""

def perform_advanced_search(query):
    print(f"[Advanced Search] Searching Google for: {query}")
    urls = []
    try:
        for j in search(query, num_results=3):
            urls.append(j)
    except Exception as e:
        print(f"[Advanced Search] Error: {e}")
        return "Failed to perform search."

    print(f"[Advanced Search] Found URLs: {urls}")
    
    scraped_data = []
    def scrape(u):
        text = fetch_text_from_url(u)
        if text:
            scraped_data.append(f"SOURCE: {u}\nCONTENT:\n{text}\n")
            
    threads = []
    for u in urls:
        t = threading.Thread(target=scrape, args=(u,))
        t.start()
        threads.append(t)
        
    for t in threads:
        t.join()
        
    if not scraped_data:
        return "Search completed but no readable content could be extracted from the top results."
        
    context = "\n".join(scraped_data)
    
    # Send it to Ollama to summarize
    ollama_url = "http://localhost:11434/api/generate"
    prompt = f"You are an expert researcher. I searched the web for '{query}'. Here is the data from the top websites:\n\n{context}\n\nPlease provide a highly detailed, extremely advanced, and well-structured answer to the query based ONLY on this information. Cite your sources using the URLs provided."
    
    payload = {
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        req = urllib.request.Request(ollama_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=60) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res.get("response", "Error generating response.")
    except Exception as e:
        return f"Error connecting to local LLM: {e}"

if __name__ == '__main__':
    print(perform_advanced_search("how to change transmission oil on honda accord 2016"))
