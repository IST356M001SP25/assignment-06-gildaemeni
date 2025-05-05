import streamlit as st
import pandas as pd
import os
import sys

# Auto-create cache folder and place_ids file if missing
PLACE_IDS_SOURCE_FILE = "cache/place_ids.csv"
if not os.path.exists("cache"):
    os.makedirs("cache")
if not os.path.exists(PLACE_IDS_SOURCE_FILE):
    pd.DataFrame({
        "place_id": [
            "ChIJUTtvv9Tz2YkRhneTbRT-1mk",
            "ChIJl2h_-pjz2YkR-VUHD9dpOF0"
        ]
    }).to_csv(PLACE_IDS_SOURCE_FILE, index=False)

# Import API functions
if __name__ == "__main__":
    sys.path.append("code")
    from apicalls import (
        get_google_place_details,
        get_azure_sentiment,
        get_azure_named_entity_recognition
    )
else:
    from code.apicalls import (
        get_google_place_details,
        get_azure_sentiment,
        get_azure_named_entity_recognition
    )

# Cache files
CACHE_REVIEWS_FILE = "cache/reviews.csv"
CACHE_SENTIMENT_FILE = "cache/reviews_sentiment_by_sentence.csv"
CACHE_ENTITIES_FILE = "cache/reviews_sentiment_by_sentence_with_entities.csv"

def reviews_step(place_ids: str | pd.DataFrame) -> pd.DataFrame:
    if isinstance(place_ids, str):
        df = pd.read_csv(place_ids)
    else:
        df = place_ids.copy()

    results = []
    for _, row in df.iterrows():
        place_id = row["place_id"]
        resp = get_google_place_details(place_id)
        result = resp.get("result", {})
        result["place_id"] = place_id
        results.append(result)

    flat = pd.json_normalize(results, record_path="reviews", meta=["place_id", "name"], errors="ignore")
    selected = flat[["place_id", "name", "author_name", "rating", "text"]]
    selected.to_csv(CACHE_REVIEWS_FILE, index=False)
    return selected

def sentiment_step(reviews: str | pd.DataFrame) -> pd.DataFrame:
    if isinstance(reviews, str):
        df = pd.read_csv(reviews)
    else:
        df = reviews.copy()

    all_rows = []
    for _, row in df.iterrows():
        text = row["text"]
        try:
            response = get_azure_sentiment(text)
            doc = response.get("results", {}).get("documents", [{}])[0]
            for sent in doc.get("sentences", []):
                entry = {
                    "place_id": row["place_id"],
                    "name": row["name"],
                    "author_name": row["author_name"],
                    "rating": row["rating"],
                    "sentence_text": sent.get("text"),
                    "sentence_sentiment": sent.get("sentiment"),
                    "confidenceScores.positive": sent.get("confidenceScores", {}).get("positive"),
                    "confidenceScores.neutral": sent.get("confidenceScores", {}).get("neutral"),
                    "confidenceScores.negative": sent.get("confidenceScores", {}).get("negative"),
                }
                all_rows.append(entry)
        except Exception as e:
            print(f"Sentiment failed for row: {e}")

    df_out = pd.DataFrame(all_rows)
    df_out.to_csv(CACHE_SENTIMENT_FILE, index=False)
    return df_out

def entity_extraction_step(sentences: str | pd.DataFrame) -> pd.DataFrame:
    if isinstance(sentences, str):
        df = pd.read_csv(sentences)
    else:
        df = sentences.copy()

    all_entities = []
    for _, row in df.iterrows():
        try:
            text = row["sentence_text"]
            resp = get_azure_named_entity_recognition(text)
            doc = resp.get("results", {}).get("documents", [{}])[0]
            for ent in doc.get("entities", []):
                new_row = row.to_dict()
                new_row.update({
                    "entity_text": ent.get("text"),
                    "entity_category": ent.get("category"),
                    "entity_subCategory": ent.get("subCategory", None),
                    "confidenceScores.entity": ent.get("confidenceScore")
                })
                all_entities.append(new_row)
        except Exception as e:
            print(f"Entity extraction failed: {e}")

    df_out = pd.DataFrame(all_entities)
    df_out.to_csv(CACHE_ENTITIES_FILE, index=False)
    return df_out

# Streamlit display
if __name__ == '__main__':
    st.write("Running ETL pipeline...")

    reviews_df = reviews_step(PLACE_IDS_SOURCE_FILE)
    st.write("✅ Step 1 complete")

    sentiment_df = sentiment_step(reviews_df)
    st.write("✅ Step 2 complete")

    entity_df = entity_extraction_step(sentiment_df)
    st.write("✅ Step 3 complete")
