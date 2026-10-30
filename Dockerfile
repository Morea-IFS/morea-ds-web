# Etapa 1: instala as dependências Python num venv
FROM python:3.11.5-slim-bookworm AS build

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt


# Etapa 2: imagem final, só com o venv pronto e o código
FROM python:3.11.5-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN useradd --create-home --uid 1000 app

# Caminhos que o settings.py usa com ENVIRONMENT=PROD (viram volumes no compose)
RUN mkdir -p /var/www/html/Morea/static /var/www/html/Morea/media \
    && chown -R app:app /var/www/html/Morea

WORKDIR /app
RUN chown app:app /app

COPY --from=build /opt/venv /opt/venv
COPY --chown=app:app . .

USER app

EXPOSE 8000

CMD ["sh", "scripts/start.sh"]
