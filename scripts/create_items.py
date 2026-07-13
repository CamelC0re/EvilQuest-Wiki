import os
import json
import requests
import time

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
except ImportError:
    pass

# --- CONFIGURATION ---
WIKI_API_URL = os.environ.get("WIKI_API_URL")
BOT_USERNAME = os.environ.get("WIKI_BOT_USERNAME")
BOT_PASSWORD = os.environ.get("WIKI_BOT_PASSWORD")
JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ItemData.json")


def get_wiki_session():
    """Establishes an authenticated session and fetches tokens."""
    session = requests.Session()

    # 1. Fetch Login Token
    r1 = session.get(
        url=WIKI_API_URL, params={"action": "query", "meta": "tokens", "type": "login", "format": "json"}
    )
    login_token = r1.json()["query"]["tokens"]["logintoken"]

    # 2. Authenticate
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
        raise Exception("Authentication failed. Check your Bot Password settings.")

    # 3. Fetch CSRF Token for Editing
    r3 = session.get(
        url=WIKI_API_URL, params={"action": "query", "meta": "tokens", "type": "csrf", "format": "json"}
    )
    csrf_token = r3.json()["query"]["tokens"]["csrftoken"]

    return session, csrf_token


def mass_create_pages():
    # Load your local items file
    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    # Connect to the Wiki API
    print("Connecting to evilquest.wiki API configuration matrix...")
    session, csrf_token = get_wiki_session()
    print(f"Authenticated successfully. Processing {len(items)} item strings...")

    created_count = 0
    skipped_count = 0

    for item in items:
        name = item.get("name")
        if not name:
            continue

        # The content body is identical for every page because Lua does the heavy lifting
        content = "{{Item}}"

        params = {
            "action": "edit",
            "title": name,
            "text": content,
            "summary": "Automated pipeline provisioning: Initialized structural item placeholder.",
            "token": csrf_token,
            "format": "json",
            "createonly": 1,  # Safe loop: throws an error if page exists instead of wiping player guides!
        }

        response = session.post(WIKI_API_URL, data=params)
        res_json = response.json()

        # Parse responses
        if "edit" in res_json and res_json["edit"]["result"] == "Success":
            print(f"[CREATED] {name}")
            created_count += 1
        elif "error" in res_json and res_json["error"]["code"] == "articleexists":
            print(f"[SKIPPED] {name} (Page already exists on wiki)")
            skipped_count += 1
        else:
            print(f"[FAILED] {name}: {res_json.get('error', res_json)}")

        # 100ms throttle to prevent choking your self-hosted Docker database engine connection pool
        time.sleep(0.1)

    print(
        f"\n[Execution Finished] Sync operations complete. Created: {created_count} | Skipped: {skipped_count}"
    )


if __name__ == "__main__":
    mass_create_pages()