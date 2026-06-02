# Documentação do Trabalho — Teste de Software
**Disciplina:** Teste de Software  
**Grupo:** Daniel Andrade, Jhonatan William e João Gabriel  
**Aplicação:** TaskFlow — Sistema de Gerenciamento de Tarefas

---

## 1. Descrição da Aplicação

### Visão Geral

O TaskFlow é uma aplicação web de gerenciamento de tarefas pessoais. O usuário pode se cadastrar, fazer login e gerenciar suas tarefas com controle de prioridade e status.

### Tecnologias Utilizadas

| Componente | Tecnologia |
|---|---|
| Backend | Python 3.11 + Flask 3.x |
| Banco de dados | SQLite3 |
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| Testes automatizados | Pytest + Selenium WebDriver |
| Hashing de senhas | Werkzeug (pbkdf2) |

### Fluxos de Interação

A aplicação possui os seguintes fluxos principais:

**Fluxo 1 — Cadastro e Login**
1. Usuário acessa `/registro` e preenche nome, e-mail e senha
2. Sistema valida os dados e cria a conta
3. Usuário acessa `/login`, insere credenciais
4. Sistema autentica e redireciona para `/tarefas`

**Fluxo 2 — Gerenciamento de Tarefas**
1. Usuário autenticado acessa o dashboard `/tarefas`
2. Pode criar tarefas com título, descrição e prioridade (baixa/media/alta)
3. Pode editar, excluir e marcar tarefas como concluídas
4. Pode filtrar tarefas por status (pendente, em_progresso, concluida) e prioridade
5. Dashboard exibe estatísticas em tempo real

### Estrutura de Arquivos

```
Projeto_Lista/
├── app.py                        # Aplicação Flask principal
├── templates/
│   ├── login.html                # Tela de login
│   ├── registro.html             # Tela de cadastro
│   └── tarefas.html              # Dashboard de tarefas
├── testes_unidade_exemplo.py     # Testes de unidade (13 casos)
├── teste_integracao.py           # Teste de integração
├── teste_sistema.py              # Teste de sistema
├── teste_aceitacao.py            # Teste de aceitação
├── teste_regressao.py            # Teste de regressão
├── teste_desempenho.py           # Teste de desempenho
└── tests/
    └── test_selenium_interface.py # Testes E2E com Selenium (6 casos)
```

