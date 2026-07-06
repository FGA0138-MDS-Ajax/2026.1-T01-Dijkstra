# Roteiro de Testes Funcionais — SIGEsporte

## Histórico de Revisão

| Data | Versão | Descrição | Autor |
|------|--------|-----------|-------|
| 06/07/2026 | 1.0 | Criação do roteiro de testes funcionais | Welder |

---

## 1. Introdução

### 1.1 Objetivo

Este documento define o roteiro de testes funcionais do sistema **SIGEsporte**, descrevendo os casos de teste que verificam, sob a perspectiva do usuário final, o comportamento das funcionalidades implementadas. Os testes aqui descritos são **manuais e caixa-preta**, executados via interface web, e complementam os testes automatizados do projeto (executados com `make test` / `pytest`).

### 1.2 Escopo

**Incluído no escopo:**

- Autenticação e cadastro de usuários (login, logout, cadastro, recuperação de senha);
- Mural público de eventos, filtros e detalhamento de eventos;
- Inscrição de alunos em eventos e ciclo de aprovação de inscrições;
- Criação, edição, publicação e exclusão de eventos (organizador);
- Gestão de inscritos e exportação de lista em CSV;
- Cadastro e gestão de espaços físicos (gestor);
- Solicitação, aprovação, reprovação e cancelamento de reservas de espaço, incluindo detecção de conflito de agenda;
- Organizações esportivas e gestão de membros;
- Área restrita, gestão de usuários e controle de acesso por perfil.

**Fora do escopo:**

- Testes de desempenho, carga e estresse;
- Testes automatizados de unidade e integração (cobertos pelo `pytest`);
- Testes de segurança ofensivos (pentest);
- Funcionalidades ainda não implementadas (ex.: notificações de novos eventos — RF04; dashboard de ocupação — RF12).

### 1.3 Referências

- [Documento de Visão](../documentos/documento_de_visao/escopo_visao_do_produto.md) — requisitos funcionais (RF01–RF12) e não funcionais;
- [Documento de Arquitetura](../documentos/documento_de_arquitetura/documento_de_arquitetura.md);
- [Protótipo de Alta Fidelidade](../prototipos/nao_funcional/prototipo_nao_funcional.md);
- Roteiros de implantação — [Visão Geral](../roteiros/main.md).

---

## 2. Ambiente de Teste

### 2.1 Preparação

| Item | Descrição |
|------|-----------|
| Aplicação | Django (SIGEsporte), executada localmente ou em VPS |
| Subida local | `docker compose up` ou `make install && make migrate && make run` |
| URL base | `http://localhost:8000` |
| Admin Django | `http://localhost:8000/admin/` (superusuário criado com `python manage.py createsuperuser`) |
| Navegadores | Google Chrome e Mozilla Firefox (versões atuais) |
| Banco de dados | SQLite (padrão do ambiente de desenvolvimento), com migrações aplicadas |

### 2.2 Massa de Dados

Antes da execução, criar os usuários de teste abaixo. O cadastro público (`/security/cadastro/`) cria usuários com perfil **Aluno**; os demais perfis devem ser ajustados pelo Admin Django ou pela tela de gestão de usuários (perfil Gestor).

| Usuário | Matrícula (login) | Perfil | Uso nos testes |
|---------|-------------------|--------|----------------|
| Aluno de Teste | `190000001` | Aluno (AL) | Inscrições, mural, área restrita |
| Aluno Secundário | `190000002` | Aluno (AL) | Concorrência de vagas, duplicidade |
| Organizador de Teste | `190000003` | Organizador (OR) | Eventos, inscritos, reservas, organizações |
| Gestor de Teste | `190000004` | Gestor (GE) | Espaços, aprovação de reservas, usuários |
| Usuário Inativo | `190000005` | Aluno (AL), `is_active = False` | Bloqueio de login |

Dados de apoio mínimos:

- 1 organização esportiva (ex.: "Atlética Dijkstra") com o Organizador de Teste como membro;
- 2 espaços físicos (ex.: "Quadra Coberta" — Disponível; "Campo Sintético" — Em Manutenção);
- 3 eventos: um **Publicado** com vagas, um **Publicado** com capacidade 1 (para teste de lotação) e um **Rascunho**.

### 2.3 Critérios de Entrada e Saída

- **Entrada:** ambiente no ar, migrações aplicadas, massa de dados criada.
- **Saída:** 100% dos casos executados; nenhum caso de prioridade **Alta** com falha aberta.

---

## 3. Convenções

### 3.1 Identificação dos Casos

Os casos seguem o padrão `CT-<módulo>-<sequencial>`:

