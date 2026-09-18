[](https://github.com/Tecnativa/doodba?utm_source=gemini)[cite: 8]
[](https://www.google.com/search?q=https://github.com/Tecnativa/doodba-copier-template/tree/v9.7.3&utm_source=gemini)[cite:
8]
[](https://www.google.com/search?q=https://github.com/odoo/odoo/tree/14.0&utm_source=gemini)[cite:
8] [](https://www.google.com/search?q=LICENSE&utm_source=gemini)[cite: 8]
[](https://pre-commit.com/?utm_source=gemini)[cite: 8]

# Doodba Odoo 14 - Ambiente de Desenvolvimento Linux (Ubuntu)

Este repositório contém a infraestrutura de desenvolvimento para o Odoo 14 baseada no
ecossistema [Doodba](https://github.com/Tecnativa/doodba?utm_source=gemini), otimizada
para **Linux Ubuntu nativo** com Nginx local, certificados SSL confiáveis via `mkcert` e
integração com módulos OCA de Inventário e RH[cite: 1, 8].

## 🏗 Arquitetura do Ambiente (`devel.yaml`)

O ambiente `devel` provisiona os seguintes serviços via Docker[cite: 1, 5]:

| Serviço      | Função                                 | Acesso (Usando `PORT_PREFIX=15`)                                                                                                      |
| ------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `nginx`      | Reverse Proxy HTTP/HTTPS com SSL Local | [http://localhost:8080](http://localhost:8080?utm_source=gemini) / [https://localhost:8443](https://localhost:8443?utm_source=gemini) |
| `odoo`       | Odoo 14 OCB (OCA)                      | Interno (`:8069` / `:8072`)                                                                                                           |
| `odoo_proxy` | Proxy de desenvolvimento/Bypass        | [http://127.0.0.1:15069](https://www.google.com/search?q=http://127.0.0.1:15069&utm_source=gemini)                                    |
| `db`         | PostgreSQL 16                          | Somente rede Docker interna                                                                                                           |
| `smtp`       | MailHog (Interceptação de Emails)      | [http://127.0.0.1:15025/](https://www.google.com/search?q=http://127.0.0.1:15025/&utm_source=gemini)                                  |
| `pgweb`      | Interface de Inspeção do PostgreSQL    | [http://127.0.0.1:15081/](https://www.google.com/search?q=http://127.0.0.1:15081/&utm_source=gemini)                                  |
| `wdb`        | Debugger Python Web                    | [http://127.0.0.1:15984/](https://www.google.com/search?q=http://127.0.0.1:15984/&utm_source=gemini)                                  |

- **Credenciais padrão:** `admin` / `admin` (dados demo instalados)[cite: 1].
- **Banco de dados:** `devel`[cite: 1].
- **Idioma padrão:** `pt_BR`[cite: 1].

---

## 🚀 1. Pré-requisitos (Ubuntu)

Certifique-se de ter o Docker Compose v2 e as ferramentas de build instaladas[cite: 1]:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip openssl libnss3-tools mkcert

```

Adicione seu usuário ao grupo `docker` (necessário logout/login para aplicar)[cite: 1]:

```bash
sudo usermod -aG docker "$USER"

```

## 🛠 2. Instalação e Configuração

### Passo 2.1: Ambiente Virtual (Host)

O Odoo roda de forma isolada, mas ferramentas de automação (Copier, Invoke, Pre-commit)
precisam de um venv no host[cite: 1]:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install "copier>=9" invoke pre-commit

```

### Passo 2.2: Exportar Variáveis de Usuário e Porta

Para evitar conflitos de portas com outras instâncias e problemas de permissão em
volumes, defina as variáveis[cite: 1, 5]:

```bash
export DOODBA_UID="$(id -u)"
export DOODBA_GID="$(id -g)"
export DOODBA_UMASK="022"
export DOODBA_GITAGGREGATE_UID="$(id -u)"
export DOODBA_GITAGGREGATE_GID="$(id -g)"
export PORT_PREFIX=15

```

_(Dica: Para não ter que exportar a porta a cada terminal, crie um arquivo `.env` na
raiz contendo `PORT_PREFIX=15`)._

### Passo 2.3: Configurar Certificado SSL Local (HTTPS)

Configure o `mkcert` para rodar o Nginx sem alertas de segurança no navegador:

```bash
mkcert -install
mkdir -p nginx/ssl
mkcert localhost
mv localhost.pem nginx/ssl/server.crt
mv localhost-key.pem nginx/ssl/server.key

```

### Passo 2.4: Corrigir Permissões e Sincronizar OCA (Git Aggregate)

Previna erros de permissão concedendo ao seu usuário o controle da pasta de
repositórios:

```bash
sudo chown -R "$(id -u):$(id -g)" odoo/custom/src
docker compose -f devel.yaml build --pull
docker compose -f devel.yaml --profile devel-setup run --rm -T devel-setup

```

### Passo 2.5: Criar Banco de Dados `devel`

O autoconfig do Postgres cria um banco vazio[cite: 1]. Para inicializar com o idioma
correto e dependências:

```bash
docker compose -f devel.yaml up -d db

# Aguarde 5-10 segundos para o Postgres iniciar
docker compose -f devel.yaml run --rm --no-deps odoo click-odoo-dropdb devel
docker compose -f devel.yaml run --rm --no-deps odoo click-odoo-initdb -n devel -m base --demo
docker compose -f devel.yaml run --rm --no-deps odoo preparedb
docker compose -f devel.yaml run --rm --no-deps odoo odoo -d devel --load-language=pt_BR --stop-after-init

```

### Passo 2.6: Subir o Ambiente e Instalar Addons

Suba todos os serviços e instale os módulos de RH e Inventário[cite: 1]:

```bash
docker compose -f devel.yaml up -d nginx

# Instala módulos no banco devel
docker compose -f devel.yaml run --rm --no-deps odoo \
  odoo -d devel -i stock,stock_request,hr,hr_personal_equipment_request,hr_employee_ppe --stop-after-init

# Restarta o serviço principal para aplicar
docker compose -f devel.yaml start odoo

```

---

## 🧪 3. Validação (Smoke Test)

Teste se a instalação de módulos e geração de fluxos de EPI e Requisição de Estoque
estão operacionais injetando o script de teste[cite: 6]:

```bash
docker compose -f devel.yaml exec -T odoo odoo shell -d devel < scripts/smoke_test_addons.py

```

**Resultado Esperado:** Mensagens `stock.request SR/00001 state=open` e
`hr.personal.equipment.request id=1 state=accepted` finalizando com `OK`[cite: 6].

---

## ⚠️ 4. Troubleshooting (Erros Esperados e Soluções)

### 1. `fatal: cannot mkdir /opt/odoo/custom/src/odoo: Permission denied`

**Causa:** A pasta `src` foi gerada pelo root do Docker e o seu container restrito não
tem permissão de escrita[cite: 1]. **Solução:**

```bash
sudo chown -R "$(id -u):$(id -g)" odoo/custom/src
export DOODBA_GITAGGREGATE_UID="$(id -u)"

```

### 2. `failed to bind host port 0.0.0.0:80/tcp: address already in use`

**Causa:** A porta 80 já está ocupada no seu Ubuntu (possivelmente pelo Apache2 ou outro
Nginx). **Solução:** O `devel.yaml` neste repositório já está ajustado para expor o
Nginx nas portas `8080:80` e `8443:443`[cite: 5].

### 3. `Bind for 127.0.0.1:14984 failed: port is already allocated`

**Causa:** Container residual de outro projeto rodando na mesma porta mapeada.
**Solução:** Alterar dinamicamente o prefixo de todas as portas do Doodba no Host[cite:
5]:

```bash
export PORT_PREFIX=15
docker compose -f devel.yaml up -d

```

### 4. `Are you trying to mount a directory onto a file (or vice-versa)?` (Erro no Nginx)

**Causa:** O Docker não encontrou o arquivo `nginx/nginx.conf` e gerou automaticamente
uma **pasta** vazia com esse nome no lugar[cite: 1]. **Solução:**

```bash
rm -rf nginx/nginx.conf
# Recrie o arquivo nginx.conf corretamente antes de subir o docker.

```

### 5. `error: failed to push some refs...` ao tentar fazer `git commit`

**Causa:** O _pre-commit_ do Doodba barra commits caso o Pylint encontre usos de `print`
ou variáveis mágicas como `env` em scripts do shell[cite: 6]. **Solução:** Bypass da
validação estrita para o commit de configuração[cite: 7]:

```bash
git add .
git commit -m "Sua mensagem" --no-verify
git push -u origin main

```
