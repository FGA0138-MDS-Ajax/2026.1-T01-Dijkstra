# Estrutura da Aplicação e Módulos

## 1. Árvore de diretórios completa

```
.
├── README.md
├── requirements.txt
├── docs/
│   ├── visao.md
│   ├── arquitetura.md
│   ├── requisitos.md
│   └── modulos.md              # este documento
├── config.py                    # configurações globais (sala_id, thresholds, índice da câmera)
├── app/
│   ├── __init__.py
│   ├── camera/
│   │   ├── __init__.py
│   │   ├── manager.py           # CameraManager: máquina de estados + loop de captura
│   │   ├── states.py            # Enum: AGUARDANDO_QR, MONITORANDO_OCUPACAO
│   │   └── capture.py           # wrapper de baixo nível sobre a webcam (OpenCV VideoCapture)
│   ├── qr/
│   │   ├── __init__.py
│   │   ├── reader.py            # decodifica QR code de um frame (pyzbar)
│   │   └── validator.py         # valida token decodificado contra o mock de reservas
│   ├── occupancy/
│   │   ├── __init__.py
│   │   ├── detector.py          # detector de pessoas (HOG do OpenCV)
│   │   └── counter.py           # contagem + debounce temporal (ocupado/livre)
│   ├── mock/
│   │   ├── __init__.py
│   │   ├── reservas.json        # dados de reserva simulados
│   │   └── reservas_repository.py  # carrega e consulta o JSON mockado
│   ├── state/
│   │   ├── __init__.py
│   │   └── app_state.py         # estado compartilhado em memória, thread-safe
│   ├── events/
│   │   ├── __init__.py
│   │   └── logger.py            # log de eventos da sessão (em memória, para o dashboard)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # instancia o FastAPI, inicia a thread da câmera no startup
│   │   ├── routes.py            # definição dos endpoints REST
│   │   └── schemas.py           # modelos Pydantic de request/response
│   └── dashboard/
│       ├── __init__.py
│       └── main.py              # aplicação Streamlit
└── scripts/
    └── gerar_qr_demo.py         # utilitário: gera a imagem do QR code de uma reserva mock, para a demo
```

## 2. Responsabilidade de cada módulo

### `config.py`
Configurações globais carregadas uma vez na inicialização: índice da
câmera (`/dev/video0`), `sala_id` monitorada, tempo de debounce da
ocupação (segundos), tempo de timeout do modo QR, intervalo de polling
do Streamlit. Mantém tudo isso fora do código dos módulos, para ajustar
sem mexer em lógica.

### `app/camera/`

- **`states.py`** — define os estados possíveis da máquina de estados
  (`AGUARDANDO_QR`, `MONITORANDO_OCUPACAO`) e as transições permitidas.
- **`capture.py`** — encapsula o `cv2.VideoCapture`: abrir, ler frame,
  liberar o dispositivo. É a única parte do sistema que toca a webcam
  diretamente, o que facilita trocar a câmera ou mockar em testes.
- **`manager.py`** — o coração da orquestração. Roda em uma thread de
  background, iniciada no `startup` do FastAPI. A cada iteração do
  loop: captura um frame via `capture.py`, decide (baseado no estado
  atual) se chama `qr/reader.py` ou `occupancy/detector.py`, aplica as
  regras de transição de estado, e escreve o resultado no
  `state/app_state.py`.

**Interface exposta:** `CameraManager.start()`, `CameraManager.stop()`,
roda em thread própria — não bloqueia a API.

### `app/qr/`

- **`reader.py`** — recebe um frame (array numpy), retorna o texto
  decodificado do QR (ou `None`, se não encontrar). Usa `pyzbar`.
- **`validator.py`** — recebe o token decodificado, consulta
  `mock/reservas_repository.py`, aplica as regras de validação
  (token existe, horário atual dentro da janela, `sala_id` confere) e
  retorna um resultado estruturado: `liberado: bool`, `motivo: str`,
  `reserva: dict | None`.

**Interface exposta:** `validar_qr(token: str) -> ResultadoValidacao`.

### `app/occupancy/`

- **`detector.py`** — recebe um frame, roda o HOG do OpenCV, retorna a
  quantidade de pessoas detectadas naquele frame. Não guarda nem
  retorna a imagem — só o número.
- **`counter.py`** — mantém um pequeno histórico das últimas
  contagens e aplica o debounce temporal: só muda o status público de
  "livre" para "ocupado" (ou vice-versa) se a nova contagem se mantiver
  estável por N segundos. Evita que uma detecção pontual (ex.: alguém
  passando na porta) dispare uma mudança de status.

**Interface exposta:** `counter.atualizar(contagem: int) -> StatusOcupacao`.

### `app/mock/`

- **`reservas.json`** — arquivo de dados simulando o formato que a API
  real de reservas devolveria (schema documentado em
  `docs/requisitos.md`).
