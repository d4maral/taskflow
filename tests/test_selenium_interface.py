import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    navegador = webdriver.Chrome(options=options)

    yield navegador

    navegador.quit()


def test_tela_inicial_carrega(driver):
    driver.get(BASE_URL)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    conteudo_pagina = driver.page_source.lower()

    assert "taskflow" in conteudo_pagina or "login" in conteudo_pagina or "tarefas" in conteudo_pagina

def test_tela_login_carrega(driver):
    driver.get(f"{BASE_URL}/login")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    conteudo_pagina = driver.page_source.lower()

    assert "login" in conteudo_pagina or "entrar" in conteudo_pagina


def test_tela_registro_carrega(driver):
    driver.get(f"{BASE_URL}/registro")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    conteudo_pagina = driver.page_source.lower()

    assert "criar conta" in conteudo_pagina or "cadastro" in conteudo_pagina or "registro" in conteudo_pagina

def encontrar_primeiro_elemento_visivel(driver, seletores):
    for seletor in seletores:
        elementos = driver.find_elements(By.CSS_SELECTOR, seletor)

        for elemento in elementos:
            if elemento.is_displayed():
                return elemento

    raise AssertionError(f"Nenhum elemento visível encontrado para os seletores: {seletores}")


def test_cadastro_usuario_com_sucesso(driver):
    email_teste = f"usuario_selenium_{int(time.time())}@teste.com"

    driver.get(f"{BASE_URL}/registro")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    campo_nome = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='nome']",
        "input[name='name']",
        "input[name='usuario']",
        "input[id='nome']",
        "input[id='name']",
        "input[id='usuario']",
        "input[type='text']"
    ])

    campo_email = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='email']",
        "input[id='email']",
        "input[type='email']"
    ])

    campo_senha = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='senha']",
        "input[name='password']",
        "input[id='senha']",
        "input[id='password']",
        "input[type='password']"
    ])

    campo_nome.send_keys("Usuário Selenium")
    campo_email.send_keys(email_teste)
    campo_senha.send_keys("senha123")

    botao_submit = encontrar_primeiro_elemento_visivel(driver, [
        "button[type='submit']",
        "input[type='submit']",
        "button"
    ])

    botao_submit.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    conteudo_pagina = driver.page_source.lower()

    assert (
        "login" in conteudo_pagina
        or "entrar" in conteudo_pagina
        or "tarefas" in conteudo_pagina
        or "minhas tarefas" in conteudo_pagina
        or "conta" in conteudo_pagina
        or "sucesso" in conteudo_pagina
    )

def test_login_com_sucesso(driver):
    email_teste = f"login_selenium_{int(time.time())}@teste.com"
    senha_teste = "senha123"

    driver.get(f"{BASE_URL}/registro")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    campo_nome = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='nome']",
        "input[name='name']",
        "input[name='usuario']",
        "input[id='nome']",
        "input[id='name']",
        "input[id='usuario']",
        "input[type='text']"
    ])

    campo_email = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='email']",
        "input[id='email']",
        "input[type='email']"
    ])

    campo_senha = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='senha']",
        "input[name='password']",
        "input[id='senha']",
        "input[id='password']",
        "input[type='password']"
    ])

    campo_nome.send_keys("Usuário Login Selenium")
    campo_email.send_keys(email_teste)
    campo_senha.send_keys(senha_teste)

    botao_submit = encontrar_primeiro_elemento_visivel(driver, [
        "button[type='submit']",
        "input[type='submit']",
        "button"
    ])

    botao_submit.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    driver.delete_all_cookies()

    driver.get(f"{BASE_URL}/login")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    campo_email_login = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='email']",
        "input[id='email']",
        "input[type='email']"
    ])

    campo_senha_login = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='senha']",
        "input[name='password']",
        "input[id='senha']",
        "input[id='password']",
        "input[type='password']"
    ])

    campo_email_login.send_keys(email_teste)
    campo_senha_login.send_keys(senha_teste)

    botao_entrar = encontrar_primeiro_elemento_visivel(driver, [
        "button[type='submit']",
        "input[type='submit']",
        "button"
    ])

    botao_entrar.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    conteudo_pagina = driver.page_source.lower()

    assert (
        "minhas tarefas" in conteudo_pagina
        or "tarefas" in conteudo_pagina
        or "dashboard" in conteudo_pagina
        or "usuário login selenium" in conteudo_pagina
    )

def test_criar_tarefa_com_sucesso(driver):
    email_teste = f"tarefa_selenium_{int(time.time())}@teste.com"
    senha_teste = "senha123"
    titulo_tarefa = f"Tarefa criada pelo Selenium {int(time.time())}"

    # Cadastro do usuário
    driver.get(f"{BASE_URL}/registro")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    campo_nome = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='nome']",
        "input[name='name']",
        "input[name='usuario']",
        "input[id='nome']",
        "input[id='name']",
        "input[id='usuario']",
        "input[type='text']"
    ])

    campo_email = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='email']",
        "input[id='email']",
        "input[type='email']"
    ])

    campo_senha = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='senha']",
        "input[name='password']",
        "input[id='senha']",
        "input[id='password']",
        "input[type='password']"
    ])

    campo_nome.send_keys("Usuário Tarefa Selenium")
    campo_email.send_keys(email_teste)
    campo_senha.send_keys(senha_teste)

    botao_submit = encontrar_primeiro_elemento_visivel(driver, [
        "button[type='submit']",
        "input[type='submit']",
        "button"
    ])

    botao_submit.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Garante que não ficou logado automaticamente
    driver.delete_all_cookies()

    # Login do usuário cadastrado
    driver.get(f"{BASE_URL}/login")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    campo_email_login = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='email']",
        "input[id='email']",
        "input[type='email']"
    ])

    campo_senha_login = encontrar_primeiro_elemento_visivel(driver, [
        "input[name='senha']",
        "input[name='password']",
        "input[id='senha']",
        "input[id='password']",
        "input[type='password']"
    ])

    campo_email_login.send_keys(email_teste)
    campo_senha_login.send_keys(senha_teste)

    botao_entrar = encontrar_primeiro_elemento_visivel(driver, [
        "button[type='submit']",
        "input[type='submit']",
        "button"
    ])

    botao_entrar.click()

    # Aguarda redirect para /tarefas após login via AJAX
    WebDriverWait(driver, 15).until(
        EC.url_contains("/tarefas")
    )

    # Abre o modal clicando em "Nova Tarefa"
    botao_nova_tarefa = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Nova Tarefa')]"))
    )
    botao_nova_tarefa.click()

    # Aguarda o campo de título ficar visível dentro do modal
    campo_titulo = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "f-titulo"))
    )
    campo_titulo.send_keys(titulo_tarefa)

    campo_desc = driver.find_element(By.ID, "f-desc")
    campo_desc.send_keys("Descrição criada automaticamente pelo Selenium.")

    botao_salvar = driver.find_element(By.XPATH, "//button[text()='Salvar']")
    botao_salvar.click()

    # Aguarda o modal fechar e a tarefa aparecer na lista
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "f-titulo"))
    )

    conteudo_pagina = driver.page_source

    assert titulo_tarefa in conteudo_pagina