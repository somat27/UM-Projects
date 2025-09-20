# UM-FSD — Distributed Marketplace in Python

University project (Fundamentos de Sistemas Distribuídos — University of Minho). This repository contains a console-based distributed marketplace implemented in Python, developed across three phases (Fase1, Fase2, Fase3). It models Producers exposing products and a Marketplace that discovers producers, browses categories, and purchases items, persisting state in JSON files per phase.

Note: This repository does not include prebuilt binaries. Run with Python from source. Data files (`BasedeDados/Produtores.json`, `BasedeDados/Produtos.json`) are created/updated at runtime inside each phase folder.

## Features
- Producers
  - Register a producer with auto-assigned ID and socket port (local loopback by default).
  - Generate random products with category, price range, and quantity; periodic stock replenishment.
  - Expose product listings and purchase handling via TCP sockets (Fase1) and Flask REST endpoints (Fase2/Fase3).
  - Heartbeat support for connection health checks; graceful client handling in threads.
- Marketplace
  - Discover active producers; browse by category and list available products with quantities and prices.
  - Buy products, maintain a subscription/purchases list, and define a resale tax per product (default configurable).
  - Connection monitoring with automatic reconnection and cleanup on producer unavailability.
  - Hybrid discovery: direct socket probing (Fase1) and REST manager discovery (Fase2/Fase3).
- Security (Fase3)
  - RSA key generation for producers and certificate handling on the marketplace.
  - Digital signatures and verification for trusted communications with the manager/marketplace flows.
- Persistence
  - JSON data per phase in `BasedeDados/` (`Produtores.json`, `Produtos.json`).

## Architecture & Data
- Language: Python 3 (tested with 3.10+)
- Interface: Console (Windows/Linux/macOS terminals)
- Networking:
  - Fase1: TCP sockets between Marketplace and Producers, with heartbeat probes.
  - Fase2: Adds REST (Flask) endpoints on Producers and discovery via a remote Manager (`http://193.136.11.170:5001`).
  - Fase3: REST + cryptography (RSA, certificate verification) for producer registration/notifications.
- Persistence: JSON files in each phase directory under `BasedeDados/`:
  - `Produtores.json` — registered producers and their inventory.
  - `Produtos.json` — product catalog (names, categories, price/quantity ranges) used to generate inventory.
- Key/cert files (Fase3):
  - `certificado.pem`, `chave_publica.pem`, `chave_privada.pem`, `manager_public_key.pem` — used for signing/verification flows.

## Requirements
- OS: Windows 10/11, Linux, or macOS with a terminal.
- Python: 3.10 or newer.
- Dependencies (install per phase needs):
  - Common: `requests`, `psutil`
  - Producer REST (Fase2/Fase3): `flask`
  - Security (Fase3): `cryptography`

Install dependencies:

```bash
pip install -r requirements.txt  # if you add one
# or install directly
pip install requests psutil flask cryptography
```

## Run
- Fase1 (local sockets)
  - Terminal 1 (Producer): `python Fase1/Produtor.py`
  - Terminal 2 (Marketplace): `python Fase1/MarketPlace.py`
- Fase2 (REST + Manager discovery)
  - Terminal 1 (Producer REST server): `python Fase2/ProdutorRest.py`
  - Terminal 2 (Marketplace REST client): `python Fase2/marketplace.py`
- Fase3 (REST + crypto)
  - Terminal 1 (Producer with RSA/Flask): `python Fase3/Produtor.py`
  - Terminal 2 (Marketplace with cert verification): `python Fase3/Marketplace.py`

Notes:
- On first run, each phase will create/update `BasedeDados/Produtores.json` and `BasedeDados/Produtos.json` as needed.
- For Fase2/Fase3, some functionality depends on the external Manager endpoint (`193.136.11.170:5001`). Ensure network access.

## Usage (Flows)
- Producer (Fase1/Fase3):
  - Menu to create a new producer or log in as an existing one (by name/ID).
  - Generates an inventory from the product catalog; periodically replenishes stock.
  - Exposes endpoints to list products and execute purchases.
- Marketplace:
  - Lists available categories and products per producer; filters out-of-stock items.
  - Purchases selected items and tracks them in a subscriptions/purchases list.
  - Defines a resale tax per purchased product (default applied on buy, editable later).
  - Monitors producer connectivity; removes products from disconnected producers.

## Repo Structure
- `Fase1/`
  - `MarketPlace.py` — marketplace (sockets)
  - `Produtor.py` — producer (sockets)
  - `BasedeDados/` — `Produtores.json`, `Produtos.json`
- `Fase2/`
  - `marketplace.py` — marketplace (REST client)
  - `ProdutorRest.py` — producer (Flask REST)
  - `ProdutorSocket.py` — auxiliary socket producer
  - `BasedeDados/` — JSON data files
- `Fase3/`
  - `Marketplace.py` — marketplace (REST + signatures/certificates)
  - `Produtor.py` — producer (REST + RSA key generation)
  - `BasedeDados/` — JSON data files
  - `certificado.pem`, `chave_publica.pem`, `chave_privada.pem`, `manager_public_key.pem`
- `.vscode/` — editor settings (if any)

## Limitations & Notes
- Local defaults: Producers bind to localhost; adapt IP/ports if running across machines.
- External dependency: Fase2/Fase3 discovery and some flows require the Manager service at `193.136.11.170:5001`.
- Data integrity: JSON files are updated concurrently; locks are used but abrupt termination may leave partial writes.
- Security scope: Fase3 implements RSA keys and signature verification for learning purposes; not hardened for production use.
- Encoding: Console messages are in Portuguese; terminals must support UTF‑8 for proper accents.

## Author & License
- Author: Tomás Gonçalves
- Course/Unit: Universidade do Minho — Fundamentos de Sistemas Distribuídos (FSD)
- License: MIT — see `LICENSE` for details.

