# Documento de Visão — PoC de Validação de Entrada e Ocupação de Espaços

## 1. Contexto

O campus já possui uma aplicação de reserva de espaços educacionais e
esportivos em produção. Essa aplicação resolve bem o problema de
**agendar** um espaço, mas não sabe dizer:

- se a pessoa que reservou realmente compareceu;
- se o espaço está sendo usado *neste momento*, independente de reserva;
- se reservas estão sendo feitas e não utilizadas (*no-show*), gerando
  ociosidade que a agenda não revela.

Este documento descreve a visão de uma **prova de conceito (PoC)**
independente, que adiciona uma camada física de verificação sobre a
aplicação existente — sem alterá-la.

## 2. Objetivo do PoC

Demonstrar, em um único espaço físico, que é possível:

1. **Validar a entrada** de uma pessoa em uma sala/quadra a partir de um
   QR code vinculado à sua reserva.
2. **Detectar de forma anônima** se o espaço está ocupado, usando
   contagem numérica de pessoas por visão computacional — sem
   identificar ou armazenar imagens de ninguém.
3. Cruzar os dois sinais para gerar um insight que a aplicação atual não
   tem hoje: **reserva ociosa** (reservado, mas ninguém apareceu ou o
   espaço esvaziou antes do previsto).

## 3. Escopo do PoC

### Dentro do escopo
- Um único espaço físico (sala ou quadra) instrumentado.
- Hardware já disponível: Raspberry Pi 3 + webcam usada. **Nenhuma
  compra de equipamento nesta fase.**
- Dados de reserva **mockados localmente**, no formato que a API real
  devolveria (sem integração de fato).
- Leitura de QR code gerado a partir de uma reserva simulada.
- Contagem numérica e anônima de pessoas no espaço (sem reconhecimento
  facial, sem identificação individual, sem gravação de imagem).
- Painel local (Streamlit) mostrando o estado atual: reserva ativa,
  status de ocupação, histórico simples da sessão de demonstração.

### Fora do escopo
- Integração real com a aplicação de reservas em produção.
- Múltiplos espaços/salas simultâneos.
- Qualquer forma de identificação de pessoas (rosto, biometria,
  matrícula via câmera).
- Persistência de longo prazo ou infraestrutura em nuvem.
- Alta disponibilidade, autenticação de usuários do painel, etc.

## 4. Por que anonimizar a contagem de pessoas

A decisão de trabalhar apenas com **contagem numérica anônima** (quantas
pessoas há no espaço, nunca quem são) é deliberada:

- Evita qualquer discussão de conformidade com legislação de proteção
  de dados pessoais, já que nenhum dado pessoal é coletado, processado
  ou armazenado pela câmera de ocupação.
- É suficiente para o objetivo do PoC: o que importa é *se* o espaço
  está em uso, não *quem* está usando.
- Simplifica a arquitetura: não há necessidade de banco de dados de
  identidades, consentimento, retenção ou descarte de imagens.

A imagem capturada pela câmera de ocupação é processada em memória e
**descartada imediatamente** após a contagem — nunca é salva em disco.

## 5. Critérios de sucesso da demonstração

O PoC é considerado bem-sucedido se, ao vivo, for possível mostrar:

1. Uma reserva mockada ativa para o espaço.
2. Uma pessoa escaneando um QR code válido → acesso liberado com
   feedback imediato.
3. Um QR code inválido ou fora do horário da reserva → acesso negado.
4. O painel refletindo, em tempo real, se o espaço está ocupado ou
   vazio, com base na contagem de pessoas.
5. Um cenário de "reserva sem comparecimento": reserva ativa, mas
   ocupação zero por um tempo configurável → o painel sinaliza a
   inconsistência.

## 6. Restrições conhecidas

- Hardware: Raspberry Pi 3 (baixo poder de processamento) + uma única
  webcam usada (não duas).
- Sem orçamento para compra de equipamento nesta fase.
- Ambiente de demonstração controlado (iluminação e enquadramento
  calibrados manualmente antes da apresentação).

## 7. Próximos passos (fora deste PoC)

- Avaliar integração de leitura/escrita real com a API de reservas.
- Avaliar escalabilidade para múltiplos espaços (um Pi por sala vs.
  arquitetura centralizada com câmeras IP).
- Definir política formal de retenção de dados caso o escopo evolua
  para além da contagem anônima.
