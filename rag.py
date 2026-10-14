from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

import random

def generate_resume_question(resume_text, skills):
    """
    Generate an interview question based on the candidate's resume.
    Uses the existing resume text and detected skills.
    """

    if not resume_text or not resume_text.strip():
        return "Please upload a readable resume first."

    if not skills:
        return (
            "Tell me about one technical project you have completed "
            "and explain the technologies you used."
        )

    import random

    skill_list = list(skills)

    skill = random.choice(skill_list)

    question_templates = [
        f"Can you explain your experience with {skill}?",
        f"How have you used {skill} in your projects?",
        f"What are the main concepts of {skill} that you know?",
        f"What challenges have you faced while working with {skill}?",
        f"How would you explain {skill} to a beginner?",
    ]

    return random.choice(question_templates)



def create_vector_store(pdf_file):

    loader = PyPDFLoader(pdf_file)

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return vectordb


def generate_question(vectordb):

    docs = vectordb.similarity_search(
        "technical interview questions",
        k=10
    )

    questions = []

    for doc in docs:

        text = doc.page_content

        # Split by question mark
        lines = text.split("?")

        for line in lines:

            line = line.strip()

            if len(line) > 5:
                questions.append(
                    line + "?"
                )

    # Remove duplicates
    questions = list(
        set(questions)
    )

    if len(questions) > 0:

        return random.choice(
            questions
        )

    return "No Question Found"


if __name__ == "__main__":

    pdf_file = r"F:\Projects_Datav\genai_prompt\Interview Questions.pdf"

    vectordb = create_vector_store(
        pdf_file
    )

    for i in range(5):

        print(
            generate_question(
                vectordb
            )
        )

        print("-" * 50)