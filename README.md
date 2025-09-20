# UM Projects — University Portfolio

A consolidated hub for my University of Minho projects. Each entry below includes a brief overview and a direct link to the project’s README with full setup, features, and usage.

**Projects**
- UM-AED1 — Friendster (C)
  - Console social network with accounts, posts (public/restricted/private), friends, and anonymized browsing.
  - Tech: C99, Windows console; binary-file persistence (`users`, `posts`, `friendships`, `lastlog`).
  - Highlights: authentication, profile editing, friend system (limit 50), stats (top posters/friends), anonymous mode.
  - Read more: [UM-AED1](UM-AED1/README.md)

- UM-AED2 — SGAU (C)
  - Console patient and doctor management with per‑doctor waitlists and consistency checks.
  - Tech: C (Windows console), text-file persistence (`patients.txt`, `doctors.txt`).
  - Highlights: CRUD for patients/doctors, waitlist add/pop, largest waitlist, startup validation.
  - Read more: UM-AED2](UM-AED2/README.md)

- UM-DAI — BRT Braga App (Java/Swing + MySQL)
  - Desktop app for bus ticketing, routes, and schedules (BRT Braga).
  - Tech: Java 17 + Swing (NetBeans/Ant), MySQL, ZXing (QR Codes), Dijkstra for routing.
  - Highlights: buy single/custom tickets, generate QR, browse line schedules, shortest path with pricing by transfers.
  - Read more: [UM-DAI](UM-DAI/README.md)

- UM-FSD — Distributed Marketplace (Python)
  - Producers expose products; a marketplace discovers, lists, and buys across phases (sockets → REST → REST+RSA).
  - Tech: Python 3, TCP sockets, Flask, JSON persistence; RSA keys and signatures in phase 3.
  - Highlights: discovery/heartbeat, category browsing, purchases with resale tax, reconnection/cleanup, security with certs.
  - Read more: [UM-FSD](UM-FSD/README.md)

- UM-IAIE — Integrations App (React + Flask)
  - Storefront + REST API integrating SAP OData, Moloni (ERP), and Imgur for media.
  - Tech: React 18 (frontend), Flask (backend), TailwindCSS; multiple `/api/*` endpoints for CRUD and integrations.
  - Highlights: products, cart/payment, admin (stock/customers/invoices), signup/signin via Moloni, image uploads.
  - Read more: [UM-IAIE](UM-IAIE/README.md)

- UM-PO — University Manager (Java)
  - Console system for courses, curricular units, professors, students, and class summaries with role‑based flows.
  - Tech: Java 17 (console), Java serialization (`Repositorio.ser`, `Administrador.ser`).
  - Highlights: admin (professors/courses/UCs), regent/director flows, attendance counts, listings and stats.
  - Read more: [UM-PO](UM-PO/README.md)

- UM-PW — Urban Incident Platform (Vue 3)
  - Mono‑repo with front‑office, back‑office, and a mobile‑friendly PWA for municipal incident reporting and audits.
  - Tech: Vue 3, Firebase (Auth/Firestore), Google Maps JS API, Cloudinary, optional OpenAI for audit suggestions.
  - Highlights: roles (user/expert/manager/admin), incident workflow, audits planning/execution, dashboards and stats.
  - Read more: [UM-PW](UM-PW/README.md) · Sub‑apps: [Front Office](UM-PW/front-office/README.md) · [Back Office](UM-PW/back-office/README.md) · [PWA](UM-PW/pwa/README.md)

- UM-SO — Mini‑Shell & Monitor (C/Linux)
  - Single‑operator shell (pipe or redirection) and a lightweight “top” reading procfs.
  - Tech: C (gnu11), Linux/POSIX (`fork`, `exec`, `pipe`, `dup2`, `alarm`), `/proc` parsing.
  - Highlights: run commands with `|`, `<`, `>`, refreshable process view with load averages and per‑PID details.
  - Read more: [UM-SO](UM-SO/README.md)

**Notes**
- Most projects are Windows‑friendly; `UM-SO` targets Linux (procfs/POSIX).
- Binaries are not committed; build/run instructions live in each project’s README.

**License**
- MIT License. See [License](LICENSE)
