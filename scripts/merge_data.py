import os
import json

def merge_entities(entity_name, data_path, staging_path):
    print(f"\n--- Merging {entity_name} ---")
    if not os.path.exists(staging_path):
        print(f"Staging file not found: {staging_path} (Skipping...)")
        return

    # Load your historical data and the new update data
    old_entities = {}
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding="utf-8") as f:
            old_entities = {item['id']: item for item in json.load(f)}
        
    with open(staging_path, 'r', encoding="utf-8") as f:
        new_entities = {item['id']: item for item in json.load(f)}

    merged_entities = []
    
    # Process all old items
    for entity_id, old_data in old_entities.items():
        if entity_id in new_entities:
            new_data = new_entities[entity_id]
            
            # DETECT RENAME: If the names don't match, save the old name
            if old_data.get('name') and new_data.get('name') and old_data['name'] != new_data['name']:
                print(f"Rename detected (ID {entity_id}): '{old_data['name']}' is now '{new_data['name']}'")
                new_data['legacyName'] = old_data['name']
            
            # Merge! new_data overwrites old_data, missing fields are preserved.
            merged_data = {**old_data, **new_data}
            merged_entities.append(merged_data)
            
            del new_entities[entity_id]
        else:
            # Item was removed from the game! Flag it as discontinued.
            old_data['discontinued'] = True
            merged_entities.append(old_data)
            print(f"Flagged as discontinued: {old_data.get('name', 'Unknown')} (ID: {entity_id})")

    # Any items left in new_items are brand new to the game
    for entity_id, new_data in new_entities.items():
        merged_entities.append(new_data)
        print(f"Added new {entity_name[:-1].lower()}: {new_data.get('name', 'Unknown')} (ID: {entity_id})")

    # Output the final JSON
    with open(data_path, 'w', encoding="utf-8") as f:
        json.dump(merged_entities, f, indent=2)
    print(f"Successfully updated {os.path.basename(data_path)}")

def merge_game_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Merge Items
    merge_entities(
        "Items",
        os.path.join(base_dir, "data", "ItemData.json"),
        os.path.join(base_dir, "staging", "items.json")
    )
    
    # Merge NPCs
    merge_entities(
        "NPCs",
        os.path.join(base_dir, "data", "NpcData.json"),
        os.path.join(base_dir, "staging", "npcs.json")
    )
    
    # Merge Rare Drop Tables
    merge_entities(
        "Rare Drop Tables",
        os.path.join(base_dir, "data", "RareDropData.json"),
        os.path.join(base_dir, "staging", "rare-drop-tables.json")
    )

if __name__ == "__main__":
    merge_game_data()