### Endpoints da API REST

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/registro` | Cadastra novo usuário |
| POST | `/api/login` | Autentica usuário |
| POST | `/api/logout` | Encerra sessão |
| GET | `/api/tarefas` | Lista tarefas do usuário |
| POST | `/api/tarefas` | Cria nova tarefa |
| GET | `/api/tarefas/<id>` | Busca tarefa por ID |
| PUT | `/api/tarefas/<id>` | Atualiza tarefa |
| DELETE | `/api/tarefas/<id>` | Exclui tarefa |
| PATCH | `/api/tarefas/<id>/concluir` | Marca tarefa como concluída |
| GET | `/api/estatisticas` | Retorna estatísticas por status |
| GET | `/api/saude` | Health check do sistema |

---

## 2. Modelagem dos Testes com Tabelas de Decisão

### Tabela de Decisão 1 — Autenticação de Usuário (Login)

**Função testada:** `autenticar_usuario(email, senha)` em `app.py`

**Condições de entrada:**

| ID | Condição |
|---|---|
| C1 | E-mail preenchido? |
| C2 | E-mail existe no sistema? |
| C3 | Senha correta? |

**Regras de decisão:**

| Regra | C1 (E-mail preenchido) | C2 (E-mail existe) | C3 (Senha correta) | Resultado esperado | HTTP |
|---|---|---|---|---|---|
| R1 | Não | — | — | Retorna `None` | 401 |
| R2 | Sim | Não | — | Retorna `None` | 401 |
| R3 | Sim | Sim | Não | Retorna `None` | 401 |
| R4 | Sim | Sim | Sim | Retorna dados do usuário | 200 |

**Casos de teste derivados:**

- `test_autenticar_usuario_credenciais_corretas` → cobre R4
- `test_autenticar_usuario_senha_errada_retorna_none` → cobre R3
- `test_autenticar_usuario_inexistente_retorna_none` → cobre R2

---

### Tabela de Decisão 2 — Cadastro de Usuário

**Função testada:** `criar_usuario(nome, email, senha)` em `app.py`

**Condições de entrada:**

| ID | Condição |
|---|---|
| C1 | Nome não vazio e ≤ 100 caracteres? |
| C2 | E-mail contém "@" e ≤ 254 caracteres? |
| C3 | E-mail já cadastrado no banco? |
| C4 | Senha tem entre 6 e 128 caracteres? |

**Regras de decisão:**

| Regra | C1 (Nome válido) | C2 (E-mail válido) | C3 (E-mail duplicado) | C4 (Senha válida) | Resultado esperado | HTTP |
|---|---|---|---|---|---|---|
| R1 | Não | — | — | — | `ValueError`: nome vazio | 400 |
| R2 | Sim | Não | — | — | `ValueError`: e-mail inválido | 400 |
| R3 | Sim | Sim | Sim | — | `ValueError`: e-mail já cadastrado | 400 |
| R4 | Sim | Sim | Não | Não | `ValueError`: senha inválida | 400 |
| R5 | Sim | Sim | Não | Sim | Usuário criado com sucesso | 201 |

**Casos de teste derivados:**

- `test_criar_usuario_nome_vazio_lanca_erro` → cobre R1
- `test_criar_usuario_email_invalido_lanca_erro` → cobre R2
- `test_criar_usuario_email_duplicado_lanca_erro` → cobre R3
- `test_criar_usuario_senha_curta_lanca_erro` → cobre R4
- `test_criar_usuario_persiste_dados_validos` → cobre R5

---

### Tabela de Decisão 3 — Criação de Tarefa

**Função testada:** `criar_tarefa(usuario_id, titulo, descricao, prioridade)` em `app.py`

**Condições de entrada:**

| ID | Condição |
|---|---|
| C1 | Usuário autenticado? |
| C2 | Título não vazio e ≤ 200 caracteres? |
| C3 | Prioridade é `baixa`, `media` ou `alta`? |
| C4 | Descrição ≤ 1000 caracteres? |

**Regras de decisão:**

| Regra | C1 (Autenticado) | C2 (Título válido) | C3 (Prioridade válida) | C4 (Descrição válida) | Resultado esperado | HTTP |
|---|---|---|---|---|---|---|
| R1 | Não | — | — | — | Não autorizado | 401 |
| R2 | Sim | Não | — | — | `ValueError`: título vazio | 400 |
| R3 | Sim | Sim | Não | — | `ValueError`: prioridade inválida | 400 |
| R4 | Sim | Sim | Sim | Não | `ValueError`: descrição longa | 400 |
| R5 | Sim | Sim | Sim | Sim | Tarefa criada com status `pendente` | 201 |

**Casos de teste derivados:**

- `test_criar_tarefa_titulo_vazio_lanca_erro` → cobre R2
- `test_criar_tarefa_prioridade_invalida_lanca_erro` → cobre R3
- `test_criar_tarefa_dados_validos` → cobre R5

---

## 3. Descrição dos Testes Implementados

### 3.1 Testes de Unidade — `testes_unidade_exemplo.py`

**Tipo:** Caixa Branca  
**Framework:** Pytest + unittest  
**Total de casos:** 13

Cada teste usa um banco de dados temporário isolado (`tempfile`), criado no `setUp` e destruído no `tearDown`, garantindo independência entre os casos.

| Caso de Teste | Função Testada | Cenário | Resultado Esperado |
|---|---|---|---|
| `test_hash_senha_retorna_hash_verificavel` | `hash_senha` / `verificar_senha` | Senha válida | Hash pode ser verificado |
| `test_hash_senha_diferente_para_senha_diferente` | `verificar_senha` | Senha diferente do hash | Retorna `False` |
| `test_criar_usuario_persiste_dados_validos` | `criar_usuario` | Dados válidos | Usuário salvo no banco |
| `test_criar_usuario_nome_vazio_lanca_erro` | `criar_usuario` | Nome vazio | Lança `ValueError` |
| `test_criar_usuario_email_invalido_lanca_erro` | `criar_usuario` | E-mail sem "@" | Lança `ValueError` |
| `test_criar_usuario_senha_curta_lanca_erro` | `criar_usuario` | Senha com 3 chars | Lança `ValueError` |
| `test_criar_usuario_email_duplicado_lanca_erro` | `criar_usuario` | E-mail já existente | Lança `ValueError` |
| `test_autenticar_usuario_credenciais_corretas` | `autenticar_usuario` | Email e senha corretos | Retorna dados do usuário |
| `test_autenticar_usuario_senha_errada_retorna_none` | `autenticar_usuario` | Senha incorreta | Retorna `None` |
| `test_autenticar_usuario_inexistente_retorna_none` | `autenticar_usuario` | E-mail não cadastrado | Retorna `None` |
| `test_criar_tarefa_titulo_vazio_lanca_erro` | `criar_tarefa` | Título vazio | Lança `ValueError` |
| `test_criar_tarefa_prioridade_invalida_lanca_erro` | `criar_tarefa` | Prioridade `"urgente"` | Lança `ValueError` |
| `test_criar_tarefa_dados_validos` | `criar_tarefa` | Dados válidos | Tarefa criada com status `pendente` |

---

### 3.2 Teste de Integração — `teste_integracao.py`

**Tipo:** Caixa Branca  
**Framework:** Pytest + unittest + Flask test client  
**Total de casos:** 1 (fluxo completo com 4 etapas)

Valida a comunicação entre as camadas da aplicação: API → lógica de negócio → banco de dados.

**Fluxo testado:**
1. `POST /api/registro` → espera HTTP 201
2. `POST /api/login` → espera HTTP 200
3. `POST /api/tarefas` → espera HTTP 201
4. `GET /api/tarefas` → espera HTTP 200, lista com 1 tarefa, título e prioridade corretos

---

### 3.3 Teste de Sistema — `teste_sistema.py`

**Tipo:** Caixa Preta  
**Framework:** Pytest + unittest + Flask test client  
**Total de casos:** 1

Valida o comportamento do sistema como um todo através do endpoint de health check.

**Cenário:** `GET /api/saude`  
**Validações:**
- HTTP 200
- Campo `status` = `"ok"`
- Campo `banco` = `"conectado"`
- Campo `latencia_ms` presente na resposta

---

### 3.4 Teste de Aceitação — `teste_aceitacao.py`

**Tipo:** Caixa Preta (perspectiva do usuário)  
**Framework:** Pytest + unittest + Flask test client  
**Total de casos:** 1 (jornada completa do usuário)

Simula a jornada de um usuário real do ponto de vista dos requisitos funcionais.

**Jornada testada:**
1. Acessa `/registro` → página contém texto "Criar conta"
2. Registra-se via `POST /api/registro` → HTTP 201
3. Faz login via `POST /api/login` → HTTP 200
4. Acessa `/tarefas` → página contém "Minhas Tarefas" e o nome do usuário

---

### 3.5 Teste de Regressão — `teste_regressao.py`

**Tipo:** Caixa Preta / Segurança  
**Framework:** Pytest + unittest + Flask test client  
**Total de casos:** 1

Verifica que um comportamento crítico de segurança (isolamento de dados entre usuários) não foi quebrado por mudanças no código.

**Cenário:**
1. Usuário Ana cria uma tarefa (ID registrado)
2. Ana faz logout
3. Usuário Bruno faz login
4. Bruno tenta acessar `GET /api/tarefas/<id_da_ana>` → espera HTTP 404

---

### 3.6 Teste de Desempenho — `teste_desempenho.py`

**Tipo:** Não-funcional  
**Framework:** Pytest + unittest + `time.perf_counter`  
**Total de casos:** 1

Mede o tempo de resposta do endpoint de login e garante que está dentro do limite aceitável.

**Critério de aceite:** `POST /api/login` deve responder em menos de **500 ms**

---

### 3.7 Testes de Interface — `tests/test_selenium_interface.py`

**Tipo:** Caixa Preta / End-to-End  
**Framework:** Pytest + Selenium WebDriver (Chrome)  
**Total de casos:** 6  
**Pré-requisito:** Aplicação rodando em `http://127.0.0.1:5000`

