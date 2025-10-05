from db.vector_db import retrieve_articles

def fetch_relevant_articles(query, top_k=5):

    article_ids_list = retrieve_articles(query, top_k=top_k)
    return article_ids_list[0]