import os
import tempfile
import unittest

import app as todo_app


class TesteIntegracao(unittest.TestCase):
    def setUp(self):
        self.db_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_temp.close()

        todo_app.app.config["TESTING"] = True
        todo_app.DATABASE = self.db_temp.name

        with todo_app.app.app_context():
            todo_app.init_db()

        self.client = todo_app.app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_temp.name):
            os.unlink(self.db_temp.name)

    def test_fluxo_registro_login_criacao_e_listagem_de_tarefas(self):
        resposta_registro = self.client.post(
            "/api/registro",
            json={"nome": "Maria", "email": "maria@email.com", "senha": "segredo123"},
        )
        self.assertEqual(resposta_registro.status_code, 201)

        resposta_login = self.client.post(
            "/api/login",
            json={"email": "maria@email.com", "senha": "segredo123"},
        )
        self.assertEqual(resposta_login.status_code, 200)

        resposta_criacao = self.client.post(
            "/api/tarefas",
            json={"titulo": "Estudar Flask", "descricao": "Capitulo 1", "prioridade": "alta"},
        )
        self.assertEqual(resposta_criacao.status_code, 201)

        resposta_listagem = self.client.get("/api/tarefas")
        self.assertEqual(resposta_listagem.status_code, 200)

        tarefas = resposta_listagem.get_json()
        self.assertEqual(len(tarefas), 1)
        self.assertEqual(tarefas[0]["titulo"], "Estudar Flask")
        self.assertEqual(tarefas[0]["prioridade"], "alta")


if __name__ == "__main__":
    unittest.main()
