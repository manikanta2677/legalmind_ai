import streamlit as st
import pandas as pd
import plotly.express as px

from modules.document_reader import read_pdf, read_docx, read_txt
from modules.contract_analyzer import analyze_contract
from modules.contract_compare import compare_contracts
from modules.local_chatbot import answer_question
from modules.database import (
    init_db,
    register_user,
    login_user,
    save_history,
    get_history,
    get_all_history,
    update_status
)
st.set_page_config(page_title="LegalMind AI", layout="wide")

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "email" not in st.session_state:
    st.session_state.email = ""


def get_file_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return read_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        return read_docx(uploaded_file)
    elif uploaded_file.name.endswith(".txt"):
        return read_txt(uploaded_file)
    return ""


def is_valid_legal_contract(text):
    legal_words = [
        "agreement", "contract", "party", "terms and conditions",
        "governing law", "confidentiality", "termination",
        "liability", "arbitration"
    ]
    score = sum(1 for word in legal_words if word in text.lower())
    return score >= 2


if not st.session_state.logged_in:

    st.title("⚖️ LegalMind AI")
    st.subheader("Login to access Legal Contract Analyzer")

    auth_type = st.radio("Choose Option", ["Login", "Register"])

    if auth_type == "Login":
        email = st.text_input("Email ID")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(email, password):
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid email or password")

    else:
        email = st.text_input("Email ID")
        password = st.text_input("Create Password", type="password")

        if st.button("Register"):
            if email.strip() == "" or password.strip() == "":
                st.warning("Enter email and password")
            elif register_user(email, password):
                st.success("Account created. Please login.")
            else:
                st.error("Email already registered")

    st.stop()


