# Ata de Reunião — MDS

| Campo                  | Informação                                   |
| ---------------------- | -------------------------------------------- |
| **Disciplina**         | Métodos de Desenvolvimento de Software (MDS) |
| **Professor**          | Ricardo Ajax Dias Kosloski                   |
| **Data**               | 23 de maio de 2026                           |
| **Horário de início**  | 09h49                                        |
| **Duração aproximada** | ~1h57min (conforme transcrição)              |

------

## Participantes presentes

| Nome                            | Matrícula | Papel                    |
| ------------------------------- | --------- | ------------------------ |
| Igor Brandão Santos Salles      | 251033162 | Facilitador / Dev        |
| Marcos Vinicius Monteiro        | 242015666 | Scrum Master             |
| Welder Rodrigues de Medeiros    | 241012409 | P.O. + novo Scrum Master |
| Ana Paula Jardim Rezende Vilela | 241010880 | Dev (front-end)          |
| Davi Gualberto Rocha            | 241012196 | Dev (front-end)          |
| Lucas Menezes Folha Brito       | 241012300 | Dev                      |
| Gustavo Lima Menezes            | 211062938 | Dev (front-end)          |

------

## Pauta

1. Situação da monitoria (ausência de supervisão desde o início)
2. Redefinição de papéis após saída do membro Nicolas
3. Padronização de commits, issues, pull requests e branches
4. Definição da primeira sprint e divisão de trabalho
5. Padrão de documentação (PEP 257) e estrutura de templates
6. Procedimento de assinatura da lista de presença (gov.br)

------

## Resumo das discussões

### 1. Monitoria

O monitor responsável pelo grupo não realizou contato desde sua designação. O grupo buscou contato por e-mail e acionou a monitora supervisora Sophia. Nos últimos dois dias o monitor respondeu, mas o problema de supervisão efetiva persiste. O grupo informou o professor sobre a situação.

### 2. Redefinição de papéis

Com a saída do membro Nicolas da comissão de gerenciamento, o grupo deliberou sobre o novo Scrum Master. Ninguém manifestou interesse alternativo, de modo que **Welder Rodrigues de Medeiros** assumiu a função de Scrum Master, acumulando-a com a de Product Owner. Os documentos de visão e arquitetura (markdown e `.doc`) deverão ser atualizados para refletir a mudança.

### 3. Padronização do repositório GitHub

Marcos apresentou os templates de pull request e de issue criados, localizados na pasta `templates` (renomeada de `tios` para evitar conflito com o Django). Para commits, adotou-se o padrão convencional:

```
<tipo>: <descrição objetiva>
```

Exemplos: `feat: criação de fluxo de eventos`, `fix: correção de bug no login`, `docs: atualização do README`.

Todo PR deve:

- Referenciar a issue relacionada pelo número (`#N`);
- Seguir o checklist do template;
- Ser revisado antes do merge.

PRs fora do padrão serão devolvidos pelo Scrum Master. Sprints serão gerenciadas via *milestones* no GitHub Projects.

### 4. Primeira sprint — escopo e divisão

O grupo acordou que a arquitetura deve partir da infraestrutura antes de avançar para funcionalidades. A lógica de desenvolvimento ficou definida assim:

1. Configurar a estrutura Django e criar a classe abstrata de CRUD;
2. Implementar a entidade Usuário com login — primeiro requisito funcional (**RF1: Autenticação de Usuário**);
3. Em paralelo, criar os templates HTML base (header, body, footer), seguindo a abordagem *mobile first*.

**Divisão de responsabilidades:**

| Frente                      | Responsáveis             |
| --------------------------- | ------------------------ |
| Estrutura Django + VPS      | Igor                     |
| Front-end / protótipo Figma | Gustavo, Ana Paula, Davi |
| Documentação / Scrum        | Welder                   |
| Padronização / PR reviews   | Marcos                   |

### 5. Padrão de documentação de código (PEP 257)

Igor apresentou o PEP 257 (*docstring conventions*) na versão padrão. O cabeçalho de cada módulo deve conter:

- Nome do módulo
- Nome do projeto
- Autor
- Data de criação
- Versão
- Última modificação (data, autor e o que foi alterado)

O versionamento segue o esquema alfa/beta/release: `0.0.1` → `0.1.0` → `1.0.0`. O pylint exige ao menos a presença do docstring, mas a conformidade com o padrão interno é responsabilidade do desenvolvedor e do revisor do PR.

### 6. Demonstração prática do fluxo Git

Marcos demonstrou ao vivo, via compartilhamento de tela, o fluxo completo:

```bash
git status
git add .
git commit -m "docs: criação de template para padronização"
git push origin <branch>
```

Em seguida, foi aberto um PR no GitHub, Welder realizou a aprovação e o merge ao vivo, e a branch foi deletada. Foi reforçado que **issues só devem ser fechadas após o merge do PR aprovado**.

### 7. Lista de presença

A lista de presença em PDF foi assinada digitalmente por cada membro via **gov.br**, em cadeia — cada participante recebe o PDF do anterior, assina e envia ao próximo. Ordem adotada:

> Igor → Welder → Ana Paula → Davi → Lucas → Gustavo → Marcos

O arquivo final será armazenado no OneDrive de Marcos, para preservação além do prazo de retenção do Teams.

------

## Decisões tomadas

- [x] Welder assumiu a função de Scrum Master (acumula com P.O.)
- [x] Pasta renomeada de `utils` para `templates`
- [x] Padrão de commit convencional adotado (`feat` / `fix` / `docs` / `refactor`…)
- [x] Abordagem *mobile first* adotada para o front-end
- [x] Tolerância de 15 minutos para entrada na reunião antes de iniciar a assinatura

------

## Ações e responsáveis

| Ação                                                         | Responsável              | Prazo          |
| ------------------------------------------------------------ | ------------------------ | -------------- |
| Atualizar documentos de visão e arquitetura (novo Scrum Master) | Welder                   | Próxima sprint |
| Configurar estrutura do projeto Django e VPS                 | Igor                     | Sábado 31/05   |
| Protótipo de média fidelidade (Figma)                        | Gustavo, Ana Paula, Davi | Sábado 31/05   |
| Criar template de commit em markdown                         | Marcos                   | Próxima sprint |
| Fixar reunião semanal recorrente (mesmo horário)             | Marcos                   | Esta semana    |
| Avisar Guilherme sobre prazo do protótipo e solicitar compartilhamento do que já foi feito | Marcos / Welder          | Imediatamente  |

------

## Observações finais

- A próxima reunião está prevista para **sábado, 31 de maio de 2026**, no mesmo horário.
- A segunda prova teórica está prevista para **6 de junho de 2026**.
- Membros que não comparecerem sem aviso prévio ficarão com falta e não assinarão a lista de presença retroativamente.
- Contribuições via abertura de issues (bugs encontrados, melhorias sugeridas) são encorajadas e contam como participação.

------

*Ata elaborada com base na transcrição automática da reunião de 23/05/2026.*