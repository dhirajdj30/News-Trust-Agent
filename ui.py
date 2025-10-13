import streamlit as st
import pandas as pd
from datetime import datetime
import random

# -----------------------------
# Dummy Data Functions
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
    st.toast(f"✅ Feedback recorded for Prediction {prediction_id}: {outcome}", icon="💬")
    return True

# -----------------------------
# Helper: Dummy Agent Logic
# -----------------------------
def generate_stock_recommendations(prompt: str):
    # Simulate categories and news sources
    sources = ["Moneycontrol", "CNBC", "Bloomberg", "Economic Times"]
    categories = ["Finance", "Seasonal", "Sports", "Policy"]

    stocks_pool = [
        "TCS", "INFY", "RELIANCE", "HDFCBANK", "ITC",
        "ASIANPAINT", "PIDILITIND", "BRITANNIA", "MARICO", "HUL",
        "ONGC", "COALINDIA", "NTPC", "TATASTEEL", "ADANIPORTS"
    ]

    recommended_stocks = random.sample(stocks_pool, 5)
    chosen_source = random.choice(sources)
    chosen_category = random.choice(categories)
    rating = round(random.uniform(7, 9.5), 2)

    result = {
        "prompt": prompt,
        "predicted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stocks_list": recommended_stocks,
        "category_name": chosen_category,
        "source_name": chosen_source,
        "rating": rating,
    }
    return result

# -----------------------------
# Streamlit Page Configuration
# -----------------------------
st.set_page_config(
    page_title="🧠 News Trust Agent Dashboard",
    page_icon="📰",
    layout="wide"
)

# -----------------------------
# Global CSS Styling
# -----------------------------
st.markdown(
    """
    <style>
    /* ====== GENERAL LAYOUT ====== */
    body, .main {
        background-color: #0f172a;
        color: #e2e8f0;
        font-family: "Inter", sans-serif;
    }
    /* ====== HEADER ====== */
    .navbar {
        background-color: #1e293b;
        padding: 1rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.4);
    }
    .navbar h1 {
        color: #38bdf8;
        margin: 0;
        font-size: 1.8rem;
    }
    .navbar span {
        color: #94a3b8;
        font-size: 1rem;
    }

    /* ====== TABS ====== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        padding: 10px 20px;
        border-radius: 10px;
        color: #e2e8f0;
        font-weight: 500;
        border: 1px solid #334155;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb;
        color: #fff;
        border: none;
    }

    /* ====== CONTAINERS ====== */
    .stMarkdown, .stDataFrame, .stColumn {
        background-color: transparent;
    }
    div[data-testid="stVerticalBlock"] {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    }

    /* ====== FOOTER ====== */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #1e293b;
        color: #94a3b8;
        text-align: center;
        padding: 0.8rem;
        font-size: 0.9rem;
        border-top: 1px solid #334155;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Header Section
# -----------------------------
st.markdown(
    """
    <div class="navbar">
        <h1>🧠 News Trust Agent</h1>
        <span> MLOps | Qualys</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Tabs Layout
# -----------------------------
tabs = st.tabs(["💬 Ask the Agent", "📈 Predictions", "⭐ Ratings Dashboard", "🗳 Feedback"])

# =============================
# Tab 0: Ask the Agent
# =============================
with tabs[0]:
    st.subheader("Ask the News Trust Agent")

    user_prompt = st.text_area("💭 Enter your query (e.g., 'Give me 5 stocks I should buy today'):")

    if st.button("🚀 Generate Prediction"):
        if user_prompt.strip():
            with st.spinner("Analyzing news and generating prediction..."):
                result = generate_stock_recommendations(user_prompt)
                st.success("Prediction generated successfully!")
                st.markdown("### 🧠 Agent Response")
                st.write(f"**Prompt:** {result['prompt']}")
                st.write(f"**Date:** {result['predicted_at']}")
                st.write(f"**Category:** {result['category_name']}")
                st.write(f"**Source:** {result['source_name']}")
                st.write(f"**Rating (Trust):** ⭐ {result['rating']}/10")
                st.write(f"**Suggested Stocks:** {', '.join(result['stocks_list'])}")
        else:
            st.warning("Please enter a valid query to generate a prediction.")
# =============================
# Tab 1: Predictions
# =============================
with tabs[1]:
    st.subheader("📊 Recent Predictions")
    df = fetch_predictions()

    if not df.empty:
        for _, row in df.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                col1.markdown(f"**🗓️ Date:** {row.predicted_at}")
                col2.markdown(f"**🎯 Target:** {row.target_date}")
                col3.metric("⭐ Rating", f"{row.rating}/10")

                st.markdown(f"**📰 Source:** `{row.source_name}` | **📂 Category:** `{row.category_name}`")
                st.markdown(f"**💼 Stocks:** `{row.stocks_list}`")

                st.progress(min(row.rating / 10, 1.0))
    else:
        st.info("No predictions found yet. Run the backend service to populate data.")

# =============================
# Tab 2: Ratings Dashboard
# =============================
with tabs[2]:
    st.subheader("⭐ Ratings Overview by Source & Category")
    df_ratings = fetch_ratings()

    if df_ratings.empty:
        st.warning("No ratings data available.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            pivot_df = df_ratings.pivot(index="source_name", columns="category_name", values="rating")
            st.dataframe(
                pivot_df.style.background_gradient(cmap="Blues"),
                use_container_width=True,
            )
        with col2:
            avg_rating = df_ratings["rating"].mean()
            top_source = df_ratings.loc[df_ratings["rating"].idxmax(), "source_name"]
            st.metric("📊 Average Rating", f"{avg_rating:.2f}")
            st.metric("🏆 Top Rated Source", top_source)

        st.markdown("### 📈 Source Ratings Trend")
        st.bar_chart(df_ratings, x="source_name", y="rating", color="category_name")

# =============================
# Tab 3: Feedback
# =============================
with tabs[3]:
    st.subheader("🗳 Provide Feedback on Predictions")

    df_feedback = fetch_predictions()
    if df_feedback.empty:
        st.warning("No predictions available for feedback.")
    else:
        for _, row in df_feedback.iterrows():
            with st.expander(f"📌 Prediction ID {row.prediction_id}: {row.source_name} ({row.category_name})"):
                st.write(f"**Predicted At:** {row.predicted_at}")
                st.write(f"**Stocks:** `{row.stocks_list}`")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Correct", key=f"correct_{row.prediction_id}"):
                        update_feedback(row.prediction_id, "Correct")
                with col2:
                    if st.button("⚠️ Partial", key=f"partial_{row.prediction_id}"):
                        update_feedback(row.prediction_id, "Partial")
                with col3:
                    if st.button("❌ Wrong", key=f"wrong_{row.prediction_id}"):
                        update_feedback(row.prediction_id, "Wrong")

# -----------------------------
# Footer Section
# -----------------------------
st.markdown(
    """
    <div class="footer">
        © 2025 News Trust Agent | Powered by Streamlit 🚀
    </div>
    """,
    unsafe_allow_html=True,
)
