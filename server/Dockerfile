FROM python:3.12-alpine AS base

WORKDIR /app

RUN apk update && apk add --no-cache \
    build-base \
    curl \
    upx \
    && curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --without dev --no-interaction --no-ansi

RUN poetry add pyinstaller

COPY . /app/

FROM base AS linux-builder
RUN poetry run pyinstaller --onefile --name myapp-linux src/main.py

# For Windows builds, we need to use a Debian-based image with Wine
FROM python:3.12-slim AS windows-builder
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wine \
    wine64 \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --without dev --no-interaction --no-ansi

RUN poetry add pyinstaller

COPY . /app/

RUN poetry run pyinstaller --onefile --name myapp-windows.exe src/main.py

FROM base AS macos-builder
RUN poetry run pyinstaller --onefile --name myapp-macos src/main.py

FROM python:3.12-alpine
WORKDIR /dist

COPY --from=linux-builder /app/dist/myapp-linux /dist/
COPY --from=windows-builder /app/dist/myapp-windows.exe /dist/
COPY --from=macos-builder /app/dist/myapp-macos /dist/

VOLUME /dist

CMD ["ls", "-la", "/dist"]