| Prefixo | Módulo |
|---------|--------|
| AUT | Autenticação e Cadastro |
| MUR | Mural de Eventos |
| INS | Inscrições em Eventos |
| EVT | Gestão de Eventos |
| GIN | Gestão de Inscritos |
| ESP | Espaços Físicos |
| RES | Reservas de Espaço |
| ORG | Organizações |
| USU | Gestão de Usuários |
| ACE | Controle de Acesso |

### 3.2 Prioridade e Status de Execução

- **Prioridade:** Alta (fluxo principal/MUST), Média (fluxo alternativo/SHOULD), Baixa (complementar/COULD).
- **Status de execução:** Passou ✅ · Falhou ❌ · Bloqueado ⛔ · Não executado ⬜

---

## 4. Casos de Teste

### 4.1 Autenticação e Cadastro (AUT)

| ID | CT-AUT-001 — Cadastro de usuário com sucesso |
|----|-----------------------------------------------|
| **Requisito** | Autenticação de usuário (US01) |
| **Prioridade** | Alta |
| **Pré-condições** | Matrícula `190000001` ainda não cadastrada |
| **Passos** | 1. Acessar `/security/cadastro/`; 2. Informar matrícula de 9 dígitos, senha e confirmação idênticas; 3. Submeter o formulário |
| **Resultado esperado** | Usuário criado com perfil **Aluno**; sistema permite login com a matrícula informada |

| ID | CT-AUT-002 — Cadastro com matrícula fora do padrão |
|----|----------------------------------------------------|
| **Requisito** | Autenticação de usuário (US01) |
| **Prioridade** | Alta |
| **Pré-condições** | Página de cadastro aberta |
| **Passos** | 1. Informar matrícula com menos de 9 dígitos ou com letras (ex.: `12345`, `ABC123456`); 2. Submeter |
| **Resultado esperado** | Cadastro rejeitado com a mensagem "A matrícula deve conter exatamente 9 dígitos numéricos (padrão UnB)." |

| ID | CT-AUT-003 — Cadastro com matrícula já existente |
|----|--------------------------------------------------|
| **Requisito** | Autenticação de usuário (US01) |
| **Prioridade** | Alta |
| **Pré-condições** | Matrícula `190000001` já cadastrada (CT-AUT-001) |
| **Passos** | 1. Acessar o cadastro; 2. Informar a mesma matrícula; 3. Submeter |
| **Resultado esperado** | Cadastro rejeitado com mensagem de matrícula já cadastrada; nenhum usuário duplicado é criado |

| ID | CT-AUT-004 — Cadastro com senhas divergentes |
|----|----------------------------------------------|
| **Requisito** | Autenticação de usuário (US01) |
| **Prioridade** | Média |
| **Pré-condições** | Página de cadastro aberta |
| **Passos** | 1. Preencher senha e confirmação com valores diferentes; 2. Submeter |
| **Resultado esperado** | Cadastro rejeitado com a mensagem "As senhas não coincidem." |

| ID | CT-AUT-005 — Login com credenciais válidas |
|----|--------------------------------------------|
| **Requisito** | Autenticação de usuário (US01) |
| **Prioridade** | Alta |
| **Pré-condições** | Usuário ativo cadastrado |
| **Passos** | 1. Acessar a tela de login; 2. Informar matrícula e senha corretas; 3. Submeter |
| **Resultado esperado** | Login efetuado; usuário redirecionado e identificado no sistema |

| ID | CT-AUT-006 — Login com credenciais inválidas |
|----|----------------------------------------------|
| **Requisito** | Autenticação de usuário (US01) |
| **Prioridade** | Alta |
| **Pré-condições** | Usuário cadastrado |
| **Passos** | 1. Acessar a tela de login; 2. Informar senha incorreta; 3. Submeter |
| **Resultado esperado** | Acesso negado com mensagem de erro; usuário permanece na tela de login |

| ID | CT-AUT-007 — Login com usuário inativo |
|----|----------------------------------------|
| **Requisito** | Perfis e permissões (US02) |
| **Prioridade** | Média |
| **Pré-condições** | Usuário `190000005` com `is_active = False` |
| **Passos** | 1. Tentar login com matrícula e senha corretas do usuário inativo |
| **Resultado esperado** | Acesso negado; usuário inativo não consegue autenticar |

| ID | CT-AUT-008 — Logout |
|----|---------------------|
| **Requisito** | Autenticação de usuário (US01) |
| **Prioridade** | Média |
| **Pré-condições** | Usuário autenticado |
| **Passos** | 1. Acionar a opção "Sair" |
| **Resultado esperado** | Sessão encerrada; usuário redirecionado para a página inicial (`home`); áreas restritas voltam a exigir login |

