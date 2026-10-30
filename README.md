# spark (morea-ds-web)

Sistema do MOREA para monitorar o consumo de água, energia e gás: os dispositivos enviam os dados por API, o sistema processa estatísticas e mostra dashboards e gráficos.

- Django 5.0, Python 3.11.5
- MySQL 8, nginx para os arquivos estáticos e a mídia
- Roda em Docker. A cada Release publicada no GitHub, o GitHub publica a imagem em `ghcr.io/morea-ifs/morea-ds-web`.

## 1. Situação atual

- CI roda a cada push na `develop` e na `main` e em todo pull request.
- O deploy ainda não é automático: quem cuida do servidor puxa a imagem (seção 7) ou liga o deploy automático (seção 7.4).

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

As variáveis de desenvolvimento (senhas `spark`/`spark`, `ENVIRONMENT=PROD` etc.) estão no próprio `docker-compose.yml`. Servem só para a sua máquina. O `.env.example` é o modelo para quem rodar sem Docker.

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

Para acessar o banco de fora (DBeaver, MySQL Workbench): host `127.0.0.1`, porta `3307`, banco `spark`, usuário `spark`, senha `spark`.

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

Fluxo de branches: trabalho em `feature/*` → PR para `develop` → PR para `main` → Release a partir da `main`. Push e merge **nunca** publicam nada; só a Release publica.

A Release continua sendo criada como a equipe já faz, pela página https://github.com/Morea-IFS/morea-ds-web/releases (*Draft a new release*, tag nova a partir da `main`) ou pelo terminal:

```bash
gh release create v1.3.0 --target main --generate-notes   # este comando dispara o release
```

O `.github/workflows/release.yml` então:

1. roda os mesmos testes do CI no commit da Release;
2. monta a imagem e publica `ghcr.io/morea-ifs/morea-ds-web:1.3.0` e `ghcr.io/morea-ifs/morea-ds-web:latest`.

Regras:

- Numeração (SemVer), continuando as Releases existentes (a última é `v1.2.1`): `v1.2.2` correção, `v1.3.0` funcionalidade nova, `v2.0.0` mudança que quebra compatibilidade.
- Release marcada como **pre-release** **não** recebe `latest`. Use para testar antes da versão final.
- Uma tag não se reaproveita. Se o release falhar, corrija e crie a próxima (`v1.3.1`).
- Acompanhe em https://github.com/Morea-IFS/morea-ds-web/actions (workflow "Release").
- Nenhum secret precisa ser cadastrado: o workflow usa o `GITHUB_TOKEN` automático.

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
docker network create spark
docker run -d --name spark-web --network spark \
  -e SECRET_KEY=... -e ENVIRONMENT=PROD \
  -e DBTYPE=MySQL -e DBNAME=spark -e DBUSER=... -e DBPASSWORD=... -e DBHOST=... -e DBPORT=3306 \
  -v spark-static:/var/www/html/Morea/static -v spark-media:/var/www/html/Morea/media \
  ghcr.io/morea-ifs/morea-ds-web:1.3.0
docker run -d --name spark-cron --network spark \
  -e SECRET_KEY=... -e ENVIRONMENT=PROD \
  -e DBTYPE=MySQL -e DBNAME=spark -e DBUSER=... -e DBPASSWORD=... -e DBHOST=... -e DBPORT=3306 \
  -v spark-media:/var/www/html/Morea/media \
  ghcr.io/morea-ifs/morea-ds-web:1.3.0 sh scripts/cron.sh
# nginx com o docker/nginx.conf (o proxy_pass aponta para http://web:8000; ajuste para spark-web)
```

Para atualizar: troque a versão da imagem e reinicie. Para voltar atrás: aponte para a versão anterior, que continua no GHCR.

### 7.4 Deploy automático na AWS (opcional)

Hoje o `release.yml` termina ao publicar a imagem. Para o servidor atualizar sozinho a cada Release, acrescente um passo no fim do job `publish`. Exemplo para EC2 com o SSM (sem abrir SSH):

```yaml
      - name: Credenciais da AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE }}   # IAM role com permissão de ssm:SendCommand
          aws-region: us-east-1
      - name: Deploy na EC2
        run: >
          aws ssm send-command --document-name AWS-RunShellScript
          --targets Key=tag:Name,Values=spark
          --parameters 'commands=["cd /opt/spark && docker compose pull && docker compose up -d"]'
```

O que isso exige do lado da AWS: uma instância EC2 com Docker, o SSM Agent e o compose em `/opt/spark` apontando para `ghcr.io/morea-ifs/morea-ds-web:latest`, uma IAM role que o GitHub possa assumir (OIDC; o workflow também precisa de `id-token: write` em `permissions`) e o segredo `AWS_DEPLOY_ROLE` cadastrado em *Settings → Secrets* do repositório. Para ECS ou EKS a ideia é a mesma: um passo final que manda o serviço puxar a imagem nova.

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
│   ├── release.yml          # Release publicada → imagem no GHCR
│   └── django.yml           # CI antigo da equipe
├── Dockerfile
├── docker-compose.yml       # ambiente local: nginx + web + cron + MySQL
├── .env.example             # variáveis, para rodar sem Docker
└── requirements.txt
```