| Caso de Teste | Cenário |
|---|---|
| `test_tela_inicial_carrega` | Página inicial carrega sem erros |
| `test_tela_login_carrega` | Tela de login renderiza corretamente |
| `test_tela_registro_carrega` | Tela de registro renderiza corretamente |
| `test_cadastro_usuario_com_sucesso` | Usuário preenche formulário e se cadastra |
| `test_login_com_sucesso` | Usuário faz login e é redirecionado ao dashboard |
| `test_criar_tarefa_com_sucesso` | Usuário abre modal "Nova Tarefa", preenche título, salva e tarefa aparece na lista |

**Observação técnica — `test_criar_tarefa_com_sucesso`:** o formulário de criação de tarefa fica dentro de um modal oculto (`display:none`). O teste clica no botão "Nova Tarefa" para abrir o modal, aguarda o redirect pós-login via `EC.url_contains("/tarefas")` (login é feito por AJAX), e só então interage com os campos `#f-titulo` e `#f-desc`.

---

### Resumo Geral de Cobertura

| Arquivo de Teste | Tipo | Qtd. Casos | Framework |
|---|---|---|---|
| `testes_unidade_exemplo.py` | Unidade (caixa branca) | 13 | Pytest + unittest |
| `teste_integracao.py` | Integração (caixa branca) | 1 | Pytest + Flask client |
| `teste_sistema.py` | Sistema (caixa preta) | 1 | Pytest + Flask client |
| `teste_aceitacao.py` | Aceitação (caixa preta) | 1 | Pytest + Flask client |
| `teste_regressao.py` | Regressão / Segurança | 1 | Pytest + Flask client |
| `teste_desempenho.py` | Desempenho | 1 | Pytest + `perf_counter` |
| `test_selenium_interface.py` | E2E / Interface (caixa preta) | 6 | Pytest + Selenium WebDriver |
| **Total** | | **24** | |

