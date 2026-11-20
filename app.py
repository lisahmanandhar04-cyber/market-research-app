import streamlit as st

from workflow import run_orchestrator

st.set_page_config(page_title="Market Research Brief", page_icon="📊")
st.title("Market Research Brief")
st.write("Enter a company or industry to generate a short research brief.")

query = st.text_input("Company or industry", placeholder="e.g. food delivery market in Nepal")

if st.button("Start research"):
    if not query.strip():
        st.error("Please enter a company or industry.")
    else:
        with st.spinner("Researching... this can take a minute."):
            try:
                state = run_orchestrator(query)
            except Exception as exc:
                st.error(f"The research run failed: {exc}")
                st.stop()

        brief = state.draft
        findings = state.findings

        if findings.is_sample_data:
            st.warning(f"This brief uses SAMPLE data, not real search results. {findings.notes}")
        else:
            st.success("This brief is based on real web search results.")

        st.subheader("Summary")
        st.write(brief.summary)

        if brief.competitors:
            st.subheader("Competitors")
            for c in brief.competitors:
                st.markdown(f"**{c.name}**: {c.description}")

        if brief.key_observations:
            st.subheader("Key observations")
            for obs in brief.key_observations:
                st.markdown(f"- {obs}")

        st.subheader("Sources")
        for s in brief.sources:
            if s.url:
                st.markdown(f"- [{s.title}]({s.url})")
            else:
                st.markdown(f"- {s.title}")

        st.subheader("Missing information")
        if brief.missing_information:
            for item in brief.missing_information:
                st.markdown(f"- {item}")
        else:
            st.write("None reported.")

        if state.feedback.issues:
            with st.expander("Critic's remaining issues"):
                for issue in state.feedback.issues:
                    st.markdown(f"- {issue}")
                st.caption(f"Revisions used: {state.revision_count}")