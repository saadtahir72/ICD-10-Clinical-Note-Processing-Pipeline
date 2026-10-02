<div align="center">

# 🏥 ICD-10 Clinical Note ETL Pipeline

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Google Gemini API](https://img.shields.io/badge/AI-Google%20Gemini%203.8%20Flash-8E7CC3?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**A production-grade, fault-tolerant ETL pipeline for clinical note structured extraction.**

[Architecture](#️-architecture--pipeline-overview) • [Features](#-features--resilience-mechanisms) • [Quickstart](#-getting-started) • [Database Queries](#-querying-the-duckdb-database)

</div>

---

A production-grade, lightweight, and scalable **ETL (Extract, Transform, Load)** pipeline built in Python. This pipeline ingests raw, unstructured clinical physician encounter notes, transforms and enriches them with official **ICD-10-CM diagnostic codes** and reasoning using the **Google Gemini API**, and loads structured records into a **DuckDB** analytical database.

---

## 🏗️ Architecture & Pipeline Overview

```text
 ┌──────────────────────┐
 │  data/raw_notes.json │ (Unstructured Clinical Notes)
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │    1. EXTRACT        │ Ingestion & validation (Pandas)
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │   2. TRANSFORM       │ Gemini AI + Pydantic Schema Validation
 │  (Google Gemini API) │ Automated Rate-Limiting & Backoff Retry Handling
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │      3. LOAD         │ DuckDB Analytical Data Store
 │   (DuckDB Store)     │ Schema drift protection & Deduplication Sync
 └──────────────────────┘