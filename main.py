import streamlit as st
import pandas as pd
from src.agent import run_audit_agent
from src.tools import save_to_dataframe

# page config
st.set_page_config(
    page_title="Structura | Submittal Auditor",
    page_icon="🏗️",
    layout="wide"
)

# header
st.title("🏗️ Structura: Intelligent Submittal Auditor")
st.markdown("""
**Automated Compliance Agent for Construction Documents.** *Powered by Hybrid NLP (SpaCy + Gemini)*
""")
st.markdown("---")

# siderbar (Context & Rules)
with st.sidebar:
    st.header("📋 Project Requirements")
    st.info("Active Compliance Rules:")
    st.text_area("Concrete Spec", "Must be Type V Sulfate Resistant", disabled=True)
    st.text_area("Rebar Spec", "Must be Grade 60", disabled=True)
    
    st.divider()
    st.caption("System Status:")
    st.success("• SpaCy: Online")
    st.success("• Gemini: Online")

# main input area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Input Submittal")
    input_text = st.text_area(
        "Paste text from Subcontractor Bid / Spec Sheet:",
        height=250,
        placeholder="Example: 'We propose using Type 1 Cement to reduce costs...'"
    )
    
    audit_btn = st.button("RUN COMPLIANCE AUDIT", type="primary", use_container_width=True)

# output area 
with col2:
    st.subheader("2. Audit Results")
    
    if audit_btn:
        if not input_text:
            st.warning("Please paste some text to audit.")
        else:
            with st.spinner("Agent is analyzing text & checking compliance..."):

                # call agent
                result_dict = run_audit_agent(input_text)
            
            # check for errors
            if "error" in result_dict:
                st.error("Agent Error")
                st.code(result_dict["explanation"])
            else:
                # high level cards
                m_col, g_col, r_col = st.columns(3)
                m_col.metric("Material", result_dict.get("material", "N/A"))
                g_col.metric("Grade Found", result_dict.get("proposed_grade", "N/A"))
                
                # risk logic for color
                risk = result_dict.get("risk_level", "Unknown")
                if risk == "High":
                    r_col.error(f"Risk: {risk}")
                elif risk == "Medium":
                    r_col.warning(f"Risk: {risk}")
                else:
                    r_col.success(f"Risk: {risk}")

                # explanation
                st.info(f"**Reasoning:** {result_dict.get('explanation', 'No explanation')}")

                # data representation
                st.markdown("### 💾 Structured Data (DB Ready)")
                st.caption("Agent output formatted for Postgres:")
                df = save_to_dataframe(result_dict)
                st.dataframe(df, hide_index=True, use_container_width=True)