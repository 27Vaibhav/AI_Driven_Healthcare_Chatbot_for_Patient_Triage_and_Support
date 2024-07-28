from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from langchain import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import SentenceTransformerEmbeddings
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
import contextlib
import io

app = Flask(__name__)
CORS(app)  # Enable CORS

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

# Define the helper function to suppress unwanted output
@contextlib.contextmanager
def suppress_output():
    with contextlib.redirect_stdout(io.StringIO()):
        with contextlib.redirect_stderr(io.StringIO()):
            yield

# Define the actual prediction function that will carry on the chatbot conversation.
def predict(message, history):
    with suppress_output():
        if message in cache:
            answer = cache[message]
        else:
            response = chain({"question": message, "chat_history": history})
            answer = response['answer']
            cache[message] = answer
    
    history.append((message, answer))
    return answer

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get('message')
    response = predict(user_input, chat_history)
    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Ensure the Flask server runs on port 5000
