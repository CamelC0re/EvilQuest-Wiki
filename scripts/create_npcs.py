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
JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "NpcData.json")


def get_wiki_session():
    session = requests.Session()
    r1 = session.get(url=WIKI_API_URL, params={"action": "query", "meta": "tokens", "type": "login", "format": "json"})
    login_token = r1.json()["query"]["tokens"]["logintoken"]

    r2 = session.post(WIKI_API_URL, data={
        "action": "login", "lgname": BOT_USERNAME, "lgpassword": BOT_PASSWORD, "lgtoken": login_token, "format": "json"
    })
    if r2.json()["login"]["result"] != "Success":
        raise Exception("Authentication failed.")

    r3 = session.get(url=WIKI_API_URL, params={"action": "query", "meta": "tokens", "type": "csrf", "format": "json"})
    return session, r3.json()["query"]["tokens"]["csrftoken"]


def deploy_npc_pipeline():
    session, csrf_token = get_wiki_session()

    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        raw_json_string = f.read()
        npcs_data = json.loads(raw_json_string)

    print("Deploying central NPC data array matrix...")
    session.post(WIKI_API_URL, data={
        "action": "edit", "title": "Module:NPCData/json", "text": raw_json_string,
        "summary": "Pushed global NPC asset arrays.", "contentmodel": "json", "token": csrf_token, "format": "json"
    })

    # Pre-scan name frequencies to determine which NPCs need disambiguation
    name_counts = {}
    for npc in npcs_data:
        name = npc.get("name")
        if name:
            name_counts[name] = name_counts.get(name, 0) + 1

    # Generate exact unique page titles
    unique_titles = set()
    for npc in npcs_data:
        name = npc.get("name")
        if not name:
            continue
            
        # Append (Lvl X) only if there are duplicate names in the database
        if name_counts[name] > 1:
            lvl = npc.get("combatLevel", "??")
            title = f"{name} (Lvl {lvl})"
        else:
            title = name
            
        unique_titles.add(title)

    print(f"Minting {len(unique_titles)} disambiguated NPC articles...")
    created, skipped = 0, 0

    for title in unique_titles:
        params = {
            "action": "edit", "title": title, "text": "{{Infobox NPC}}",
            "summary": "Provisioned disambiguated NPC placeholder.",
            "token": csrf_token, "format": "json", "createonly": 1,
        }

        res = session.post(WIKI_API_URL, data=params).json()

        if "edit" in res and res["edit"]["result"] == "Success":
            print(f"[CREATED] {title}")
            created += 1
        elif "error" in res and res["error"]["code"] == "articleexists":
            print(f"[SKIPPED] {title} (Page exists)")
            skipped += 1

        time.sleep(0.1)

    print(f"\n[Finished] Created: {created} | Skipped: {skipped}")

if __name__ == "__main__":
    deploy_npc_pipeline()