# UM-IAIE — React + Flask Integrations App

University project (IAIE — University of Minho). This repository contains a React storefront (frontend) and a Flask API (backend) that integrates with external services: SAP OData, Moloni (ERP), and Imgur for image uploads.

Note: This repository does not include any secrets nor external data. To run integrations, configure API credentials in `backend/app/config.py` (development) or via environment variables in production.

## Features
- Storefront (React): product listing, details, cart and payment flow.
- Account: signup/signin backed by Moloni customers (VAT + name).
- Admin pages: stock, customers and invoices management; buy products.
- Integrations:
  - SAP OData: list and create products (CSRF token flow handled).
  - Moloni: access token, products, customers, invoices endpoints.
  - Imgur: image upload and public link retrieval.

## Architecture & Data
- Language: JavaScript (React 18) + Python 3 (Flask)
- Interface: Web UI (localhost:3000) + REST API (localhost:5000)
- Backend: Flask app factory with blueprints under `/api/*`:
  - `GET /api/sap/products` — list SAP products
  - `POST /api/sap/products` — create SAP product
  - `POST /api/moloni/signup` — create customer (signup)
  - `POST /api/moloni/signin` — validate customer (signin)
  - `POST /api/moloni/products` — list products
  - `POST /api/moloni/invoices` — list invoices
  - `POST /api/moloni/customers` — list customers
  - `POST /api/imgur/upload` — upload image (multipart/form-data)
- Frontend: React app with TailwindCSS; pages for Shop, Product Details, Cart, Payment, Admin, Account.

## Requirements
- Windows 10/11 with PowerShell/CMD (recommended; `start.bat` provided)
- Node.js 16+ and npm
- Python 3.11+ with `venv`
- Network access to external services (SAP, Moloni, Imgur)

## Run
After configuring credentials (see Configuration), from the project root:
- Windows (recommended): double‑click `start.bat`
  - Creates/activates `venv`, installs Python deps, installs npm deps, starts React and Flask together.
  - Frontend: http://localhost:3000
  - Backend API: http://127.0.0.1:5000

Manual run (any OS):
- Backend
  - Create venv: `python -m venv venv`
  - Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
  - Install deps: `pip install -r backend/requirements.txt`
  - Start API: `python backend/run.py`
- Frontend
  - `cd frontend`
  - Install deps: `npm install`
  - Start: `npm start`

## Build
- Frontend production build:
  - `cd frontend && npm run build`
  - Output in `frontend/build`
- Backend is Python (no build step); run via `python backend/run.py`.

## Configuration
Development defaults live in `backend/app/config.py`.
- For local testing, you may edit that file.
- For production, prefer environment variables and never commit secrets.

Required values (per service):
- SAP: API URL, client, username, password
- Moloni: API URL, client ID/secret, username, password
- Imgur: client ID

## Usage (flows)
- Public pages: Shop, Product Details, Cart, Payment
- Account: Sign Up/Sign In via Moloni customers (uses VAT + name)
- Admin: Stock, Customer and Invoice management; Buy products
- Media: Upload images to Imgur from the Admin flows

## Repo Structure
- `start.bat` — bootstrap script (venv, deps, start dev servers)
- `backend/run.py` — Flask entry point
- `backend/app/__init__.py` — Flask app factory and blueprints
- `backend/app/config.py` — integration settings (replace with env vars in prod)
- `backend/app/routes/` — API blueprints: `sap.py`, `moloni.py`, `imgur.py`
- `backend/requirements.txt` — backend dependencies
- `frontend/` — React app (TailwindCSS, Redux); `package.json` scripts

## Limitations & Notes
- Secrets: `backend/app/config.py` currently stores credentials in plain text for development. Move these to environment variables before any public use.
- CORS: API allows `http://localhost:3000` on `"/api/*"` paths.
- External services: valid SAP, Moloni and Imgur accounts are required.
- Windows‑first tooling: `start.bat` is Windows‑specific; manual commands work cross‑platform.

## Author & License
- Course/Unit: University of Minho — IAIE
- License: MIT — see `LICENSE` for details.

