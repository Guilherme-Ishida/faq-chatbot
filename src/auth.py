from functools import wraps

from flask import (
    session,
    redirect,
    url_for,
    flash
)

# =========================================================
# USERS HARDCODED
# =========================================================

USERS = {

    "admin": {

        "password": "admin123",

        "role": "admin",

        "name": "Administrador",
    },

    "usuario": {

        "password": "user123",

        "role": "user",

        "name": "Usuário",
    },
}

# =========================================================
# AUTHENTICATION
# =========================================================

def authenticate(
    username: str,
    password: str
):

    print("\n========== LOGIN ==========")
    print("USERNAME:", username)
    print("PASSWORD:", password)

    user = USERS.get(username)

    print("USER FOUND:", user)

    if not user:

        print("USUARIO NAO EXISTE")
        return None

    if user["password"] != password:

        print("SENHA INCORRETA")
        return None

    print("LOGIN OK")

    return {

        "username": username,

        "role": user["role"],

        "name": user["name"],
    }

# =========================================================
# SESSION
# =========================================================

def login_user(user: dict):

    session["username"] = user["username"]

    session["role"] = user["role"]

    session["name"] = user["name"]

    print("SESSION:", dict(session))


def logout_user():

    session.clear()


def current_user():

    if "username" not in session:
        return None

    return {

        "username": session["username"],

        "role": session["role"],

        "name": session["name"],
    }

# =========================================================
# DECORATORS
# =========================================================

def login_required(f):

    @wraps(f)

    def decorated(*args, **kwargs):

        if not current_user():

            flash(
                "Faça login para continuar.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return f(*args, **kwargs)

    return decorated


def admin_required(f):

    @wraps(f)

    def decorated(*args, **kwargs):

        user = current_user()

        if not user:

            flash(
                "Faça login para continuar.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        if user["role"] != "admin":

            flash(
                "Acesso restrito a administradores.",
                "danger"
            )

            return redirect(
                url_for("index")
            )

        return f(*args, **kwargs)

    return decorated