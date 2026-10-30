# SPARCC (morea-ds-web)

Sistema do MOREA para monitorar o consumo de água, energia e gás: os dispositivos enviam os dados por API, o sistema processa estatísticas e mostra dashboards e gráficos.

- Django 5.0, Python 3.11.5
- MySQL 8, nginx para os arquivos estáticos e a mídia
- Roda em Docker. A cada tag `v*`, o GitHub publica a imagem em `ghcr.io/morea-ifs/morea-ds-web`, cria uma Release e, se a AWS estiver configurada, atualiza o servidor (EC2).

## 1. Situação atual

- CI roda a cada push na `develop` e na `main` e em todo pull request.
- O deploy automático na EC2 já está no `release.yml`, mas só roda depois que a AWS for configurada (seção 7.4). Até lá, a tag publica a imagem e a Release, e o job de deploy é pulado.

## 2. Dependências

Só precisa de **Docker** com o plugin **Compose**. Tudo roda em contêiner.

- Linux: https://docs.docker.com/engine/install/ (depois, `sudo usermod -aG docker $USER` e abrir o terminal de novo)
- Windows ou macOS: https://docs.docker.com/desktop/

Confira:

```bash
docker --version          # 24 ou mais novo
docker compose version    # v2 ou mais novo
```

Versões fixadas no projeto: Python 3.11.5 (`Dockerfile`), MySQL 8.4.3 e nginx 1.27.2 (`docker-compose.yml`), bibliotecas Python em `requirements.txt`.

## 3. Primeira vez na máquina

```bash
git clone https://github.com/Morea-IFS/morea-ds-web.git
cd morea-ds-web

# Baixa as imagens do MySQL e do nginx, monta a imagem do app e sobe os quatro contêineres.
# Na primeira vez demora alguns minutos (download + instalação das dependências).
docker compose up --build

# Em outro terminal: cria o usuário administrador
docker compose exec web python manage.py createsuperuser
```

Abra http://localhost:8000 (site) e http://localhost:8000/admin (painel). As migrations e o `collectstatic` rodam sozinhos quando o app sobe (`scripts/start.sh`).

O que o `docker compose up` sobe:

| Contêiner | Imagem | Porta no seu PC |
|---|---|---|
| `nginx` | `nginx:1.27.2-alpine` | 8000 (entrega o site, os estáticos e a mídia) |
| `web` | montada do `Dockerfile` | só interna (gunicorn na 8000) |
| `cron` | a mesma do `web` | nenhuma (jobs periódicos, ver abaixo) |
| `db` | `mysql:8.4.3` | 3307 (para não colidir com um MySQL local na 3306) |

As variáveis de desenvolvimento (senhas `sparcc`/`sparcc`, `ENVIRONMENT=PROD` etc.) estão no próprio `docker-compose.yml`. Servem só para a sua máquina. O `.env.example` é o modelo para quem rodar sem Docker.

O contêiner `cron` roda os jobs do `CRONJOBS` (`morea_ds/settings.py`) pelo `scripts/cron.sh`: `app.data_processing.run` a cada hora cheia e `app.graphs.generateAllMotes24hRaw` às 3h (UTC). O `settings.py` aponta o job horário para `hourlyDataProcessing`, que não existe no código; por isso o `cron.sh` chama `run`.

## 4. Dia a dia

```bash
docker compose up            # sobe (sem --build: usa a imagem já montada)
docker compose up -d         # sobe em segundo plano
docker compose logs -f web   # acompanha o log do app
docker compose down          # para e remove os contêineres (mantém o banco)
docker compose down -v       # para e APAGA o banco, os estáticos e a mídia (volumes)

# Qualquer comando do Django roda dentro do contêiner web:
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py test
docker compose exec web python manage.py shell
```

Quando precisa de `--build` de novo: mudou o `requirements.txt`, o `Dockerfile` ou os `scripts/`. Mudança só em código Python, template ou arquivo estático também exige rebuild, porque o código é copiado para dentro da imagem.

Para acessar o banco de fora (DBeaver, MySQL Workbench): host `127.0.0.1`, porta `3307`, banco `sparcc`, usuário `sparcc`, senha `sparcc`.

## 5. Testes e CI

O `manage.py test` ainda roda 0 testes (`app/tests.py` está vazio). O CI confere o resto.

`.github/workflows/ci.yml` roda em push na `develop` e na `main` e em todo pull request:

| Job | O que confere |
|---|---|
| `test` | instala as dependências, `manage.py check`, `makemigrations --check` (falha se alguém mudou um model sem gerar a migration), `migrate` e `test`, tudo contra um MySQL |
| `docker` | monta a imagem, sobe com MySQL e exige resposta 200 em `/admin/login/` e `/` |

