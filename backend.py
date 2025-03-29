from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_PATH = "donationdata.csv"

# Update the get_donations endpoint


@app.get("/donations")
def get_donations():
    if not os.path.exists(CSV_PATH):
        return {"error": "Donations file not found"}, 404

    try:
        df = pd.read_csv(CSV_PATH)
        df['verified'] = df['verified'].astype(bool)

        # Convert locations string to list
        df['locations'] = df['locations'].fillna('').apply(
            lambda x: [loc.strip() for loc in x.split(',') if loc.strip()]
        )

        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}, 500


@app.get("/crisis-data")
def get_crisis_data():
    return {
        "deaths": 1644,
        "injured": 3408,
        "missing": 139,
        "last_updated": "2024-03-30T20:00:00+06:30",
        "source": "Myanmar Now"
    }