| ID | CT-AUT-009 — Recuperação de senha |
|----|-----------------------------------|
| **Requisito** | Autenticação de usuário (US01) |
| **Prioridade** | Baixa |
| **Pré-condições** | Usuário cadastrado |
| **Passos** | 1. Acessar "Esqueceu a senha" na tela de login; 2. Seguir o fluxo informado |
| **Resultado esperado** | Fluxo de recuperação exibido conforme protótipo, com orientações para redefinição |

### 4.2 Mural de Eventos (MUR)

| ID | CT-MUR-001 — Visualizar mural público de eventos |
|----|--------------------------------------------------|
| **Requisito** | RF01 — Visualizar mural de eventos |
| **Prioridade** | Alta |
| **Pré-condições** | Ao menos um evento com status **Publicado**; usuário **não** autenticado |
| **Passos** | 1. Acessar `/eventos/` sem estar logado |
| **Resultado esperado** | Mural exibido com os eventos publicados (nome, data, horário, local, imagem quando houver), sem exigir login |

| ID | CT-MUR-002 — Evento em rascunho não aparece no mural |
|----|------------------------------------------------------|
| **Requisito** | RF01 / RF06 |
| **Prioridade** | Alta |
| **Pré-condições** | Evento com status **Rascunho** cadastrado |
| **Passos** | 1. Acessar o mural de eventos; 2. Procurar pelo evento em rascunho |
| **Resultado esperado** | O evento em rascunho **não** é listado no mural público |

| ID | CT-MUR-003 — Filtrar eventos |
|----|------------------------------|
| **Requisito** | RF03 — Filtrar eventos por modalidade |
| **Prioridade** | Média |
| **Pré-condições** | Eventos publicados com nomes/modalidades distintas |
| **Passos** | 1. Acessar o mural; 2. Utilizar o filtro/busca (`/eventos-filtro/`) com um termo específico (ex.: "Futsal") |
| **Resultado esperado** | Apenas os eventos compatíveis com o filtro são exibidos; limpar o filtro restaura a lista completa |

| ID | CT-MUR-004 — Visualizar detalhes de um evento |
|----|-----------------------------------------------|
| **Requisito** | RF01 |
| **Prioridade** | Alta |
| **Pré-condições** | Evento publicado existente |
| **Passos** | 1. No mural, clicar em um evento |
| **Resultado esperado** | Página `/evento/<id>/` exibe nome, descrição, data, horário, local, capacidade e situação de vagas do evento |

### 4.3 Inscrições em Eventos (INS)

| ID | CT-INS-001 — Inscrever-se em evento com vagas |
|----|-----------------------------------------------|
| **Requisito** | RF02 — Realizar inscrição em evento |
| **Prioridade** | Alta |
| **Pré-condições** | Aluno autenticado; evento publicado com vagas disponíveis |
| **Passos** | 1. Abrir os detalhes do evento; 2. Acionar "Inscrever-se" |
| **Resultado esperado** | Mensagem "Inscrição solicitada. Aguardando aprovação."; inscrição criada com status **Pendente** |

| ID | CT-INS-002 — Impedir inscrição duplicada |
|----|------------------------------------------|
| **Requisito** | RF02 |
| **Prioridade** | Alta |
| **Pré-condições** | Aluno já inscrito no evento (CT-INS-001) |
| **Passos** | 1. Acessar novamente o evento; 2. Tentar inscrever-se de novo |
| **Resultado esperado** | Aviso "Você já está inscrito neste evento."; nenhuma inscrição adicional é criada |

| ID | CT-INS-003 — Bloquear inscrição em evento lotado |
|----|--------------------------------------------------|
| **Requisito** | RF02 |
| **Prioridade** | Alta |
| **Pré-condições** | Evento com capacidade 1 e vaga já ocupada por outro aluno |
| **Passos** | 1. Autenticar com o segundo aluno; 2. Tentar inscrever-se no evento |
| **Resultado esperado** | Mensagem "Não há mais vagas disponíveis para este evento."; inscrição não é criada |

| ID | CT-INS-004 — Cancelar inscrição |
|----|---------------------------------|
| **Requisito** | RF02 |
| **Prioridade** | Alta |
| **Pré-condições** | Aluno com inscrição ativa em um evento |
| **Passos** | 1. Acessar o evento (ou "Eventos Inscritos" na área restrita); 2. Acionar "Cancelar inscrição" |
| **Resultado esperado** | Mensagem "Inscrição cancelada com sucesso."; inscrição passa a **Cancelada** e a vaga é liberada |

