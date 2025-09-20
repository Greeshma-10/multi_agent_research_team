import streamlit as st
from multi_agent import researcher_agent, summarizer_agent, writer_agent, critic_agent

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

        # Display Report
        st.subheader("📄 Final Report")
        st.markdown(report, unsafe_allow_html=True)

        # Display Critiques
        st.subheader("🔍 Paper Critiques")
        for c in critiques:
            with st.expander(c['title']):
                st.markdown(c['critique'])
                st.markdown(f"[Read more]({c['url']})")

        # Download Option
        st.download_button(
            label="💾 Download Report",
            data=report,
            file_name=f"research_report_{query.replace(' ','_')}.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()
