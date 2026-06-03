# Bootstrap Inicial do Host

## Objetivo

Realizar a configuração inicial de uma VPS recém-criada com Ubuntu 24.04 LTS, preparando o sistema operacional para as próximas etapas de segurança, virtualização e publicação de serviços.

## Pré-requisitos

* VPS provisionada e acessível por SSH;
* Usuário administrativo criado pelo provedor;
* Acesso ao terminal local.

---

## Acesso Inicial

Conecte-se à instância utilizando SSH:

```bash
ssh ubuntu@IP_DO_SERVIDOR
```

Eleve privilégios para o usuário root:

```bash
sudo su -l
```

Defina uma senha para o usuário root:

```bash
passwd
```

> Embora o acesso remoto via root possa ser desabilitado posteriormente, manter uma senha local definida simplifica procedimentos de recuperação e manutenção.

---

## Configuração de Hostname

Defina o nome permanente da máquina:

```bash
echo metis.duat.site > /etc/hostname
```

Atualize também o arquivo de resolução local:

```bash
nano /etc/hosts
```

Exemplo:

```text
127.0.0.1 localhost
127.0.1.1 metis.duat.site metis
```

---

## Configuração de Fuso Horário

Configure o fuso horário adequado para a localização da infraestrutura ou equipe responsável.

```bash
dpkg-reconfigure tzdata
```

Exemplo:

```text
America/Sao_Paulo
```

---

## Configuração de Atualizações Automáticas

Configurar a política de atualizações automáticas do sistema:

```bash
dpkg-reconfigure unattended-upgrades
```

---

## Atualização Completa do Sistema

Atualize os índices de pacotes:

```bash
apt update
```

Instale todas as atualizações disponíveis:

```bash
apt dist-upgrade
```

Remova arquivos temporários de pacotes:

```bash
apt clean
```

Remova dependências não utilizadas:

```bash
apt autoremove
```

---

## Verificação de Recursos

Verifique memória disponível:

```bash
free -h
```

Verifique armazenamento disponível:

```bash
df -hT
```

---

## Criação de Área de Swap

Criar o diretório de armazenamento:

```bash
mkdir -p /var/cache/swap/
```

Criar o arquivo de swap:

```bash
touch /var/cache/swap/file
chmod 600 /var/cache/swap/file
```

Alocar 4 GB:

```bash
fallocate -l 4G /var/cache/swap/file
```

Criar a área de swap:

```bash
mkswap -L swap /var/cache/swap/file
```

Ativar:

```bash
swapon /var/cache/swap/file
```

Validar:

```bash
free -ht
```

Persistir após reinicializações:

```bash
echo '/var/cache/swap/file none swap 0 0' >> /etc/fstab
```

---

## Reinicialização

Após as alterações de hostname, timezone e atualização do sistema, reinicie a máquina:

```bash
shutdown -r now
```

---

## Validação Pós-Reinicialização

Verifique o hostname:

```bash
hostnamectl
```

Verifique o fuso horário:

```bash
timedatectl
```

Verifique a swap:

```bash
swapon --show
free -ht
```

Verifique o espaço em disco:

```bash
df -hT
```

---

## Resultado Esperado

Ao final desta etapa o servidor deverá possuir:

* Hostname configurado;
* Fuso horário configurado;
* Sistema operacional atualizado;
* Área de swap persistente;
* Reinicialização validada;
* Ambiente pronto para as etapas de segurança e instalação de serviços.