st.sidebar.success(f"Logged in: {st.session_state.email}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.rerun()

feature = st.sidebar.selectbox(
    "Choose Feature",
    [
        "Contract Analysis",
        "Contract Comparison",
        "Chat With Contract",
        "History"
    ]
)

st.title("⚖️ LegalMind AI")
st.subheader("Advanced Legal Contract Analyzer Without API")


if feature == "Contract Analysis":

    input_type = st.radio("Choose Input Type", ["Upload File", "Paste Text"])
    contract_text = ""

    if input_type == "Upload File":
        uploaded_file = st.file_uploader("Upload Contract", type=["pdf", "docx", "txt"])

        if uploaded_file:
            contract_text = get_file_text(uploaded_file)
            st.success("Document loaded successfully")
            st.info(f"Extracted {len(contract_text)} characters from the document.")

            with st.expander("View Full Extracted Text"):
                st.text_area("Extracted Contract Text", contract_text, height=500)

    else:
        contract_text = st.text_area("Paste Contract Text", height=350)

    if st.button("Analyze Contract"):

        if contract_text.strip() == "":
            st.warning("Please upload or paste contract text.")

        elif not is_valid_legal_contract(contract_text):
            st.error("This document does not appear to be a legal contract.")

        else:
            report = analyze_contract(contract_text)

            save_history(
                st.session_state.email,
                report["contract_type"],
                report["risk_level"],
                report["risk_score"]
            )

            st.header("📄 Contract Analysis Report")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Contract Type", report["contract_type"])
            c2.metric("Risk Level", report["risk_level"])
            c3.metric("Risk Score", f"{report['risk_score']}/100")
            c4.metric("Missing Clauses", len(report["missing_clauses"]))

            st.subheader("1. Summary")
            st.info(report["summary"])

            st.subheader("2. Extracted Entities")
            entities = report["entities"]

            st.write("**Parties:**", entities.get("parties", []) or "Not found")
            st.write("**Money:**", entities.get("money", []) or "Not found")
            st.write("**Dates / Durations:**", entities.get("dates", []) or "Not found")
            st.write("**Emails:**", entities.get("emails", []) or "Not found")
            st.write("**Phone Numbers:**", entities.get("phones", []) or "Not found")

            st.subheader("3. Clauses Found with Confidence")

            if report["found_clauses"]:
                for clause_name, clause_data in report["found_clauses"].items():
                    with st.expander(f"✅ {clause_name} - {clause_data['confidence']}% confidence"):
                        st.write("**Matched Keywords:**", ", ".join(clause_data["keywords"]))
                        st.write("**Extracted Clause Text:**")
                        st.write(clause_data["text"])
            else:
                st.warning("No clauses detected.")

            st.subheader("4. Missing Clauses")

            if report["missing_clauses"]:
                for clause in report["missing_clauses"]:
                    st.error(clause)
            else:
                st.success("No major missing clauses found.")

            st.subheader("5. Risk Analysis")

            risk_df = pd.DataFrame({
                "Category": ["Safe", "Risk"],
                "Score": [100 - report["risk_score"], report["risk_score"]]
            })

            fig = px.pie(
                risk_df,
                names="Category",
                values="Score",
                title="Contract Risk Distribution"
            )

            st.plotly_chart(fig, use_container_width=True)
            st.progress(report["risk_score"] / 100)
            st.write(f"Risk Level: **{report['risk_level']}**")

            if report["risk_reasons"]:
                for reason in report["risk_reasons"]:
                    st.warning(reason)

            st.subheader("6. Recommendations")

            if report["missing_clauses"]:
                for clause in report["missing_clauses"]:
                    st.write(f"- Add a clear **{clause}** to improve contract safety.")
            else:
                st.success("Contract contains most important clauses.")

            text_report = f"""
LEGALMIND AI - CONTRACT ANALYSIS REPORT

Contract Type: {report['contract_type']}
Risk Level: {report['risk_level']}
Risk Score: {report['risk_score']}/100

Summary:
{report['summary']}

Missing Clauses:
{', '.join(report['missing_clauses']) if report['missing_clauses'] else 'None'}

Disclaimer:
This tool provides contract assistance only. It is not legal advice.
"""

            st.download_button(
                "Download TXT Report",
                text_report,
                file_name="contract_analysis_report.txt",
                mime="text/plain"
            )


elif feature == "Contract Comparison":

    st.header("📑 Contract Comparison")

    file1 = st.file_uploader("Upload Contract A", type=["pdf", "docx", "txt"], key="contract_a")
    file2 = st.file_uploader("Upload Contract B", type=["pdf", "docx", "txt"], key="contract_b")

    if file1 is not None and file2 is not None:
        text1 = get_file_text(file1)
        text2 = get_file_text(file2)

        result = compare_contracts(text1, text2)

        st.success("Comparison Completed")
        st.metric("Similarity Score", f"{result['similarity']}%")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Added Terms")
            st.write(result["added"])

        with col2:
            st.subheader("Removed Terms")
            st.write(result["removed"])


elif feature == "Chat With Contract":

    st.header("💬 Chat With Contract")

    uploaded_file = st.file_uploader("Upload Contract", type=["pdf", "docx", "txt"], key="chat_contract")

    if uploaded_file:
        contract_text = get_file_text(uploaded_file)

        st.success("Contract loaded successfully")
        st.info(f"Extracted {len(contract_text)} characters from the document.")

        with st.expander("View Contract Text"):
            st.text_area("Contract Text", contract_text, height=400)

        question = st.text_input("Ask a question about the contract")

        if st.button("Ask Question"):
            if question.strip() == "":
                st.warning("Please enter a question.")
            else:
                answer = answer_question(contract_text, question)
                st.subheader("Answer")
                st.success(answer)


elif feature == "History":

    st.header("📜 Analysis History")

    rows = get_history(st.session_state.email)

    if rows:
        df = pd.DataFrame(
            rows,
            columns=["Contract Type", "Risk Level", "Risk Score", "Date"]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No analysis history found.")
elif feature == "Approval Workflow":

    st.header("✅ Contract Approval Workflow")

    admin_email = "admin@legalmind.com"

    if st.session_state.email != admin_email:
        st.warning("Only admin can access approval workflow.")
        st.info("Login using: admin@legalmind.com")
    else:
        rows = get_all_history()

        if not rows:
            st.info("No contracts submitted yet.")
        else:
            for row in rows:
                record_id, email, contract_type, risk_level, risk_score, status, created_at = row

                with st.expander(f"{contract_type} | {email} | {status}"):

                    st.write("**User Email:**", email)
                    st.write("**Contract Type:**", contract_type)
                    st.write("**Risk Level:**", risk_level)
                    st.write("**Risk Score:**", risk_score)
                    st.write("**Current Status:**", status)
                    st.write("**Submitted At:**", created_at)

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(f"Approve {record_id}"):
                            update_status(record_id, "Approved")
                            st.success("Contract approved.")
                            st.rerun()

                    with col2:
                        if st.button(f"Reject {record_id}"):
                            update_status(record_id, "Rejected")
                            st.error("Contract rejected.")
                            st.rerun()