| ID | CT-INS-005 — Consultar eventos inscritos na área restrita |
|----|-----------------------------------------------------------|
| **Requisito** | RF02 |
| **Prioridade** | Média |
| **Pré-condições** | Aluno com ao menos uma inscrição |
| **Passos** | 1. Autenticar como aluno; 2. Acessar "Eventos Inscritos" na área restrita |
| **Resultado esperado** | Lista exibe as inscrições do aluno com o status atual de cada uma (Pendente, Aprovada, Rejeitada ou Cancelada) |

| ID | CT-INS-006 — Inscrição exige autenticação |
|----|-------------------------------------------|
| **Requisito** | RF02 / US01 |
| **Prioridade** | Alta |
| **Pré-condições** | Usuário não autenticado |
| **Passos** | 1. Acessar um evento publicado sem login; 2. Tentar inscrever-se |
| **Resultado esperado** | Usuário é redirecionado para a tela de login; inscrição não é criada |

### 4.4 Gestão de Eventos (EVT)

| ID | CT-EVT-001 — Criar evento como rascunho |
|----|-----------------------------------------|
| **Requisito** | RF06 — Criar e editar evento |
| **Prioridade** | Alta |
| **Pré-condições** | Organizador autenticado, vinculado a uma organização |
| **Passos** | 1. Acessar a gestão de eventos na área restrita; 2. Acionar "Novo evento"; 3. Preencher nome, data, horário, local, capacidade, organização e descrição; 4. Salvar com status **Rascunho** |
| **Resultado esperado** | Evento criado e listado na gestão do organizador; não aparece no mural público |

| ID | CT-EVT-002 — Publicar evento |
|----|------------------------------|
| **Requisito** | RF06 |
| **Prioridade** | Alta |
| **Pré-condições** | Evento em rascunho criado pelo organizador |
| **Passos** | 1. Editar o evento; 2. Alterar o status para **Publicado**; 3. Salvar |
| **Resultado esperado** | Evento passa a ser exibido no mural público e aceita inscrições |

| ID | CT-EVT-003 — Validar campos obrigatórios do evento |
|----|----------------------------------------------------|
| **Requisito** | RF06 |
| **Prioridade** | Média |
| **Pré-condições** | Formulário de novo evento aberto |
| **Passos** | 1. Submeter o formulário sem preencher campos obrigatórios (nome, data, horário, local, capacidade) |
| **Resultado esperado** | Evento não é criado; mensagens de validação indicam os campos pendentes |

| ID | CT-EVT-004 — Editar evento existente |
|----|--------------------------------------|
| **Requisito** | RF06 |
| **Prioridade** | Alta |
| **Pré-condições** | Evento criado pelo organizador |
| **Passos** | 1. Abrir o evento na gestão; 2. Alterar nome, capacidade ou descrição; 3. Salvar |
| **Resultado esperado** | Alterações persistidas e refletidas no detalhe e no mural (se publicado) |

| ID | CT-EVT-005 — Excluir evento |
|----|-----------------------------|
| **Requisito** | RF08 — Cancelar reserva ou evento |
| **Prioridade** | Média |
| **Pré-condições** | Evento de teste criado pelo organizador |
| **Passos** | 1. Na gestão de eventos, acionar a exclusão do evento; 2. Confirmar |
| **Resultado esperado** | Evento removido da gestão e do mural público |

### 4.5 Gestão de Inscritos (GIN)

| ID | CT-GIN-001 — Listar inscritos do evento |
|----|-----------------------------------------|
| **Requisito** | RF07 — Gerenciar lista de inscritos |
| **Prioridade** | Alta |
| **Pré-condições** | Organizador autenticado; evento com inscrições pendentes |
| **Passos** | 1. Acessar a gestão de inscrições do evento |
| **Resultado esperado** | Lista exibe os alunos inscritos com nome, matrícula, data de solicitação e status |

| ID | CT-GIN-002 — Aprovar inscrição pendente |
|----|-----------------------------------------|
| **Requisito** | RF07 |
| **Prioridade** | Alta |
| **Pré-condições** | Inscrição com status **Pendente** |
| **Passos** | 1. Na gestão de inscrições, acionar "Aprovar" para uma inscrição pendente |
| **Resultado esperado** | Inscrição passa a **Aprovada**, com avaliador e data de avaliação registrados; vaga contabilizada |

| ID | CT-GIN-003 — Reprovar inscrição sem motivo é bloqueado |
|----|--------------------------------------------------------|
| **Requisito** | RF07 |
| **Prioridade** | Alta |
| **Pré-condições** | Inscrição com status **Pendente** |
| **Passos** | 1. Acionar "Reprovar" sem preencher o motivo |
| **Resultado esperado** | Mensagem "Informe o motivo da reprovação."; status permanece **Pendente** |

