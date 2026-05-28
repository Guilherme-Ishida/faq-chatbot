from flask import Flask, render_template, request, redirect, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

from src.helper import (
    download_embedding,
    load_pdf_files,
    extract_qa_pairs
)

from src.prompt import system_prompt
from src.guardrail import has_injection

from src.auth import (
    authenticate,
    login_user,
    logout_user,
    current_user,
    login_required,
    admin_required,
)

from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv

import os


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY não está definida")

os.environ["GROQ_API_KEY"] = api_key

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "troque-esta-chave-em-producao"
)

# =========================================================
# SECURITY
# =========================================================

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[],
)

csp = {
    "default-src": "'self'",

    "script-src": [
        "'self'",
        "'unsafe-inline'",
        "https://code.jquery.com",
        "https://ajax.googleapis.com",
    ],

    "style-src": [
        "'self'",
        "'unsafe-inline'",
        "https://fonts.googleapis.com",
        "https://use.fontawesome.com",
    ],

    "font-src": [
        "'self'",
        "https://fonts.gstatic.com",
        "https://use.fontawesome.com",
        "data:",
    ],

    "img-src": [
        "'self'",
        "data:",
    ],

    "connect-src": [
        "'self'",
    ],
}

Talisman(
    app,
    force_https=False,
    strict_transport_security=False,
    content_security_policy=csp,
    frame_options='DENY',
    referrer_policy='strict-origin-when-cross-origin',
)

# =========================================================
# PATHS
# =========================================================

CHROMA_DIR = "chroma_db"
UPLOAD_DIR = "data"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# =========================================================
# EMBEDDINGS / VECTORSTORE
# =========================================================

embedding = download_embedding()

vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embedding
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# =========================================================
# LLM
# =========================================================

chatModel = ChatGroq(
    model="llama-3.3-70b-versatile"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(
    chatModel,
    prompt
)

rag_chain = create_retrieval_chain(
    retriever,
    question_answer_chain
)

# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user():
        return redirect(url_for("index"))

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = authenticate(
            username,
            password
        )

        if user:

            login_user(user)

            return redirect(
                url_for("index")
            )

        flash(
            "Usuário ou senha inválidos.",
            "danger"
        )

    return render_template("login.html")


@app.route("/logout")
def logout():

    logout_user()

    return redirect(url_for("login"))

# =========================================================
# CHAT
# =========================================================

@app.route("/")
@login_required
def index():

    user = current_user()

    return render_template(
        "chat.html",
        user=user
    )


@app.route("/get", methods=["POST"])
@login_required
@limiter.limit(
    "5 per minute",
    error_message="Muitas requisições. Tente novamente em breve."
)
def chat():

    msg = request.form.get(
        "msg",
        ""
    ).strip()

    if not msg or len(msg) > 500:
        return "Entrada inválida.", 400

    if has_injection(msg):
        return "Não posso processar essa solicitação.", 400

    try:

        response = rag_chain.invoke(
            {"input": msg}
        )

        return str(response["answer"])

    except Exception as e:

        app.logger.error(
            "Erro ao invocar RAG chain: %s",
            e
        )

        return "Serviço temporariamente indisponível.", 503

# =========================================================
# ADMIN PANEL
# =========================================================

@app.route("/admin")
@admin_required
def admin():

    docs = []

    if os.path.isdir(UPLOAD_DIR):

        docs = [
            f for f in os.listdir(UPLOAD_DIR)
            if f.lower().endswith(".pdf")
        ]

    try:

        total_vetores = (
            vectorstore._collection.count()
        )

    except Exception:

        total_vetores = "—"

    return render_template(
        "admin.html",
        user=current_user(),
        docs=docs,
        total_vetores=total_vetores,
    )

# =========================================================
# UPLOAD PDF
# =========================================================

@app.route("/admin/upload", methods=["POST"])
@admin_required
def admin_upload():

    file = request.files.get("document")

    if (
        not file
        or not file.filename.lower().endswith(".pdf")
    ):

        flash(
            "Envie um arquivo PDF válido.",
            "danger"
        )

        return redirect(url_for("admin"))

    # -----------------------------------------------------
    # SAVE PDF
    # -----------------------------------------------------

    dest = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    file.save(dest)

    # -----------------------------------------------------
    # INDEX PDF
    # -----------------------------------------------------

    try:

        docs = load_pdf_files(UPLOAD_DIR)

        new_docs = [
            d for d in docs
            if file.filename in d.metadata.get("source", "")
        ]

        qa_docs = (
            extract_qa_pairs(new_docs)
            if new_docs else []
        )

        if qa_docs:

            vectorstore.add_documents(
                qa_docs
            )

            flash(
                f"'{file.filename}' indexado "
                f"com sucesso "
                f"({len(qa_docs)} pares Q&A).",
                "success"
            )

        else:

            flash(
                f"'{file.filename}' salvo, "
                f"mas nenhum par Q&A foi encontrado.",
                "warning"
            )

    except Exception as e:

        flash(
            f"Erro ao indexar: {e}",
            "danger"
        )

    return redirect(url_for("admin"))

# =========================================================
# DELETE PDF
# =========================================================

@app.route("/admin/delete", methods=["POST"])
@admin_required
def admin_delete():

    filename = request.form.get(
        "filename",
        ""
    ).strip()

    if not filename:

        flash(
            "Nome do arquivo não informado.",
            "danger"
        )

        return redirect(url_for("admin"))

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    # -----------------------------------------------------
    # REMOVE FILE
    # -----------------------------------------------------

    if os.path.exists(file_path):

        os.remove(file_path)

    # -----------------------------------------------------
    # REMOVE VECTORS
    # -----------------------------------------------------

    try:

        result = vectorstore._collection.get(
            include=["metadatas"]
        )

        ids_to_delete = []

        for doc_id, metadata in zip(
            result["ids"],
            result["metadatas"]
        ):

            source = metadata.get(
                "source",
                ""
            )

            source = source.replace("\\", "/")

            if filename.lower() in source.lower():

                ids_to_delete.append(doc_id)

        if ids_to_delete:

            vectorstore._collection.delete(
                ids=ids_to_delete
            )

            flash(
                f"'{filename}' removido "
                f"com sucesso "
                f"({len(ids_to_delete)} vetores apagados).",
                "success"
            )

        else:

            flash(
                f"Arquivo removido do disco, "
                f"mas nenhum vetor foi encontrado.",
                "warning"
            )

    except Exception as e:

        flash(
            f"Erro ao remover vetores: {e}",
            "danger"
        )

    return redirect(url_for("admin"))

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False,
        use_reloader=False
    )