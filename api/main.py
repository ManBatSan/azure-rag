# api/main.py

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.chains import RetrievalQA
from langchain_core.prompts.prompt import PromptTemplate
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai.chat_models.azure import AzureChatOpenAI
from pydantic import BaseModel

# from api.cosmos_retriever import CosmosVectorRetriever
from api.faiss_retriever import FaissApiRetriever

load_dotenv(override=True)

app = FastAPI()

AZ_SEARCH_NAME = os.environ["AZ_SEARCH_NAME"]
AZ_SEARCH_KEY = os.environ["AZ_SEARCH_ADMIN_KEY"]
AZ_SEARCH_INDEX = os.environ.get("AZ_SEARCH_INDEX", "rag-index")

COSMOS_URI = os.environ["COSMOS_URI"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
COSMOS_DB = os.environ.get("COSMOS_DB")
COSMOS_CONTAINER = os.environ.get("COSMOS_CONTAINER")

PG_PASSWORD = os.getenv("TF_VAR_pg_admin_password")

# Initialize your LLM once
llm = AzureChatOpenAI(
    deployment_name="gpt-4o-mini",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_ALT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0.0,
)

# Build your prompt template (could be a PromptTemplate object)
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question: {question}
Answer:""",
)


class ChatRequest(BaseModel):
    question: str


def get_retriever(name: str):
    k = 5

    EMBEDDER = AzureOpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_type="azure",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_ALT"),
    )

    if name == "faiss":
        return FaissApiRetriever(
            endpoint=os.getenv("FAISS_SEARCH_URL", "http://localhost:8001/search"),
            k=k,
            api_key=None,
            embedder=EMBEDDER,
        )

    # if name == "cosmosdb":

    #     store = CosmosVectorRetriever(k=k, embedder=EMBEDDER)
    #     return store

    # if name == "cognitive_search":
    #     from langchain_community.vectorstores import AzureSearch

    #     store = AzureSearch(
    #         azure_search_endpoint=f"https://{AZ_SEARCH_NAME}.search.windows.net",
    #         azure_search_key=AZ_SEARCH_KEY,
    #         index_name=AZ_SEARCH_INDEX,
    #         embedding_function=EMBEDDER.embed_query,
    #     )
    #     return store.as_retriever(search_type="similarity", k=k)

    # if name == "postgres":
    #     from langchain_postgres.vectorstores import PGVector

    #     connection_string = PGVector.connection_string_from_db_params(
    #         user="pgadminuser",
    #         password=PG_PASSWORD,
    #         host="azrag-pg.postgres.database.azure.com",
    #         port=5432,
    #         database="ragdb",
    #     )
    #     store = PGVector(
    #         connection_string=connection_string,
    #         embedding_function=EMBEDDER.embed_query,
    #     )
    #     return store.as_retriever(k=k)

    raise ValueError(f"Unknown store: {name}")


# Build the RetrievalQA chain once
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=get_retriever("faiss"),
    return_source_documents=False,
    chain_type_kwargs={"prompt": prompt},
)


@app.post("/chat")
def chat(req: ChatRequest):
    answer = qa_chain(req.question)
    return {"answer": answer}


@app.post("/chat/{store_name}")
def chat_custom(req: ChatRequest, store_name: str):
    retriever = get_retriever(store_name)
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt},
    )
    return {"answer": chain(req.question)}
