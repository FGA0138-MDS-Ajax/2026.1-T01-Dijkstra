# PoC — Validação de Entrada e Ocupação de Espaços via QR Code + Visão Computacional

Prova de conceito de uma camada independente de verificação física para
espaços educacionais/esportivos do campus. Roda em um **Raspberry Pi 3**
com uma **webcam única**, sem qualquer alteração na aplicação de
reservas existente.

Valida a entrada de pessoas por QR code (vinculado a uma reserva
mockada) e detecta, de forma **anônima e puramente numérica**, se o
espaço está ocupado — sem reconhecimento facial, sem persistência de
imagens.

> Documentação completa: [`docs/visao.md`](docs/visao.md) ·
> [`docs/arquitetura.md`](docs/arquitetura.md) ·
> [`docs/requisitos.md`](docs/requisitos.md)

## Stack

- **FastAPI** — API local, estado em memória
- **Streamlit** — dashboard de demonstração
- **OpenCV** + **pyzbar** — leitura de QR code
- **OpenCV (HOG)** — contagem anônima de pessoas
- Dados de reserva **mockados** em JSON local (sem integração real)

## Pré-requisitos

- Raspberry Pi 3 com Raspberry Pi OS instalado
- Webcam USB compatível (UVC)
- Python 3.9+
- Acesso à rede local do Pi (para acessar o dashboard de outro
  dispositivo, se desejado)

> No Pi 3, instale os pacotes de visão computacional via
> [piwheels](https://www.piwheels.org/) para evitar compilar o OpenCV
> do zero — isso costuma ser a maior fonte de demora no setup inicial.
>
> `pyzbar` depende da biblioteca de sistema `libzbar0`. Instale antes
> do `pip install`:
> ```bash
> sudo apt update && sudo apt install -y libzbar0
> ```

## Instalação

```bash
git clone <repo>
cd <repo>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Como rodar

Em dois terminais separados (ou usando um gerenciador de processos):

```bash
# Terminal 1 — API
uvicorn app.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Dashboard
streamlit run app/dashboard/main.py
```

O serviço de câmera (máquina de estados QR ↔ contagem de ocupação) é
iniciado junto com a API e roda em segundo plano.

Acesse o dashboard em `http://<ip-do-pi>:8501`.

Variáveis de ambiente opcionais do dashboard:

| Variável | Padrão | Para quê |
|---|---|---|
| `DASHBOARD_API_URL` | `http://localhost:8000` | Onde a API está rodando (ajuste se o dashboard rodar em outra máquina) |
| `DASHBOARD_POLL_SECONDS` | `3` | Intervalo de atualização automática |
| `DASHBOARD_NO_SHOW_MINUTOS` | `10` | Minutos sem ocupação, com reserva ativa, até disparar o alerta de possível não comparecimento |

## Preparando uma demonstração

O `app/mock/reservas.json` versionado tem datas fixas (2026-07-01),
úteis para os testes automatizados, mas que não batem com o horário
real de uma apresentação. Use os scripts abaixo antes de demonstrar:

```bash
# Gera uma reserva "ao vivo" (começando agora) + o QR code correspondente
python scripts/preparar_demo.py --usuario "Maria Silva" --duracao-minutos 60

# Ou, se preferir manter as reservas de exemplo do repositório e só
# gerar as imagens de QR a partir delas:
python scripts/gerar_qr_demo.py
```

As imagens geradas ficam em `scripts/qrcodes/` — abra a imagem no
celular (ou imprima) para escanear na câmera durante a demo.

> Se a API já estiver rodando quando você rodar `preparar_demo.py`,
> reinicie a API para que o novo mock seja lido.

## Estrutura de pastas

```
.
├── README.md
├── requirements.txt
├── config.py
├── docs/
│   ├── visao.md
│   ├── arquitetura.md
│   ├── requisitos.md
│   └── modulos.md
├── app/
│   ├── camera/          # CameraManager (máquina de estados) + webcam
│   ├── qr/               # Leitura e validação de QR code
│   ├── occupancy/         # Detecção e contagem de pessoas (HOG + debounce)
│   ├── mock/               # Dados de reserva simulados (JSON + repositório)
│   ├── state/               # AppState — estado compartilhado em memória
│   ├── events/                # EventLogger — log de eventos da sessão
│   ├── api/                    # FastAPI — endpoints e montagem das dependências
│   └── dashboard/                # Streamlit — painel de demonstração
├── scripts/
│   ├── gerar_qr_demo.py    # Gera QR codes a partir do mock atual
│   └── preparar_demo.py    # Gera uma reserva "ao vivo" + QR, num só passo
└── tests/                    # 71 testes cobrindo todos os módulos acima
```

## Escopo desta PoC

-  Um único espaço físico instrumentado
-  Hardware já disponível (Pi 3 + webcam usada) — sem compra de equipamento
-  Dados de reserva mockados localmente
-  Contagem de pessoas anônima e numérica (sem imagens persistidas)
-  Sem integração real com a aplicação de reservas em produção
-  Sem suporte a múltiplos espaços simultâneos

Detalhes completos em [`docs/visao.md`](docs/visao.md) e
[`docs/requisitos.md`](docs/requisitos.md).

## Privacidade

Nenhuma imagem capturada pela câmera é gravada em disco. A contagem de
pessoas produz apenas um número, descartando o frame logo em seguida.
Veja a seção 7 de [`docs/arquitetura.md`](docs/arquitetura.md) para mais
detalhes sobre as decisões de privacidade por design.
