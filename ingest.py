import os
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.document_loaders import UnstructuredFileLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant

print("Initializing embeddings...")
embeddings = SentenceTransformerEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")
print("Embeddings done...")

data_folder = "C:/Users/Vaibhav/AI_Driven_Healthcare_Chatbot_for_Patient_Triage_and_Support/data/"
loader = DirectoryLoader(data_folder, glob="**/*.pdf", show_progress=True, loader_cls=UnstructuredFileLoader)

print("Loading documents...")
documents = loader.load()
print(f"Loaded {len(documents)} documents.")


text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=70)
texts = text_splitter.split_documents(documents)

print(f"Split into {len(texts)} text chunks.")

url = "http://localhost:6333" # This is the same URL that must match Step 4d
qdrant = Qdrant.from_documents(
    texts, 
    embeddings, 
    url=url,
    prefer_grpc=False,
    collection_name="vector_db"
)

print("Vector DB Successfully Created!")