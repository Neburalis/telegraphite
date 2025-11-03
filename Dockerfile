FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml setup.cfg README.md uv.lock /app/
COPY telegraphite /app/telegraphite
COPY scripts /app/scripts
COPY contact_patterns.txt channels.txt example_config.yaml /app/

RUN uv pip install --system --no-cache .

VOLUME ["/app/data"]

ENTRYPOINT ["telegraphite"]
CMD ["once"]

