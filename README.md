# GenAI Project - LLaMA 2 with RAG

A Flask-based REST API demonstrating local LLM deployment with Retrieval-Augmented Generation (RAG). This project showcases how RAG can overcome the knowledge cutoff limitations of language models by injecting up-to-date facts at inference time.

## Project Overview

This project contains two Flask applications:

| Application | Port | Description |
|-------------|------|-------------|
| `app/app.py` | 5001 | Basic LLaMA 2 inference API |
| `rag/rag.py` | 5002 | RAG-enhanced API with knowledge base |

### How It Works

**Basic App (`app.py`):**
- Loads the LLaMA 2 7B Chat model (quantized GGUF format)
- Accepts prompts via REST API and returns model predictions
- Limited to the model's training data (knowledge cutoff)

**RAG App (`rag.py`):**
- Extends the basic app with a knowledge base (`knowledge_base.py`)
- Searches for relevant facts based on keywords in the user's prompt
- Injects matching facts into the system message before inference
- Allows the model to provide accurate, up-to-date answers

## Prerequisites

Install the following tools:

- [Hugging Face CLI](https://huggingface.co/docs/huggingface_hub/en/installation)
- [jq](https://jqlang.github.io/jq/download/) (for JSON formatting)
- [Docker Engine](https://docs.docker.com/engine/install/)

## Setup

### 1. Authenticate to Hugging Face

Follow the [CLI authentication guide](https://huggingface.co/docs/huggingface_hub/en/guides/cli).

### 2. Download the Model

```bash
huggingface-cli download TheBloke/Llama-2-7B-Chat-GGUF llama-2-7b-chat.Q2_K.gguf --local-dir .
```

> **Note:** Feel free to use any compatible GGUF foundation model of your choice.

### 3. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Applications

### Option 1: Run Locally

**Basic App:**
```bash
python app/app.py
```

**RAG App:**
```bash
python rag/rag.py
```

### Option 2: Run with Docker

**Build and run the basic app:**
```bash
docker build -f app/Dockerfile.app -t llama-app .
docker run -p 5001:5001 llama-app
```

**Build and run the RAG app:**
```bash
docker build -f rag/Dockerfile.rag -t llama-rag .
docker run -p 5002:5002 llama-rag
```

## API Usage

### Endpoint

Both applications expose a single endpoint:

```
POST /predict
Content-Type: application/json
```

**Request Body:**
```json
{
  "prompt": "Your question here",
  "sys_msg": "Optional system message to guide the model's behavior"
}
```

### Example: General Query

```bash
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a poem about humanity?",
    "sys_msg": "You are a helpful, respectful, and honest assistant. Always provide safe, unbiased, and positive responses."
  }' | jq .
```

## Demonstrating the Power of RAG

This section demonstrates how RAG solves the knowledge cutoff problem inherent in LLMs.

### The Problem: Outdated Knowledge

When asking the **basic app** (without RAG) about current events:

```bash
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Who is the President of United States of America?",
    "sys_msg": "If a question is unclear or incorrect, explain why. If unsure, do not provide false information."
  }' | jq .
```

**Response (Incorrect - based on training data cutoff):**
```
"I apologize, but as of my knowledge cutoff on March 10th, 2023, there is no current
President of the United States. The most recent Presidential election was held on
November 3rd, 2020... the current President of the United States is Joe Biden."
```

The model's answer is outdated because it only knows information up to its training cutoff date.

### The Solution: RAG with Knowledge Base

The RAG application uses `knowledge_base.py` to store current facts:

```python
FACTS = [
    {
        "keywords": ["president", "usa", "united states", "america", ...],
        "fact": "As of January 2025, Donald Trump is the 47th President of the United States..."
    },
    {
        "keywords": ["vice president", "usa", "united states", "vp", ...],
        "fact": "As of January 2025, JD Vance is the Vice President of the United States."
    }
]
```

When a user's prompt contains matching keywords, the relevant facts are automatically injected into the system message, giving the model access to current information.

### RAG in Action

Asking the same question to the **RAG app**:

```bash
curl -X POST http://localhost:5002/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Who is the President of United States of America?",
    "sys_msg": "If a question is unclear or incorrect, explain why. If unsure, do not provide false information."
  }' | jq .
```

**Response (Correct - enhanced with RAG):**
```
"As of January 2025, the current President of the United States is Donald Trump.
As you provided the correct information that Donald Trump is the 47th President
of the United States and that Joe Biden is no longer the President, I can confirm
that the current President is indeed Donald Trump."
```

The RAG-enhanced model now provides accurate, up-to-date information by leveraging the injected facts from the knowledge base.

## Project Structure

```
GenAI-Project/
├── app/
│   ├── app.py              # Basic Flask API
│   └── Dockerfile.app      # Docker config for basic app
├── rag/
│   ├── rag.py              # RAG-enhanced Flask API
│   ├── knowledge_base.py   # Facts database for RAG
│   └── Dockerfile.rag      # Docker config for RAG app
├── requirements.txt        # Python dependencies
├── llama-2-7b-chat.Q2_K.gguf  # LLaMA 2 model (download separately)
└── README.md
```

## Cleanup

Stop and remove Docker containers and images:

```bash
# List running containers
docker ps

# Stop container
docker stop <container_id>

# Remove images
docker rmi llama-app llama-rag -f
```

## Key Takeaways

1. **LLMs have knowledge cutoffs** - They only know information from their training data
2. **RAG bridges the gap** - By injecting relevant facts at inference time, models can provide current information
3. **Simple yet powerful** - This keyword-based RAG implementation demonstrates the core concept with minimal complexity
4. **Extensible** - Add more facts to `knowledge_base.py` to expand the model's current knowledge
