# TaskFlow — Sistema de Lista de Tarefas

Aplicação Flask com frontend web completo, desenvolvida para suportar
todos os tipos de testes da atividade acadêmica.

## Estrutura do Projeto

```
todo_app/
├── app.py              # Aplicação principal (Flask + lógica de negócio)
├── requirements.txt    # Dependências
├── todo.db             # Banco SQLite (gerado automaticamente)
└── templates/
    ├── login.html      # Tela de login
    ├── registro.html   # Tela de cadastro
    └── tarefas.html    # Dashboard de tarefas
```

## Como Executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar o servidor
python app.py

# 3. Acessar no navegador
http://localhost:5000
```

## Endpoints da API REST

| Método | Endpoint                        | Descrição                  | Auth |
|--------|---------------------------------|----------------------------|------|
| POST   | /api/registro                   | Cadastrar usuário           | ✗    |
| POST   | /api/login                      | Autenticar usuário          | ✗    |
| POST   | /api/logout                     | Encerrar sessão             | ✗    |
| GET    | /api/tarefas                    | Listar tarefas              | ✓    |
| POST   | /api/tarefas                    | Criar tarefa                | ✓    |
| GET    | /api/tarefas/<id>               | Buscar tarefa               | ✓    |
| PUT    | /api/tarefas/<id>               | Atualizar tarefa            | ✓    |
| DELETE | /api/tarefas/<id>               | Excluir tarefa              | ✓    |
| PATCH  | /api/tarefas/<id>/concluir      | Marcar como concluída       | ✓    |
| GET    | /api/estatisticas               | Estatísticas do usuário     | ✓    |
| GET    | /api/saude                      | Health check do sistema     | ✗    |

## Funções Testáveis por Tipo de Teste

### Unidade
- `hash_senha(senha)`
- `criar_usuario(nome, email, senha)`
- `autenticar_usuario(email, senha)`
- `criar_tarefa(usuario_id, titulo, descricao, prioridade)`
- `atualizar_tarefa(tarefa_id, usuario_id, **campos)`
- `excluir_tarefa(tarefa_id, usuario_id)`
- `listar_tarefas(usuario_id, status, prioridade)`
- `concluir_tarefa(tarefa_id, usuario_id)`
- `estatisticas_tarefas(usuario_id)`

### Integração
- Fluxo: registro → login → criar tarefa → listar
- API + banco de dados

### Sistema
- Fluxo completo via endpoints REST
- Health check `/api/saude`

### Aceitação
- Login com credenciais válidas/inválidas
- CRUD completo de tarefas via UI

### Regressão
- Re-execução de todos os casos após mudanças

### Desempenho
- Tempo de login (< 200ms)
- Listagem com muitas tarefas
- Requisições simultâneas
