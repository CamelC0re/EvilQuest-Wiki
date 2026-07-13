import os
import json
import requests

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
except ImportError:
    pass

WIKI_API_URL = os.environ.get("WIKI_API_URL")
BOT_USERNAME = os.environ.get("WIKI_BOT_USERNAME")
BOT_PASSWORD = os.environ.get("WIKI_BOT_PASSWORD")


def get_wiki_session():
    session = requests.Session()

    # Get Login Token
    r1 = session.get(
        url=WIKI_API_URL, params={"action": "query", "meta": "tokens", "type": "login", "format": "json"}
    )
    login_token = r1.json()["query"]["tokens"]["logintoken"]

    # Authenticate Bot Credentials
    r2 = session.post(
        WIKI_API_URL,
        data={
            "action": "login",
            "lgname": BOT_USERNAME,
            "lgpassword": BOT_PASSWORD,
            "lgtoken": login_token,
            "format": "json",
        },
    )
    if r2.json()["login"]["result"] != "Success":
        raise Exception("Authentication failed.")

    # Get CSRF Token
    r3 = session.get(
        url=WIKI_API_URL, params={"action": "query", "meta": "tokens", "type": "csrf", "format": "json"}
    )
    return session, r3.json()["query"]["tokens"]["csrftoken"]


def sync_json_data():
    session, csrf_token = get_wiki_session()

    # Load your updated file string directly
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ItemData.json")
    with open(data_path, "r", encoding="utf-8") as f:
        json_payload = f.read()

    # Post update payload straight to the JSON subpage
    params = {
        "action": "edit",
        "title": "Module:ItemData/json",
        "text": json_payload,
        "summary": "Automated pipeline system: Synced global item dataset code profiles.",
        "contentmodel": "json",
        "token": csrf_token,
        "format": "json",
    }

    print(f"Submitting edit to {params['title']}...")
    print(f"Payload length being sent: {len(json_payload)} characters.")
    print(f"First 100 chars of payload: {repr(json_payload[:100])}")
    
    response = session.post(WIKI_API_URL, data=params)
    print("Pipeline sync status response:", response.json())


if __name__ == "__main__":
    sync_json_data()