| ID | CT-GIN-004 — Reprovar inscrição com motivo |
|----|--------------------------------------------|
| **Requisito** | RF07 |
| **Prioridade** | Alta |
| **Pré-condições** | Inscrição com status **Pendente** |
| **Passos** | 1. Acionar "Reprovar"; 2. Informar o motivo; 3. Confirmar |
| **Resultado esperado** | Inscrição passa a **Rejeitada** com o motivo registrado; aluno visualiza o status atualizado |

| ID | CT-GIN-005 — Aprovar apenas inscrições pendentes |
|----|--------------------------------------------------|
| **Requisito** | RF07 |
| **Prioridade** | Média |
| **Pré-condições** | Inscrição já **Aprovada** ou **Rejeitada** |
| **Passos** | 1. Tentar aprovar novamente a mesma inscrição (reenvio da ação) |
| **Resultado esperado** | Mensagem "Apenas inscrições pendentes podem ser aprovadas."; status não é alterado |

| ID | CT-GIN-006 — Aprovar todas as inscrições pendentes |
|----|----------------------------------------------------|
| **Requisito** | RF07 |
| **Prioridade** | Média |
| **Pré-condições** | Evento com duas ou mais inscrições pendentes |
| **Passos** | 1. Acionar "Aprovar todos" na gestão de inscrições |
| **Resultado esperado** | Mensagem "N inscrição(ões) aprovada(s) com sucesso."; todas as pendentes passam a **Aprovada**. Sem pendentes, exibe "Não há inscrições pendentes para aprovar." |

| ID | CT-GIN-007 — Exportar inscrições em CSV |
|----|------------------------------------------|
| **Requisito** | RF09 — Gerar relatório de inscritos |
| **Prioridade** | Baixa |
| **Pré-condições** | Evento com inscrições registradas |
| **Passos** | 1. Na gestão de inscrições, acionar "Exportar CSV" |
| **Resultado esperado** | Arquivo CSV baixado contendo os dados dos inscritos e seus status |

### 4.6 Espaços Físicos (ESP)

| ID | CT-ESP-001 — Cadastrar espaço físico |
|----|--------------------------------------|
| **Requisito** | RF11 — Cadastrar e gerenciar espaços |
| **Prioridade** | Alta |
| **Pré-condições** | Gestor autenticado |
| **Passos** | 1. Acessar `/espacos/`; 2. Acionar "Novo espaço" (`/espacos/novo/`); 3. Preencher nome, localização e descrição; 4. Salvar |
| **Resultado esperado** | Espaço criado com status **Disponível** e listado na relação de espaços |

| ID | CT-ESP-002 — Editar espaço físico |
|----|-----------------------------------|
| **Requisito** | RF11 |
| **Prioridade** | Média |
| **Pré-condições** | Espaço cadastrado |
| **Passos** | 1. Abrir o espaço; 2. Alterar descrição e localização; 3. Salvar |
| **Resultado esperado** | Alterações persistidas e exibidas no detalhe do espaço |

| ID | CT-ESP-003 — Alterar status do espaço |
|----|---------------------------------------|
| **Requisito** | RF11 |
| **Prioridade** | Alta |
| **Pré-condições** | Espaço com status **Disponível** |
| **Passos** | 1. Editar o espaço; 2. Alterar o status para **Em Manutenção** (e depois **Desativado**); 3. Salvar |
| **Resultado esperado** | Status atualizado com o indicador visual correspondente em cada mudança |

| ID | CT-ESP-004 — Excluir espaço físico |
|----|------------------------------------|
| **Requisito** | RF11 |
| **Prioridade** | Média |
| **Pré-condições** | Espaço de teste sem reservas relevantes |
| **Passos** | 1. Acionar a exclusão do espaço; 2. Confirmar |
| **Resultado esperado** | Espaço removido da listagem |

| ID | CT-ESP-005 — Acesso a espaços restrito ao gestor |
|----|--------------------------------------------------|
| **Requisito** | US02 — Perfis e permissões |
| **Prioridade** | Alta |
| **Pré-condições** | Usuário autenticado com perfil **Aluno** ou **Organizador** |
| **Passos** | 1. Acessar diretamente `/espacos/` e `/espacos/novo/` |
| **Resultado esperado** | Acesso negado (HTTP 403 ou redirecionamento); telas de gestão de espaços não são exibidas |

### 4.7 Reservas de Espaço (RES)