Para fazer o mesmo localmente antes de abrir o PR:

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web python manage.py test
```

Há também o `django.yml`, CI antigo mantido pela equipe. Ele roda em push em qualquer branch e em PR para a `main`.

## 6. Como publicar uma versão (CD)

Fluxo de branches: trabalho em `feature/*` → PR para `develop` → PR para `main` → tag na `main`. Push e merge **nunca** publicam nada; só a tag publica.

```bash
git fetch origin
git tag v1.3.0 origin/main      # marca o commit atual da main
git push origin v1.3.0          # este push dispara o release
```

O `.github/workflows/release.yml` então:

1. roda os mesmos testes do CI no commit da tag;
2. monta a imagem e publica `ghcr.io/morea-ifs/morea-ds-web:1.3.0` e `ghcr.io/morea-ifs/morea-ds-web:latest`;
3. cria a Release em https://github.com/Morea-IFS/morea-ds-web/releases com as notas geradas dos PRs;
4. atualiza a EC2 para a versão nova (job `deploy`, só quando a AWS está configurada, ver 7.4).

Regras:

- Numeração (SemVer), continuando as Releases existentes (a última é `v1.2.1`): `v1.2.2` correção, `v1.3.0` funcionalidade nova, `v2.0.0` mudança que quebra compatibilidade.
- Não crie a Release pela página do GitHub: o workflow cria. Basta a tag.
- Tag com sufixo (`v1.3.0-rc1`) vira **pre-release**, **não** recebe `latest` e **não** faz deploy. Use para testar antes da versão final.
- Uma tag não se reaproveita. Se o release falhar, corrija e crie a próxima (`-rc2`, `v1.3.1`).
- Acompanhe em https://github.com/Morea-IFS/morea-ds-web/actions (workflow "Release").
- Para publicar a imagem e a Release não é preciso cadastrar nada: o workflow usa o `GITHUB_TOKEN` automático. O deploy precisa das variáveis da seção 7.4.

## 7. Rodar a imagem publicada (deploy)

Para quem cuida do servidor (AWS ou outro). O pipeline entrega a imagem; subir é daqui para a frente.

### 7.1 Puxar a imagem

```bash
docker pull ghcr.io/morea-ifs/morea-ds-web:1.3.0     # ou :latest
```

Se o pacote estiver privado, antes: `docker login ghcr.io` com um token do GitHub de escopo `read:packages`.

### 7.2 O que a imagem precisa para subir

| Variável | Valor em produção |
|---|---|
| `SECRET_KEY` | chave longa e secreta do Django |
| `DEBUG` | não definir (só o valor `True` liga o debug) |
| `ENVIRONMENT` | `PROD` (estáticos em `/var/www/html/Morea/static`, mídia em `/var/www/html/Morea/media`) |
| `DBTYPE` | `MySQL` (exatamente assim, com maiúsculas) |
| `DBNAME`, `DBUSER`, `DBPASSWORD`, `DBHOST`, `DBPORT` | dados do MySQL |

Guarde essas variáveis num cofre (AWS Secrets Manager, Parameter Store ou equivalente), nunca no repositório.

Além das variáveis:

- um **MySQL 8** acessível pela imagem (RDS, ou contêiner ao lado);
- a imagem escuta na porta **8000** (gunicorn); coloque um **nginx** na frente, como o `docker/nginx.conf`, porque com `DEBUG` desligado o Django não entrega estáticos nem mídia;
- um **volume em `/var/www/html/Morea/media`** (gráficos gerados e fotos de perfil) e outro em **`/var/www/html/Morea/static`**, os dois compartilhados com o nginx;
- um **segundo contêiner da mesma imagem** com o comando `sh scripts/cron.sh`, para os jobs periódicos;
- health check: `GET /admin/login/` → 200;
- na primeira subida, crie o superusuário: `python manage.py createsuperuser` dentro do contêiner.

As migrations e o `collectstatic` rodam sozinhos a cada subida (`scripts/start.sh`).

### 7.3 Exemplo mínimo com Docker puro

O jeito mais simples é usar o `docker-compose.yml` deste repositório trocando `build: .` por `image: ghcr.io/morea-ifs/morea-ds-web:1.3.0` e as variáveis pelas de produção. Com `docker run`, as peças são estas:

```bash
docker network create sparcc
docker run -d --name sparcc-web --network sparcc \
  -e SECRET_KEY=... -e ENVIRONMENT=PROD \
  -e DBTYPE=MySQL -e DBNAME=sparcc -e DBUSER=... -e DBPASSWORD=... -e DBHOST=... -e DBPORT=3306 \
  -v sparcc-static:/var/www/html/Morea/static -v sparcc-media:/var/www/html/Morea/media \
  ghcr.io/morea-ifs/morea-ds-web:1.3.0
docker run -d --name sparcc-cron --network sparcc \
  -e SECRET_KEY=... -e ENVIRONMENT=PROD \
  -e DBTYPE=MySQL -e DBNAME=sparcc -e DBUSER=... -e DBPASSWORD=... -e DBHOST=... -e DBPORT=3306 \
  -v sparcc-media:/var/www/html/Morea/media \
  ghcr.io/morea-ifs/morea-ds-web:1.3.0 sh scripts/cron.sh
# nginx com o docker/nginx.conf (o proxy_pass aponta para http://web:8000; ajuste para sparcc-web)
```

Para atualizar: troque a versão da imagem e reinicie. Para voltar atrás: aponte para a versão anterior, que continua no GHCR.

### 7.4 Deploy automático na EC2

O job `deploy` do `release.yml` atualiza a EC2 a cada tag de versão final. Ele usa o **SSM** da AWS (não abre SSH) e entra na AWS por **OIDC** (nenhuma chave da AWS fica guardada no GitHub). Na EC2, ele roda:

```bash
cd /opt/sparcc && export SPARCC_TAG=<versão> && docker compose pull && docker compose up -d
```

e espera o resultado: se o comando falhar na EC2, o job fica vermelho.

O job só roda quando estas **variáveis** existem no repositório, em *Settings → Secrets and variables → Actions → Variables* (não são segredos: são identificadores):

| Variável | Valor | Obrigatória |
|---|---|---|
| `AWS_DEPLOY_ROLE` | ARN da IAM role que o GitHub assume (ex.: `arn:aws:iam::123456789012:role/sparcc-deploy`) | sim |
| `EC2_INSTANCE_ID` | id da instância (ex.: `i-0abc123...`) | sim |
| `AWS_REGION` | região da instância | não (padrão `us-east-1`) |
| `DEPLOY_PATH` | pasta do compose na EC2 | não (padrão `/opt/sparcc`) |

Sem `AWS_DEPLOY_ROLE` ou `EC2_INSTANCE_ID`, o job `deploy` é pulado e o release termina verde.

O que precisa existir do lado da AWS (feito por quem cuida da conta):

1. **Provedor OIDC do GitHub** no IAM (`token.actions.githubusercontent.com`, audiência `sts.amazonaws.com`).
2. **IAM role** com relação de confiança nesse provedor, limitada ao repositório e às tags (`repo:Morea-IFS/morea-ds-web:ref:refs/tags/v*`), e permissão `ssm:SendCommand` (documento `AWS-RunShellScript` e a instância) e `ssm:GetCommandInvocation`.
3. **EC2** com Docker + plugin Compose e o **SSM Agent** ativo, com um perfil de instância que tenha a política `AmazonSSMManagedInstanceCore`.
4. Em `/opt/sparcc` na EC2: o `docker-compose.yml` deste repositório com duas mudanças nos serviços `web` e `cron` (trocar `build: .` pela imagem) e as variáveis de produção (seção 7.2) no lugar das de desenvolvimento, mais o `docker/nginx.conf`:

   ```yaml
       image: ghcr.io/morea-ifs/morea-ds-web:${SPARCC_TAG:-latest}
   ```

5. Se o pacote do GHCR estiver privado: `docker login ghcr.io` na EC2 com um token de escopo `read:packages`.

Para voltar atrás: na EC2, `cd /opt/sparcc && export SPARCC_TAG=<versão anterior> && docker compose up -d`.

## 8. Estrutura do projeto

```
morea-ds-web/
├── app/                     # o aplicativo Django
│   ├── models.py            # usuários, dispositivos e seus logs, dados coletados e processados, gráficos, notícias
│   ├── views.py             # páginas, dashboards e API dos dispositivos
│   ├── urls.py              # rotas
│   ├── data_processing.py   # estatísticas por hora (job do cron)
│   ├── graphs.py            # gráficos de 24 h com plotly (job do cron)
│   ├── migrations/
│   ├── templates/
│   └── tests.py             # vazio por enquanto
├── morea_ds/                # configuração do projeto Django (settings, urls, wsgi)
├── static/                  # CSS, JS e imagens do site
├── media/defaults/          # imagens padrão (as geradas e enviadas ficam no volume)
├── scripts/
│   ├── start.sh             # migrate + collectstatic + gunicorn (ponto de entrada da imagem)
│   └── cron.sh              # jobs periódicos (contêiner cron)
├── docker/nginx.conf        # nginx do docker-compose
├── config/                  # arquivos do deploy antigo (nginx e systemd)
├── install.sh               # instalação antiga, sem Docker
├── .github/workflows/
│   ├── ci.yml               # testes e smoke test da imagem
│   ├── release.yml          # tag v* → imagem no GHCR + Release + deploy na EC2
│   └── django.yml           # CI antigo da equipe
├── Dockerfile
├── docker-compose.yml       # ambiente local: nginx + web + cron + MySQL
├── .env.example             # variáveis, para rodar sem Docker
└── requirements.txt
```
