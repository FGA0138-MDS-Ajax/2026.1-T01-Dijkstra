# Relatório de Testes — SIGEsporte

Este documento detalha os testes automatizados implementados no **SIGEsporte**, como executá-los e os resultados obtidos na última execução da suíte de testes.

---

## 1. Como Executar os Testes

Os testes do projeto utilizam o framework `pytest` integrado ao Django (`pytest-django`) e são configurados para gerar relatórios de cobertura de código (`pytest-cov`).

### Pré-requisitos

Certifique-se de que o ambiente virtual está ativo e as dependências de desenvolvimento instaladas:

```bash
# 1. Ativar o ambiente virtual
source .venv/bin/activate

# 2. Instalar dependências (caso não tenha instalado)
make install
```

### Comandos de Execução

Você pode executar os testes utilizando os atalhos do `Makefile` ou rodando o `pytest` diretamente.

* **Execução Padrão (Rápida):**
  Executa toda a suíte de testes.
  ```bash
  make test
  ```
  *(Ou execute diretamente: `pytest`)*

* **Execução com Detalhamento (Verbose):**
  Mostra o nome de cada teste individual e seu status de execução.
  ```bash
  pytest -v
  ```

* **Relatório de Cobertura no Terminal:**
  Executa os testes e exibe a cobertura de cada arquivo do projeto diretamente no console.
  ```bash
  pytest --cov=apps --cov-report=term-missing
  ```

* **Relatório de Cobertura em HTML:**
  Gera um relatório interativo em HTML (salvo na pasta `htmlcov/`), permitindo visualizar quais linhas de código não foram cobertas pelos testes.
  ```bash
  pytest --cov=apps --cov-report=html
  ```

---

## 2. Testes Implementados

A suíte possui **391 testes automatizados** distribuídos entre as camadas de controle, regras de negócio, persistência de dados e segurança do sistema.

Abaixo está o detalhamento dos arquivos de teste e suas respectivas responsabilidades:

### 🔹 Módulo `core` (Aplicação Principal)

* **Controllers (Visualização e Roteamento):**
  * `test_crud_eventos_controller.py`: Testes de gerenciamento de eventos (criação, listagem, edição, detalhe e exclusão).
  * `test_espacos_controller.py`: Testes para controle e fluxo de espaços físicos disponíveis para eventos.
  * `test_eventos_controller.py`: Testes da API JSON de eventos, paginação, filtros por data e serialização de eventos (com/sem imagens).
  * `test_home_controller.py`: Testes da visualização principal (Home) com paginação e filtros.
  * `test_inscricoes_aluno_controller.py`: Fluxo de inscrição de alunos em eventos, validação de limite de vagas e cancelamentos.
  * `test_inscricoes_controller.py`: Gestão de inscrições (aprovação, reprovação individual/lote e exportação para arquivo CSV).
  * `test_membros_organizacao_controller.py`: Testes de vinculação de membros a organizações esportivas.
  * `test_organizacoes_controller.py`: Operações de CRUD para organizações esportivas.
  * `test_reservas_controller.py`: Controle de reservas de espaços físicos, contemplando aprovação, reprovação e cancelamento.
* **Models (Modelos de Banco de Dados):**
  * `test_espacos_models.py`, `test_eventos_models.py`, `test_inscricao_models.py`, `test_organizacoes_models.py`, `test_reservas_models.py`: Validação de integridade dos dados, representações `__str__` e validações de modelo personalizadas.
* **Repositories (Acesso a Dados):**
  * `test_espacos_repository.py`, `test_eventos_repository.py`, `test_organizacoes_repository.py`: Garantia do funcionamento correto das consultas SQL encapsuladas na camada de repositórios.
* **Services (Regras de Negócio):**
  * `test_espacos_service.py`, `test_eventos_service.py`, `test_organizacoes_service.py`: Validações de negócio de alta complexidade (conflitos de horário, limites de capacidade, regras de gestores).
* **Forms (Formulários):**
  * `test_forms.py`: Testes para validação e processamento de inputs dos formulários da aplicação `core`.

### 🔹 Módulo `security` (Segurança e Autenticação)

* `test_area_restrita_controller.py`: Teste de acesso e controle de permissões de acordo com os papéis do usuário (Aluno, Organizador, Gestor).
* `test_cadastro_controller.py`: Validação do fluxo de registro de novos usuários no sistema.
* `test_eventos_controller.py` (Security): Testes de permissões e privacidade específicas para ações de manipulação de eventos.
* `test_forms.py` (Security): Testes de validação dos formulários de login e cadastro.
* `test_security_controllers.py`: Fluxos de login, logout e autenticação geral do Django.
* `test_usuario_controller.py`: Testes para visualização e edição de perfis de usuário.
* `test_usuarios_repositories.py` & `test_usuarios_services.py`: Testes de segurança de dados do usuário e persistência.

### 🔹 Módulo `utils` (Utilitários do Sistema)

* `test_config.py`: Validação de configurações gerais e ambiente do projeto.
* `test_log_rotator.py` & `test_log_rotator_main.py`: Testes unitários para rotação automática e compactação de logs do sistema.
* `test_logger.py`: Testes do logger customizado e comportamento de gravação de arquivos de log.
* `test_telemetria.py`: Testes do coletor de estatísticas de execução de recursos.

---

## 3. Resultados dos Testes e Cobertura

Abaixo está o resultado da última execução completa da suíte de testes e o relatório de cobertura. O projeto atinge **100% de cobertura de código (Code Coverage)**.

### Execução dos Testes (`pytest`)

