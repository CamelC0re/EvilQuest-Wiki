import os
import sys
import requests

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
except ImportError:
    pass

# 1. Capture Environment Variables from GitHub Secrets
WIKI_API_URL = os.environ.get("WIKI_API_URL")
BOT_USERNAME = os.environ.get("WIKI_BOT_USERNAME")
BOT_PASSWORD = os.environ.get("WIKI_BOT_PASSWORD")

if not all([WIKI_API_URL, BOT_USERNAME, BOT_PASSWORD]):
    print("❌ Critical configuration error: Missing required execution secrets.")
    sys.exit(1)

# 2. Define the Mapping Matrix matching local repository paths to active wiki pages
ASSET_SYNC_MATRIX = [
    {"file": "modules/ItemData.lua", "title": "Module:ItemData", "model": "Scribunto"},
    {"file": "modules/NpcData.lua", "title": "Module:NPCData", "model": "Scribunto"},
    {"file": "data/ItemData.json", "title": "Module:ItemData/json", "model": "json"},
    {"file": "data/NpcData.json", "title": "Module:NPCData/json", "model": "json"},
    {"file": "styles/Common.css", "title": "MediaWiki:Common.css", "model": "css"}
]

# Dynamically discover templates from subdirectories
for root, _, files in os.walk("templates"):
    # Skip templates in the root directory (so we ignore the old legacy files that haven't been deleted yet)
    if os.path.normpath(root) == "templates":
        continue
    
    for file in files:
        if file.endswith(".wikitext"):
            local_path = os.path.join(root, file).replace("\\", "/")
            base_name = file[:-9] # Remove .wikitext
            
            # Handle edge cases
            if base_name == "Wiki_Discord":
                title_name = "Wiki/Discord"
            else:
                title_name = base_name.replace("_", " ")
            
            wiki_title = f"Template:{title_name}"
            ASSET_SYNC_MATRIX.append({
                "file": local_path,
                "title": wiki_title,
                "model": "wikitext"
            })

def execute_wiki_sync():
    session = requests.Session()
    session.headers.update({"User-Agent": "EvilQuestWikiSyncBot/1.0 (CI/CD Deployment)"})

    print("🔑 Commencing secure authorization sequence...")
    
    # Sequence A: Retrieve unique login token payload
    token_req = session.get(WIKI_API_URL, params={
        "action": "query", "meta": "tokens", "type": "login", "format": "json"
    })
    token_req.raise_for_status()
    login_token = token_req.json()["query"]["tokens"]["logintoken"]

    # Sequence B: Log in using Bot Password credentials
    login_auth = session.post(WIKI_API_URL, data={
        "action": "login", "lgname": BOT_USERNAME, "lgpassword": BOT_PASSWORD, "lgtoken": login_token, "format": "json"
    })
    if login_auth.json()["login"]["result"] != "Success":
        print(f"❌ Authentication denied: {login_auth.json()['login'].get('reason', 'Unknown failure')}")
        sys.exit(1)

    # Sequence C: Acquire the mandatory runtime CSRF token for page modification
    csrf_req = session.get(WIKI_API_URL, params={
        "action": "query", "meta": "tokens", "type": "csrf", "format": "json"
    })
    csrf_token = csrf_req.json()["query"]["tokens"]["csrftoken"]
    print("✅ Session established. Processing files...")

    # 3. Iterate through mapping matrix and push changes
    for asset in ASSET_SYNC_MATRIX:
        local_path = asset["file"]
        wiki_title = asset["title"]
        content_model = asset["model"]

        if not os.path.exists(local_path):
            print(f"⚠️ Skipping tracking target: Local file '{local_path}' was not found.")
            continue

        with open(local_path, "r", encoding="utf-8") as file_stream:
            raw_content = file_stream.read()

        print(f"📤 Syncing '{local_path}' ──> [[{wiki_title}]]...")
        
        edit_payload = {
            "action": "edit",
            "title": wiki_title,
            "text": raw_content,
            "token": csrf_token,
            "bot": True,
            "summary": "🔄 Automated Git-to-Wiki synchronization update [CI Pipeline]",
            "format": "json"
        }

        # Force structural assignment if updating raw data structures
        if content_model == "json":
            edit_payload["contentmodel"] = "json"

        response = session.post(WIKI_API_URL, data=edit_payload)
        response_data = response.json()

        if "error" in response_data:
            print(f"❌ Sync failed for [[{wiki_title}]]: {response_data['error'].get('info')}")
        else:
            print(f"✨ Successfully deployed [[{wiki_title}]]! Revision ID: {response_data['edit'].get('newrevid')}")

if __name__ == "__main__":
    execute_wiki_sync()