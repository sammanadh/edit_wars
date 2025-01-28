import pandas as pd
from src.constants import urls
import requests
from datetime import datetime

def fetch_all_revisions(article_name):
    try:
        url = f"https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": article_name,
            "rvprop": "timestamp|user|ids",
            "rvlimit": "max"
        }

        # Pagination loop to collect all revisions
        all_revisions = []
        while True:
            response = requests.get(url, params = params)
            response.raise_for_status() 
            data = response.json()

            page = list(data["query"]["pages"].values())[0]
            if "revisions" not in page:
                break

            all_revisions.extend(page["revisions"])

            # Handle pagination
            if "continue" in data:
                params["rvcontinue"] = data["continue"]["rvcontinue"]
            else:
                break 
        
        revisions_df = pd.DataFrame(all_revisions)
        return revisions_df
    
    except Exception as e:
        print(f"Error fetching revisions for {article_name}: {e}")
        return None

def get_article_stats(article_name):
    # revisions
    revisions_df = fetch_all_revisions(article_name)
    revisions_df["timestamp"] = pd.to_datetime(revisions_df["timestamp"])

    total_edits = revisions_df.shape[0]
    contributors = revisions_df["user"].nunique()
    last_edit = revisions_df["timestamp"].max().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "Article Name": article_name,
        "Total Edits": total_edits,
        "Number of Contributors": contributors,
        "Last Edit Timestamp": last_edit,
    }

def format_timestamp_readable(iso_timestamp):
    # Parse the ISO timestamp
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    # Format it into a user-friendly format
    return dt.strftime("%B %d, %Y, %I:%M %p")