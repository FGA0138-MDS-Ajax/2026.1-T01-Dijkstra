# SIGEsporte — Sistema de Gerenciamento Esportivo

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-6.0.5-green.svg)](https://www.djangoproject.com/)
[![Tests Status](https://img.shields.io/badge/tests-391%20passed-success.svg)](#)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#)
[![Linter](https://img.shields.io/badge/pylint-10.0%2F10-brightgreen.svg)](#)

O **SIGEsporte** é um Sistema de Gerenciamento Esportivo desenvolvido como projeto prático na disciplina de **Métodos de Desenvolvimento de Software (MDS)** da Universidade de Brasília (UnB), ministrada pelo professor Ricardo Ajax. O sistema visa facilitar a organização de eventos esportivos, a reserva de espaços físicos (como quadras e campos) e a inscrição de alunos nas atividades do campus.

---

## 🌐 Links do Projeto

* 🚀 **Sistema em Produção:** [https://sigesporte.duat.site/](https://sigesporte.duat.site/)
* 📚 **Documentação Oficial (GitHub Pages):** [https://fga0138-mds-ajax.github.io/2026.1-T01-Dijkstra/](https://fga0138-mds-ajax.github.io/2026.1-T01-Dijkstra/)

---

## 📚 Documentação (GitHub Pages / MkDocs)

A nossa documentação oficial é publicada via GitHub Pages e gerada automaticamente pelo **MkDocs**. Ela contém toda a fundamentação teórica, metodológica e relatórios de progresso do projeto.

Ao acessar a página de documentação, você encontrará:

1. **Atas de Reunião:** Registros semanais e de checkpoints contendo discussões, decisões e divisão de tarefas de todas as sprints.
2. **Documento de Visão:** Declaração de escopo, perfis de acesso (Aluno, Organizador, Gestor), matriz de comunicação, gerenciamento de riscos e o planejamento detalhado das sprints.
3. **Documento de Arquitetura:** Visão lógica, padrões arquiteturais (MVC adaptado para Repository/Service), modelos de banco de dados e diagramas de classes e de casos de uso.
4. **Protótipos:** Links e detalhamentos dos protótipos de baixa e alta fidelidade.
5. **Roteiros de Implantação:** Guia completo de deploy em VPS, configuração do host com Incus, segurança, Nginx e Docker Compose.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+ / Python 3.14
* **Web Framework:** Django 6.0.5 (com Django REST Framework / Django templates)
* **Banco de Dados:** SQLite (em desenvolvimento e testes) e PostgreSQL (em produção via Docker)
* **Suíte de Testes:** pytest + pytest-django + pytest-cov
* **Qualidade de Código (Linting):** pylint + pylint-django
* **Ambiente isolado:** Docker e Docker Compose

---

## 📐 Arquitetura do Sistema

O projeto adota uma arquitetura limpa, com clara divisão de responsabilidade e desacoplamento do framework Django:

```text
2026.1-T01-Dijkstra/
├── apps/
│   ├── core/               # Domínio principal da aplicação
│   │   ├── controllers/    # Camada de controle e visualização (Views)
│   │   ├── models/         # Modelos de dados (Eventos, Espaços, Inscrições, Reservas)
│   │   ├── repositories/   # Acesso ao banco de dados (Queries e persistência)
│   │   └── services/       # Regras e validações de negócio
│   ├── security/           # Autenticação, controle de perfil e segurança
│   └── utils/              # Ferramentas globais (logs, telemetria, configurações)
├── config/                 # Configurações globais do Django
├── tests/                  # Testes automatizados da aplicação
├── Makefile                # Automação de comandos e atalhos de dev
└── docker-compose.yml      # Configuração para deploy e produção
```

---

## 🚀 Primeiros Passos (Desenvolvimento Local)

> [!NOTE]
> Para orientações detalhadas de boas práticas, padronização de código, fluxo de Git e ambientação rápida da equipe, consulte o nosso [Guia de Uso (GUIA_DE_USO.md)](GUIA_DE_USO.md).

### Pré-requisitos
* Python 3.10 ou superior
* Gerenciador de pacotes `pip`
* Terminal Bash (Linux/macOS)

### Instalação e Execução

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/fga-eps-mds/2026.1-T01-Dijkstra.git
   cd 2026.1-T01-Dijkstra
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   make venv
   source .venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   make install
   ```

4. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais locais
   ```

5. **Aplique as migrações no banco de dados:**
   ```bash
   make migrate
   ```

6. **Inicie o servidor local:**
   ```bash
   make run
   ```
   A aplicação estará disponível em `http://127.0.0.1:8000/`.

---

## Testes Automatizados e Cobertura

O projeto adota a prática de **100% de cobertura de código** em todos os arquivos de lógica de negócio e controllers para garantir a estabilidade do sistema. A suíte é composta por **391 testes unitários e de integração**.

> [!NOTE]
> Para um detalhamento completo dos testes implementados, seus respectivos arquivos e histórico de resultados da última execução, consulte o [Relatório de Testes (RELATORIO_TESTES.md)](RELATORIO_TESTES.md).

### Executar os Testes
Para rodar toda a suíte de testes usando o `pytest`:
```bash
make test
```

### Relatório de Cobertura no Terminal
```bash
pytest --cov=apps --cov-report=term-missing
```

### Relatório de Cobertura em HTML
Para gerar uma visualização detalhada em HTML:
```bash
pytest --cov=apps --cov-report=html
# Abra a página gerada no seu navegador: htmlcov/index.html
```

---

## 📜 Comandos Disponíveis (`Makefile`)

O `Makefile` abstrai comandos longos do Django e utilitários. Use `make <comando>` na raiz do repositório:

| Comando | Descrição | Comando Original |
| :--- | :--- | :--- |
| `make help` | Exibe a mensagem de ajuda e comandos | `@echo ...` |
| `make venv` | Cria o ambiente virtual em `.venv` | `python3 -m venv .venv` |
| `make install` | Instala dependências do `requirements.txt` | `pip install -r requirements.txt` |
| `make run` | Inicia o servidor local de desenvolvimento | `python3 manage.py runserver` |
| `make check` | Valida a integridade das configurações Django | `python3 manage.py check` |
| `make migrations` | Cria novas migrações para os modelos | `python3 manage.py makemigrations` |
| `make migrate` | Aplica as migrações no banco de dados | `python3 manage.py migrate` |
| `make shell` | Abre o shell do Django com o contexto carregado | `python3 manage.py shell` |
| `make test` | Executa a suíte de testes com `pytest` | `pytest` |
| `make lint` | Executa análise estática de código com `pylint` | `pylint apps/ config/` |
| `make clear` | Remove caches, arquivos `.pyc` e deleta a `.venv` | `rm -rf .venv ...` |
| `make limpar` | Remove caches e arquivos `.pyc`, mantendo a `.venv` | `rm -rf .pytest_cache ...` |
| `make user` | Cria um superusuário administrador | `python manage.py createsuperuser` |

---

## 🔒 Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha as variáveis conforme necessário:

* `SECRET_KEY`: Chave secreta única do Django.
* `DEBUG`: Defina como `True` em desenvolvimento e `False` em produção.
* `CSRF_TRUSTED_ORIGINS`: URLs confiáveis para requisições CSRF (necessário para deploy).

---

## 🤝 Contribuindo

1. Crie uma branch de recurso a partir da branch `developer` (`feat/nome-do-recurso` ou `fix/nome-do-bug`).
2. Escreva testes para a nova funcionalidade ou correção.
3. Certifique-se de que os testes estão passando (`make test`) e o linter não acusa erros (`make lint`).
4. Abra um Pull Request detalhado apontando para a branch `developer`.

---

## 📄 Licença

Este projeto é software livre licenciado sob a [MIT License](LICENSE).
