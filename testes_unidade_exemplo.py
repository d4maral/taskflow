import os
import tempfile
import unittest

import app as todo_app


class TestesUnidadeTodoApp(unittest.TestCase):
    def setUp(self):
        self.db_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_temp.close()

        todo_app.app.config["TESTING"] = True
        todo_app.DATABASE = self.db_temp.name

        with todo_app.app.app_context():
            todo_app.init_db()

    def tearDown(self):
        if os.path.exists(self.db_temp.name):
            os.unlink(self.db_temp.name)

    # ── hash_senha ────────────────────────────────────────────────────────────

    def test_hash_senha_retorna_hash_verificavel(self):
        senha = "senha123"
        hash_gerado = todo_app.hash_senha(senha)
        self.assertTrue(todo_app.verificar_senha(senha, hash_gerado))

    def test_hash_senha_diferente_para_senha_diferente(self):
        hash1 = todo_app.hash_senha("senha123")
        self.assertFalse(todo_app.verificar_senha("outrasenha", hash1))

    # ── criar_usuario ─────────────────────────────────────────────────────────

    def test_criar_usuario_persiste_dados_validos(self):
        with todo_app.app.app_context():
            usuario = todo_app.criar_usuario("Maria", "maria@email.com", "segredo123")
            usuario_db = todo_app.buscar_usuario_por_id(usuario["id"])

        self.assertIsNotNone(usuario_db)
        self.assertEqual(usuario_db["nome"], "Maria")
        self.assertEqual(usuario_db["email"], "maria@email.com")

    def test_criar_usuario_nome_vazio_lanca_erro(self):
        with todo_app.app.app_context():
            with self.assertRaises(ValueError):
                todo_app.criar_usuario("", "x@email.com", "senha123")

    def test_criar_usuario_email_invalido_lanca_erro(self):
        with todo_app.app.app_context():
            with self.assertRaises(ValueError):
                todo_app.criar_usuario("João", "emailsemarroba", "senha123")

    def test_criar_usuario_senha_curta_lanca_erro(self):
        with todo_app.app.app_context():
            with self.assertRaises(ValueError):
                todo_app.criar_usuario("João", "joao@email.com", "123")

    def test_criar_usuario_email_duplicado_lanca_erro(self):
        with todo_app.app.app_context():
            todo_app.criar_usuario("João", "joao@email.com", "senha123")
            with self.assertRaises(ValueError):
                todo_app.criar_usuario("João2", "joao@email.com", "outrasenha")

    # ── autenticar_usuario ────────────────────────────────────────────────────

    def test_autenticar_usuario_credenciais_corretas(self):
        with todo_app.app.app_context():
            todo_app.criar_usuario("Ana", "ana@email.com", "minhasenha")
            resultado = todo_app.autenticar_usuario("ana@email.com", "minhasenha")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["email"], "ana@email.com")

    def test_autenticar_usuario_senha_errada_retorna_none(self):
        with todo_app.app.app_context():
            todo_app.criar_usuario("Ana", "ana@email.com", "minhasenha")
            resultado = todo_app.autenticar_usuario("ana@email.com", "senhaerrada")
        self.assertIsNone(resultado)

    def test_autenticar_usuario_inexistente_retorna_none(self):
        with todo_app.app.app_context():
            resultado = todo_app.autenticar_usuario("naoexiste@email.com", "qualquer")
        self.assertIsNone(resultado)

    # ── criar_tarefa ──────────────────────────────────────────────────────────

    def test_criar_tarefa_titulo_vazio_lanca_erro(self):
        with todo_app.app.app_context():
            with self.assertRaises(ValueError):
                todo_app.criar_tarefa(1, "")

    def test_criar_tarefa_prioridade_invalida_lanca_erro(self):
        with todo_app.app.app_context():
            with self.assertRaises(ValueError):
                todo_app.criar_tarefa(1, "Minha tarefa", prioridade="urgente")

    def test_criar_tarefa_dados_validos(self):
        with todo_app.app.app_context():
            usuario = todo_app.criar_usuario("Bob", "bob@email.com", "senha123")
            tarefa = todo_app.criar_tarefa(usuario["id"], "Estudar pytest", prioridade="alta")
        self.assertEqual(tarefa["titulo"], "Estudar pytest")
        self.assertEqual(tarefa["status"], "pendente")
        self.assertEqual(tarefa["prioridade"], "alta")


if __name__ == "__main__":
    unittest.main()
