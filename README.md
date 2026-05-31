# IBS Logistics Orchestrator: Multi-Agent Freight Resolution Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://python.langchain.com/docs/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Apache Kafka](https://img.shields.io/badge/Apache_Kafka-Event_Streaming-black.svg)](https://kafka.apache.org/)

## Overview

The IBS Logistics Orchestrator is an event-driven, multi-agent AI platform designed to actively resolve routing anomalies in airline freight and baggage systems. It ingests real-time scan events via Apache Kafka and utilizes a LangGraph Supervisor Architecture to autonomously investigate delays, predict downstream impacts, and orchestrate ground staff dispatch.

---

## Core Architecture & Features

- **Multi-Agent Reasoning (LangGraph):** A Supervisor router dynamically delegates logistical tasks to specialized sub-agents:
  - **Logistics Agent:** Queries flight schedules and cargo capacities for rerouting.
  - **Compliance Agent:** Evaluates packaging regulations and safety protocols.
  - **Dispatch Agent:** Interfaces with HR systems to assign tasks to available ground staff.
- **Event-Driven Ingestion (Apache Kafka):** Simulates high-throughput barcode scans and triggers agentic workflows instantly upon detecting anomalies.
- **RESTful Microservices (FastAPI):** Exposes secure endpoints for manual workflow triggers and real-time state monitoring.
- **External API Integration:** Features custom LangChain tools that securely wrap mock internal airline systems.

---

## Project Structure

```text
ibs-logistics-orchestrator/
├── api/
│   ├── main.py
│   ├── routes.py
│   └── schemas.py
├── agents/
│   ├── supervisor.py
│   ├── sub_agents.py
│   ├── state.py
│   └── tools.py
├── streaming/
│   ├── consumer.py
│   └── producer.py
├── mock_services/
│   ├── flight_api.py
│   └── hr_api.py
├── core/
│   ├── config.py
│   └── logger.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

---

## Quick Start Guide

### 1. Prerequisites

- Python 3.10+
- Docker & Docker Compose
- OpenAI or Google Gemini API Key

### 2. Installation

```bash
git clone https://github.com/yourusername/ibs-logistics-orchestrator.git
cd ibs-logistics-orchestrator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
# or GEMINI_API_KEY=your_gemini_api_key_here

# Kafka Configuration
KAFKA_BROKER_URL=localhost:9092
KAFKA_TOPIC_ANOMALIES=logistics.anomalies

# API Settings
PORT=8000
ENVIRONMENT=development
```

### 4. Running the System

**Start the infrastructure (Kafka):**

```bash
docker-compose up -d
```

**Start the FastAPI server:**

```bash
uvicorn api.main:app --reload --port 8000
```

> API documentation available at: http://localhost:8000/docs

**Start the Kafka consumer:**

```bash
python -m streaming.consumer
```

**Simulate an event:**

```bash
python -m streaming.producer --type "missed_connection" --package_id "PKG-9942"
```