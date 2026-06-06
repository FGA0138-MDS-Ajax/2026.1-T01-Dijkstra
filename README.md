# SIGEsporte

Sistema de Gerenciamento Esportivo desenvolvido como projeto da disciplina de **Métodos de Desenvolvimento de Software**, ministrada pelo professor Ricardo Ajax na Universidade de Brasília (UnB).

🌐 **Site:** [https://sigesporte.duat.site/](https://sigesporte.duat.site/)
📚 **Documentação:** [https://fga0138-mds-ajax.github.io/2026.1-T01-Dijkstra/](https://fga0138-mds-ajax.github.io/2026.1-T01-Dijkstra/)

---

## Tecnologias

- **Python 3** + **Django 6.0.5**
- **SQLite** (banco de dados local para desenvolvimento)
- **pytest** + **pytest-cov** (testes e cobertura)
- **pylint** (análise estática de código)
- **django-environ** (gerenciamento de variáveis de ambiente)

---

## Arquitetura

O projeto adota uma arquitetura modular baseada em Django, com separação clara de responsabilidades:

```
2026.1-T01-Dijkstra/
├── apps/
│   ├── core/               # Aplicação principal do sistema
│   │   ├── controllers/    # Camada de controle (views)
│   │   ├── models/         # Modelos de dados (Eventos, Espaços, Organizações)
│   │   ├── repositories/   # Acesso ao banco de dados
│   │   └── services/       # Regras de negócio
│   ├── security/           # Autenticação e regras de segurança
│   └── utils/              # Utilitários globais (logs, config, telemetria)
├── config/                 # Configurações globais do Django
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── tests/                  # Testes automatizados
├── .env.example            # Exemplo de variáveis de ambiente
├── Makefile                # Atalhos de desenvolvimento
├── manage.py
└── requirements.txt
```

---

## Primeiros Passos

### Pré-requisitos

- Python 3.10+
- `pip`

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/fga-eps-mds/2026.1-T01-Dijkstra.git
cd 2026.1-T01-Dijkstra

# 2. Crie e ative o ambiente virtual
make venv
source .venv/bin/activate   # Linux/macOS

# 3. Instale as dependências
make install

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com seus valores

# 5. Aplique as migrações
make migrate

# 6. Inicie o servidor de desenvolvimento
make run
```

O servidor estará disponível em **http://127.0.0.1:8000/**.

---

## Comandos disponíveis (`Makefile`)

| Comando | Descrição |
| :--- | :--- |
| `make help` | Lista todos os comandos disponíveis |
| `make venv` | Cria o ambiente virtual em `.venv` |
| `make install` | Instala as dependências do `requirements.txt` |
| `make run` | Inicia o servidor de desenvolvimento |
| `make check` | Valida a configuração do Django |
| `make migrations` | Gera arquivos de migração |
| `make migrate` | Aplica as migrações no banco de dados |
| `make shell` | Abre o shell interativo do Django |
| `make test` | Executa os testes com pytest |
| `make lint` | Analisa o código com pylint |
| `make clear` | Remove caches, arquivos compilados e o `.venv` |
| `make limpar` | Remove caches e arquivos compilados (mantém o `.venv`) |
| `make user` | Cria um superusuário administrador |

---

## Testes

```bash
make test
```

Para visualizar o relatório de cobertura:

```bash
pytest --cov=apps --cov-report=term-missing
```

---

## Variáveis de Ambiente

Copie `.env.example` para `.env` e preencha os valores:

| Variável | Descrição |
| :--- | :--- |
| `SECRET_KEY` | Chave secreta do Django (use uma chave forte em produção) |
| `DEBUG` | `True` em desenvolvimento, `False` em produção |

---

## Contribuindo

Antes de abrir uma *Issue* ou submeter um *Pull Request*, consulte os templates disponíveis na branch `docs` e siga o fluxo abaixo:

1. Crie uma branch a partir de `developer` com um nome descritivo
2. Implemente as alterações
3. Rode `make lint` e `make test` antes de commitar
4. Abra um Pull Request com descrição clara do que foi feito

---

## Licença

Este projeto está sob a licença descrita no arquivo [LICENSE](LICENSE).
