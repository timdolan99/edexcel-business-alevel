# 🎓 OCR A-level Socratic Tutor App and Teacher Analytics Console

An adaptive Socratic tutoring system built for OCR A-level Computer Science using LangGraph, LangChain, and Streamlit. This application dynamically ingests specification documents and guides students through computer science concepts using pedagogical scaffolding and safety-critical guardrails. The tutor app is Zero-PII; no logins; no profiles; all processing based in the UK

The aim of this tutoring app is to develop disciplinary literacy - subject specific vocabulary - often the difference between B/C and A/A* grade performance on Papers 1 and 2. 

The Tutor seeks to develop disciplinary through 4 different challenges:
1. Socratic dialogue - a 7-turn mechanism in which the tutor asks questions to test understanding of a particular subtopic
2. Retrieval quizzes - 10 short answer questions focused on specific key terms within a particular subtopic
3. Extended answer questions - 9 or 12 mark questions on a bigger topic that are scored against use of subject specific vocabulary
4. Rewrite the answer - 4 or 6 mark questions in which the user has to rewrite an answer written in layperson's language using and are are scored for their  use of subject specific vocabulary

Teacher app is a console that allows teachers to view cohort-based data analytics on where students are struggling with using key terms. Using the on-board agent teachers can either drill deeper into the data or generate AFL resources like starter questions based on key weaknesses identified in a topic

## 📂 Directory Structure

```text
msc-socratic-chatbot/
├── .streamlit/
│   └── secrets.toml
├── chroma_db/ 
├── syllabus/
│   └── ocr_alevel_computer_science_syllabus.pdf
├── app.py
├── ingest_corpus.py
├── requirements.txt
└── socratic_fsm.py
└── teacher_app.py
└── generate_test_data.py
└── course_spec.json




4. Quantitative RAG Quality Matrix (evaluate_system_rag.py)
Benchmarks factual faithfulness (Groundedness) and Context Relevance under adversarial conditions using an LLM-as-a-Judge framework:

python evaluate_system_rag.py

