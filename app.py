from langchain import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import SentenceTransformerEmbeddings
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant

# Load a local BioMistral LLM model with specified settings.
local_llm = "C:/Users/Vaibhav/AI_Driven_Healthcare_Chatbot_for_Patient_Triage_and_Support/model/BioMistral-7B.Q4_K_M.gguf"
llm = LlamaCpp(model_path=local_llm, temperature=0.3, max_tokens=2048, top_p=1, n_ctx=2048)

# Define a prompt template to guide LLM responses.
prompt_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Chat History: {chat_history}
Question: {question}

Only return the helpful answer. Answer must be detailed and well explained.
Helpful answer:
"""

# Create sentence embeddings model for representing text as vectors.
embeddings = SentenceTransformerEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")

# Connect to a Qdrant vector database for storing and retrieving information.
url = "http://localhost:6333"
client = QdrantClient(url=url, prefer_grpc=False)
db = Qdrant(client=client, embeddings=embeddings, collection_name="vector_db")

# Initialize a retriever for searching within the database.
retriever = db.as_retriever(search_kwargs={"k": 1})

# Create an empty chat history list to track conversation.
chat_history = []

# Initialize cache
cache = {}

# Create the custom chain
chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever)

# Define the actual prediction function that will carry on the chatbot conversation.
def predict(message, history):
    # Check if the message is already in cache
    if message in cache:
        answer = cache[message]
        print("Fetching from cache...")
    else:
        response = chain({"question": message, "chat_history": history})
        answer = response['answer']
        # Store the answer in cache
        cache[message] = answer
        print("Fetching from database...")
    
    history.append((message, answer))
    return answer

# Run the chatbot in a loop
if __name__ == "__main__":
    print("AI-Driven Healthcare Chatbot for Patient Triage and Support")
    print("Type 'exit' to end the conversation.")
    while True:
        user_input = input("Enter your medical query here: ")
        if user_input.lower() == 'exit':
            break
        response = predict(user_input, chat_history)
        print("Chatbot:", response)
