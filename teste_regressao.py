import os
import tempfile
import unittest

import app as todo_app


class TesteRegressao(unittest.TestCase):
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

    def test_usuario_nao_deve_acessar_tarefa_de_outro_usuario(self):
        self.client.post(
            "/api/registro",
            json={"nome": "Ana", "email": "ana@email.com", "senha": "segredo123"},
        )
        self.client.post(
            "/api/login",
            json={"email": "ana@email.com", "senha": "segredo123"},
        )
        resposta_tarefa = self.client.post(
            "/api/tarefas",
            json={"titulo": "Tarefa privada", "descricao": "sigilo", "prioridade": "media"},
        )
        tarefa_id = resposta_tarefa.get_json()["id"]
        self.client.post("/api/logout", json={})

        self.client.post(
            "/api/registro",
            json={"nome": "Bruno", "email": "bruno@email.com", "senha": "segredo123"},
        )
        self.client.post(
            "/api/login",
            json={"email": "bruno@email.com", "senha": "segredo123"},
        )

        resposta_busca = self.client.get(f"/api/tarefas/{tarefa_id}")

        self.assertEqual(resposta_busca.status_code, 404)
        self.assertEqual(resposta_busca.get_json()["erro"], "Tarefa não encontrada.")


if __name__ == "__main__":
    unittest.main()
