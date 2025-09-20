import streamlit as st
from multi_agent import researcher_agent, summarizer_agent, writer_agent, critic_agent

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# PDF Creator (text-only version)
def create_pdf(report_text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    textobject = c.beginText(40, height - 50)
    textobject.setFont("Times-Roman", 12)

    for line in report_text.split("\n"):
        textobject.textLine(line)
    c.drawText(textobject)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def main():
    st.set_page_config(page_title="AI Research Assistant", layout="wide")
    st.title("📑 AI-Powered Research Assistant")
    st.markdown("Fetch, summarize, critique, and compile research papers into a formal research report.")

    # Input Section
    query = st.text_input("Enter your research topic:", "quantum computing drug discovery")
    max_results = st.slider("Number of papers to fetch:", 1, 10, 5)

    if st.button("Generate Report"):
        # Step 1: Researcher Agent
        with st.spinner("🔎 Fetching papers from arXiv..."):
            papers = researcher_agent(query, max_results=max_results)
        if not papers:
            st.error("No papers found. Try another query.")
            return

        # Step 2: Summarizer Agent
        with st.spinner("✍️ Summarizing abstracts..."):
            summaries = summarizer_agent(papers)

        # Step 3: Critic Agent
        with st.spinner("🧐 Critiquing research..."):
            critiques = critic_agent(summaries)

        # Step 4: Writer Agent
        with st.spinner("📑 Compiling final report..."):
            report = writer_agent(summaries, query)

        # A4 Page Styling
        st.markdown(
            """
            <style>
            .report-container {
                width: 210mm;       /* A4 width */
                min-height: 297mm;  /* A4 height */
                padding: 20mm;
                margin: auto;
                background-color: white;
                color: black;
                box-shadow: 0 0 10px rgba(0,0,0,0.15);
                font-family: 'Times New Roman', serif;
                line-height: 1.6;
            }
            .report-container h1,
            .report-container h2,
            .report-container h3,
            .report-container p {
                color: black;
            }
            a { color: #1a73e8; text-decoration: none; }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Build full HTML report
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

            html_report += f"""
            <h3>{i}. {paper['title']}</h3>
            <p>{paper['summary']}</p>
            <p><a href="{paper['url']}" target="_blank">Read more</a></p>
            """
            if critique:
                html_report += f"<p><strong>Critique:</strong> {critique}</p>"

        html_report += "</div>"

        # Render it properly
        st.markdown(html_report, unsafe_allow_html=True)


        # Collapsible Critiques (separate section)
        st.subheader("🔍 Detailed Critiques")
        for c in critiques:
            with st.expander(c['title']):
                st.markdown(c['critique'])
                st.markdown(f"[Read more]({c['url']})")

        # PDF Download
        pdf_file = create_pdf(report)
        st.download_button(
            label="📄 Download Report as PDF",
            data=pdf_file,
            file_name=f"research_report_{query.replace(' ','_')}.pdf",
            mime="application/pdf"
        )


if __name__ == "__main__":
    main()
