from flask import (
    Flask, request, render_template, redirect, url_for,
    flash, session, abort, send_from_directory
)
import sqlite3, os, re, uuid, mimetypes
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# ----------------- CONFIG -----------------
app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET", "troque-isto-em-producao")  # use variável de ambiente em prod

DB_NAME = "biblioteca.db"
UPLOAD_FOLDER = "uploads"
DOC_FOLDER = os.path.join(UPLOAD_FOLDER, "documentos")
COMP_FOLDER = os.path.join(UPLOAD_FOLDER, "comprovantes")

os.makedirs(DOC_FOLDER, exist_ok=True)
os.makedirs(COMP_FOLDER, exist_ok=True)

# Cookies mais rígidos
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # True atrás de HTTPS
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10 MB por request
)

# extensões permitidas para upload
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".pdf"}

# ----------------- DB -----------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,           -- agora é HASH
        nome TEXT NOT NULL,
        endereco TEXT NOT NULL,
        telefone TEXT NOT NULL,
        multas REAL DEFAULT 0.0,
        documento TEXT,
        comprovante TEXT
    )
    """)
    conn.commit()
    conn.close()

# ----------------- UTILS -----------------
def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

def rand_filename(original_name: str) -> str:
    base = secure_filename(original_name) or "file"
    _, ext = os.path.splitext(base)
    ext = ext.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("Extensão de arquivo não permitida.")
    return f"{uuid.uuid4().hex}{ext}"

def is_safe_file(path: str) -> bool:
    # pequena checagem de type; não é bala de prata, mas ajuda
    mime, _ = mimetypes.guess_type(path)
    return (mime and (mime.startswith("image/") or mime == "application/pdf"))

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login primeiro.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

# ----------------- ROUTES -----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        cpf = request.form.get("cpf", "")
        senha = request.form.get("senha", "")
        nome = request.form.get("nome", "")
        endereco = request.form.get("endereco", "")
        telefone = request.form.get("telefone", "")

        if not all([cpf, senha, nome, endereco, telefone]):
            flash("Preencha todos os campos.")
            return redirect(url_for("register"))

        if not validar_cpf(cpf):
            flash("CPF inválido!")
            return redirect(url_for("register"))

        # hash de senha
        senha_hash = generate_password_hash(senha)

        # uploads (opcionais)
        documento = request.files.get("documento")
        comprovante = request.files.get("comprovante")

        doc_filename = None
        comp_filename = None
        try:
            if documento and documento.filename:
                doc_filename = rand_filename(documento.filename)
                doc_path = os.path.join(DOC_FOLDER, doc_filename)
                documento.save(doc_path)
                if not is_safe_file(doc_path):  # checagem simples de mimetype
                    os.remove(doc_path)
                    raise ValueError("Tipo de arquivo de documento inválido.")

            if comprovante and comprovante.filename:
                comp_filename = rand_filename(comprovante.filename)
                comp_path = os.path.join(COMP_FOLDER, comp_filename)
                comprovante.save(comp_path)
                if not is_safe_file(comp_path):
                    os.remove(comp_path)
                    raise ValueError("Tipo de arquivo de comprovante inválido.")
        except ValueError as e:
            flash(str(e))
            return redirect(url_for("register"))

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO usuarios (cpf, senha, nome, endereco, telefone, documento, comprovante)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cpf, senha_hash, nome, endereco, telefone, doc_filename, comp_filename))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("Erro: CPF já cadastrado!")
            return redirect(url_for("register"))
        conn.close()
        flash("Usuário cadastrado com sucesso!")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cpf = request.form.get("cpf", "")
        senha = request.form.get("senha", "")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE cpf=?", (cpf,)).fetchone()
        conn.close()

        if user and check_password_hash(user["senha"], senha):
            # zera a sessão antiga e cria nova (evita fixation)
            session.clear()
            session["user_id"] = user["id"]
            session["nome"] = user["nome"]
            session.permanent = True  # segue config de cookie
            flash("Login realizado com sucesso!")
            return redirect(url_for("profile"))
        else:
            flash("CPF ou senha inválidos.")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta.")
    return redirect(url_for("login"))

@app.route("/profile")
@login_required
def profile():
    # só pega o usuário logado
    uid = session["user_id"]
    conn = get_db_connection()
    u = conn.execute("SELECT * FROM usuarios WHERE id=?", (uid,)).fetchone()
    conn.close()
    if not u:
        session.clear()
        return redirect(url_for("login"))
    return render_template("profile.html", u=u, nome=session.get("nome"))

# servir arquivos: APENAS se o arquivo pertencer ao usuário logado
@app.route("/uploads/<tipo>/<filename>")
@login_required
def uploaded_file(tipo, filename):
    uid = session["user_id"]

    if tipo == "documentos":
        folder = DOC_FOLDER
        coluna = "documento"
    elif tipo == "comprovantes":
        folder = COMP_FOLDER
        coluna = "comprovante"
    else:
        abort(404)

    conn = get_db_connection()
    row = conn.execute(f"SELECT {coluna} FROM usuarios WHERE id=?", (uid,)).fetchone()
    conn.close()

    if not row or row[coluna] != filename:
        abort(403)  # proibido acessar arquivo que não é seu

    path = os.path.join(folder, filename)
    if not os.path.isfile(path):
        abort(404)

    return send_from_directory(folder, filename, as_attachment=False)

# --------- MAIN ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
