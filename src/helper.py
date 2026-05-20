import re
from langchain_community.document_loaders import DirectoryLoader, PyPDFium2Loader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from typing import List


def load_pdf_files(data):
    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFium2Loader
    )
    return loader.load()


def extract_qa_pairs(docs: list) -> List[Document]:
    full_text = "\n".join([doc.page_content for doc in docs])

    pattern = r"PERGUNTA\s+\d+:\s*(.*?)\s*RESPOSTA\s+\d+:\s*(.*?)(?=PERGUNTA\s+\d+:|$)"
    matches = re.findall(pattern, full_text, re.DOTALL)

    qa_docs = []
    for i, (pergunta, resposta) in enumerate(matches, 1):
        content = f"PERGUNTA: {pergunta.strip()}\nRESPOSTA: {resposta.strip()}"
        qa_docs.append(
            Document(
                page_content=content,
                metadata={"source": "FAQ", "numero": i}
            )
        )

    return qa_docs


def download_embedding():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    return HuggingFaceEmbeddings(model_name=model_name)
