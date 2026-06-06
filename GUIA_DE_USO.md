# Guia de Uso e Estrutura do Projeto SIGEsporte

Este documento serve como um guia rápido para apresentar a estrutura do projeto, ensinar como utilizar os atalhos disponibilizados via `Makefile` e apresentar práticas recomendadas para o desenvolvimento.

---

## 1. Estrutura do Projeto

O repositório está estruturado baseando-se no framework **Django** com uma separação lógica de responsabilidades bem definida. Abaixo está a explicação dos principais diretórios e arquivos:

*   **`apps/`**: Diretório que concentra os módulos e funcionalidades do sistema.
    *   **`core/`**: Aplicação principal do sistema.
    *   **`security/`**: Aplicação responsável por regras de segurança e autenticação.
    *   *Nota arquitetural:* Cada aplicação dentro de `apps/` subdivide-se internamente em pastas focadas nas responsabilidades: `controllers/`, `models/`, `repositories/` e `services/`. Essa abordagem isola a regra de negócios do roteamento.
    *   **`utils/`**: Utilitários globais do projeto (scripts de logs, configuração, telemetria).
*   **`config/`**: Pasta de configurações globais do Django. Contém o arquivo `settings.py`, roteamento base `urls.py`, `asgi.py` e `wsgi.py`.
*   **`tests/`**: Onde os testes automatizados ficam armazenados, separados para testar funcionalidades específicas.
*   **`manage.py`**: Ponto de entrada padrão para os comandos administrativos do Django.
*   **`Makefile`**: Arquivo responsável por automatizar e simplificar a execução de comandos frequentes no projeto (como rodar testes, subir o servidor, etc.).
*   **`mkdocs.yml`**: Configuração global do MkDocs para geração do site estático de documentação.
*   **`requirements.txt`**: Lista de todas as dependências de pacotes Python necessárias para rodar o projeto.

---

## 2. O uso do `Makefile`

O `Makefile` foi configurado para simplificar a vida do desenvolvedor abstraindo comandos longos. Para utilizá-lo, basta digitar `make <comando>` no terminal (na raiz do projeto).

Aqui estão os comandos disponíveis e o que eles fazem:

| Comando | Descrição | Comando Original Executado |
| :--- | :--- | :--- |
| **`make help`** | Exibe a lista de todos os comandos disponíveis no Makefile. | `@echo ...` |
| **`make venv`** | Cria um ambiente virtual na pasta `.venv`. | `python3 -m venv .venv` |
| **`make install`** | Instala todas as dependências do `requirements.txt`. | `pip install -r requirements.txt` |
| **`make run`** | Inicia o servidor local de desenvolvimento do Django. | `python3 manage.py runserver` |
| **`make check`** | Realiza uma checagem/validação no projeto para encontrar possíveis problemas de configuração no Django. | `python3 manage.py check` |
| **`make migrations`**| Detecta as alterações feitas nos modelos e cria os arquivos de migração necessários. | `python3 manage.py makemigrations` |
| **`make migrate`** | Aplica as migrações (mudanças de esquema) no banco de dados. | `python3 manage.py migrate` |
| **`make shell`** | Abre o console interativo do Django já conectado ao contexto do banco de dados e aplicações. | `python3 manage.py shell` |
| **`make test`** | Executa a suíte de testes automatizados do sistema utilizando o **pytest**. | `pytest` |
| **`make lint`** | Roda a análise estática de código nas pastas `apps/` e `config/` usando o **pylint** para identificar problemas de formatação/bugs. | `pylint apps/ config/` |
| **`make clear`** | Efetua uma faxina geral no repositório: remove pastas `__pycache__`, arquivos compilados `.pyc`, caches do pytest e coverage, limpa logs e também exclui o ambiente virtual `.venv`. | Diversos comandos `rm` e `find` |
| **`make limpar`** | Similar ao `make clear`, mas preserva o ambiente virtual `.venv`. | Diversos comandos `rm` e `find` |
| **`make user`** | Cria um superusuário para acessar o painel administrativo. | `python manage.py createsuperuser` |
---

## 3. Fluxo de Trabalho Básico (Primeiros Passos)

Se você acabou de clonar o repositório, o passo a passo para começar a programar seria:

1.  **Crie o ambiente virtual:**
    ```bash
    make venv
    ```
2.  **Ative o ambiente virtual:**
    *   No Linux/MacOS: `source .venv/bin/activate`
    *   *(Nota: não se esqueça de sempre estar com o ambiente ativo antes de rodar os próximos passos)*
3.  **Instale as dependências:**
    ```bash
    make install
    ```
4.  **Crie e aplique o banco de dados (Migrations):**
    ```bash
    make migrate
    ```
5.  **Rode a aplicação localmente:**
    ```bash
    make run
    ```
    O servidor estará disponível por padrão em `http://127.0.0.1:8000/`. O software tem uma aplicação rodando no site: https://sigesporte.duat.site/

---

## 4. Dicas Úteis Adicionais

### Padronização (Templates)
Antes de criar uma nova *Issue* ou submeter um *Pull Request* no repositório remoto, confira a pasta `templates/` na branch docs. Nela existem padrões em formato `.md` que a equipe acordou usar para descrever novas funcionalidades, reportar bugs, formatar as mensagens de commit e criar nomes de branch adequados.

### Qualidade de Código
Habitue-se a rodar os testes e ferramentas de linting antes de submeter novos códigos:
*   `make test` para verificar se você não quebrou nada já existente.
*   `make lint` para garantir que as regras de estilo de código estão sendo respeitadas na equipe.
