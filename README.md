# 📑 AI-Powered Research Assistant

An interactive **Streamlit application** that fetches, summarizes, critiques, and compiles research papers into a structured report.  
The app uses **arXiv API** for research papers and **Google Gemini (via `google-generativeai`)** to generate structured summaries, critiques, and final reports.

---

## 🚀 Features
- 🔎 **Researcher Agent**: Fetches research papers from arXiv based on your query.  
- ✍️ **Summarizer Agent**: Summarizes abstracts into a structured 5-part format (Background, Objective, Methods, Results, Conclusion).  
- 🧐 **Critic Agent**: Evaluates limitations, assumptions, and future directions.  
- 📑 **Writer Agent**: Compiles results into a polished research-style report.  
- 📄 **PDF Export**: Download the report in an A4-formatted PDF with proper headings and styling.  
- 🎨 **Styled UI**: Clean report-style rendering directly inside Streamlit.  

---

## 🛠️ Tech Stack
- [Python 3.12+](https://www.python.org/)  
- [Streamlit](https://streamlit.io/) (UI framework)  
- [Google Generative AI](https://ai.google.dev/) (Gemini API for LLM capabilities)  
- [arXiv API](https://arxiv.org/help/api/index) (fetching research papers)  
- [ReportLab](https://www.reportlab.com/) (PDF generation)  
- [python-dotenv](https://pypi.org/project/python-dotenv/) (environment variable management)  

---

## 📂 Project Structure
```text
.
├── app.py # Main Streamlit app
├── multi_agent.py # Researcher, summarizer, critic, writer agents
├── requirements.txt # Python dependencies
├── .env # API keys (not committed to repo)
└── README.md # Project documentation
```

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/research-assistant.git
cd research-assistant
```
### 2. Create & activate a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Set up environment variables
Create a .env file in the project root with:

```ini

GEMINI_API_KEY=your_gemini_api_key_here
```
### ▶️ Usage
Run the Streamlit app:

```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

### 📄 Example Workflow
1. Enter a research query (e.g., quantum computing drug discovery).

2. Choose how many papers to fetch (1–10).

3. Click Generate Report.

4. View:

  📋 Structured summaries

  🧐 Critiques with limitations and future directions

  📑 Full compiled report

5. Download report as a PDF.

### 🔒 Environment & API Keys
Requires a Gemini API key from Google AI Studio.

Keys must be stored in .env file and never committed to version control.
