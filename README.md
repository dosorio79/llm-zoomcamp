# LLM Zoomcamp 2026

My working repository for the [LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp) by DataTalksClub.

This repo contains lesson material, homework projects, and an evolving standalone `cli_rag` project that started from the Homework 1 Agentic RAG implementation and is now being expanded with vector search, hybrid search, and a cleaner CLI architecture.

The course is a practical, hands-on introduction to building applications with LLMs, retrieval-augmented generation, agents, evaluation, monitoring, and production-oriented workflows.

## Repository structure

    .
    ├── Lessons/
    │   └── Course lesson notebooks, examples, and experiments
    │
    ├── Homework/
    │   └── Homework solutions by module
    │
    └── cli_rag/
        └── Work-in-progress standalone CLI RAG project

## Main sections

### Lessons

The `Lessons/` directory contains notes, notebooks, and experiments developed while following the course modules.

These materials are mostly exploratory and are used to understand the core concepts before applying them in homework solutions or standalone projects.

Typical contents include:

- course notebooks
- small experiments
- retrieval examples
- prompt and API tests
- notes from module exercises

### Homework

The `Homework/` directory contains my solutions for the course assignments.

Each homework folder is organized by module and may include:

- notebooks
- Python scripts
- helper modules
- local data or indexing logic
- CLI experiments
- explanations and final answers

The first homework started with a basic RAG pipeline and was later expanded into an agentic RAG flow using function calling.

### cli_rag

The `cli_rag/` directory is a work-in-progress standalone project based on the Agentic RAG implementation developed in Homework 1.

The goal is to progressively refactor the homework implementation into a cleaner and more modular CLI application for experimenting with different RAG patterns.

Current and planned directions include:

- plain RAG
- agentic RAG
- text search
- vector search
- hybrid search
- reusable retrieval components
- shared ingestion and indexing logic
- CLI-based interaction

This part of the repository is still under active development, especially in the development branch.

## Why this repo exists

This repository is both a course workspace and a learning log.

The goal is not only to complete the homework, but also to progressively refactor the solutions into reusable components and better project structure.

Main learning objectives:

- understand RAG from first principles
- build retrieval pipelines without hiding too much behind frameworks
- compare plain RAG versus agentic RAG
- experiment with vector and hybrid search
- track token usage and cost
- build a usable CLI around the pipeline
- keep the implementation simple enough to understand and extend

## Technologies used

Depending on the module and branch, the repo may use:

- Python
- OpenAI API
- minsearch
- SQLite
- vector search libraries
- Rich for CLI formatting
- dotenv for configuration
- Jupyter notebooks
- modular Python scripts

Additional dependencies may appear as the course progresses.

## Development status

This repo is actively evolving during the course.

Some parts are intentionally simple because they follow the course exercises closely. Other parts, especially `cli_rag`, are being refactored into a cleaner standalone implementation.

The `dev` branch may contain newer work that is not yet fully reflected in the main branch.

## Course reference

LLM Zoomcamp is a free course by DataTalksClub covering practical LLM application development.

Official repository:

https://github.com/DataTalksClub/llm-zoomcamp

Course topics include:

- search and retrieval
- RAG pipelines
- vector search
- evaluation
- agents
- monitoring
- production considerations
- final project development

## Notes

This repository reflects my personal learning process through the course.

Some folders contain direct homework-oriented code, while others contain refactored or experimental versions of the same ideas.
