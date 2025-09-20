# UM-SO — Console Mini‑Shell and System Monitor in C

University project (Operating Systems — University of Minho). This console application, written in C, parses and executes simple shell commands with a single operator (redirection or pipe) and includes a lightweight “top”‑like monitor that reads from procfs to display system and process information.

Note: This repository does not include prebuilt binaries. Build locally to try the executable.

## Features
- Command execution with a single operator:
  - Output redirection: `>` to a file.
  - Input redirection: `<` from a file.
  - Pipe: `|` from one process to another.
- Process monitor (“top” mode):
  - Refreshes every 10 seconds; press `q` to exit.
  - CPU load averages (1, 5, 15 minutes).
  - Total processes and processes in Running state.
  - Table with PID, state (Running/Sleeping/Idle), username, and command line.

## Architecture & Data
- Language: C (targets POSIX; tested with GCC, gnu99/gnu11).
- Interface: Linux terminal.
- Data sources (procfs and system files):
  - `/proc/loadavg` — CPU load averages and process counters.
  - `/proc/<pid>/status` — process state and UID.
  - `/proc/<pid>/cmdline` — command line for each process.
  - `/etc/passwd` — map UID to username.
- Main structures (see `ProjetoSOParse.c`):
  - `typedef struct comands` — parsed command/operator and argv arrays for cmd1/cmd2.
  - `typedef struct Info_Processo` — PID, state letter, username, and command line.

## Requirements
- Linux with procfs (`/proc`) available.
- GCC (MinGW/MSVC are not supported; this project uses POSIX APIs like `fork`, `exec`, `pipe`, `dup2`, `alarm`).
- A terminal that supports `clear`.

## Build
- GCC (recommended):
  ```bash
  gcc -std=gnu11 -O2 -Wall -Wextra ProjetoSOParse.c -o so-monitor
  ```
  Alternatively, use `-std=gnu99` if preferred.

## Run
After building, from the project directory:
- Process monitor (refresh every 10s, quit with `q`):
  - `./so-monitor top`
- Command execution examples (single operator supported):
  - No operator: `./so-monitor ls -l`
  - Output redirection: `./so-monitor ls -l > out.txt`
  - Input redirection: `./so-monitor wc -l < out.txt`
  - Pipe: `./so-monitor ls -l | wc -l`

## Usage Details
- Only one operator among `>`, `<`, `|` is allowed at a time.
- The parser builds `argv` arrays for the first and optional second command.
- The executor uses `fork()`, `exec*()`, `pipe()`, `dup2()`, and `waitpid()` to realize the requested operation.
- “top” mode sets an `alarm()` to refresh and listens for `q` from stdin to exit.

## Repo Structure
- `ProjetoSOParse.c` — main source code.
- `Rel_final_SO2324_G15.pdf` — project report (Portuguese).

## Limitations & Notes
- Linux‑only: relies on `/proc` and POSIX system calls.
- Single operator: the program enforces at most one operator per invocation.
- Argument handling: the current `exec` calls only pass the program and one extra argument per command; multi‑argument commands may need adaptation.
- Process listing: shows up to 20 Running and 20 other processes per refresh.
- UI: uses `system("clear")`; messages and identifiers include Portuguese terms.

## Author & License
- Author: Tomás Gonçalves
- Course/Unit: University of Minho — Sistemas Operativos (SO)
- License: MIT — see `LICENSE` for details.

