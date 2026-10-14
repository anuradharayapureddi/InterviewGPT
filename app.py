
import re
import sqlite3
import tempfile

import pandas as pd
import streamlit as st

from resume_parser import extract_resume_text
from skill_extractor import extract_skills
from rag import (
    create_vector_store,
    generate_question,
    generate_resume_question,
)
from evaluator import evaluate_answer
from database import create_database, save_interview


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="InterviewGPT | AI Interview Coach",
    page_icon="🤖",
    layout="wide",
)

# Create/update database before using it.
create_database()


# -----------------------------
# Custom Styling
# -----------------------------

st.markdown("""
<style>
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #9CA3AF;
        font-size: 1.05rem;
        margin-top: 5px;
        margin-bottom: 22px;
    }

    .section-note {
        color: #9CA3AF;
        font-size: 0.95rem;
    }

    div[data-testid="stFileUploader"] {
        border-radius: 12px;
    }

    div.stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Header
# -----------------------------

st.markdown(
    '<div class="main-title">🤖 InterviewGPT</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Your AI-powered interview preparation assistant'
    '</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Resume Analysis  ·  RAG  ·  Groq AI  ·  Answer Evaluation"
)

st.divider()


# -----------------------------
# Resume Upload
# -----------------------------

st.header("📄 Resume Analysis")

st.markdown(
    '<div class="section-note">'
    'Upload your resume to identify your skills and review your profile.'
    '</div>',
    unsafe_allow_html=True,
)

resume = st.file_uploader(
    "Upload your Resume (PDF)",
    type=["pdf"],
    key="resume_uploader",
)

if resume is not None:

    if st.session_state.get("resume_filename") != resume.name:
        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf",
            ) as tmp:
                tmp.write(resume.getvalue())
                resume_path = tmp.name

            with st.spinner("Analyzing your resume..."):
                resume_text = extract_resume_text(resume_path)
                skills = extract_skills(resume_text)

            st.session_state.resume_filename = resume.name
            st.session_state.resume_text = resume_text
            st.session_state.resume_skills = skills

        except Exception:
            st.error(
                "Unable to process this resume. Please try another PDF."
            )
            st.exception(Exception)

    if "resume_text" in st.session_state:
        st.success("Resume uploaded and processed successfully!")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📑 Resume Preview")

            with st.expander(
                "View extracted resume text",
                expanded=False,
            ):
                st.write(
                    st.session_state.resume_text[:3000]
                    or "No readable text found in this PDF."
                )

                if len(st.session_state.resume_text) > 3000:
                    st.caption(
                        "Preview limited to the first 3,000 characters."
                    )

        with col2:
            st.subheader("🧠 Detected Skills")
            skills = st.session_state.resume_skills

            if skills:
                st.caption(f"{len(skills)} skills identified")
                skill_columns = st.columns(2)

                for index, skill in enumerate(skills):
                    with skill_columns[index % 2]:
                        st.markdown(f"🔹 {skill}")
            else:
                st.warning("No skills detected in this resume.")

st.divider()


# -----------------------------
# Resume-Based Interview Question
# -----------------------------

st.header("🎯 Resume-Based Interview")

if st.session_state.get("resume_text"):
    if st.button(
        "Generate Resume-Based Question",
        use_container_width=True,
    ):
        question = generate_resume_question(
            st.session_state.resume_text,
            st.session_state.resume_skills,
        )

        st.session_state.question = question
        st.session_state.pop("feedback", None)
        st.session_state.pop("last_evaluated_answer", None)
        st.success("Resume-based question generated!")
else:
    st.info("Upload your resume to generate a resume-based question.")


# -----------------------------
# Interview Questions PDF
# -----------------------------

st.divider()
st.header("📚 Interview Question Generator")

st.markdown(
    '<div class="section-note">'
    'Upload an interview question PDF to generate a question using RAG.'
    '</div>',
    unsafe_allow_html=True,
)

interview_pdf = st.file_uploader(
    "Upload Interview Questions (PDF)",
    type=["pdf"],
    key="interview_pdf_uploader",
)

if interview_pdf is not None:
    if st.button(
        "✨ Generate Interview Question",
        use_container_width=True,
    ):
        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf",
            ) as tmp:
                tmp.write(interview_pdf.getvalue())
                pdf_path = tmp.name

            with st.spinner("Preparing your interview question..."):
                vectordb = create_vector_store(pdf_path)
                question = generate_question(vectordb)

            if question and question != "No Question Found":
                st.session_state.question = question
                st.session_state.pop("feedback", None)
                st.session_state.pop("last_evaluated_answer", None)
                st.success("Interview question generated!")
            else:
                st.warning(
                    "No question was generated. Please try another PDF."
                )

        except Exception as e:
            st.error(
                "Question generation failed. Please check the PDF and try again."
            )
            st.exception(e)


# -----------------------------
# Interview Question and Answer
# -----------------------------

if st.session_state.get("question"):

    st.divider()
    st.header("🎤 Your Interview")

    with st.container(border=True):
        st.caption("YOUR QUESTION")
        st.markdown(f"### {st.session_state.question}")

    answer = st.text_area(
        "✍️ Type your answer below",
        height=180,
        placeholder="Explain your answer here...",
        key="candidate_answer",
    )

    if st.button(
        "📊 Evaluate My Answer",
        type="primary",
        use_container_width=True,
    ):
        if not answer.strip():
            st.warning("Please enter your answer before evaluating.")

        else:
            try:
                with st.spinner("Evaluating your answer with AI..."):
                    feedback = evaluate_answer(
                        st.session_state.question,
                        answer,
                    )

                # Extract scores from the feedback.
                technical_match = re.search(
                    r"Technical Score:\s*(\d+)\s*/\s*10",
                    feedback,
                    re.IGNORECASE,
                )

                communication_match = re.search(
                    r"Communication Score:\s*(\d+)\s*/\s*10",
                    feedback,
                    re.IGNORECASE,
                )

                technical_score = (
                    int(technical_match.group(1))
                    if technical_match else None
                )

                communication_score = (
                    int(communication_match.group(1))
                    if communication_match else None
                )

                # Save the interview only once.
                save_interview(
                    st.session_state.question,
                    answer,
                    feedback,
                    technical_score,
                    communication_score,
                )

                st.session_state.feedback = feedback
                st.session_state.last_evaluated_answer = answer

                st.success("Answer evaluated and saved successfully!")

            except Exception as e:
                st.error("Answer evaluation failed. Please try again.")
                st.exception(e)


    # Display the latest evaluation.
    if st.session_state.get("feedback"):

        st.divider()
        st.header("📈 Interview Feedback")

        if (
            st.session_state.get("last_evaluated_answer")
            != st.session_state.get("candidate_answer", "")
        ):
            st.info(
                "Your displayed feedback belongs to your last evaluated answer."
            )

        with st.container(border=True):
            st.markdown(st.session_state.feedback)

        if st.button(
            "🔄 Try Another Question",
            use_container_width=True,
        ):
            st.session_state.pop("question", None)
            st.session_state.pop("feedback", None)
            st.session_state.pop("last_evaluated_answer", None)
            st.session_state.pop("candidate_answer", None)
            st.rerun()


# -----------------------------
# Interview History Dashboard
# -----------------------------


st.divider()
st.header("📈 Interview History Dashboard")

conn = sqlite3.connect("interview_history.db")

try:
    history = pd.read_sql_query(
        """
        SELECT
            id,
            question,
            answer,
            technical_score,
            communication_score,
            feedback,
            created_at
        FROM interview_history
        ORDER BY id ASC
        """,
        conn,
    )
finally:
    conn.close()

if not history.empty:

    history["technical_score"] = pd.to_numeric(
        history["technical_score"], errors="coerce"
    )
    history["communication_score"] = pd.to_numeric(
        history["communication_score"], errors="coerce"
    )

    valid_technical = history["technical_score"].dropna()
    valid_communication = history["communication_score"].dropna()

    # Summary
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Interviews", len(history))

    col2.metric(
        "Average Technical Score",
        f"{valid_technical.mean():.1f}/10"
        if not valid_technical.empty else "N/A",
    )

    col3.metric(
        "Average Communication Score",
        f"{valid_communication.mean():.1f}/10"
        if not valid_communication.empty else "N/A",
    )

    # Best scores
    st.subheader("🏆 Best Scores")

    col4, col5 = st.columns(2)

    col4.metric(
        "Best Technical Score",
        f"{valid_technical.max():.0f}/10"
        if not valid_technical.empty else "N/A",
    )

    col5.metric(
        "Best Communication Score",
        f"{valid_communication.max():.0f}/10"
        if not valid_communication.empty else "N/A",
    )

    # Line chart
    st.subheader("📈 Interview Progress")

    chart_data = history[
        ["id", "technical_score", "communication_score"]
    ].rename(
        columns={
            "id": "Interview",
            "technical_score": "Technical Score",
            "communication_score": "Communication Score",
        }
    ).set_index("Interview")

    if chart_data.notna().any().any():
        st.line_chart(
            chart_data,
            y=["Technical Score", "Communication Score"],
            
        )
    else:
        st.info("Scores will appear here after an evaluation.")

    # Bar chart
    st.subheader("📊 Score Comparison")

    if not valid_technical.empty or not valid_communication.empty:
        average_scores = pd.DataFrame({
            "Average Score": [
                valid_technical.mean(),
                valid_communication.mean(),
            ]
        }, index=["Technical", "Communication"])

        st.bar_chart(
            average_scores,
            y="Average Score",
            
        )

    # History table
    st.subheader("📋 Past Interview Attempts")

    st.dataframe(
        history.sort_values("id", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info(
        "No interview history yet. Complete an interview to see your results here."
    )

# -----------------------------
# Footer
# -----------------------------

st.divider()

st.caption(
    "InterviewGPT | AI Interview Coach | Built with Streamlit and Groq"
)
