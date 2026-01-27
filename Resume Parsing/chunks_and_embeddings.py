from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np

# embedding model
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_text(text)

# chunks
print("CHUNKS: \n")
for i, chunk in enumerate(chunks):
    print(f"chunk {i+1}:")
    print(chunk)
    print("-" * 60)

# embeddings
print("\n EMBEDDINGS : \n")
chunk_embeddings = embeddings.embed_documents(chunks)

# display embeddings
for i, emb in enumerate(chunk_embeddings):
    print(f"embedding for chunk {i+1}:")
    print(np.array(emb)[:10], "...")
    print(f"embedding length: {len(emb)}")
    print("-" * 60)
