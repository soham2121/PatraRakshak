FROM node:20-slim AS web
WORKDIR /web
COPY web/package*.json ./
RUN npm ci
COPY web/ .
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY pyproject.toml .
COPY patrarakshak/ patrarakshak/
RUN pip install --no-cache-dir ".[transformer]"
COPY --from=web /web/dist web/dist
RUN useradd --create-home app
USER app
ENV PR_MODEL_DIR=/models/muril-ens
EXPOSE 8000
CMD ["uvicorn", "patrarakshak.api:app", "--host", "0.0.0.0", "--port", "8000"]
