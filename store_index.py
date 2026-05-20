from dotenv import load_dotenv
import os
from src.helper import load_pdf_files, extract_qa_pairs, download_embedding
from langchain_chroma import Chroma

load_dotenv()

path_data = os.getenv("PATH_DATA")
if not path_data:
    raise RuntimeError("PATH_DATA não está definida. Configure o arquivo .env antes de indexar.")

extracted_data = load_pdf_files(path_data)
qa_docs = extract_qa_pairs(extracted_data)

print(f"Pares Q&A extraídos: {len(qa_docs)}")

embedding = download_embedding()

vectorstore = Chroma.from_documents(
    documents=qa_docs,
    embedding=embedding,
    persist_directory="chroma_db"
)

print(f"Total indexado no ChromaDB: {vectorstore._collection.count()}")
