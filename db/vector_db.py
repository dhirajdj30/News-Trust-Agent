
from datetime import datetime
from db.fetch import fetch_todays_articles
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def store_in_vector_db():
    print(f"🚀 Storing today's articles in vector DB ({datetime.now().date()})")

    articles = fetch_todays_articles()
    if not articles:
        print("No new articles found for today.")
        return

    # Using HuggingFace sentence transformer embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    docs, metadatas = [], []
    for article_id, title, content, url, published_at in articles:
        text = f"{title}\n\n{content}"
        docs.append(text)
        metadatas.append({
            "article_id": article_id,
            "title": title,
            "url": url,
            "published_at": str(published_at)
        })

    # Create or load FAISS index
    vector_db = FAISS.from_texts(texts=docs, embedding=embeddings, metadatas=metadatas)
    vector_db.save_local("./vector_store/faiss_index")  # save index locally
    print(f"✅ Stored {len(docs)} articles in FAISS vector DB.")

def retrieve_articles(query, top_k=5):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Load FAISS index
    vector_db = FAISS.load_local("./vector_store/faiss_index", embeddings, allow_dangerous_deserialization=True)

    results = vector_db.similarity_search(query, k=top_k)
    article_ids = [r.metadata['article_id'] for r in results]
    print("🔎 Retrieved relevant articles:" )

    for r in results:
        print(f"  - {r.metadata['title']} ({r.metadata['url']})")

    return article_ids

if __name__ == "__main__":
    store_in_vector_db()
    # # Example retrieval
    retrieve_articles("top 3 stock to buy today", top_k=3)
