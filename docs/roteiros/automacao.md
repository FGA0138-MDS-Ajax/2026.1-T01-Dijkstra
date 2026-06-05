# Deploy — SiGEsporte na VPS

Registro das ações realizadas para configurar e publicar a aplicação Django (SiGEsporte) em uma VPS usando Docker, Nginx Proxy Manager e CI/CD via GitHub Actions.

---

## 1. Criação de usuários na VPS

Script `users.sh` — cria o usuário, define senha padrão e força troca no primeiro login:

```bash
#!/bin/bash

set -e

DEFAULT_PASSWORD='Tr0c@r123!'

if [ $# -ne 1 ]; then
    echo "Uso: $0 <usuario>"
    exit 1
fi

USERNAME=$(echo "$1" | tr '[:upper:]' '[:lower:]')

if id "$USERNAME" &>/dev/null; then
    echo "Usuário '$USERNAME' já existe."
else
    echo "Criando usuário '$USERNAME'..."
    useradd -m -s /bin/bash "$USERNAME"
fi

echo "${USERNAME}:${DEFAULT_PASSWORD}" | chpasswd

# Força troca da senha no próximo login
chage -d 0 "$USERNAME"

echo
echo "Usuário : $USERNAME"
echo "Senha   : $DEFAULT_PASSWORD"
echo "Status  : senha redefinida e troca obrigatória no próximo login"
```

Usuários criados:

```
bash users.sh revisor
Criando usuário 'revisor'...

Usuário : revisor
Senha   : Tr0c@r123!
Status  : senha redefinida e troca obrigatória no próximo login
```

```
bash usuarios.sh automation
Criando usuário 'automation'...

Usuário : automation
Senha   : Tr0c@r123!
Status  : senha redefinida e troca obrigatória no próximo login
```

---

## 2. DNS — Cloudflare

Apontar o domínio para o IP da VPS criando um registro A:

```
app.seu.dominio.com  →  IP_DA_VPS
```

---

## 3. Nginx Proxy Manager (NPM)

### 3.1 Estrutura de diretórios

```bash
mkdir -p /opt/docker
chgrp docker /opt/docker

# Como usuário 500+
mkdir -p /opt/docker/npm
```

### 3.2 `docker-compose.yml`

```yaml
services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    container_name: npm
    restart: unless-stopped
    ports:
      - '80:80'    # HTTP público
      - '443:443'  # HTTPS público
      - '81:81'    # Painel de administração
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
```

### 3.3 Subir o container

```bash
docker compose up
```