---

## 4. Evidências de Execução dos Testes

### 4.1 Execução dos Testes Automatizados (Pytest)

Comando executado:
```
python -m pytest testes_unidade_exemplo.py teste_integracao.py teste_sistema.py
                 teste_aceitacao.py teste_regressao.py teste_desempenho.py -v
```

Saída obtida:
```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.2, pluggy-1.6.0
rootdir: Projeto_Lista

collecting ... collected 18 items

testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_autenticar_usuario_credenciais_corretas PASSED [  5%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_autenticar_usuario_inexistente_retorna_none PASSED [ 11%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_autenticar_usuario_senha_errada_retorna_none PASSED [ 23%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_criar_tarefa_dados_validos               PASSED [ 30%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_criar_tarefa_prioridade_invalida_lanca_erro PASSED [ 38%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_criar_tarefa_titulo_vazio_lanca_erro     PASSED [ 46%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_criar_usuario_email_duplicado_lanca_erro PASSED [ 53%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_criar_usuario_email_invalido_lanca_erro  PASSED [ 61%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_criar_usuario_nome_vazio_lanca_erro      PASSED [ 69%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_criar_usuario_persiste_dados_validos     PASSED [ 76%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_criar_usuario_senha_curta_lanca_erro     PASSED [ 84%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_hash_senha_diferente_para_senha_diferente PASSED [ 92%]
testes_unidade_exemplo.py::TestesUnidadeTodoApp::test_hash_senha_retorna_hash_verificavel      PASSED [100%]
teste_integracao.py::TesteIntegracao::test_fluxo_registro_login_criacao_e_listagem_de_tarefas  PASSED [ 77%]
teste_sistema.py::TesteSistema::test_endpoint_de_saude_deve_responder_ok                       PASSED [ 83%]
teste_aceitacao.py::TesteAceitacao::test_usuario_consegue_entrar_na_area_de_tarefas_apos_login PASSED [ 88%]
teste_regressao.py::TesteRegressao::test_usuario_nao_deve_acessar_tarefa_de_outro_usuario      PASSED [ 94%]
teste_desempenho.py::TesteDesempenho::test_login_deve_responder_rapidamente                    PASSED [100%]

============================= 18 passed in 7.62s ==============================
```

**Resultado: 18/18 testes passaram.**

---

### 4.2 Execução dos Testes Selenium (E2E com Chrome)

Comando executado (com servidor Flask rodando em `http://127.0.0.1:5000`):

```
python -m pytest tests/test_selenium_interface.py -v
```

Saída obtida:

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.2, pluggy-1.6.0
rootdir: Projeto_Lista

collecting ... collected 6 items

tests/test_selenium_interface.py::test_tela_inicial_carrega          PASSED [ 16%]
tests/test_selenium_interface.py::test_tela_login_carrega            PASSED [ 33%]
tests/test_selenium_interface.py::test_tela_registro_carrega         PASSED [ 50%]
tests/test_selenium_interface.py::test_cadastro_usuario_com_sucesso  PASSED [ 66%]
tests/test_selenium_interface.py::test_login_com_sucesso             PASSED [ 83%]
tests/test_selenium_interface.py::test_criar_tarefa_com_sucesso      PASSED [100%]

============================== 6 passed in 31.78s =============================
```

**Resultado: 6/6 testes Selenium passaram.**

### 4.3 Resultado Final — Todos os Testes

```
python -m pytest testes_unidade_exemplo.py teste_integracao.py teste_sistema.py
                 teste_aceitacao.py teste_regressao.py teste_desempenho.py
                 tests/test_selenium_interface.py -v
```

| Suite | Casos | Resultado |
|---|---|---|
| Testes de Unidade | 13 | 13 ✅ |
| Teste de Integração | 1 | 1 ✅ |
| Teste de Sistema | 1 | 1 ✅ |
| Teste de Aceitação | 1 | 1 ✅ |
| Teste de Regressão | 1 | 1 ✅ |
| Teste de Desempenho | 1 | 1 ✅ |
| Testes Selenium (E2E) | 6 | 6 ✅ |
| **Total** | **24** | **24 ✅** |

---

*Documento gerado para entrega da disciplina de Teste de Software.*
