# LoanDefault MLBC - Frontend

React + Vite + TypeScript + Tailwind CSS frontend for the LoanDefault MLBC
academic project.

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # points at the backend API, defaults to http://127.0.0.1:8000/api
```

## Run (development)

```bash
npm run dev
```

Opens at http://localhost:5173. Requires the backend API running (see
`backend/README.md`).

## Build (production)

```bash
npm run build
```

Type-checks with `tsc -b` and produces an optimized bundle in `dist/`.
Verified to build cleanly with zero TypeScript errors.

## Pages

- `/` - Dashboard (portfolio stats, risk distribution, recent activity)
- `/predict` - Loan Risk Prediction form
- `/applications` - Application management (search, filter, sort, actions)
- `/applications/:id` - Application details, ML assessment, blockchain info, audit timeline
- `/analytics` - Portfolio-wide analytics and charts
- `/model` - ML model metrics, comparison, and feature importance
- `/blockchain` - Blockchain network status and transaction history
- `/verify` - Look up and verify any application's blockchain record
- `/settings` - System status and configuration (no secrets displayed)

## Structure

```
src/
  api/          Axios-based API client modules, one per backend resource
  components/   layout / common / forms / tables / charts / risk / blockchain / audit
  pages/        One component per route
  hooks/        Reusable data-fetching hooks
  types/        Shared TypeScript interfaces
  utils/        Formatters, constants, validators
```

Every page calls the real backend API -- there is no hardcoded or mocked
data in the frontend.
