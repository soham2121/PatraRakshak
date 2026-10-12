# PatraRakshak web UI

React + TypeScript + Vite. The production build (`npm run build`, output in `dist/`) is served by FastAPI at `/`.

For development, run the API and the Vite dev server side by side:

```bash
uvicorn patrarakshak.api:app   # from the repo root, port 8000
cd web && npm run dev          # proxies /api to port 8000 (see vite.config.ts)
```
