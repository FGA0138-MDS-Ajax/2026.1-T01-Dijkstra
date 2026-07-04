# Documento de Arquitetura — PoC de Validação de Entrada e Ocupação

## 1. Visão geral

O sistema roda inteiramente **em um único Raspberry Pi 3**, com uma
**webcam única** compartilhada entre dois modos de captura. Não há
dependência de rede externa, nuvem ou banco de dados persistente — tudo
é local e efêmero, adequado ao caráter de PoC.

```
┌─────────────────────────────────────────────────────────────┐
│                      Raspberry Pi 3                         │
│                                                             │
│   Webcam ──► Camera Manager (máquina de estados)            │
│                 │                                           │
│         ┌───────┴────────┐                                  │
│         ▼                ▼                                  │
│   Modo QR (pyzbar)   Modo Contagem (OpenCV HOG)             │
│         │                │                                  │
│         ▼                ▼                                  │
│   Validação vs.      Contagem numérica                      │
│   reserva mock        (anônima, sem imagem persistida)      │
│         │                │                                  │
│         └───────┬────────┘                                  │
│                  ▼                                          │
│         FastAPI — estado em memória                         │
│                  │                                          │
│                  ▼                                          │
│         Streamlit — dashboard local                         │
└─────────────────────────────────────────────────────────────┘
```

## 2. Por que uma câmera só (e como isso funciona)

Como não há orçamento para uma segunda câmera, a mesma webcam atende os
dois propósitos por meio de uma **máquina de estados** simples:

- **Estado `AGUARDANDO_QR`**: a câmera fica em modo de captura de alta
  frequência, tentando decodificar um QR code a cada frame. É o estado
  padrão perto do horário de reservas.
- **Estado `MONITORANDO_OCUPACAO`**: após uma validação de entrada bem
  sucedida (ou em intervalos programados), a câmera passa a capturar em
  baixa frequência (ex.: 1 frame a cada poucos segundos) e roda a
  contagem de pessoas em vez da leitura de QR.
- A transição entre estados é controlada por tempo e por eventos (QR
  lido com sucesso, timeout sem detecção de QR, etc.), com um pequeno
  *debounce* para evitar troca de modo excessiva.

Essa divisão também ajuda a compensar o poder de processamento limitado
do Pi 3: o sistema nunca roda os dois pipelines de visão computacional
ao mesmo tempo.

## 3. Componentes

### 3.1 Camera Manager
Responsável por capturar frames da webcam e rotear para o pipeline
correto conforme o estado atual. Único ponto de acesso ao hardware da
câmera — evita conflito de recursos.

### 3.2 QR Reader Service
- Biblioteca: `pyzbar` sobre frames capturados via `OpenCV`.
- Decodifica o token do QR e consulta os dados mockados de reserva.
- Aplica as regras de validação (token existe, horário atual dentro da
  janela da reserva, espaço correto).
- Retorna um resultado binário (liberado/negado) + motivo, que é
  publicado no estado do FastAPI.

### 3.3 People Counter Service
- Abordagem: detector HOG (*Histogram of Oriented Gradients*) do
  próprio OpenCV — leve o suficiente para rodar no Pi 3 a baixa taxa de
  quadros, sem necessidade de modelos de deep learning.
- Processa o frame **em memória** e produz apenas um número (contagem
  de pessoas detectadas). O frame é descartado logo em seguida — nunca
  gravado em disco, nunca associado a identidade.
- Aplica um *debounce* temporal (ex.: só considera "ocupado" se a
  contagem > 0 se mantiver por N segundos), para evitar oscilação por
  falsos positivos pontuais.

### 3.4 Dados de reserva (mock)
Um arquivo JSON local simula a estrutura que a API real da aplicação de
reservas devolveria. Ver `docs/requisitos.md` para o schema.

### 3.5 FastAPI — estado em memória
- Mantém o estado atual do sistema (reserva ativa, resultado da última
  validação de QR, contagem/ocupação atual) em uma estrutura simples em
  memória — sem banco de dados.
- Expõe endpoints REST consumidos pelo dashboard:
  - `GET /reserva/atual` — reserva mockada vigente para o espaço.
  - `GET /entrada/status` — resultado da última validação de QR.
  - `GET /ocupacao/status` — contagem atual e se está "ocupado/livre".
  - `POST /entrada/validar` — chamado internamente pelo QR Reader
    Service ao processar um QR.

### 3.6 Streamlit — dashboard
- Consome os endpoints do FastAPI em polling (a cada poucos segundos).
- Exibe: reserva ativa, status de entrada (última validação), status de
  ocupação, e um log simples de eventos da sessão de demonstração.

## 4. Fluxo de dados — entrada (QR)

1. Câmera captura frame em modo `AGUARDANDO_QR`.
2. QR Reader Service decodifica o token.
3. Token é comparado contra o JSON mock de reservas.
4. Regra de validação: token existe? horário atual dentro da janela?
   espaço confere?
5. Resultado publicado no FastAPI (`POST /entrada/validar`).
6. Feedback imediato (LED/tela/terminal) + Streamlit atualiza no
   próximo polling.

## 5. Fluxo de dados — ocupação (CV)

1. Câmera captura frame em modo `MONITORANDO_OCUPACAO` (baixa
   frequência).
2. People Counter Service roda HOG sobre o frame.
3. Contagem numérica é obtida; frame é descartado.
4. Debounce temporal decide se o status muda de "livre" para "ocupado"
   (ou vice-versa).
5. Estado atualizado no FastAPI; Streamlit reflete no próximo polling.

## 6. Decisões técnicas e trade-offs

| Decisão | Motivo | Trade-off aceito |
|---|---|---|
| Câmera única com máquina de estados | Sem orçamento para 2ª câmera | Não monitora ocupação e entrada simultaneamente em tempo real |
| HOG em vez de rede neural (YOLO/MobileNet) | Roda em CPU fraca do Pi 3 sem acelerador | Menor precisão de detecção que um modelo de deep learning |
| Contagem anônima, sem persistência de imagem | Evita qualquer vínculo com legislação de proteção de dados | Não é possível auditar visualmente depois — só os números ficam registrados |
| Estado em memória (sem banco de dados) | Simplicidade, adequado a uma PoC de curta duração | Estado é perdido a cada reinício do processo |
| Dados de reserva mockados localmente | Não é permitido tocar na aplicação existente nesta fase | Nenhuma validação end-to-end com dados reais |

## 7. Privacidade e segurança (por design)

- Nenhuma imagem é gravada em disco em nenhum momento.
- Nenhum dado biométrico ou de identificação facial é processado — a
  contagem de pessoas é puramente numérica (bounding boxes descartadas
  após a contagem).
- O QR code identifica a **reserva**, não a pessoa fisicamente via
  câmera — a câmera de ocupação não sabe quem está no espaço, apenas
  quantas silhuetas humanas foram detectadas.
- Toda a comunicação (FastAPI ↔ Streamlit) ocorre localmente na rede do
  Pi, sem exposição externa nesta fase de PoC.

## 8. Limitações conhecidas

- Precisão da contagem de pessoas depende de iluminação e ângulo da
  câmera — requer calibração manual no local antes de qualquer
  demonstração.
- HOG tende a ter mais falsos negativos com pessoas paradas ou em
  poses não-frontais, comparado a modelos de deep learning.
- Sistema single-tenant: um Pi cobre um único espaço físico.
- Sem persistência: reiniciar o processo apaga o histórico da sessão.
