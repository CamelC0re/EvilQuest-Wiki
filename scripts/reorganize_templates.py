import os
import shutil

base = r"c:\Users\Onizuka\Projects\EvilQuest\Wiki\Repo\templates"
dirs = ["infoboxes", "items", "drops", "shops", "smithing", "utility"]

for d in dirs:
    os.makedirs(os.path.join(base, d), exist_ok=True)

moves = [
    ("Infobox_Item.wikitext", "infoboxes"),
    ("Infobox_Npc.wikitext", "infoboxes"),
    ("Item.wikitext", "items"),
    ("ItemDescription.wikitext", "items"),
    ("ItemSources.wikitext", "items")
]

for src, dest_dir in moves:
    src_path = os.path.join(base, src)
    dest_path = os.path.join(base, dest_dir, src)
    if os.path.exists(src_path):
        shutil.move(src_path, dest_path)
        print(f"Moved {src} to {dest_dir}/")

files = [
    r"drops\ChestLootData.wikitext",
    r"drops\ChestLootItem.wikitext",
    r"drops\ItemChests.wikitext",
    r"drops\ItemDrops.wikitext",
    r"drops\MobDropInventoryData.wikitext",
    r"drops\MobDropItem.wikitext",
    r"shops\ItemShops.wikitext",
    r"shops\ItemStalls.wikitext",
    r"shops\ShopInventoryData.wikitext",
    r"shops\ShopInventoryTest.wikitext",
    r"shops\ShopItem.wikitext",
    r"shops\ShopItemDataTest.wikitext",
    r"shops\ShopItemTest.wikitext",
    r"shops\StallInventoryData.wikitext",
    r"shops\StallItem.wikitext",
    r"smithing\ItemSmithing.wikitext",
    r"smithing\SmithingData.wikitext",
    r"smithing\SmithingRecipe.wikitext",
    r"utility\NoHeaderLines.wikitext",
    r"utility\Popular_pages.wikitext",
    r"utility\Wiki_Discord.wikitext"
]

for f in files:
    file_path = os.path.join(base, f)
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as fp:
            fp.write("<!-- Placeholder -->\n")
        print(f"Created {f}")

print("Directory restructuring completed successfully!")
