from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from src.helper import download_embedding
from src.prompt import system_prompt
from src.guardrail import has_injection
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY não está definida")
os.environ["GROQ_API_KEY"] = api_key

app = Flask(__name__)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[],
)

csp = {
    'default-src': "'self'",
    'script-src': "'self' code.jquery.com",
    'style-src': "'self' fonts.googleapis.com use.fontawesome.com",
    'font-src': "'self' fonts.gstatic.com use.fontawesome.com",
    'img-src': "'self' data:",
    'connect-src': "'self'",
}
Talisman(
    app,
    force_https=False,
    strict_transport_security=False,
    content_security_policy=csp,
    frame_options='DENY',
    referrer_policy='strict-origin-when-cross-origin',
)

embedding = download_embedding()

vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

chatModel = ChatGroq(model="llama-3.3-70b-versatile")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)


@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["POST"])
@limiter.limit("5 per minute", error_message="Muitas requisições. Tente novamente em breve.")
def chat():
    msg = request.form.get("msg", "").strip()
    if not msg or len(msg) > 500:
        return "Entrada inválida.", 400
    if has_injection(msg):
        return "Não posso processar essa solicitação.", 400
    try:
        response = rag_chain.invoke({"input": msg})
        return str(response["answer"])
    except Exception as e:
        app.logger.error("Erro ao invocar RAG chain: %s", e)
        return "Serviço temporariamente indisponível.", 503


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)