- **`reservas_repository.py`** — camada de acesso a esse JSON: carrega
  em memória na inicialização, expõe funções de consulta
  (`buscar_por_token`, `reserva_atual_da_sala`). Isolar essa leitura
  aqui é o que permite, no futuro, trocar o mock por uma chamada real à
  API sem alterar `qr/validator.py`.

### `app/state/`

- **`app_state.py`** — um objeto singleton (protegido por
  `threading.Lock`) que guarda o estado atual do sistema: reserva
  vigente, último resultado de validação de QR, status de ocupação
  atual, timestamp da última atualização de cada um. É o único ponto de
  escrita da `CameraManager` e o único ponto de leitura da API — evita
  qualquer necessidade de banco de dados para esta PoC.

### `app/events/`

- **`logger.py`** — mantém uma lista em memória (com limite de
  tamanho) dos últimos eventos da sessão: "entrada validada às 14:03",
  "sala ficou vazia às 14:20 com reserva ativa", etc. Consumido pelo
  dashboard para mostrar o histórico da demonstração.

### `app/api/`

- **`main.py`** — cria a instância do FastAPI, registra as rotas, e no
  evento de `startup` inicia a `CameraManager` em background; no
  `shutdown`, chama `CameraManager.stop()` para liberar a câmera
  corretamente.
- **`routes.py`** — define os endpoints:
  - `GET /reserva/atual`
  - `GET /entrada/status`
  - `GET /ocupacao/status`
  - `GET /eventos` (histórico da sessão)
- **`schemas.py`** — modelos Pydantic usados nas respostas dos
  endpoints acima, garantindo um contrato estável para o dashboard (e
  para uma futura integração real).

### `app/dashboard/`

- **`main.py`** — aplicação Streamlit que faz polling nos endpoints do
  FastAPI a cada poucos segundos e renderiza: reserva ativa, status de
  entrada, status de ocupação, e a lista de eventos recentes.

### `scripts/gerar_qr_demo.py`
Utilitário fora da aplicação principal: lê `mock/reservas.json` e gera
uma imagem PNG do QR code correspondente a um `qr_token`, para ser
exibida no celular (ou impressa) durante a demonstração.

## 3. Fluxo de execução (quem chama quem)

1. `api/main.py` sobe o FastAPI e inicia `camera/manager.py` em uma
   thread separada.
2. `CameraManager` roda em loop contínuo, alternando entre os dois
   modos:
   - **Modo QR**: `camera/capture.py` → `qr/reader.py` →
     `qr/validator.py` (que consulta `mock/reservas_repository.py`) →
     escreve resultado em `state/app_state.py` → registra evento em
     `events/logger.py`.
   - **Modo ocupação**: `camera/capture.py` → `occupancy/detector.py`
     → `occupancy/counter.py` → escreve resultado em
     `state/app_state.py` → registra evento em `events/logger.py` (se
     houver mudança de status).
3. `api/routes.py` apenas **lê** o `app_state.py` — nunca dispara
   processamento de imagem diretamente. Isso mantém a API rápida mesmo
   com o Pi processando visão computacional em paralelo.
4. `dashboard/main.py` faz polling HTTP nos endpoints e renderiza.

## 4. Por que essa separação

- **Testabilidade**: `qr/validator.py` e `occupancy/counter.py` não
  dependem de câmera nem de FastAPI — dá para testar a lógica de
  validação e de debounce com frames/contagens simulados, sem hardware.
- **Substituição futura do mock**: como `mock/reservas_repository.py`
  é a única porta de entrada para dados de reserva, trocar por uma
  chamada real à API de produção não exige alterar `qr/validator.py`
  nem nenhum outro módulo.
- **Isolamento de hardware**: só `camera/capture.py` toca a webcam
  diretamente. Se a câmera mudar (outro modelo, outra porta), o resto
  do sistema não é afetado.
- **Sem necessidade de banco de dados**: `state/app_state.py`
  centraliza tudo que precisa ser consultado pela API, mantendo a PoC
  simples e adequada ao Pi 3.

## 5. Ordem sugerida de implementação

1. `mock/` (dados e repositório) — não depende de nada.
2. `qr/reader.py` e `occupancy/detector.py` — testáveis isoladamente com
   imagens estáticas, antes de mexer na webcam de verdade.
3. `qr/validator.py` e `occupancy/counter.py` — lógica pura, fácil de
   testar com valores simulados.
4. `state/app_state.py` e `events/logger.py`.
5. `camera/` (capture → manager) — só agora entra a webcam real.
6. `api/` — conecta tudo via endpoints.
7. `dashboard/` — última camada, consome a API já funcionando.
8. `scripts/gerar_qr_demo.py` — a qualquer momento, é independente do
   resto.

Essa ordem deixa a integração com o hardware real (a parte mais
arriscada, como já discutimos) para depois de toda a lógica já estar
validada com dados simulados.
