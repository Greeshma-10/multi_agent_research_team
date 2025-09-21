import streamlit as st
from multi_agent import researcher_agent, summarizer_agent, writer_agent, critic_agent
import re
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

def create_pdf_from_html(html_report: str) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)
    
    # Base styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CustomHeading1", parent=styles["Heading1"],
                              fontSize=18, leading=22, spaceAfter=12, spaceBefore=12, alignment=1))  
    styles.add(ParagraphStyle(name="CustomHeading2", parent=styles["Heading2"],
                              fontSize=14, leading=18, spaceAfter=8, spaceBefore=10))
    styles.add(ParagraphStyle(name="CustomHeading3", parent=styles["Heading3"],
                              fontSize=12, leading=14, spaceAfter=6, spaceBefore=8))
    styles.add(ParagraphStyle(name="BodyTextCustom", parent=styles["Normal"],
                              fontSize=11, leading=14))

    story = []

    for block in html_report.split("\n"):
        block = block.strip()
        if not block:
            story.append(Spacer(1, 12))
            continue

        # Map tags → custom styles
        if block.startswith("<h1>"):
            story.append(Paragraph(block, styles["CustomHeading1"]))
        elif block.startswith("<h2>"):
            story.append(Paragraph(block, styles["CustomHeading2"]))
        elif block.startswith("<h3>"):
            story.append(Paragraph(block, styles["CustomHeading3"]))
        else:
            story.append(Paragraph(block, styles["BodyTextCustom"]))

        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Step 2: Add the new helper function ---
def sanitize_agent_output(text: str) -> str:
    """
    Cleans up inconsistent output from an LLM agent.
    - Removes markdown code fences (```...```).
    - Strips leading/trailing whitespace.
    """
    # Pattern to find content inside ```...```, including language hints like ```html
    code_block_pattern = r"```(?:[a-zA-Z]+\n)?(.*)```"
    
    match = re.search(code_block_pattern, text, re.DOTALL)
    
    if match:
        # If it's a code block, extract the content inside
        return match.group(1).strip()
    else:
        # Otherwise, just return the text, stripped of whitespace
        return text.strip()


def main():
    st.set_page_config(page_title="AI Research Assistant", layout="wide")
    st.title("📑 AI-Powered Research Assistant")
    st.markdown("Fetch, summarize, critique, and compile research papers into a formal research report.")

    # Input Section
    query = st.text_input("Enter your research topic:", "quantum computing drug discovery")
    max_results = st.slider("Number of papers to fetch:", 1, 10, 5)

    if st.button("Generate Report"):
        with st.spinner("🔎 Fetching papers from arXiv..."):
            papers = researcher_agent(query, max_results=max_results)
        if not papers:
            st.error("No papers found. Try another query.")
            return

        with st.spinner("✍️ Summarizing abstracts..."):
            summaries = summarizer_agent(papers)

        with st.spinner("🧐 Critiquing research..."):
            critiques = critic_agent(summaries)

        with st.spinner("📑 Compiling final report..."):
            report = writer_agent(summaries, query)

        st.markdown(
            """
            <style>
            .report-container {
                width: 210mm;       /* A4 width */
                min-height: 297mm;  /* A4 height */
                padding: 20mm; margin: auto; background-color: white;
                color: black; box-shadow: 0 0 10px rgba(0,0,0,0.15);
                font-family: 'Times New Roman', serif; line-height: 1.6;
            }
            .report-container h1, .report-container h2,
            .report-container h3, .report-container p { color: black; }
            a { color: #1a73e8; text-decoration: none; }
            </style>
            """,
            unsafe_allow_html=True
        )

        html_report = f"""
        <div class="report-container">
            <h1>Research Report on {query}</h1>
            <h2>Introduction</h2>
            <p>This report compiles and summarizes recent research papers related to <em>{query}</em>. 
            The following sections provide concise summaries of key papers, highlighting their contributions.</p>
            <h2>Paper Summaries</h2>
        """

        for i, paper in enumerate(summaries, 1):
            critique = next((c["critique"] for c in critiques if c["title"] == paper["title"]), None)

            # --- Step 3: Use the sanitization function ---
            summary_text = sanitize_agent_output(paper['summary'])

            html_report += f"""
            <h3>{i}. {paper['title']}</h3>
            {summary_text}
            <p><a href="{paper['url']}" target="_blank">Read more</a></p>
            """
            if critique:
                html_report += f"<p><strong>Critique:</strong> {sanitize_agent_output(critique)}</p>"

        html_report += "</div>"
        st.markdown(html_report, unsafe_allow_html=True)

        st.subheader("🔍 Detailed Critiques")
        for c in critiques:
            with st.expander(c['title']):
                st.markdown(sanitize_agent_output(c['critique'])) # Sanitize here too!
                st.markdown(f"[Read more]({c['url']})")

        pdf_file = create_pdf_from_html(report)
        st.download_button(
            label="📄 Download Report as PDF",
            data=pdf_file,
            file_name=f"research_report_{query.replace(' ','_')}.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()