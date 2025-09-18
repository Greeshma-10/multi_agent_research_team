import requests
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai



def researcher_agent(query, max_results=5):
    """
    Researcher Agent: searches arXiv for papers related to a query.
    
    Args:
        query (str): research topic
        max_results (int): number of papers to fetch
    
    Returns:
        List of dicts: [{'title': ..., 'abstract': ..., 'url': ...}, ...]
    """
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query=all:{query}&start=0&max_results={max_results}"
    
    response = requests.get(base_url + search_query)
    if response.status_code != 200:
        print("Error fetching data from arXiv")
        return []
    
    import xml.etree.ElementTree as ET
    root = ET.fromstring(response.text)
    
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
        abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
        url = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()
        papers.append({"title": title, "abstract": abstract, "url": url})
    
    return papers

# Test
query = "quantum computing drug discovery"
papers = researcher_agent(query)
for i, paper in enumerate(papers):
    print(f"{i+1}. {paper['title']}")


# Load .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def summarizer_agent(papers):
    summaries = []
    model = genai.GenerativeModel("gemini-1.5-flash")
    for paper in papers:
        prompt = f"Summarize the following abstract in 7-8 sentences and display in points:\n{paper['abstract']}"
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.5,
                    "max_output_tokens": 150
                }
            )
            summary_text = response.text.strip()
            summaries.append({"title": paper['title'], "summary": summary_text, "url": paper['url']})
        except Exception as e:
            print(f"Error summarizing {paper['title']}: {e}")
            summaries.append({"title": paper['title'], "summary": "Error summarizing paper.", "url": paper['url']})
    return summaries
# Test
summaries = summarizer_agent(papers)
for s in summaries:
    print(f"{s['title']}\nSummary: {s['summary']}\n")
    
    
    