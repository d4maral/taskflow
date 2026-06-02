import os
import tempfile
import time
import unittest

import app as todo_app


class TesteDesempenho(unittest.TestCase):
    def setUp(self):
        self.db_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_temp.close()

        todo_app.app.config["TESTING"] = True
        todo_app.DATABASE = self.db_temp.name

        with todo_app.app.app_context():
            todo_app.init_db()

        self.client = todo_app.app.test_client()
        self.client.post(
            "/api/registro",
            json={"nome": "Carlos", "email": "carlos@email.com", "senha": "segredo123"},
        )

    def tearDown(self):
        if os.path.exists(self.db_temp.name):
            os.unlink(self.db_temp.name)

    def test_login_deve_responder_rapidamente(self):
        inicio = time.perf_counter()
        resposta = self.client.post(
            "/api/login",
            json={"email": "carlos@email.com", "senha": "segredo123"},
        )
        duracao = time.perf_counter() - inicio

        self.assertEqual(resposta.status_code, 200)
        self.assertLess(duracao, 0.5)


if __name__ == "__main__":
    unittest.main()
