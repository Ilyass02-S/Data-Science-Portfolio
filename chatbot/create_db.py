from langchain_community.document_loaders import JSONLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from utils import metadata_func

# Using JSONLoader to load the documents.
# This uses jq, so that has to be installed in the venv. It is included in the requirements.txt.
loader = JSONLoader(
    file_path="persistent/chatbot/data/movies.json",
    jq_schema=".[]",                # .[] jq schema means that the file is a list of json objects.
    content_key="Film_title",         # This will be the key that gets put into the page_content in a document.
    metadata_func=metadata_func     # Here we can specify how to extract metadata from each json object.
)

docs = loader.load()

# Same embedding options as in the creating_vector_db.py example from earlier examples.
encode_kwargs = {"normalize_embeddings": True}

# NOTE! If you run this script on your own machine, you need to change this to "cpu" or "gpu" if you run a windows or
# linux machine. On ARM based macOS "mps" should be fine.
model_kwargs = {"device": "cuda"}

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    encode_kwargs=encode_kwargs,
    model_kwargs=model_kwargs,
    show_progress=True
)

vector_store = Chroma(
    collection_name="movies",
    embedding_function=embeddings,
    persist_directory="./data/chroma_db"
)


vector_store.add_documents(docs)

