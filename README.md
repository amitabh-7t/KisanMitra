# KisanMitra — Vernacular AI Agronomist (MVP)

**KisanMitra** is an open-source vernacular agronomist assistant that provides real-time, farmer-friendly agricultural advice in local languages.  
This repository contains the Phase 1 MVP: voice/text I/O, a lightweight advisory backend, and a starter dataset & evaluation pipeline.

## Goals (Phase 1)
- Real-time Q&A in [Pilot Language e.g., Hindi] + English
- Support voice input (ASR) and voice output (TTS)
- Provide crop-specific recommendations with provenance links
- Offline-first design for low-connectivity areas

## What’s included
- `/backend` — FastAPI backend that handles ASR transcripts, LLM prompts, and returns advice.
- `/frontend` — PWA (React) with mic input, text display, and TTS playback.
- `/data` — Starter dataset: 500 Q/A pairs, glossary, label format.
- `/models` — integration scripts to run open LMs / ASR locally or call hosted models.
- `/evaluation` — test harness and annotation UI for human evaluation.

## Quick start (developer)
1. Clone repo
2. Create `.env` with API settings (see `.env.example`)
3. Start backend:
   ```bash
   cd backend
   docker compose up --build
