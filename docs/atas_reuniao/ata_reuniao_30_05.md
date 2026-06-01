# Ata de Reunião — MDS

| Campo | Informação |
|---|---|
| **Disciplina** | Métodos de Desenvolvimento de Software (MDS) |
| **Professor** | Ricardo Ajax Dias Kosloski |
| **Data** | 30 de maio de 2026 |
| **Tipo de reunião** | Sprint 1 Review + Retrospectiva + Sprint 2 Planning |
| **Horário de início** | ~00h03 (conforme transcrição) |
| **Duração aproximada** | ~1h10min (conforme transcrição) |

---

## Participantes presentes

| Nome | Papel |
|---|---|
| Welder Rodrigues de Medeiros | P.O. / Scrum Master — facilitador da reunião |
| Marcos Vinicius Monteiro | Scrum Master / Dev |
| Igor Brandão Santos Salles | Dev (back-end / infraestrutura) |
| Guilherme Monteiro | Dev (back-end / front-end) |
| Ana Paula Jardim Rezende Vilela | Dev (front-end / protótipo) |
| Davi Gualberto Rocha | Dev (front-end / protótipo) |
| Lucas Menezes Folha Brito | Dev (back-end / front-end) |
| Gustavo Lima Menezes | Dev (back-end / front-end) |

## Pauta

1. Sprint 1 Review — apresentação do protótipo (Figma/Canva) e estado da aplicação
2. Discussão sobre campos sensíveis no cadastro de usuário (LGPD)
3. Alinhamento técnico: CRUD de eventos, banco de dados e arquitetura Django
4. Sprint 2 Planning — definição do escopo e MVP para sábado 06/06
5. Pontos de processo: comunicação, proatividade e divisão de issues

---

## Resumo das discussões

### 1. Sprint 1 Review — protótipo e aplicação

Welder abriu a reunião e solicitou que os membros responsáveis pelo front-end apresentassem as entregas da sprint. **Ana Paula** apresentou o protótipo navegável desenvolvido no Canva, esclarecendo que a tela exibida inicialmente não era a página inicial, mas uma tela interna. O protótipo contém:

- Navbar comum a todas as páginas;
- Página inicial com listagem de eventos e campo de filtro por data de início e fim;
- Tela de detalhe do evento;
- Sistema de menu hamburger (menu sanduíche / burger) para navegação.

Welder observou que o filtro por nome de evento ficará para uma sprint futura, e que a paginação de resultados (para quando houver muitos eventos) também deverá ser adicionada posteriormente.

O **Guilherme** mostrou o estado atual da aplicação rodando, apontando que os eventos visíveis no front-end foram inseridos manualmente, sem passar pelo back-end, pois o CRUD ainda não está integrado. A lógica de filtro por data já está implementada no front, mas depende do back-end para funcionar com dados reais.

### 2. LGPD e campos sensíveis no cadastro de usuário

Igor levantou uma preocupação importante sobre o protótipo do formulário de cadastro de usuário, que incluía campos como CPF e e-mail institucional. Os pontos discutidos foram:

- **Matrícula** é suficiente como identificador único — ela é pública e não há risco legal em armazená-la;
- **CPF** não deve ser coletado sob nenhuma hipótese, pois exige controles de segurança robustos (criptografia, política de retenção, conformidade com a LGPD) que o grupo não tem tempo de implementar adequadamente;
- **E-mail** pode ser coletado para fins de recuperação de senha, mas com cautela;
- A coleta de CPF vinculada a e-mail e matrícula expõe o projeto a denúncias junto à ANPD e pode ter consequências legais sérias;
- Igor citou o exemplo de um TCC de colega que tratava exatamente da tensão entre dados pessoais e sistemas digitais.

**Decisão:** remover o campo CPF do formulário de cadastro. O e-mail pode ser mantido apenas para recuperação de senha, preferencialmente substituído por métodos alternativos (perguntas de segurança, login social via Google) para evitar a necessidade de um servidor SMTP próprio.

Welder endossou a posição e formalizou: a equipe não assumirá o risco de coletar dados sensíveis sem a infraestrutura de segurança adequada.

### 3. Alinhamento técnico — CRUD, banco de dados e arquitetura Django

Igor e Guilherme debateram o estado do back-end e a estratégia para a próxima sprint:

