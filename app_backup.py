
import streamlit as st
import tempfile

from resume_parser import extract_resume_text
from skill_extractor import extract_skills
from rag import create_vector_store, generate_question
from evaluator import evaluate_answer

# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="InterviewGPT | AI Interview Coach",
    page_icon="🤖",
    layout="wide"
)

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
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your AI-powered interview preparation assistant'
    '</div>',
    unsafe_allow_html=True
)

st.caption("Resume Analysis  ·  RAG  ·  Groq AI  ·  Answer Evaluation")

st.divider()

# -----------------------------
# Resume Upload
# -----------------------------

st.header("📄 Resume Analysis")

st.markdown(
    '<div class="section-note">'
    'Upload your resume to identify your skills and review your profile.'
    '</div>',
    unsafe_allow_html=True
)

resume = st.file_uploader(
    "Upload your Resume (PDF)",
    type=["pdf"],
    key="resume_uploader"
)

if resume is not None:

    if st.session_state.get("resume_filename") != resume.name:

        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:
                tmp.write(resume.getvalue())
                resume_path = tmp.name

            with st.spinner("Analyzing your resume..."):
                resume_text = extract_resume_text(resume_path)
                skills = extract_skills(resume_text)

            st.session_state.resume_filename = resume.name
            st.session_state.resume_text = resume_text
            st.session_state.resume_skills = skills

        except Exception as e:
            st.error("Unable to process this resume. Please try another PDF.")
            st.exception(e)

    if "resume_text" in st.session_state:

        st.success("Resume uploaded and processed successfully!")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📑 Resume Preview")

            with st.expander("View extracted resume text", expanded=False):
                st.write(
                    st.session_state.resume_text[:3000]
                    or "No readable text found in this PDF."
                )

                if len(st.session_state.resume_text) > 3000:
                    st.caption("Preview limited to the first 3,000 characters.")

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
# Interview Questions PDF
# -----------------------------

st.header("📚 Interview Question Generator")

st.markdown(
    '<div class="section-note">'
    'Upload an interview question PDF to generate a question using RAG.'
    '</div>',
    unsafe_allow_html=True
)

interview_pdf = st.file_uploader(
    "Upload Interview Questions (PDF)",
    type=["pdf"],
    key="interview_pdf_uploader"
)

if interview_pdf is not None:

    if st.button(
        "✨ Generate Interview Question",
        use_container_width=True
    ):

        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:
                tmp.write(interview_pdf.getvalue())
                pdf_path = tmp.name

            with st.spinner("Preparing your interview question..."):
                vectordb = create_vector_store(pdf_path)
                question = generate_question(vectordb)

            if question:
                st.session_state.question = question
                st.session_state.pop("feedback", None)
                st.session_state.pop("last_evaluated_answer", None)
                st.success("Interview question generated!")
            else:
                st.warning("No question was generated. Please try again.")

        except Exception as e:
            st.error("Question generation failed. Please check the PDF and try again.")
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
        key="candidate_answer"
    )

    if st.button(
        "📊 Evaluate My Answer",
        type="primary",
        use_container_width=True
    ):

        if not answer.strip():
            st.warning("Please enter your answer before evaluating.")

        else:
            try:
                with st.spinner("Evaluating your answer with AI..."):
                    feedback = evaluate_answer(
                        st.session_state.question,
                        answer
                    )

                st.session_state.feedback = feedback
                st.session_state.last_evaluated_answer = answer

            except Exception as e:
                st.error("Answer evaluation failed. Please try again.")
                st.exception(e)

    # Keep the latest evaluation visible after Streamlit reruns.
    if st.session_state.get("feedback"):

        st.divider()
        st.header("📈 Interview Feedback")

        if (
            st.session_state.get("last_evaluated_answer")
            != st.session_state.get("candidate_answer", "")
        ):
            st.info("Your displayed feedback belongs to your last evaluated answer.")

        with st.container(border=True):
            st.markdown(st.session_state.feedback)

        if st.button("🔄 Try Another Question", use_container_width=True):
            st.session_state.pop("question", None)
            st.session_state.pop("feedback", None)
            st.session_state.pop("last_evaluated_answer", None)
            st.session_state.pop("candidate_answer", None)
            st.rerun()

# -----------------------------
# Footer
# -----------------------------

st.divider()

st.caption(
    "InterviewGPT | AI Interview Coach | Built with Streamlit and Groq"
)
