import psycopg2
from datetime import datetime

# Feedback scoring weights
OUTCOME_SCORES = {
    "Correct": 10,
    "Partial": 5,
    "Wrong": 0
}

def update_news_rating(prediction_id, feedback_outcome, star_rating=None):
    conn = psycopg2.connect(
        dbname="newsdb",
        user="youruser",
        password="yourpass",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Get source_id and category_id from prediction
    cur.execute("""
        SELECT source_id, category_id 
        FROM predictions 
        WHERE prediction_id = %s
    """, (prediction_id,))
    result = cur.fetchone()
    if not result:
        print("Prediction not found")
        return
    source_id, category_id = result

    # Compute feedback score
    feedback_score = OUTCOME_SCORES.get(feedback_outcome, 5)
    if star_rating:
        # Blend outcome score with user star rating
        feedback_score = (feedback_score + (star_rating * 2)) / 2  

    # Fetch current rating
    cur.execute("""
        SELECT rating, rating_count 
        FROM news_ratings 
        WHERE source_id = %s AND category_id = %s
    """, (source_id, category_id))
    row = cur.fetchone()

    if row:
        old_rating, rating_count = row
        new_rating = ((old_rating * rating_count) + feedback_score) / (rating_count + 1)

        cur.execute("""
            UPDATE news_ratings 
            SET rating = %s, rating_count = rating_count + 1, last_updated = %s
            WHERE source_id = %s AND category_id = %s
        """, (new_rating, datetime.now(), source_id, category_id))
    else:
        # If no entry yet, insert one
        cur.execute("""
            INSERT INTO news_ratings (source_id, category_id, rating, rating_count, last_updated)
            VALUES (%s, %s, %s, 1, %s)
        """, (source_id, category_id, feedback_score, datetime.now()))

    conn.commit()
    cur.close()
    conn.close()

    print(f"Updated rating for source_id={source_id}, category_id={category_id}")

# Example usage:
# After user feedback on prediction 12:
update_news_rating(prediction_id=12, feedback_outcome="Correct", star_rating=4)




import psycopg2
from datetime import datetime

OUTCOME_SCORES = {"Correct": 10, "Partial": 5, "Wrong": 0}

def update_rating(prediction_id, outcome):
    conn = psycopg2.connect(dbname="newsdb", user="youruser", password="pwd", host="localhost")
    cur = conn.cursor()

    cur.execute("SELECT source_id, category_id FROM predictions WHERE prediction_id = %s", (prediction_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError("prediction not found")
    source_id, category_id = row

    cur.execute("SELECT rating, rating_count FROM news_ratings WHERE source_id=%s AND category_id=%s",
                (source_id, category_id))
    r = cur.fetchone()

    obs = OUTCOME_SCORES.get(outcome, 5)
    if r:
        old_rating, count = r
        alpha = 1.0 / (1 + count)
        new_rating = old_rating * (1 - alpha) + obs * alpha
        cur.execute("""
            UPDATE news_ratings SET rating=%s, rating_count=rating_count+1, last_updated=%s
            WHERE source_id=%s AND category_id=%s
        """, (new_rating, datetime.utcnow(), source_id, category_id))
    else:
        cur.execute("""
            INSERT INTO news_ratings (source_id, category_id, rating, rating_count, last_updated)
            VALUES (%s, %s, %s, 1, %s)
        """, (source_id, category_id, obs, datetime.utcnow()))

    conn.commit()
    cur.close()
    conn.close()
    return True
