

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)




def evaluate_answer(question, answer):

    prompt = f"""
You are evaluating a candidate for a FRESHER or ENTRY-LEVEL
technical interview.

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate the candidate fairly using these rules:

1. Judge the answer based on correctness, relevance, and
   understanding of the question.
2. Do not expect senior-level knowledge, advanced edge cases,
   or production-level experience from a fresher.
3. Do not give a very low score only because the answer is short.
   A short answer can receive a good score if it is correct
   and covers the main points.
4. Give credit for every correct concept mentioned.
5. Identify incorrect statements separately from missing concepts.
6. Evaluate communication based on clarity and understandable
   language. Do not penalize minor grammar mistakes heavily.
7. If the answer is empty or irrelevant, explain that clearly.
8. Never invent concepts the candidate did not mention.
9. Give an improved answer in simple English that a fresher
   can understand and speak in an interview.
10. Do not make real hiring decisions. Give learning-focused
    recommendations only.
    
11. Score technical correctness based on the actual answer.
12. A correct, concise definition should receive good marks
    even if it does not include advanced details.
13. Do not penalize the same missing concept multiple times.
14. Do not claim spelling or grammar errors unless they
    actually appear in the candidate's answer.
15. Keep feedback proportional to the difficulty of the question.
16. Award partial credit when the answer is partly correct.
17. Do not require examples unless the question asks for one
    or an example is necessary to explain the concept.
    18. Match the evaluation depth to the question. Do not expect advanced details for a basic definition question.

19. Separate essential concepts from optional advanced concepts. Do not reduce the score heavily for missing optional details.

20. For a basic RNN definition, prioritize sequential data and recurrent information flow. Treat hidden state as an important concept, while weight sharing, BPTT, and applications may be additional details depending on the question.

21. Give a score that reflects the candidate's actual answer. Do not award or deduct marks based only on the length of the answer.

22. Do not describe grammar errors unless they are present in the candidate's original answer.
23. For comparison questions, prioritize the differences explicitly requested in the question. Do not require unrelated advanced properties for full marks.

24. Award full or near-full technical marks when the candidate correctly explains all essential differences with valid examples. Missing optional details should cause only a small deduction, if any.

25. Do not repeat the same missing concept under Weaknesses, Missing Concepts, and Improvement Tips unless each mention adds a different useful explanation.

26. Ensure every evaluation is based on the candidate's actual answer and the exact question asked.
27. For basic definition questions, award strong marks when the central concept is correct. Missing implementation details such as Q, K, V, scaled dot-product attention, concatenation, and linear projection should affect the score according to the question's expected depth.

28. Do not treat a short answer as incorrect merely because it lacks advanced details. Evaluate correctness, completeness, and question difficulty separately.

29. Make the Practice Recommendation consistent with the score and the candidate's actual understanding. A partially correct answer may need more practice, but do not overstate weaknesses.
30. For basic definition questions, distinguish essential concepts from optional implementation details.

31. Do not deduct significant marks for omitting class names, code examples, persistence, or advanced implementation details unless the question explicitly asks for them.

32. Check technical statements for correctness, including whether code examples and APIs are appropriate for the stated framework version. Do not present outdated APIs as universally current.

33. Keep the Improved Answer proportional to the question. Start with a short, interview-ready answer, then add optional details only when useful.

34. The Practice Recommendation must reflect the candidate's demonstrated understanding, not simply the number of missing details.
35. If the candidate's answer is completely unrelated to the question, assign a very low technical score and clearly explain the mismatch.

36. For an irrelevant answer, recommend reviewing the concept from the basics before attempting advanced practice.

37. Evaluate communication separately from technical correctness. A clear sentence can receive a good communication score even when it does not answer the technical question.

38. Never award technical marks merely because an unrelated answer is factually correct in another subject.



Return the evaluation in this exact structure:

## 1. Technical Score: X/10
Explain the score in simple language.

## 2. Communication Score: X/10
Explain clarity and communication fairly.

## 3. Strengths
List the concepts the candidate explained correctly.

## 4. Weaknesses
List mistakes or unclear parts, if any.

## 5. Missing Concepts
Mention important points that should be added.
Write "None" if no important concepts are missing.

## 6. Improved Answer
Provide a correct, interview-ready answer in simple English.
Include a short example when useful.

## 7. Practice Recommendation
Choose one:
- Ready to Practise the Next Question
- Needs a Little More Practice
- Review the Basics First

Give 2 or 3 specific improvement tips.

Keep the feedback constructive, encouraging, and suitable
for a fresher. Scores must be between 0 and 10.
"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "system",
                "content": """
You are a fair and supportive technical interview evaluator
for fresh graduates and entry-level candidates.

Your subjects include:
- Python
- SQL
- Machine Learning
- Deep Learning
- NLP
- Generative AI
- RAG
- LangChain

Use simple English. Be accurate, encouraging, and specific.
Award marks according to the candidate's actual understanding.
Do not judge the candidate's overall job eligibility.
Follow the requested evaluation structure.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,
        max_tokens=1500
    )

    return response.choices[0].message.content



if __name__ == "__main__":

    print("=" * 70)
    print("INTERVIEW ANSWER EVALUATOR")
    print("=" * 70)

    question = input(
        "\nEnter Interview Question:\n\n"
    )

    answer = input(
        "\nEnter Candidate Answer:\n\n"
    )

    result = evaluate_answer(
        question,
        answer
    )

    print("\n")
    print("=" * 70)
    print("INTERVIEW EVALUATION REPORT")
    print("=" * 70)
    print(result)