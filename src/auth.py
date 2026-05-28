from functools import wraps

from flask import (
    session,
    redirect,
    url_for,
    flash
)

from werkzeug.security import check_password_hash

# =========================================================
# USERS
# =========================================================

USERS = {

    "admin": {

        "password_hash": "scrypt:32768:8:1$EfU4N21fgabAoaDD$c12ef0e127c06434c48eac25512a0d4ded098b7ab219407a6bac4a93c6ef65e225836c353790fd110e366b714a03ced36e1cf1eb9ae0266508c625554590b897",

        "role": "admin",

        "name": "Administrador",
    },

    "usuario": {

        "password_hash": "scrypt:32768:8:1$VkBJ1lanXTNmxqe1$a94026fa7d5ad4c4382404c04f3af8c654b765a8512af6228553af1cd26c907a49bb1a4d677661783d99ae27d5169c1deac028af11b146d05f74f8b54398205f",

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

    user = USERS.get(username)

    if not user:
        return None

    if not check_password_hash(user["password_hash"], password):
        return None

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
