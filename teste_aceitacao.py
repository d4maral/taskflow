import os
import tempfile
import unittest

import app as todo_app


class TesteAceitacao(unittest.TestCase):
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

    def test_usuario_consegue_entrar_na_area_de_tarefas_apos_login(self):
        pagina_registro = self.client.get("/registro")
        self.assertEqual(pagina_registro.status_code, 200)
        self.assertIn("Criar conta", pagina_registro.get_data(as_text=True))

        resposta_registro = self.client.post(
            "/api/registro",
            json={"nome": "Joao", "email": "joao@email.com", "senha": "segredo123"},
        )
        self.assertEqual(resposta_registro.status_code, 201)

        resposta_login = self.client.post(
            "/api/login",
            json={"email": "joao@email.com", "senha": "segredo123"},
        )
        self.assertEqual(resposta_login.status_code, 200)

        pagina_tarefas = self.client.get("/tarefas")
        html = pagina_tarefas.get_data(as_text=True)

        self.assertEqual(pagina_tarefas.status_code, 200)
        self.assertIn("Minhas Tarefas", html)
        self.assertIn("Joao", html)


if __name__ == "__main__":
    unittest.main()