| ID | CT-RES-001 — Solicitar reserva de espaço |
|----|------------------------------------------|
| **Requisito** | RF05 — Solicitar reserva de espaço |
| **Prioridade** | Alta |
| **Pré-condições** | Organizador autenticado; evento próprio criado; espaço **Disponível** |
| **Passos** | 1. Acessar a solicitação de reserva; 2. Selecionar espaço e evento; 3. Informar data/hora de início e fim; 4. Submeter |
| **Resultado esperado** | Reserva criada com status **Pendente** e visível em "Minhas Reservas" |

| ID | CT-RES-002 — Aprovar reserva (gestor) |
|----|---------------------------------------|
| **Requisito** | RF10 — Aprovar ou reprovar reservas |
| **Prioridade** | Alta |
| **Pré-condições** | Gestor autenticado; reserva **Pendente** sem conflito |
| **Passos** | 1. Acessar a gestão de reservas; 2. Abrir a reserva pendente; 3. Acionar "Aprovar" |
| **Resultado esperado** | Reserva passa a **Aprovada**, com avaliador registrado; solicitante visualiza o novo status |

| ID | CT-RES-003 — Reprovar reserva com motivo |
|----|------------------------------------------|
| **Requisito** | RF10 |
| **Prioridade** | Alta |
| **Pré-condições** | Reserva **Pendente** |
| **Passos** | 1. Na gestão de reservas, acionar "Reprovar"; 2. Informar o motivo; 3. Confirmar |
| **Resultado esperado** | Reserva passa a **Reprovada** com o motivo registrado e visível ao solicitante |

| ID | CT-RES-004 — Bloquear solicitação com conflito de agenda |
|----|----------------------------------------------------------|
| **Requisito** | RNF02 — Concorrência de agenda |
| **Prioridade** | Alta |
| **Pré-condições** | Reserva **Aprovada** para a "Quadra Coberta" (ex.: 10h–12h) |
| **Passos** | 1. Como organizador, solicitar nova reserva para o **mesmo espaço** com período sobreposto (ex.: 11h–13h) |
| **Resultado esperado** | Sistema impede/sinaliza o conflito; a reserva sobreposta não pode ser efetivada |

| ID | CT-RES-005 — Bloquear aprovação de reserva conflitante |
|----|--------------------------------------------------------|
| **Requisito** | RNF02 |
| **Prioridade** | Alta |
| **Pré-condições** | Duas reservas **Pendentes** para o mesmo espaço com períodos sobrepostos; uma delas aprovada em seguida |
| **Passos** | 1. Aprovar a primeira reserva; 2. Tentar aprovar a segunda (sobreposta) |
| **Resultado esperado** | Aprovação da segunda reserva é bloqueada com indicação de conflito; apenas uma reserva **Aprovada** por período/espaço |

| ID | CT-RES-006 — Reserva sem conflito em horário adjacente |
|----|--------------------------------------------------------|
| **Requisito** | RNF02 |
| **Prioridade** | Média |
| **Pré-condições** | Reserva **Aprovada** das 10h às 12h na "Quadra Coberta" |
| **Passos** | 1. Solicitar e aprovar reserva no mesmo espaço das 12h às 14h (períodos que apenas se tocam) |
| **Resultado esperado** | Reserva adjacente é aceita e aprovada normalmente (sobreposição exige início < fim do outro período e vice-versa) |

| ID | CT-RES-007 — Cancelar reserva |
|----|-------------------------------|
| **Requisito** | RF08 — Cancelar reserva ou evento |
| **Prioridade** | Média |
| **Pré-condições** | Reserva do organizador com status **Pendente** ou **Aprovada** |
| **Passos** | 1. Em "Minhas Reservas", acionar "Cancelar" na reserva; 2. Confirmar |
| **Resultado esperado** | Reserva passa a **Cancelada** e o período volta a ficar livre para novas reservas |

### 4.8 Organizações (ORG)

| ID | CT-ORG-001 — Criar organização |
|----|--------------------------------|
| **Requisito** | Gestão de organizações (Documento de Visão, seção de perfis) |
| **Prioridade** | Média |
| **Pré-condições** | Usuário com permissão de criação autenticado |
| **Passos** | 1. Acessar `/organizacoes/`; 2. Acionar "Nova organização"; 3. Preencher nome e descrição; 4. Salvar |
| **Resultado esperado** | Organização criada e listada em `/organizacoes/` |

| ID | CT-ORG-002 — Editar organização |
|----|---------------------------------|
| **Requisito** | Gestão de organizações |
| **Prioridade** | Média |
| **Pré-condições** | Organização cadastrada |
| **Passos** | 1. Abrir a organização; 2. Alterar nome/descrição; 3. Salvar |
| **Resultado esperado** | Alterações persistidas e refletidas na listagem e no detalhe |

