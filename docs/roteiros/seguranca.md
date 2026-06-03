# Segurança Básica do Host

## Objetivo

Aplicar uma configuração mínima de segurança em uma VPS recém-provisionada antes da instalação de serviços e aplicações.

Esta etapa inclui:

* Limpeza de regras de firewall pré-existentes;
* Configuração do UFW;
* Instalação do Fail2Ban;
* Endurecimento do SSH;
* Validação após reinicialização.

---

## Limpeza de Regras Existentes

Remova regras pré-existentes do iptables.

```bash
iptables -F
iptables -X
```

Persistir o estado atual:

```bash
netfilter-persistent save
```

Verificar:

```bash
iptables -L
```

Resultado esperado:

```text
Chain INPUT (policy ACCEPT)
Chain FORWARD (policy ACCEPT)
Chain OUTPUT (policy ACCEPT)
```

---

## Instalação do UFW

Instalar:

```bash
apt install ufw
```

Verificar aplicações conhecidas:

```bash
ufw app list
```

Exemplo:

```text
Available applications:
  OpenSSH
```

---

## Liberação de Acesso SSH

Permitir conexões SSH:

```bash
ufw allow OpenSSH
```

Verificar status:

```bash
ufw status
```

Resultado esperado:

```text
Status: inactive
```

---

## Ativação do Firewall

Ativar:

```bash
ufw enable
```

Confirme a ativação quando solicitado.

---

## Abertura de Portas

Permitir acesso HTTP:

```bash
ufw allow 80/tcp
```

Permitir acesso HTTPS:

```bash
ufw allow 443/tcp
```

Permitir acesso ao painel administrativo futuro:

```bash
ufw allow 81/tcp
```

Permitir acesso SSH alternativo:

```bash
ufw allow 2222/tcp
```

Aplicar alterações:

```bash
ufw reload
```

---

## Instalação do Fail2Ban

Instalar:

```bash
apt install fail2ban
```

Verificar funcionamento:

```bash
systemctl status fail2ban
```

Resultado esperado:

```text
Active: active (running)
```

Habilitar inicialização automática:

```bash
systemctl enable fail2ban
```

---

## Endurecimento do SSH

Editar a configuração:

```bash
nano /etc/ssh/sshd_config
```

Recomendações mínimas:

```text
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
PermitEmptyPasswords no
```

Aplicar alterações:

```bash
systemctl restart ssh
```

> Antes de encerrar a sessão atual, valide a conexão SSH em um segundo terminal.

---

## Reinicialização

Após concluir as alterações de segurança:

```bash
shutdown -r now
```

---

## Validação Pós-Reinicialização

Verificar firewall:

```bash
ufw status verbose
```

Verificar Fail2Ban:

```bash
systemctl status fail2ban
```

Verificar SSH:

```bash
systemctl status ssh
```

Verificar portas abertas:

```bash
ss -tulpn
```

---

## Resultado Esperado

Ao final desta etapa o servidor deverá possuir:

* Firewall ativo;
* Portas mínimas liberadas;
* Fail2Ban habilitado;
* Serviço SSH configurado;
* Configurações persistidas após reinicialização;
* Ambiente preparado para instalação dos serviços da infraestrutura.
