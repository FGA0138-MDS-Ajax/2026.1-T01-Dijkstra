# Documento de Requisitos — PoC de Validação de Entrada e Ocupação

## 1. Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF01 | O sistema deve capturar frames de vídeo de uma webcam conectada ao Raspberry Pi. | Alta |
| RF02 | O sistema deve decodificar QR codes presentes no frame capturado. | Alta |
| RF03 | O sistema deve validar o token do QR code contra uma base de dados de reservas mockada localmente. | Alta |
| RF04 | A validação deve considerar: existência do token, janela de horário da reserva (início/fim) e correspondência com o espaço monitorado. | Alta |
| RF05 | O sistema deve fornecer feedback imediato (visual e/ou sonoro) do resultado da validação: acesso liberado ou negado. | Alta |
| RF06 | O sistema deve contar, de forma numérica e anônima, quantas pessoas estão presentes no espaço monitorado. | Alta |
| RF07 | A contagem de pessoas não deve identificar indivíduos nem persistir imagens capturadas. | Alta |
| RF08 | O sistema deve aplicar um tempo de estabilização (debounce) antes de mudar o status de ocupação, para evitar oscilação por detecções pontuais. | Média |
| RF09 | O sistema deve expor uma API local com o estado atual: reserva vigente, último resultado de validação de entrada, status de ocupação. | Alta |
| RF10 | O sistema deve exibir um painel (dashboard) com o estado atual em tempo quase real. | Alta |
| RF11 | O painel deve sinalizar quando houver reserva ativa sem ocupação detectada por um período configurável ("possível não comparecimento"). | Média |
| RF12 | O sistema deve alternar automaticamente entre modo de leitura de QR e modo de contagem de ocupação, usando a mesma câmera. | Alta |

## 2. Requisitos não funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RNF01 | O sistema deve rodar integralmente em um Raspberry Pi 3, sem depender de hardware adicional não disponível hoje. | Alta |
| RNF02 | O sistema deve rodar com uma única webcam, sem exigir uma segunda câmera. | Alta |
| RNF03 | Nenhuma imagem capturada deve ser persistida em disco em nenhum momento. | Alta |
| RNF04 | O sistema não deve depender de conectividade com a internet ou serviços externos para funcionar durante a demonstração. | Alta |
| RNF05 | O sistema não deve realizar nenhuma chamada real à aplicação de reservas em produção. | Alta |
| RNF06 | O tempo de resposta entre a leitura de um QR code válido e o feedback ao usuário deve ser perceptivelmente imediato (poucos segundos). | Média |
| RNF07 | O sistema deve continuar funcional mesmo com processamento limitado (CPU sem aceleração de hardware para visão computacional). | Alta |
| RNF08 | O código deve ser organizado de forma que a futura substituição do mock de reservas por uma integração real seja possível sem redesenhar a arquitetura. | Baixa |

## 3. Requisitos de dados — mock de reserva

Estrutura simulando o retorno esperado da API de reservas real:

```json
{
  "sala_id": "LAB-203",
  "reservas": [
    {
      "reserva_id": "r001",
      "usuario_id": "u123",
      "usuario_nome": "Maria Silva",
      "inicio": "2026-07-01T14:00:00",
      "fim": "2026-07-01T16:00:00",
      "qr_token": "a1b2c3d4e5"
    }
  ]
}
```

Campos mínimos exigidos para a validação (RF03/RF04):
- `qr_token`: identificador único codificado no QR code do usuário.
- `sala_id`: deve corresponder ao espaço monitorado pelo Pi.
- `inicio` / `fim`: janela de validade da reserva.

## 4. Fora de escopo (não são requisitos deste PoC)

- Autenticação de usuários no dashboard.
- Persistência de dados além da sessão de demonstração em execução.
- Suporte a múltiplos espaços simultâneos.
- Qualquer forma de identificação pessoal via câmera (reconhecimento
  facial, biometria).
- Integração de leitura ou escrita com a aplicação de reservas em
  produção.