```text
============================= test session starts ==============================
platform linux -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0 -- /home/mont/2026.1-T01-Dijkstra/.venv/bin/python3
cachedir: .pytest_cache
django: version: 6.0.5, settings: config.settings (from ini)
rootdir: /home/mont/2026.1-T01-Dijkstra
configfile: pyproject.toml
plugins: django-4.10.0, cov-7.1.0
collecting ... collected 391 items

(Execução de 391 testes...)
........................................................................
============================= 391 passed in 48.27s =============================
```

### Relatório de Cobertura (`Coverage Report`)

```text
============================= tests coverage ==============================
_______________ coverage: platform linux, python 3.14.5-final-0 ________________

Name                                                                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------------------------------------------------
apps/__init__.py                                                                        0      0   100%
apps/core/__init__.py                                                                   0      0   100%
apps/core/admin.py                                                                      0      0   100%
apps/core/apps.py                                                                       4      0   100%
apps/core/controllers/__init__.py                                                       0      0   100%
apps/core/controllers/crud_eventos_controller.py                                       61      0   100%
apps/core/controllers/espacos_controller.py                                            56      0   100%
apps/core/controllers/eventos_controller.py                                            63      0   100%
apps/core/controllers/home_controller.py                                               16      0   100%
apps/core/controllers/inscricoes_controller.py                                        118      0   100%
apps/core/controllers/membros_organizacao_controller.py                                34      0   100%
apps/core/controllers/organizacoes_controller.py                                       62      0   100%
apps/core/controllers/reservas_controller.py                                          128      0   100%
apps/core/forms.py                                                                     69      0   100%
apps/core/migrations/0001_initial.py                                                    8      0   100%
apps/core/migrations/0002_dados_iniciais.py                                            16      0   100%
apps/core/migrations/0003_alter_evento_descricao_alter_evento_horario_and_more.py       4      0   100%
apps/core/migrations/0004_espacofisico.py                                               7      0   100%
apps/core/migrations/0005_evento_status.py                                              6      0   100%
apps/core/migrations/0005_organizacao.py                                                7      0   100%
apps/core/migrations/0006_merge_0002_dados_iniciais_0005_organizacao.py                 4      0   100%
apps/core/migrations/0007_alter_evento_descricao_alter_evento_horario.py                4      0   100%
apps/core/migrations/0008_inscricao.py                                                  7      0   100%
apps/core/migrations/0009_evento_vagas_ocupadas.py                                      4      0   100%
apps/core/migrations/0010_reservaespaco.py                                              7      0   100%
apps/core/migrations/0011_usuarioorganizacao.py                                         6      0   100%
apps/core/migrations/0012_inscricao_avaliacao.py                                        6      0   100%
apps/core/migrations/0013_alter_usuarioorganizacao_options_and_more.py                  6      0   100%
apps/core/migrations/0013_evento_vinculo_organizador_organizacao.py                    31      0   100%
apps/core/migrations/0014_merge_20260624_1810.py                                        4      0   100%
apps/core/migrations/__init__.py                                                        0      0   100%
apps/core/models/__init__.py                                                            6      0   100%
apps/core/models/espacos_models.py                                                     32      0   100%
apps/core/models/eventos_models.py                                                     31      0   100%
apps/core/models/inscricao_models.py                                                   28      0   100%
apps/core/models/organizacoes_models.py                                                27      0   100%
apps/core/models/reservas_models.py                                                    37      0   100%
apps/core/repositories/__init__.py                                                      0      0   100%
apps/core/repositories/espacos_repository.py                                           30      0   100%
apps/core/repositories/eventos_repository.py                                           49      0   100%
apps/core/repositories/organizacoes_repository.py                                      46      0   100%
apps/core/services/__init__.py                                                          0      0   100%
apps/core/services/espacos_service.py                                                  22      0   100%
apps/core/services/eventos_service.py                                                  27      0   100%
apps/core/services/organizacoes_service.py                                             33      0   100%
apps/core/urls.py                                                                      40      0   100%
apps/security/__init__.py                                                               0      0   100%
apps/security/admin.py                                                                  7      0   100%
apps/security/apps.py                                                                   4      0   100%
apps/security/controllers/__init__.py                                                   0      0   100%
apps/security/controllers/area_restrita_controller.py                                 122      0   100%
apps/security/controllers/cadastro_controller.py                                       22      0   100%
apps/security/controllers/usuario_controller.py                                        66      0   100%
apps/security/forms.py                                                                 27      0   100%
apps/security/migrations/0001_initial.py                                               10      0   100%
apps/security/migrations/0002_alter_usuario_groups.py                                   4      0   100%
apps/security/migrations/__init__.py                                                    0      0   100%
apps/security/models/__init__.py                                                        2      0   100%
apps/security/models/usuario_models.py                                                 33      0   100%
apps/security/repositories/__init__.py                                                  0      0   100%
apps/security/repositories/usuarios_repositories.py                                    36      0   100%
apps/security/services/__init__.py                                                      0      0   100%
apps/security/services/usuarios_services.py                                             9      0   100%
apps/security/urls.py                                                                   7      0   100%
apps/utils/__init__.py                                                                  0      0   100%
apps/utils/config.py                                                                    6      0   100%
apps/utils/log_rotator.py                                                              68      0   100%
apps/utils/logger.py                                                                   61      0   100%
apps/utils/telemetria.py                                                               27      0   100%
-----------------------------------------------------------------------------------------------------------------
TOTAL                                                                                1657      0   100%
================================================================================================================-
```