| ID | CT-ORG-003 — Adicionar membro à organização |
|----|---------------------------------------------|
| **Requisito** | Gestão de organizações |
| **Prioridade** | Média |
| **Pré-condições** | Organização cadastrada; usuário-alvo existente |
| **Passos** | 1. Abrir os membros da organização; 2. Acionar "Adicionar membro"; 3. Selecionar o usuário; 4. Confirmar |
| **Resultado esperado** | Usuário passa a constar como membro; vínculo duplicado do mesmo usuário na mesma organização não é permitido |

| ID | CT-ORG-004 — Remover membro da organização |
|----|--------------------------------------------|
| **Requisito** | Gestão de organizações |
| **Prioridade** | Média |
| **Pré-condições** | Organização com membro vinculado |
| **Passos** | 1. Na lista de membros, acionar "Remover" para um membro; 2. Confirmar |
| **Resultado esperado** | Vínculo removido; usuário deixa de aparecer entre os membros |

### 4.9 Gestão de Usuários (USU)

| ID | CT-USU-001 — Visualizar e editar perfil próprio |
|----|--------------------------------------------------|
| **Requisito** | US02 — Perfil de usuário |
| **Prioridade** | Média |
| **Pré-condições** | Usuário autenticado |
| **Passos** | 1. Acessar `/security/area-restrita/perfil/`; 2. Conferir os dados; 3. Alterar dados editáveis e salvar |
| **Resultado esperado** | Dados exibidos corretamente; alterações persistidas |

| ID | CT-USU-002 — Alterar tipo de perfil de um usuário |
|----|---------------------------------------------------|
| **Requisito** | US02 |
| **Prioridade** | Alta |
| **Pré-condições** | Gestor autenticado; usuário-alvo com perfil **Aluno** |
| **Passos** | 1. Acessar a gestão de usuários na área restrita; 2. Alterar o perfil do usuário-alvo para **Organizador**; 3. Salvar |
| **Resultado esperado** | Perfil atualizado; no próximo acesso o usuário passa a ter as permissões de organizador |

| ID | CT-USU-003 — Inativar usuário |
|----|-------------------------------|
| **Requisito** | US02 |
| **Prioridade** | Alta |
| **Pré-condições** | Gestor autenticado; usuário-alvo ativo |
| **Passos** | 1. Na gestão de usuários, acionar "Inativar" para o usuário-alvo |
| **Resultado esperado** | Usuário marcado como inativo e impedido de autenticar (ver CT-AUT-007) |

| ID | CT-USU-004 — Excluir usuário |
|----|------------------------------|
| **Requisito** | US02 |
| **Prioridade** | Média |
| **Pré-condições** | Gestor autenticado; usuário-alvo de teste sem vínculos que impeçam a exclusão |
| **Passos** | 1. Na gestão de usuários, acionar "Excluir"; 2. Confirmar |
| **Resultado esperado** | Usuário removido da base e ausente da listagem |

### 4.10 Controle de Acesso (ACE)

| ID | CT-ACE-001 — Área restrita exige autenticação |
|----|-----------------------------------------------|
| **Requisito** | US01 / US02 |
| **Prioridade** | Alta |
| **Pré-condições** | Usuário não autenticado |
| **Passos** | 1. Acessar diretamente `/security/area-restrita/` e subpáginas |
| **Resultado esperado** | Redirecionamento para a tela de login, preservando o destino original após autenticar |

| ID | CT-ACE-002 — Aluno não acessa funções de organizador |
|----|------------------------------------------------------|
| **Requisito** | US02 |
| **Prioridade** | Alta |
| **Pré-condições** | Aluno autenticado |
| **Passos** | 1. Acessar diretamente URLs de gestão de eventos, gestão de inscrições e solicitação de reserva |
| **Resultado esperado** | Acesso negado (HTTP 403) ou redirecionamento; nenhuma ação de organizador é executada |

| ID | CT-ACE-003 — Organizador não acessa funções de gestor |
|----|-------------------------------------------------------|
| **Requisito** | US02 |
| **Prioridade** | Alta |
| **Pré-condições** | Organizador autenticado |
| **Passos** | 1. Acessar diretamente a gestão de espaços, a aprovação de reservas e a gestão de usuários |
| **Resultado esperado** | Acesso negado (HTTP 403) ou redirecionamento; ações de gestor indisponíveis |

