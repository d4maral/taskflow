import os
import tempfile
import unittest

import app as todo_app


class TesteSistema(unittest.TestCase):
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

    def test_endpoint_de_saude_deve_responder_ok(self):
        resposta = self.client.get("/api/saude")

        self.assertEqual(resposta.status_code, 200)
        dados = resposta.get_json()
        self.assertEqual(dados["status"], "ok")
        self.assertEqual(dados["banco"], "conectado")
        self.assertIn("latencia_ms", dados)


if __name__ == "__main__":
    unittest.main()
