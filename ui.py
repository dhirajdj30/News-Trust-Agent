import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
# from db.fetch import fetch_predictions, fetch_ratings
# from db.update import update_feedback


# -----------------------------
# Dummy fetch functions
# -----------------------------
def fetch_predictions():
    data = [
        {
            "prediction_id": 1,
            "predicted_at": "2025-10-05 09:00:00",
            "target_date": "2025-10-06",
            "stocks_list": "['TCS', 'INFY', 'HDFCBANK', 'RELIANCE', 'ITC']",
            "category_name": "Finance",
            "source_name": "Moneycontrol",
            "rating": 8.5,
        },
        {
            "prediction_id": 2,
            "predicted_at": "2025-10-05 09:00:00",
            "target_date": "2025-10-06",
            "stocks_list": "['ASIANPAINT', 'PIDILITIND', 'BRITANNIA', 'MARICO', 'HUL']",
            "category_name": "Seasonal",
            "source_name": "CNBC",
            "rating": 7.8,
        },
    ]
    return pd.DataFrame(data)

def fetch_ratings():
    data = [
        {"source_name": "Moneycontrol", "category_name": "Finance", "rating": 8.5, "rating_count": 25},
        {"source_name": "Moneycontrol", "category_name": "Seasonal", "rating": 7.2, "rating_count": 18},
        {"source_name": "CNBC", "category_name": "Finance", "rating": 7.8, "rating_count": 30},
        {"source_name": "CNBC", "category_name": "Sports", "rating": 8.1, "rating_count": 22},
        {"source_name": "Bloomberg", "category_name": "Finance", "rating": 9.0, "rating_count": 40},
    ]
    return pd.DataFrame(data)

def update_feedback(prediction_id, outcome):
    # Dummy update for now (no DB)
    st.toast(f"✅ Feedback recorded for Prediction {prediction_id}: {outcome}", icon="💬")
    return True

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="News Trust Agent", layout="wide")
st.title("📰 News Trust Agent Dashboard")

tabs = st.tabs(["📈 Predictions", "⭐ Ratings Dashboard", "🗳 Feedback"])

# =============================
# Tab 1: Predictions
# =============================
with tabs[0]:
    st.subheader("Recent Predictions")

    df = fetch_predictions()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No predictions found yet. Run app.py to generate predictions.")

# =============================
# Tab 2: Ratings Dashboard
# =============================
with tabs[1]:
    st.subheader("News Source Ratings by Category")

    df_ratings = fetch_ratings()
    if df_ratings.empty:
        st.warning("No ratings data available.")
    else:
        pivot_df = df_ratings.pivot(index="source_name", columns="category_name", values="rating")
        st.dataframe(pivot_df.style.background_gradient(cmap="YlGn"), use_container_width=True)

        st.bar_chart(df_ratings, x="source_name", y="rating", color="category_name")

# =============================
# Tab 3: Feedback
# =============================
with tabs[2]:
    st.subheader("Provide Feedback for Predictions")

    df_feedback = fetch_predictions()
    if df_feedback.empty:
        st.warning("No predictions available for feedback.")
    else:
        for _, row in df_feedback.iterrows():
            st.markdown(f"### Prediction ID: {row.prediction_id}")
            st.write(f"**Date:** {row.predicted_at}")
            st.write(f"**Stocks Predicted:** {row.stocks_list}")
            st.write(f"**Source:** {row.source_name} ({row.category_name})")

            col1, col2, col3 = st.columns(3)
            if col1.button("✅ Correct", key=f"correct_{row.prediction_id}"):
                update_feedback(row.prediction_id, "Correct")
            if col2.button("⚠️ Partial", key=f"partial_{row.prediction_id}"):
                update_feedback(row.prediction_id, "Partial")
            if col3.button("❌ Wrong", key=f"wrong_{row.prediction_id}"):
                update_feedback(row.prediction_id, "Wrong")
