# UM-PO — Console University Management in Java

University project (Object-Oriented Programming — University of Minho). This is a console application, written in Java, that manages a simple university domain (courses, curricular units, professors, students and class summaries) and persists data to serialized files in the working directory.

Note: This repository does not include the data files (`Repositorio.ser`, `Administrador.ser`). Build and run locally to generate them.

## Features
- Authentication and roles:
  - Administrator: username + password (persisted locally).
  - Professor: login via mechanographic number; role-aware menus.
  - Role-sensitive flows for Professor, UC Regent (Regente) and Course Director.
- Administrator capabilities:
  - Manage Professors: add, remove, edit basic information.
  - Manage Courses: create with Director, remove, rename, list.
  - Manage Curricular Units (UCs): create with Regent, assign/remove teaching staff.
  - Global listings: courses, UCs, students and professors.
- Professor/Regent/Director capabilities:
  - Professor: view associated UC(s), manage and consult class summaries (teórica/prática/laboratorial), check attendance counts.
  - UC Regent: manage UC team (add professors), enroll/remove students, view presences.
  - Course Director: rename course and view course statistics (students, professors, UCs).
- Persistence: automatic creation and update of `.ser` files in the working directory.

## Architecture & Data
- Language: Java (targeting Java 17)
- Interface: console (text UI)
- Persistence: Java serialization files created next to the executable:
  - `Repositorio.ser` — serialized instance of the `Universidade` aggregate.
  - `Administrador.ser` — serialized administrator credentials.
- Main structures (see `src/main/java/BackEnd`):
  - `Universidade` — root aggregate holding courses and professors.
  - `Curso` — course with director, UCs and enrolled students.
  - `UnidadeCurricular` — curricular unit with Regent, teaching team and summaries.
  - `Professor`, `Aluno`, `Administrador` — actors/entities of the domain.
  - `SumarioAula` — class summary with type and attendance list.
  - `Ficheiro` — serialization gateway for loading/saving data.

## Requirements
- Java 17+ (JDK)
- A terminal (Windows, macOS, or Linux)
- Optional: Maven 3.8+ to build/package

## Run
After building, from the project directory:
- With Maven JAR on the classpath:
  - `mvn -q -DskipTests package`
  - `java -cp target/ProjetoPO-1.0-SNAPSHOT.jar FrontEnd.ProjetoPO`
- First run will create `Repositorio.ser` and `Administrador.ser` if absent.
  - Default administrator credentials are created if missing: username `admin`, password `root`.

## Build
- Maven (recommended):
  - Package: `mvn -DskipTests package`
  - Run main: `java -cp target/ProjetoPO-1.0-SNAPSHOT.jar FrontEnd.ProjetoPO`
- Manual javac (alternative):
  - Compile: `javac -d target/classes src/main/java/**/*.java`
  - Run: `java -cp target/classes FrontEnd.ProjetoPO`

## Usage (flows)
- Start / Login:
  - Administrator — username and password (stored in `Administrador.ser`).
  - Professor — mechanographic number; menus adapt to roles held.
- Administrator menu:
  - Manage Professors, Courses and UCs; list courses/UCs/students/professors.
- Professor menu:
  - Professor: view UCs, record/consult class summaries and attendance counts.
  - UC Regent (if applicable): manage UC staff, enroll/remove students, view presences.
  - Course Director (if applicable): rename course and view course statistics.

## Repo Structure
- `src/main/java/FrontEnd/ProjetoPO.java` — program entry point (main).
- `src/main/java/FrontEnd/Menus.java` — console menus and interaction flows.
- `src/main/java/FrontEnd/Consola.java` — console helpers and input validation.
- `src/main/java/BackEnd/*.java` — domain model and persistence helpers.
- `dist/javadoc/` — generated Javadoc (HTML).
- Data files generated at runtime (not in repo): `Repositorio.ser`, `Administrador.ser`.

## Limitations & Notes
- Storage: uses Java serialization; files are not encrypted nor human‑readable.
- Security: administrator credentials are stored in plaintext within serialized files (academic scope).
- Localization: console UI text is in Portuguese.
- Portability: standard Java console; should run on Windows/macOS/Linux with JDK 17+.

## Author & License
- Author: Tomás Gonçalves
- Course/Unit: University of Minho — Programação Orientada a Objetos (PO)
- License: MIT — see `LICENSE` for details.
