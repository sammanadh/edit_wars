import pandas as pd
from src.constants import urls
import requests
from datetime import datetime

API_URL = "https://en.wikipedia.org/w/api.php"

def fetch_contributor_data(username):
    try:
        url = API_URL
        params = {
            "action": "query",
            "list": "usercontribs",
            "ucuser": username,
            "uclimit": "max",
            "ucprop": "title|timestamp|ids",
            "format": "json",
        }

        contribs = []

        while True:
            response = requests.get(url, params=params).json()
            contribs = response["query"]["usercontribs"]
            if not contribs:
                break
            contribs.extend(contribs)

            if "continue" in response:
                params["uccontinue"] = response["continue"]["uccontinue"]
            else:
                break

        if not contribs:
            return None

        df = pd.DataFrame(contribs)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    except Exception as e:
        print(f"Error fetching contributor data: {e}")
        return None

def fetch_all_revisions(article_name):
    try:
        url = API_URL
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": article_name,
            "rvprop": "timestamp|user|ids",
            "rvlimit": "max"
        }

        all_revisions = []
        while True:
            response = requests.get(url, params = params)
            response.raise_for_status() 
            data = response.json()

            page = list(data["query"]["pages"].values())[0]
            if "revisions" not in page:
                break

            all_revisions.extend(page["revisions"])

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
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return dt.strftime("%B %d, %Y, %I:%M %p")