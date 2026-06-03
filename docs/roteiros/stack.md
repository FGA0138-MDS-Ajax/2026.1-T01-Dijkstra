# Virtualização com Incus

## Objetivo

Transformar a VPS em um host de virtualização leve utilizando Incus.

A partir desta etapa, aplicações e serviços não serão instalados diretamente no sistema operacional principal. Em vez disso, serão executados em containers dedicados administrados pelo Incus.

## Arquitetura

```text
Internet
    │
    ▼
Host Ubuntu 24.04
    │
    ├── UFW
    ├── Fail2Ban
    ├── Incus
    │
    ▼
Container: stack
    │
    ├── Docker
    ├── Docker Compose
    ├── Aplicações
    └── Serviços
```

O host permanece responsável apenas por:

* Rede;
* Firewall;
* Encaminhamento de portas;
* Virtualização;
* Administração do ambiente.

As aplicações serão executadas dentro dos containers.

---

## Instalação do Incus

Instalar:

```bash
apt install incus
```

Inicializar o ambiente:

```bash
incus admin init
```

### Configuração utilizada

| Item                              | Valor    |
| --------------------------------- | -------- |
| Clustering                        | Não      |
| Storage Backend                   | BTRFS    |
| Storage Pool                      | default  |
| Loop Device                       | 30 GiB   |
| Network Bridge                    | incusbr0 |
| Exposição Remota                  | Não      |
| Atualização Automática de Imagens | Sim      |

---

## Criação do Container Principal

Criar o container:

```bash
incus init images:ubuntu/24.04 stack
```

Verificar:

```bash
incus ls
```

---

## Perfil de Proxy

Criar perfil:

```bash
incus profile create proxy-stack
```

Adicionar dispositivo de encaminhamento:

```bash
incus profile device add proxy-stack multi-range proxy \
  listen="tcp:0.0.0.0:80,81,443,2222" \
  connect="tcp:127.0.0.1:80,81,443,22"
```

Verificar:

```bash
incus profile show proxy-stack
```

---

## Associação do Perfil

Adicionar o perfil ao container:

```bash
incus profile add stack proxy-stack
```

---

## Habilitação de Recursos Necessários

Permitir execução de containers aninhados:

```bash
incus config set stack \
  security.nesting=true \
  security.syscalls.intercept.mknod=true \
  security.syscalls.intercept.setxattr=true
```

Validar:

```bash
incus config show stack --expanded
```

---

## Inicialização do Container

Iniciar:

```bash
incus start stack
```

Acessar:

```bash
incus shell stack
```

---

## Habilitação de Encaminhamento IPv4

No host principal:

```bash
sysctl -w net.ipv4.ip_forward=1
```

Persistir:

```bash
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
```

---

# Preparação do Container

A partir deste ponto os comandos são executados dentro do container `stack`.

Atualizar:

```bash
apt update
apt dist-upgrade
apt clean
```

---

## Dependências Básicas

Instalar ferramentas de uso geral:

```bash
apt install \
    htop \
    bash-completion \
    curl \
    wget \
    build-essential \
    emacs-nox \
    zstd \
    zip \
    unzip \
    rar \
    unrar \
    python3-venv \
    ca-certificates \
    openssh-server
```

---

## Repositório Oficial Docker

Criar diretório de chaves:

```bash
install -m 0755 -d /etc/apt/keyrings
```

Baixar chave:

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
```

Permissões:

```bash
chmod a+r /etc/apt/keyrings/docker.asc
```

Adicionar repositório:

```bash
tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```

---

## Instalação do Docker

Instalar:

```bash
apt update

apt install \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin
```

---

## Teste de Funcionamento

Executar:

```bash
docker run hello-world
```

Resultado esperado:

```text
Hello from Docker!
```

Verificar:

```bash
docker ps
```

---

## Limpeza Inicial

Remover imagens e containers de teste:

```bash
docker system prune --all
```

---

## Resultado Esperado

Ao final desta etapa o ambiente deverá possuir:

* Host Ubuntu dedicado ao gerenciamento;
* Incus configurado e operacional;
* Container `stack` criado;
* Encaminhamento de portas configurado;
* Docker funcional dentro do container;
* Ambiente preparado para implantação das aplicações.
