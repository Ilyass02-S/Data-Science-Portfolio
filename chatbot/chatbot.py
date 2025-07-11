from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from utils import create_prompt_template
model = "llama3.2:3b"
db_path = "./data/chroma_db"
k = 5
prompt_template = create_prompt_template()
chat_history = []
llm = OllamaLLM(model=model, num_ctx=5000)

encode_kwargs = {"normalize_embeddings": True}
model_kwargs = {"device": "cuda"}

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    encode_kwargs=encode_kwargs,
    model_kwargs=model_kwargs,
)

db = Chroma(persist_directory=db_path, embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": k})

chain = prompt_template | llm
print("Ready...")

while True:
    human_input = HumanMessage(content=input("What movie are you interested in? "))
    response = chain.invoke({
        "context": retriever.invoke(human_input.content),
        "chat_history": chat_history,
        "input": [human_input]
    })
    chat_history.append(human_input)
    chat_history.append(AIMessage(content=response))
    print("Answer: ", response)

