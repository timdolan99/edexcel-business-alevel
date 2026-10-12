import os, json, tomllib
from pydantic import BaseModel, Field
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# --- Key Retrieval ---
secrets_path = os.path.join(".streamlit", "secrets.toml")
if os.path.exists(secrets_path) and "GOOGLE_API_KEY" not in os.environ:
    with open(secrets_path, "rb") as f:
        secrets = tomllib.load(f)
        os.environ["GOOGLE_API_KEY"] = secrets.get("GOOGLE_API_KEY") or secrets.get("GEMINI_API_KEY", "")

# --- Dynamic Schema Definition ---
class SubjectSpec(BaseModel):
    course_title: str = Field(description="Overall course title, e.g. Edexcel A-Level Business or Edexcel GCSE History")
    subject: str = Field(description="Subject name, e.g. Business Studies or History")
    level: str = Field(description="Qualification level, e.g. GCSE or A-Level")
    target_turns: int = Field(description="Target exchange turns: set 5 for GCSE/IGCSE, 7 for A-Level/IB")
    topics: Dict[str, List[str]] = Field(description="Map of EVERY Unit/Component title to its full list of subtopics")

def process_corpus():
    syllabus_dir = "./syllabus"
    if not os.path.exists(syllabus_dir):
        print(f"⚠️ Directory '{syllabus_dir}' does not exist.")
        return

    pdf_files = sorted([f for f in os.listdir(syllabus_dir) if f.lower().endswith(".pdf")])
    if not pdf_files:
        print(f"⚠️ No PDFs found in {syllabus_dir}/")
        return

    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")

    master_spec = {}

    for pdf in pdf_files:
        print(f"🔍 Processing {pdf} from {syllabus_dir}...")
        pdf_path = os.path.join(syllabus_dir, pdf)
        docs = PyPDFLoader(pdf_path).load()
        
        # Read ALL preliminary pages (up to 40) sequentially to capture full syllabus outline
        overview_docs = docs[:min(40, len(docs))]
        full_overview_text = "\n--- PAGE ---\n".join([d.page_content for d in overview_docs])

        prompt = (
            "You are an expert curriculum analyst.\n"
            "Thoroughly analyze the provided specification text from the syllabus document.\n"
            "Extract the exact course title, subject name, qualification level, appropriate turn count, "
            "and EVERY single unit/component alongside ALL corresponding subtopics.\n\n"
            "Extraction Rules:\n"
            "- course_title: Full Exam Board and Qualification Name (e.g., 'Edexcel A-Level Business')\n"
            "- subject: Core Subject Name (e.g., 'Business Studies')\n"
            "- level: Qualification Level ('GCSE', 'A-Level', etc.)\n"
            "- target_turns: Integer 7 if level is A-Level or equivalent, 5 if GCSE/IGCSE\n"
            "- topics: A dictionary where keys are major Unit/Theme/Component names "
            "and values are lists of distinct subtopic strings under that unit.\n\n"
            f"Specification Text:\n{full_overview_text[:150000]}"
        )

        try:
            spec = llm.with_structured_output(SubjectSpec).invoke(prompt)
            
            master_spec = {
                "course_title": spec.course_title,
                "subject": spec.subject,
                "level": spec.level,
                "target_turns": spec.target_turns,
                "topics": spec.topics
            }
            print(f"   ✅ Successfully extracted {len(spec.topics)} main units for {spec.course_title}")
        except Exception as e:
            print(f"   ⚠️ Spec extraction error on {pdf}: {e}")

        # Index document chunks into ChromaDB
        chunks = splitter.split_documents(docs)
        for c in chunks:
            c.metadata["source_file"] = pdf
        
        for i in range(0, len(chunks), 100):
            vectorstore.add_documents(chunks[i:i + 100])
        print(f"   ✅ Indexed {len(chunks)} chunks into ChromaDB.")

    # Save dynamic course_spec.json
    with open("course_spec.json", "w", encoding="utf-8") as f:
        json.dump(master_spec, f, indent=2)
    print("\n🚀 Saved course_spec.json successfully!")

if __name__ == "__main__":
    process_corpus()