# Ata de Reunião - Grupo Dijkstra

**Disciplina:** Métodos de Desenvolvimento de Software (MDS)
**Professor:** Ricardo Ajax Dias Kosloski
**Data da Reunião:** 06 de Maio de 2026
**Duração:** Aproximadamente 1 hora e 4 minutos (00:00:22 - 01:04:19)
**Pauta Principal:** Realização do Documento de Arquitetura do SIGEsporte

## Participantes Presentes

```
Davi Gualberto Rocha - 241012196
Igor Brandão Santos Salles - 251033162
Lucas Menezes Folha Brito - 241012300
Marcos Vinicius Monteiro - 242015666
Ana Paula Jardim Rezende Vilela – 241010880
Welder Rodrigues de Medeiros – 241012409
Gustavo Lima Menezes – 211062938
```
Nicolas Coqueiro Almeida De Freitas (222007059) esteve presente antes do início da
gravação, mas teve que se ausentar a partir das 20h. Gustavo saiu da reunião 20
minutos antes de seu fim.

## Pautas

```
Definição das tecnologias e do estilo arquitetural;
Metas e restrições arquiteturais;
Visões do documento (uso, lógica, estrutural, implementação)
Divisão de tarefas e fluxo de trabalho no GitHub.
```
## 2. Discussões e Decisões

**2.1 Framework Back-end**
A decisão já consta no Documento de Visão: back-end em Python e Django. É levantada a ideia
do uso do Flask, mas foi decidido o uso do Django, por oferecer mais, ser mais poderoso e para
preservar a coerência com o Documento de Visão.

**2.2 Banco de Dados**

Optou-se por utilizar SQLite.


**2.3 Infraestrutura e Deploy**

Foi levantada a ideia de usar o PythonAnywhere, mas houve preferência para o uso do Docker,
portanto o Deploy será via Docker em um servidor do Igor, com Nginx como proxy e TLS via
Let’s Encrypt.

**2.4 Estilo Arquitetural**

O estilo arquitetural será o padrão MVT (Model-View-Template), padrão nativo do Django, além
de ser mais simples e sugestão do professor. MVT é adequado para projetos de médio-porte e
tem a vantagem da velocidade de desenvolvimento.

**2.5 Arquitetura Monolítica**

Com apenas um mês e meio de prazo, uma arquitetura complexa seria inviável, portanto, um
monolito seria ideal – sem microsserviços ou APIs separadas.

**2.6 Padrão de Codificação**

PEP-8 e Pylint. O padrão de codificação será o PEP-8, como ferramenta de Lint tanto Pylint como
Ruff foram recomendados, mas preferência pelo Pylint.

**2.7 Diagrama de Classes**

O diagrama de classes é exigido no documento e vários modelos estão disponíveis no grupo do
Whatsapp, e devem ser colocados do Documento de Arquitetura. Uma ferramenta recomendada
para outros diagramas UML é Mermaid, visto que o GitHub tem suporte ao Mermaid (sem
necessidade de compilar ou exportar imagens).

**2.8 Visões do Documento de Arquitetura**

Além da discussão sobre os diagramas de classe, foi discutido sobre o escopo do produto
(perspectiva do usuário), e como não há terceiro documento de escopo o detalhamento dele
será incluído no próprio Documento de Arquitetura. Também foi definido que não haverá
versão mobile, somente uma versão web que deve ser uma página responsiva.

**2.9 Fluxo de Trabalho no GitHub**

- Quem for mais experiente no GitHub ficará responsável para guiar quem tem menos
experiência, além de serem definidos como administradores do repositório.


- Nada será adicionado/alterado no repositório sem revisão prévia, portanto, revisão
obrigatória.
- Todo o conteúdo (desde os documentos) será adicionado ao GitHub.
- Fluxo para evitar danificar o repositório: Clonar branch, desenvolver, abrir Pull Request.

## 3. Divisão de Tarefas

Igor e Marcos ficaram responsáveis pela formatação ABNT, incluindo referências
bibliográficas;

Ana Paula será “gestora” de documentação de padronização, validando docstrings,
padrão de código e formatação dos documentos (vale ressaltar que mais de uma vez foi dito
que o cargo de gestor de documentação não será aplicado a ninguém específico, sendo então
dever de todos, mas entende-se que é necessário que alguém de fato fique de olho nos detalhes)

Marcos vai subir os documentos do Teams para o GitHub e registrar tarefas pendentes.

Obs.: Faltou a divisão do Documento de Arquitetura para que cada membro possa
participar de seu desenvolvimento.