- Os eventos atualmente exibidos no front foram inseridos diretamente no banco, sem passar pela API Django, o que impede a filtragem real por data;
- O CRUD de eventos é a peça central: sem ele, o filtro, a listagem real e o login não funcionam corretamente;
- **Proposta de Igor:** cada desenvolvedor trabalha com um banco de dados SQLite local para o seu domínio (sem amarrar dependências entre si), e ao final a gente consolida os schemas com um diff. Isso permite desenvolvimento paralelo sem esperar que uma parte fique pronta para que outra comece;
- Igor alertou que o Django é muito intrínsecado — front e back dependem muito um do outro — e que conflitos de merge são esperados à medida que o desenvolvimento paralelo avance. A solução é comunicação constante e issues bem delimitadas;
- Guilherme sugeriu que cada pessoa pegue telas ou funcionalidades distintas para evitar conflito de código (ex.: uma pessoa faz filtro por data, outra faz a tela de detalhe do evento);
- Igor reforçou que o código com lint passando deve ir para a base mesmo que imperfeito, pois ter algo na branch principal é melhor do que bloquear tudo esperando perfeição.

### 4. Sprint 2 Planning — MVP para 06/06

Welder conduziu o planejamento do que será entregue até o próximo sábado. O escopo acordado como **MVP** é:

| Entrega | Observação |
|---|---|
| Página inicial com listagem de eventos | Já há protótipo e parte do front implementado |
| Filtro de eventos por data (início e fim) | Depende do CRUD de eventos integrado ao back-end |
| Tela de detalhe do evento | Considerada simples pelos membros |
| CRUD de eventos (criar, editar, visualizar, excluir) | Guilherme assumiu responsabilidade |
| Login | Avaliado como fora do escopo para esta sprint — ficará para a próxima |

O login foi retirado do escopo da sprint 2 após discussão: a autenticação depende de várias outras peças estarem no lugar, e incluí-la arriscaria comprometer as demais entregas. 

Marcos e Igor reforçaram que sprints devem ter escopo realista para evitar frustração, e que issues adicionais podem ser incorporadas ao longo da semana conforme o andamento.

### 5. Processo: comunicação e proatividade

Marcos fez um apelo à comunicação interna: antes de começar qualquer issue, o membro deve avisar o grupo para evitar trabalho duplicado. Exemplificou que, se dois membros implementam a mesma funcionalidade de filtro simultaneamente sem se comunicar, o grupo perde tempo e gera conflitos desnecessários.

Guilherme propôs que a organização de tarefas seja feita com mais granularidade — dividir funcionalidades grandes em sub-tarefas menores atribuídas a pessoas específicas, reduzindo colisões de código.

Welder lembrou que, como P.O., ele define o valor a ser entregue (as histórias de usuário), mas a divisão interna das tarefas técnicas é responsabilidade da equipe de desenvolvimento.

---

## Decisões tomadas

- [x] Campo CPF removido do formulário de cadastro de usuário
- [x] Login excluído do escopo da Sprint 2 — ficará para sprint posterior
- [x] CRUD de eventos definido como entrega central da Sprint 2
- [x] Estratégia de banco SQLite local por desenvolvedor adotada para a sprint, com consolidação posterior
- [x] Guilherme assumiu o CRUD de eventos (US RF3: cadastrar, editar, visualizar, excluir evento)
- [x] MVP da Sprint 2: página inicial + listagem + filtro por data + detalhe do evento

---

## Ações e responsáveis

| Ação | Responsável | Prazo |
|---|---|---|
| Implementar CRUD de eventos (criar, editar, excluir) e integrá-lo ao back-end Django | Guilherme | Sábado 06/06 |
| Integrar filtro por data de início e fim com dados reais do banco | Guilherme / Igor | Sábado 06/06 |
| Finalizar templates HTML (header, body, footer) e tela de detalhe do evento | Ana Paula / Davi / Gustavo | Sábado 06/06 |
| Concluir configuração da estrutura Django e branch de desenvolvimento | Igor | Sábado 06/06 |
| Atualizar issues e milestone no GitHub Projects com o escopo da Sprint 2 | Welder | Imediatamente |
| Comunicar ao grupo antes de iniciar qualquer nova issue | Todos | Contínuo |

---

## Observações finais

- A próxima reunião (Sprint 2 Review + Sprint 3 Planning) está prevista para **sábado, 06 de junho de 2026**.
- A segunda prova teórica da disciplina está marcada para **06 de junho de 2026**.
- A política de tolerância de entrada em reunião é de **15 minutos** — após esse prazo, a lista de presença é encerrada.
- Membros devem avisar o grupo com antecedência em caso de atraso ou ausência.

---

*Ata elaborada com base na transcrição automática da reunião de 30/05/2026.*