| ID | CT-ACE-004 — Ações de aprovação exigem o perfil correto |
|----|---------------------------------------------------------|
| **Requisito** | US02 / RF10 |
| **Prioridade** | Alta |
| **Pré-condições** | Aluno autenticado; IDs válidos de inscrição e reserva pendentes |
| **Passos** | 1. Submeter diretamente as URLs de aprovação/reprovação de inscrição e de reserva com o perfil de aluno |
| **Resultado esperado** | Requisições rejeitadas; status das inscrições e reservas permanece inalterado |

---

## 5. Matriz de Rastreabilidade

| Requisito | Descrição | Casos de teste |
|-----------|-----------|----------------|
| US01 | Autenticação (login/cadastro) | CT-AUT-001 a CT-AUT-009, CT-INS-006, CT-ACE-001 |
| US02 | Perfis e permissões | CT-AUT-007, CT-ESP-005, CT-USU-001 a CT-USU-004, CT-ACE-001 a CT-ACE-004 |
| RF01 | Visualizar mural de eventos | CT-MUR-001, CT-MUR-002, CT-MUR-004 |
| RF02 | Realizar inscrição em evento | CT-INS-001 a CT-INS-006 |
| RF03 | Filtrar eventos por modalidade | CT-MUR-003 |
| RF05 | Solicitar reserva de espaço | CT-RES-001 |
| RF06 | Criar e editar evento | CT-EVT-001 a CT-EVT-004, CT-MUR-002 |
| RF07 | Gerenciar lista de inscritos | CT-GIN-001 a CT-GIN-006 |
| RF08 | Cancelar reserva ou evento | CT-EVT-005, CT-RES-007 |
| RF09 | Gerar relatório de inscritos (CSV) | CT-GIN-007 |
| RF10 | Aprovar ou reprovar reservas | CT-RES-002, CT-RES-003, CT-ACE-004 |
| RF11 | Cadastrar e gerenciar espaços | CT-ESP-001 a CT-ESP-004 |
| RNF02 | Concorrência de agenda | CT-RES-004, CT-RES-005, CT-RES-006 |

> RF04 (notificações) e RF12 (dashboard de ocupação) não possuem casos de teste por ainda não terem sido implementados (prioridades COULD/SHOULD do backlog).

---

## 6. Registro de Execução

Preencher a cada ciclo de teste (copiar a tabela para cada nova rodada):

**Ciclo:** ______ · **Data:** ___/___/______ · **Testador:** ______________ · **Build/commit:** ______________

| Caso | Status (✅/❌/⛔/⬜) | Observações / Evidências |
|------|--------------------|--------------------------|
| CT-AUT-001 | | |
| CT-AUT-002 | | |
| CT-AUT-003 | | |
| CT-AUT-004 | | |
| CT-AUT-005 | | |
| CT-AUT-006 | | |
| CT-AUT-007 | | |
| CT-AUT-008 | | |
| CT-AUT-009 | | |
| CT-MUR-001 | | |
| CT-MUR-002 | | |
| CT-MUR-003 | | |
| CT-MUR-004 | | |
| CT-INS-001 | | |
| CT-INS-002 | | |
| CT-INS-003 | | |
| CT-INS-004 | | |
| CT-INS-005 | | |
| CT-INS-006 | | |
| CT-EVT-001 | | |
| CT-EVT-002 | | |
| CT-EVT-003 | | |
| CT-EVT-004 | | |
| CT-EVT-005 | | |
| CT-GIN-001 | | |
| CT-GIN-002 | | |
| CT-GIN-003 | | |
| CT-GIN-004 | | |
| CT-GIN-005 | | |
| CT-GIN-006 | | |
| CT-GIN-007 | | |
| CT-ESP-001 | | |
| CT-ESP-002 | | |
| CT-ESP-003 | | |
| CT-ESP-004 | | |
| CT-ESP-005 | | |
| CT-RES-001 | | |
| CT-RES-002 | | |
| CT-RES-003 | | |
| CT-RES-004 | | |
| CT-RES-005 | | |
| CT-RES-006 | | |
| CT-RES-007 | | |
| CT-ORG-001 | | |
| CT-ORG-002 | | |
| CT-ORG-003 | | |
| CT-ORG-004 | | |
| CT-USU-001 | | |
| CT-USU-002 | | |
| CT-USU-003 | | |
| CT-USU-004 | | |
| CT-ACE-001 | | |
| CT-ACE-002 | | |
| CT-ACE-003 | | |
| CT-ACE-004 | | |

---

## 7. Registro de Defeitos

Defeitos encontrados devem ser registrados como **issues no GitHub** do projeto, seguindo o template em `templates/template_issus.md`, contendo: caso de teste relacionado (ID), passos para reproduzir, resultado obtido × esperado, evidências (prints/logs) e ambiente (build/commit). Vincular a issue ao caso de teste na coluna "Observações" do registro de execução.
