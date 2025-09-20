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
        prompt = f"""
Summarize the following abstract in a structured research format. 
Organize the summary under these sections:
1. Background
2. Objective
3. Methods
4. Results
5. Conclusion

Ensure each section is concise (1–2 sentences) and captures the essence of the abstract clearly.

Abstract:
{paper['abstract']}
"""

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
    
    
    
def writer_agent(summaries, topic):
    """
    Writer Agent: compiles all paper summaries into a structured research-style report.
    
    Args:
        summaries (list): list of dicts with 'title', 'summary', 'url'
        topic (str): the research topic
    
    Returns:
        str: formatted research report
    """
    report_sections = []
    for s in summaries:
        section = f"### {s['title']}\n{s['summary']}\n[Read more]({s['url']})\n"
        report_sections.append(section)

    report = f"""
# Research Report on {topic}

## Introduction
This report compiles and summarizes recent research papers related to *{topic}*.
The following sections provide concise summaries of key papers, highlighting their contributions.

## Paper Summaries
{chr(10).join(report_sections)}

## Conclusion
This report consolidates current findings from multiple sources.
It may serve as a foundation for deeper exploration, critical analysis, and potential project directions.
"""
    return report

topic = query  # you already have the search topic
report = writer_agent(summaries, topic)

# Print report
print(report)

def critic_agent(summaries):
    """
    Critic Agent: evaluates each paper summary for limitations, assumptions, or open challenges.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    critiques = []
    
    for s in summaries:
        prompt = f"""
You are a critical reviewer. Analyze the following summary of a research paper.

Paper Title: {s['title']}
Summary: {s['summary']}

Identify:
1. Potential limitations or weaknesses
2. Assumptions made
3. Gaps or unanswered questions
4. Possible improvements or future directions
"""
        try:
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.6, "max_output_tokens": 200}
            )
            critique_text = response.text.strip()
            critiques.append({"title": s['title'], "critique": critique_text, "url": s['url']})
        except Exception as e:
            critiques.append({"title": s['title'], "critique": f"Error generating critique: {e}", "url": s['url']})
    
    return critiques
# Call critic agent
critiques = critic_agent(summaries)

# Print results for visibility
for c in critiques:
    print(f"--- {c['title']} ---")
    print(c['critique'])
    print(f"[Read more]({c['url']})\n")
