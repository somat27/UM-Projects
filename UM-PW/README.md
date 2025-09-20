# Urban Incident Management (PW) — Front/Back Office + PWA in Vue
University project (Web Programming). A mono‑repo with three Vue 3 applications that simulate a municipal incident platform: citizens report issues, managers triage and plan audits, and field experts operate via a mobile‑friendly PWA. Data is persisted in Firebase (Auth/Firestore) and media is uploaded to Cloudinary.

Note: This repository does not include built artifacts nor production secrets. Build locally and create .env files for API keys.

## Features
- Account authentication and roles (usuario, perito, gestor, admin) via Firebase Auth.
- Incident reporting with address/coordinates, description, and media upload (Cloudinary).
- Live map with filters by status and type (Google Maps JavaScript API).
- Workflow: Pending → Analysis → Resolved/Rejected; approval flow in Back Office.
- Audits: suggest (optional AI), plan, run, and finalize audits tied to incidents.
- Resource management: experts (“peritos”), materials, and professionals.
- Dashboards and statistics (ApexCharts) for incidents, audits, resources, and map view.
- Citizen feedback collection and aggregation.

## Architecture & data
- Language: JavaScript (Vue 3, Vue Router, Bootstrap 5).
- Interface: SPA (Front/Back Office) and mobile‑friendly PWA.
- Maps: Google Maps JavaScript API.
- Persistence: Firebase Firestore (incidents, audits, users, resources, feedback).
- Auth: Firebase Authentication (email/password and Google provider).
- Media: Cloudinary unsigned uploads.
- Optional AI: OpenAI API for audit suggestions in Back Office.
- Main apps:
  - front-office — public portal for incident reporting and tracking.
  - back-office — administration console with dashboards and approvals.
  - pwa — simplified mobile interface for field experts.

## Requirements
- Node.js 18+ and npm.
- Google Maps API key with Maps JavaScript API enabled.
- Firebase project (Auth + Firestore).
- Optional: OpenAI API key (enables AI suggestions in Back Office).

## Run
After setting environment variables (see below), run each app independently from its folder:

PowerShell/CMD:
```
cd front-office
echo VUE_APP_API_KEY=your_google_maps_key > .env.local
npm install
npm run serve

cd ../back-office
echo VUE_APP_API_KEY=your_google_maps_key > .env.local
echo VUE_APP_OPENAI_API_KEY=your_openai_key >> .env.local  # optional
npm install
npm run serve

cd ../pwa
npm install
npm run serve
```
On first run, the apps will read/write data in your Firebase project; no local database files are created.

## Build
Create production bundles into each app’s `dist/` folder:
```
npm run build
```
Run the command inside each app directory (`front-office`, `back-office`, `pwa`).

## Environment variables
Create a `.env.local` file in each app as needed.
- Front Office: `VUE_APP_API_KEY` — Google Maps API key.
- Back Office: `VUE_APP_API_KEY`, `VUE_APP_OPENAI_API_KEY` (optional).
- PWA: none by default.

## Firebase configuration
Replace the demo Firebase configuration with your own credentials in:
- `front-office/src/services/firebase.js:1`
- `back-office/src/firebase.js:1`
- `pwa/src/firebase/firebase.js:1`
Move secrets to environment variables for production and avoid committing keys.

## Cloudinary uploads
If you use your own Cloudinary account, update:
- `front-office/src/services/cloudinary.js:1`
- `pwa/src/firebase/firebase.js:64`

## Usage (flows)
- Front Office: report incident → attach media → submit; browse incidents and map; send feedback.
- Back Office: log in → review and approve incidents → create/track audits → manage experts/materials/professionals → view dashboards.
- PWA: log in → access a simplified interface aligned with field operations.

## Repo structure
- `front-office/` — public SPA for citizens (Vue 3).
- `back-office/` — admin SPA with dashboards and approvals (Vue 3).
- `pwa/` — mobile‑friendly SPA for field experts (Vue 3).
- `README.md` — this file.

## Limitations & notes
- Secrets: do not commit real API keys. Use `.env.local` or CI/CD secrets.
- Keys: restrict your Google Maps key to allowed referrers.
- PWA: mobile‑first SPA; offline support is not configured by default.
- Security: example/demo keys in code should be replaced before production.

## Authors & license
- Authors: see repository contributors.
- License: MIT — see `LICENSE` for details.
