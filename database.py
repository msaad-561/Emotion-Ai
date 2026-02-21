"""
database.py — MongoDB Atlas connection module
Handles all DB operations for the Emotion Detection System.
"""
from pymongo import MongoClient
from datetime import datetime
import os

# ────────────────────────────────────────────────
#  CONNECTION STRING
#  Store sensitive credentials in env var in production.
#  For dev, we keep it here.
# ────────────────────────────────────────────────
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://emotionalai:zAyoD1r8ycModQEw@cluster0.ofceuzz.mongodb.net/?appName=Cluster0"
)

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Ping to confirm connection
    client.admin.command("ping")
    db = client["emotion_ai"]
    emotions_col = db["emotions"]
    print("✅ MongoDB Atlas connected successfully!")
except Exception as e:
    print(f"⚠️  MongoDB connection failed: {e}")
    print("   App will run using in-memory storage as fallback.")
    client = None
    db = None
    emotions_col = None


# ────────────────────────────────────────────────
#  CRUD HELPERS
# ────────────────────────────────────────────────

def save_emotion(username: str, emotion: str):
    """Insert one emotion detection record for a user."""
    if emotions_col is None:
        return False
    record = {
        "username":  username,
        "emotion":   emotion,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_at": datetime.utcnow()
    }
    emotions_col.insert_one(record)
    return True


def get_user_history(username: str, limit: int = 100) -> list:
    """Return recent emotion records for a user, newest first."""
    if emotions_col is None:
        return []
    records = list(
        emotions_col.find(
            {"username": username},
            {"_id": 0, "username": 0, "created_at": 0}  # exclude internal fields
        ).sort("created_at", -1).limit(limit)
    )
    return records


def get_user_counts(username: str) -> dict:
    """Return total detections per emotion for a user."""
    base = {"Happy": 0, "Sad": 0, "Angry": 0, "Relaxed": 0, "Stressed": 0}
    if emotions_col is None:
        return base

    pipeline = [
        {"$match": {"username": username}},
        {"$group": {"_id": "$emotion", "count": {"$sum": 1}}}
    ]
    for doc in emotions_col.aggregate(pipeline):
        if doc["_id"] in base:
            base[doc["_id"]] = doc["count"]
    return base


def get_mood_scores(username: str, limit: int = 20) -> list:
    """Return mood scores (0-100) for the last N detections."""
    score_map = {
        "Happy": 100, "Relaxed": 80, "Neutral": 60,
        "Stressed": 40, "Sad": 20, "Angry": 0
    }
    history = get_user_history(username, limit)
    # Reverse to chronological order (oldest → newest)
    history = list(reversed(history))
    return [score_map.get(r["emotion"], 50) for r in history]