Acessar o painel em `seu.dominio.com:81` e configurar certificado SSL (Let's Encrypt / ECDSA / RSA) para o domínio/serviço desejado.

---

## 4. Preparação da aplicação Django

### 4.1 Variáveis de ambiente (`.env`)

Ajustar `.env.example` adicionando os hosts permitidos:

```
ALLOWED_HOSTS=duat.site,sigesporte.duat.site,IP_DA_VPS
```

### 4.2 `config/settings.py`

```python
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

STATIC_ROOT = BASE_DIR / "staticfiles"
```

### 4.3 Dependências

```bash
pip install --upgrade pip
pip install gunicorn
pip freeze >> requirements.txt
```

---

## 5. Build e deploy da aplicação

### 5.1 Estrutura de diretórios

```bash
/opt/docker/
├── npm/
│   └── docker-compose.yml
└── sigesporte/
    ├── Dockerfile
    ├── docker-compose.yml
    └── .env
```

### 5.2 Build da imagem

```bash
cd /opt/docker/sigesporte
docker build -t sigesporte_alpha_001 .
```

Log do build:

```
[+] Building 307.8s (13/13) FINISHED                                docker:default
 => [builder 1/5] FROM docker.io/library/python:3.12-slim           11.8s
 => [builder 2/5] RUN apt-get update && apt-get install -y git gcc   92.6s
 => [builder 3/5] RUN git clone --depth=1 --branch developer \
      https://github.com/FGA0138-MDS-Ajax/2026.1-T01-Dijkstra        10.4s
 => [builder 4/5] WORKDIR /app                                        0.6s
 => [builder 5/5] RUN python -m venv /app/.venv && pip install ...   69.6s
 => [stage-1 3/5] COPY --from=builder /app /app                       9.2s
 => [stage-1 4/5] RUN mkdir -p /app/media /app/staticfiles            3.7s
 => [stage-1 5/5] RUN echo "STATIC_ROOT = ..." >> settings.py        1.8s
 => exporting to image                                                82.4s
 => => naming to docker.io/library/sigesporte_alpha_001:latest
```

### 5.3 Criar o arquivo `.env` na VPS

```bash
echo "SECRET_KEY=sua_chave_aqui" > .env
echo "DEBUG=False" >> .env
echo "ALLOWED_HOSTS=seu.dominio.com,IP_DA_VPS" >> .env
```

### 5.4 Subir os containers

```bash
docker compose up -d --build
```

Log:

```
[+] Running 3/3
 ✔ Image sigesporte-web       Built
 ✔ Network sigesporte_default Created
 ✔ Container sigesporte-web-1 Started
```

### 5.5 Verificar containers em execução

```bash
docker ps
```

```
CONTAINER ID   IMAGE                             PORTS                          NAMES
945bba5035cb   sigesporte_alpha_001              0.0.0.0:8000->8000/tcp         sigesporte-web-1
f767c2e09168   jc21/nginx-proxy-manager:latest   0.0.0.0:80-81->80-81/tcp,
                                                 0.0.0.0:443->443/tcp           npm
```

### 5.6 Log da aplicação (migrações + servidor)

```
web-1  | Operations to perform:
web-1  |   Apply all migrations: admin, auth, contenttypes, core, sessions
web-1  | Running migrations:
web-1  |   Applying contenttypes.0001_initial... OK
web-1  |   Applying auth.0001_initial... OK
web-1  |   Applying admin.0001_initial... OK
web-1  |   Applying core.0001_initial... OK
web-1  |   Applying core.0002_dados_iniciais... OK
web-1  |   Applying core.0003_alter_evento_descricao... OK
web-1  |   Applying core.0004_espacofisico... OK
web-1  |   Applying core.0005_organizacao... OK
web-1  |   Applying core.0005_evento_status... OK
web-1  |   Applying core.0006_merge_0002_dados_iniciais_0005_organizacao... OK
web-1  |   Applying sessions.0001_initial... OK
web-1  |
web-1  | 134 static files copied to '/app/staticfiles', 4 skipped due to conflict.
web-1  | Django version 6.0.5, using settings 'config.settings'
web-1  | Starting development server at http://0.0.0.0:8000/
```

> **Atenção:** o servidor de desenvolvimento Django não deve ser usado em produção. Substituir por Gunicorn/uWSGI + configuração WSGI/ASGI adequada.

---

## 6. CI/CD — GitHub Actions (autodeploy)

### 6.1 Geração do par de chaves SSH para o usuário `automation`

```bash
ssh-keygen -t rsa -b 4096 -C "automation@duat.site"
```

```
Your identification has been saved in /home/automation/.ssh/id_rsa
Your public key has been saved in /home/automation/.ssh/id_rsa.pub
The key fingerprint is:
SHA256:QOgFf7/76IpPskhxPE+bkgzeMe1+6hErZVKMkYkpmF8 automation@duat.site
```

Adicionar a chave pública ao arquivo de chaves autorizadas da VPS:

```bash
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 6.2 Secrets no GitHub

Acessar **Settings > Secrets and variables > Actions** e adicionar:

| Secret | Valor |
|---|---|
| `VPS_HOST` | IP ou domínio da VPS |
| `VPS_USER` | Usuário SSH (ex: `automation`) |
| `VPS_SSH_KEY` | Conteúdo de `~/.ssh/id_rsa` (chave privada) |
| `VPS_PORT` | Porta SSH (normalmente `22`) |

### 6.3 Workflow `.github/workflows/deploy.yml`

A cada push na branch `developer`, o GitHub Actions conecta na VPS via SSH, entra na pasta do projeto, rebuilda a imagem e recria o container.

```yaml
name: Deploy SiGEsporte

on:
  push:
    branches:
      - developer

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          port: ${{ secrets.VPS_PORT }}
          script: |
            cd /opt/docker/sigesporte
            docker compose down
            docker compose up -d --build
```

---

## Interfaces de rede da VPS

```
eth0   inet 10.135.56.128/24
docker0  inet 172.17.0.1/16
br-ee82b8a67c12  inet 172.18.0.1/16  (rede NPM)
br-653c8c02f6fd  inet 172.19.0.1/16  (rede sigesporte)
```