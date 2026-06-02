"""
Sistema de Lista de Tarefas
Aplicação Flask com suporte a testes de unidade, integração, sistema,
aceitação, regressão e desempenho.
"""

import os
import sqlite3
import time
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash

# ─── Configuração ────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-secreta-lista-tarefas-2024")
DATABASE = "todo.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Prioridades válidas
PRIORIDADES_VALIDAS = {"baixa", "media", "alta"}
STATUS_VALIDOS = {"pendente", "em_progresso", "concluida"}


# ─── Banco de Dados ──────────────────────────────────────────────────────────

def get_db():
    """Retorna conexão com o banco de dados (uma por requisição)."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    """Cria as tabelas se não existirem."""
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nome      TEXT    NOT NULL,
                email     TEXT    NOT NULL UNIQUE,
                senha     TEXT    NOT NULL,
                criado_em TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tarefas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id  INTEGER NOT NULL,
                titulo      TEXT    NOT NULL,
                descricao   TEXT    DEFAULT '',
                prioridade  TEXT    NOT NULL DEFAULT 'media',
                status      TEXT    NOT NULL DEFAULT 'pendente',
                criado_em   TEXT    NOT NULL,
                atualizado_em TEXT  NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );

            CREATE INDEX IF NOT EXISTS idx_tarefas_usuario ON tarefas(usuario_id);
            CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
        """)
        db.commit()
    logger.info("Banco de dados inicializado.")


# ─── Utilitários ─────────────────────────────────────────────────────────────

