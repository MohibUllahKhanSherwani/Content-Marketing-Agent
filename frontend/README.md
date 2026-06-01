# Frontend Dashboard

React + TypeScript + Vite dashboard for the Content Marketing Agent Team.

## Run Locally

### 1) Install dependencies

```bash
npm install
```

### 2) Start dev server

```bash
npm run dev
```

If backend is not on default URL, set:

```bash
# PowerShell
$env:VITE_API_BASE_URL="http://127.0.0.1:8000"
npm run dev
```

## Quality Checks

```bash
npm test
npm run lint
npm run build
```

## Routes

- `/review-queue`
- `/publication-audit`
- `/campaign-workspace`
- `/calendar`
- `/connectors`
- `/telemetry`

## E2E (Playwright)

Install browser binaries:

```bash
npx playwright install chromium
```

Run E2E suite:

```bash
npm run test:e2e
```

If browser download is slow, retry install later and keep running unit tests in the meantime.
