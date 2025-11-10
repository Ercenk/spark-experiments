# spark-experiments Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-08

## Active Technologies
- TypeScript 5.x (frontend), existing backend Python 3.11 (unchanged for this feature) + React 18, Vite 5, @fluentui/react-components, Axios (HTTP), Zod (runtime validation of API responses) (002-spa-control)
- N/A (ephemeral in-memory state only) (002-spa-control)
- TypeScript 5.x (frontend), React 18.x + `@fluentui/react-components` (base primitives), internal service modules (`services/health.ts`, `services/logs.ts`), Vite build tooling (001-spa-styling)
- N/A (theme preference persisted in localStorage) (001-spa-styling)
- Python 3.11 (existing generator codebase) + Pydantic (config validation), asyncio/threading (scheduling), existing generator modules (006-emulated-generation)
- JSON Lines files (existing bronze layer format) (006-emulated-generation)
- TypeScript 5.x (frontend), Node.js 20+ (build tooling) + React 18, Vite 5, @fluentui/react-components, Axios (HTTP), Zod (schema validation) (007-ui-emulated-display)
- localStorage (theme preference only), no database (007-ui-emulated-display)

- Python 3.11 (generators), Spark 3.5.0 (Bitnami image) + PySpark, delta-spark, pydantic (for config validation), pytest (testing) (001-driving-batch-generators)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.11 (generators), Spark 3.5.0 (Bitnami image): Follow standard conventions

## Recent Changes
- 007-ui-emulated-display: Added TypeScript 5.x (frontend), Node.js 20+ (build tooling) + React 18, Vite 5, @fluentui/react-components, Axios (HTTP), Zod (schema validation)
- 006-emulated-generation: Added Python 3.11 (existing generator codebase) + Pydantic (config validation), asyncio/threading (scheduling), existing generator modules
- 001-spa-styling: Added TypeScript 5.x (frontend), React 18.x + `@fluentui/react-components` (base primitives), internal service modules (`services/health.ts`, `services/logs.ts`), Vite build tooling


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
