# api/faiss_retriever.py

import os
from typing import List, Optional

import requests
from dotenv import load_dotenv
from langchain.schema import BaseRetriever, Document
from langchain_openai import AzureOpenAIEmbeddings
from pydantic import Field

load_dotenv(override=True)

# endpoint = os.environ["EMBEDDINGS_ENDPOINT"]
# key      = os.environ["EMBEDDINGS_KEY"]


class FaissApiRetriever(BaseRetriever):
    """
    A LangChain retriever that calls your FAISS service over HTTP.
    """

    endpoint: str
    k: int
    api_key: Optional[str]
    embedder: AzureOpenAIEmbeddings = Field(
        default_factory=lambda: AzureOpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_type="azure",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_ALT"),
        )
    )

    def get_relevant_documents(self, query: str) -> List[Document]:

        q_vec = self.embedder.embed_query(query)

        # Step 2: call your FAISS API
        payload = {"vector": q_vec, "k": self.k}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = requests.post(self.endpoint, json=payload, headers=headers)
        resp.raise_for_status()
        hits = resp.json()["results"]

        # Step 3: turn each hit into a LangChain Document
        docs = [
            Document(page_content=hit["text"], metadata={"id": hit["id"], "score": hit["score"]})
            for hit in hits
        ]
        return docs
