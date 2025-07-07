# azure-rag

## Project Overview

This repository implements a Retrieval-Augmented Generation (RAG) proof-of-concept on Azure, powering a chat interface over the **ioASQ13** dataset. We will:

1. Ingest and preprocess the ioASQ13 data.  
2. Generate dense embeddings for each chunk.  
3. Store embeddings in a vector store.  
4. Build a FastAPI-based chat API that:  
   - Retrieves relevant context via vector search.  
   - Feeds context + user prompt to a language model.  
5. Wrap everything in IaC and CI/CD pipelines for repeatable, code-driven deployment.

## Technologies

| Category       | Option                                      |
| -------------- | ------------------------------------------- |
| Vector Store   | 1. **Azure Cognitive Search** + Azure OpenAI Embeddings<br>2. **Azure Cosmos DB** Vector Search<br>3. **Azure Database for PostgreSQL** + **pgvector** |
| Orchestration  | **LangChain** (for prompt chaining & retrieval logic) |

> You can switch between the three vector stores by swapping the `storage/` backend module.

## Repo Structure

```
azure-rag/
├── README.md
├── ROADMAP.md
├── data-downloader/       # Download challenge data
│   └── download_data.py
├── dev-setup/             # Precommits install
│   ├── install_precommit.sh
│   └── install_precommit.bat
├── environment.yml        # Conda environment specification
├── infrastructure/        # IaC templates (Bicep / ARM / Terraform)
├── ingestion/             # Data extraction & chunking scripts
├── embeddings/            # Embedding generation code
├── storage/               # Vector-store adapters (cosmosdb/, cognitive_search/, pgvector/)
├── api/                   # FastAPI app + LangChain integration
├── tests/                 # Unit & integration tests
└── ci/                    # CI/CD workflows (GitHub Actions)
```

## Getting Started

1. **Clone the repo**  
   ```bash
   git clone https://github.com/ManBatSan/azure-rag.git
   cd azure-rag
   ```

2. **Create & activate the Conda environment**  
   ```bash
   conda create -n azure-rag python=3.11 -y
   conda activate azure-rag
   ```

3. **Install pre-commit hooks**  
   - **Unix/macOS**  
     ```bash
     bash scripts/install_precommit.sh
     ```  
   - **Windows**  
     ```bat
     scripts\install_precommit.bat
     ```

4. **Download the ioASQ13 data**  
   ```bash
   python3 scripts/download_data.py --dataset enelpol/rag-mini-bioasq --config question-answer-passages
   python3 scripts/download_data.py --dataset enelpol/rag-mini-bioasq --config text-corpus
   ```

5. **Provision Azure services** using IaC in `infrastructure/`.  
   ```bash
   # example for Terraform
   cd infrastructure/terraform
   terraform init
   terraform apply
   ```

6. **Run ingestion & embedding**  
   ```bash
   python3 ingestion/chunk_data.py
   python3 embeddings/generate_embeddings.py
   ```

7. **Start the API**  
   ```bash
   uvicorn api.main:app --reload
   ```

---

For detailed instructions on each phase (IaC, ingestion, embeddings, API, testing, deployment), see **ROADMAP.md**.  
```