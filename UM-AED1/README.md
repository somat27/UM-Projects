# Friendster (AED1) — Console Social Network in C

University project (Algorithms and Data Structures I — University of Minho). Friendster is a console application, written in C, that simulates a simple social network and persists data to binary files in the working directory.

Note: This repository does not include prebuilt binaries nor the data files (`users`, `posts`, `friendships`, `lastlog`). Build locally to try the executable.

## Features
- Account registration: first/last name, email, birth date, phone, username and masked password input.
- Authentication (login) and session flow.
- Posts feed with three visibility levels:
  - Public (1), Restricted (2), Private (3).
- Profile: view/edit data and description; toggle account visibility (public/private).
- Friend system: add/remove, list friends (limit of 50 friends per user).
- Posts: create, edit and delete; list by visibility and by author.
- Account search by first name.
- Global stats: last logged‑in account, user with most posts, user with most friends, total users and total posts.
- Anonymous mode: view only public posts without authentication.

## Architecture & data
- Language: C (targeting C99/gnu99 for compatibility)
- Interface: Windows console
- Persistence: binary files created in the working directory when needed:
  - `users` — users (records of `struct User`).
  - `posts` — posts (records of `struct Post`).
  - `friendships` — friendships (records of `struct Friendship`).
  - `lastlog` — last logged‑in user.
  - Temporary files: `aux`, `auxfile` (used on edit/delete flows).
- Main structures (see `Friendster.c`):
  - `struct User`: account metadata (id, name, email, phone, username, password, birth date, description, visibility).
  - `struct Post`: post id, type, author, text, datetime, and author names at posting time.
  - `struct Friendship`: friendship relation (source/followed) plus names.

## Requirements
- Windows 10/11 with a terminal (CMD/PowerShell).
- To run: build from source (no binaries are included).
- To build on Windows:
  - MinGW‑w64 (GCC) or MSYS2, or Microsoft Visual C (MSVC).
  - The program uses `getch()` and console I/O; Windows is the supported environment.

## Run
After building, from the project directory:
- PowerShell/CMD: `./Friendster.exe`
- On first run, the app will create the data files if absent.

## Build
- MinGW‑w64 (recommended on Windows):
  - With MSYS2, install GCC: `pacman -S mingw-w64-x86_64-gcc`
  - Compile:
    ```bash
    gcc -std=gnu99 -O2 -Wall -Wextra Friendster.c -o Friendster.exe
    ```
- Microsoft Visual C (MSVC):
  - In “Developer Command Prompt for VS”:
    ```bat
    cl /O2 /W4 Friendster.c /Fe:Friendster.exe
    ```
  - Note: this project targets Windows console APIs and `conio.h`; POSIX headers like `<unistd.h>` may be ignored by MSVC.

## Usage (flows)
- Start screen:
  - 1) Log In — username + password.
  - 2) Create Account — guided registration.
  - 3) Anonymous Mode — view public posts only.
  - 4) Statistics — global indicators.
  - 5) Exit.
- After login:
  - Feed: view/create posts (by chosen visibility), search accounts.
  - Profile: view posts, edit account and description, list friends, open post menu (create/edit/delete).
  - Friends: add/remove; visibility respects friendship and account visibility.

## Repo structure
- `Friendster.c` — main source code.
- Data files are generated at runtime: `users`, `posts`, `friendships`, `lastlog` (not included in repo).

## Limitations & notes
- Platform: designed for Windows console; POSIX systems need adaptations (`getch()`, screen clear, includes).
- Encoding: all UI text is now in English; no special locale is required.
- Security: passwords are stored in plaintext in `users` (academic project scope).
- Limits: up to 200 accounts and 50 friends per user.
- Integrity: edit/delete operations use temporary files; abrupt termination may leave `aux`/`auxfile` artifacts.

## Author & license
- Author: Tomás Gonçalves
- Course/Unit: University of Minho - AED I
- License: MIT — see `LICENSE` for details.
