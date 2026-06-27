# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Clona o repositório limpo diretamente de dentro do container
# tem de considerar o cache do system
RUN git clone --depth=1 --branch developer \
    https://github.com/FGA0138-MDS-Ajax/2026.1-T01-Dijkstra \
    /app

WORKDIR /app

RUN python -m venv /app/.venv \
    && /app/.venv/bin/pip install --upgrade pip \
    && /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# ── Runtime stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app /app

RUN mkdir -p /app/media /app/staticfiles


# Injecao para producao e resultado particular
# Adiciona as configurações direto no final do settings.py com redirecionamento correto (>>)
RUN echo "" >> /app/config/settings.py && \
    echo "DEBUG = False" >> /app/config/settings.py && \
    echo "STATIC_ROOT = BASE_DIR / 'staticfiles'" >> /app/config/settings.py && \
    echo "ALLOWED_HOSTS = ['sigesporte.duat.site', 'duat.site', 'localhost', '127.0.0.1']" >> /app/config/settings.py && \
    echo "SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')" >> /app/config/settings.py && \
    echo "CSRF_TRUSTED_ORIGINS = ['https://sigesporte.duat.site', 'https://*.duat.site']" >> /app/config/settings.py

#removido para compatibilidade 

# porta
EXPOSE 8000

# sem mudanças para unicornio ainda.
CMD ["sh", "-c", \
    "python manage.py migrate --noinput && \
     python manage.py collectstatic --noinput && \
     python manage.py runserver 0.0.0.0:8000"]