def hash_senha(senha: str) -> str:
    """Retorna hash seguro da senha (pbkdf2 com salt)."""
    return generate_password_hash(senha)


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Verifica senha contra hash armazenado."""
    return check_password_hash(hash_armazenado, senha)


def login_required(f):
    """Decorator: redireciona para login se não autenticado."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario_id" not in session:
            if request.is_json:
                return jsonify({"erro": "Não autenticado"}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def row_to_dict(row):
    return dict(row) if row else None


# ─── Módulo de Usuários ───────────────────────────────────────────────────────

def criar_usuario(nome: str, email: str, senha: str) -> dict:
    """
    Cria um novo usuário.
    Retorna dict com dados do usuário ou lança ValueError.
    """
    if not nome or not nome.strip():
        raise ValueError("Nome não pode ser vazio.")
    if len(nome.strip()) > 100:
        raise ValueError("Nome deve ter no máximo 100 caracteres.")
    if not email or "@" not in email:
        raise ValueError("E-mail inválido.")
    if len(email.strip()) > 254:
        raise ValueError("E-mail inválido.")
    if not senha or len(senha) < 6:
        raise ValueError("Senha deve ter pelo menos 6 caracteres.")
    if len(senha) > 128:
        raise ValueError("Senha deve ter no máximo 128 caracteres.")

    db = get_db()
    existente = db.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone()
    if existente:
        raise ValueError("E-mail já cadastrado.")

    agora = datetime.utcnow().isoformat()
    cur = db.execute(
        "INSERT INTO usuarios (nome, email, senha, criado_em) VALUES (?, ?, ?, ?)",
        (nome.strip(), email.strip().lower(), hash_senha(senha), agora),
    )
    db.commit()
    logger.info("Usuário criado: %s", email)
    return {"id": cur.lastrowid, "nome": nome.strip(), "email": email.strip().lower(), "criado_em": agora}


def autenticar_usuario(email: str, senha: str) -> dict | None:
    """
    Autentica credenciais.
    Retorna dados do usuário ou None se inválido.
    """
    if not email or not senha:
        return None
    db = get_db()
    row = db.execute(
        "SELECT * FROM usuarios WHERE email = ?",
        (email.strip().lower(),),
    ).fetchone()
    if row and verificar_senha(senha, row["senha"]):
        return row_to_dict(row)
    return None


def buscar_usuario_por_id(usuario_id: int) -> dict | None:
    db = get_db()
    row = db.execute("SELECT id, nome, email, criado_em FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return row_to_dict(row)


# ─── Módulo de Tarefas ────────────────────────────────────────────────────────

def criar_tarefa(usuario_id: int, titulo: str, descricao: str = "",
                 prioridade: str = "media") -> dict:
    """Cria tarefa para o usuário. Lança ValueError em dados inválidos."""
    if not titulo or not titulo.strip():
        raise ValueError("Título não pode ser vazio.")
    if len(titulo.strip()) > 200:
        raise ValueError("Título deve ter no máximo 200 caracteres.")
    if len(descricao) > 1000:
        raise ValueError("Descrição deve ter no máximo 1000 caracteres.")
    if prioridade not in PRIORIDADES_VALIDAS:
        raise ValueError(f"Prioridade inválida. Use: {PRIORIDADES_VALIDAS}")

    agora = datetime.utcnow().isoformat()
    db = get_db()
    cur = db.execute(
        """INSERT INTO tarefas (usuario_id, titulo, descricao, prioridade, status, criado_em, atualizado_em)
           VALUES (?, ?, ?, ?, 'pendente', ?, ?)""",
        (usuario_id, titulo.strip(), descricao.strip(), prioridade, agora, agora),
    )
    db.commit()
    logger.info("Tarefa criada: '%s' (usuário %d)", titulo, usuario_id)
    return {"id": cur.lastrowid, "usuario_id": usuario_id, "titulo": titulo.strip(),
            "descricao": descricao.strip(), "prioridade": prioridade,
            "status": "pendente", "criado_em": agora, "atualizado_em": agora}


def listar_tarefas(usuario_id: int, status: str = None, prioridade: str = None) -> list[dict]:
    """Lista tarefas do usuário com filtros opcionais."""
    db = get_db()
    query = "SELECT * FROM tarefas WHERE usuario_id = ?"
    params = [usuario_id]

    if status:
        if status not in STATUS_VALIDOS:
            raise ValueError(f"Status inválido. Use: {STATUS_VALIDOS}")
        query += " AND status = ?"
        params.append(status)

    if prioridade:
        if prioridade not in PRIORIDADES_VALIDAS:
            raise ValueError(f"Prioridade inválida. Use: {PRIORIDADES_VALIDAS}")
        query += " AND prioridade = ?"
        params.append(prioridade)

    query += " ORDER BY criado_em DESC"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def buscar_tarefa(tarefa_id: int, usuario_id: int) -> dict | None:
    """Busca tarefa garantindo que pertence ao usuário."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?",
        (tarefa_id, usuario_id),
    ).fetchone()
    return row_to_dict(row)


def atualizar_tarefa(tarefa_id: int, usuario_id: int, **campos) -> dict:
    """
    Atualiza campos de uma tarefa. Campos aceitos:
    titulo, descricao, prioridade, status
    """
    tarefa = buscar_tarefa(tarefa_id, usuario_id)
    if not tarefa:
        raise ValueError("Tarefa não encontrada.")

    campos_validos = {"titulo", "descricao", "prioridade", "status"}
    atualizacoes = {}

    for campo, valor in campos.items():
        if campo not in campos_validos:
            continue
        if campo == "titulo" and (not valor or not valor.strip()):
            raise ValueError("Título não pode ser vazio.")
        if campo == "prioridade" and valor not in PRIORIDADES_VALIDAS:
            raise ValueError(f"Prioridade inválida. Use: {PRIORIDADES_VALIDAS}")
        if campo == "status" and valor not in STATUS_VALIDOS:
            raise ValueError(f"Status inválido. Use: {STATUS_VALIDOS}")
        atualizacoes[campo] = valor.strip() if isinstance(valor, str) else valor

    if not atualizacoes:
        return tarefa

    agora = datetime.utcnow().isoformat()
    atualizacoes["atualizado_em"] = agora

    set_clause = ", ".join(f"{c} = ?" for c in atualizacoes)
    valores = list(atualizacoes.values()) + [tarefa_id, usuario_id]
    db = get_db()
    db.execute(
        f"UPDATE tarefas SET {set_clause} WHERE id = ? AND usuario_id = ?", valores
    )
    db.commit()
    logger.info("Tarefa %d atualizada.", tarefa_id)
    return buscar_tarefa(tarefa_id, usuario_id)


def excluir_tarefa(tarefa_id: int, usuario_id: int) -> bool:
    """Exclui tarefa. Retorna True se excluída, False se não encontrada."""
    tarefa = buscar_tarefa(tarefa_id, usuario_id)
    if not tarefa:
        return False
    db = get_db()
    db.execute("DELETE FROM tarefas WHERE id = ? AND usuario_id = ?", (tarefa_id, usuario_id))
    db.commit()
    logger.info("Tarefa %d excluída.", tarefa_id)
    return True


def concluir_tarefa(tarefa_id: int, usuario_id: int) -> dict:
    """Atalho para marcar tarefa como concluída."""
    return atualizar_tarefa(tarefa_id, usuario_id, status="concluida")


def estatisticas_tarefas(usuario_id: int) -> dict:
    """Retorna contagem de tarefas por status."""
    db = get_db()
    rows = db.execute(
        "SELECT status, COUNT(*) as total FROM tarefas WHERE usuario_id = ? GROUP BY status",
        (usuario_id,),
    ).fetchall()
    stats = {"pendente": 0, "em_progresso": 0, "concluida": 0, "total": 0}
    for r in rows:
        stats[r["status"]] = r["total"]
        stats["total"] += r["total"]
    return stats


# ─── Rotas Web (Frontend) ─────────────────────────────────────────────────────

@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect(url_for("tarefas_page"))
    return redirect(url_for("login_page"))


@app.route("/login", methods=["GET"])
def login_page():
    if "usuario_id" in session:
        return redirect(url_for("tarefas_page"))
    return render_template("login.html")


@app.route("/registro", methods=["GET"])
def registro_page():
    return render_template("registro.html")


@app.route("/tarefas", methods=["GET"])
@login_required
def tarefas_page():
    usuario = buscar_usuario_por_id(session["usuario_id"])
    return render_template("tarefas.html", usuario=usuario)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ─── API REST ─────────────────────────────────────────────────────────────────

@app.route("/api/registro", methods=["POST"])
def api_registro():
    dados = request.get_json() or {}
    try:
        usuario = criar_usuario(dados.get("nome", ""), dados.get("email", ""), dados.get("senha", ""))
        return jsonify({"mensagem": "Usuário criado com sucesso.", "usuario": usuario}), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/login", methods=["POST"])
def api_login():
    dados = request.get_json() or {}
    inicio = time.time()
    usuario = autenticar_usuario(dados.get("email", ""), dados.get("senha", ""))
    duracao = time.time() - inicio

    if not usuario:
        return jsonify({"erro": "Credenciais inválidas."}), 401

    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]
    logger.info("Login bem-sucedido em %.4fs — usuário %d", duracao, usuario["id"])
    return jsonify({"mensagem": "Login realizado.", "usuario": {"id": usuario["id"], "nome": usuario["nome"]}}), 200


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"mensagem": "Logout realizado."}), 200


@app.route("/api/tarefas", methods=["GET"])
@login_required
def api_listar_tarefas():
    status = request.args.get("status")
    prioridade = request.args.get("prioridade")
    try:
        tarefas = listar_tarefas(session["usuario_id"], status=status, prioridade=prioridade)
        return jsonify(tarefas), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/tarefas", methods=["POST"])
@login_required
def api_criar_tarefa():
    dados = request.get_json() or {}
    try:
        tarefa = criar_tarefa(
            session["usuario_id"],
            dados.get("titulo", ""),
            dados.get("descricao", ""),
            dados.get("prioridade", "media"),
        )
        return jsonify(tarefa), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/tarefas/<int:tarefa_id>", methods=["GET"])
@login_required
def api_buscar_tarefa(tarefa_id):
    tarefa = buscar_tarefa(tarefa_id, session["usuario_id"])
    if not tarefa:
        return jsonify({"erro": "Tarefa não encontrada."}), 404
    return jsonify(tarefa), 200


@app.route("/api/tarefas/<int:tarefa_id>", methods=["PUT"])
@login_required
def api_atualizar_tarefa(tarefa_id):
    dados = request.get_json() or {}
    try:
        tarefa = atualizar_tarefa(tarefa_id, session["usuario_id"], **dados)
        return jsonify(tarefa), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/tarefas/<int:tarefa_id>", methods=["DELETE"])
@login_required
def api_excluir_tarefa(tarefa_id):
    excluida = excluir_tarefa(tarefa_id, session["usuario_id"])
    if not excluida:
        return jsonify({"erro": "Tarefa não encontrada."}), 404
    return jsonify({"mensagem": "Tarefa excluída."}), 200


@app.route("/api/tarefas/<int:tarefa_id>/concluir", methods=["PATCH"])
@login_required
def api_concluir_tarefa(tarefa_id):
    try:
        tarefa = concluir_tarefa(tarefa_id, session["usuario_id"])
        return jsonify(tarefa), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/estatisticas", methods=["GET"])
@login_required
def api_estatisticas():
    stats = estatisticas_tarefas(session["usuario_id"])
    return jsonify(stats), 200


@app.route("/api/saude", methods=["GET"])
def api_saude():
    """Endpoint de health check para testes de sistema."""
    inicio = time.time()
    try:
        db = get_db()
        db.execute("SELECT 1").fetchone()
        duracao = (time.time() - inicio) * 1000
        return jsonify({"status": "ok", "banco": "conectado", "latencia_ms": round(duracao, 2)}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
