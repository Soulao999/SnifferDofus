import databaseManager
import json
from pathlib import Path

ITEMS_JSON_PATH = Path("data/Items.json")
ITEMS_TYPES_JSON_PATH = Path("data/ItemTypes.json")
TEXT_JSON_PATH = Path("data/i18n_fr.json")
EFFECTS_JSON_PATH = Path("data/Effects.json")

if __name__ == "__main__":
    with open(ITEMS_JSON_PATH) as jsonFile:
        itemJson = json.load(jsonFile)
        jsonFile.close()

    with open(TEXT_JSON_PATH,encoding='utf8') as jsonFile:
        textJson = json.load(jsonFile)
        jsonFile.close()
    textJson = textJson["texts"]
    #GUIToName = {item[id]:textJson[str(item["nameId"])] for item in itemJson}
    GIDToName = {}
    for item in itemJson:
        try:
            GIDToName[item["id"]] = textJson[str(item["nameId"])]
        except KeyError as e:
            print(e)
    

    # with open("output.txt", 'w',encoding='utf8') as f:
    #     for key,value in GIDToName.items():
    #         f.write(f"{key} : {value}\n")

    dbManager = databaseManager.DatabaseManager()
    query = f"INSERT INTO {databaseManager.ITEMS_TABLE_NAME} (GID,name) VALUES "
    for key,value in GIDToName.items():
        value = value.replace("'","''")
        query += f"({key},'{value}'),"
    query = query[:len(query)-1]
    query += ';'
    dbManager.sendQuery(query)
    dbManager.stop()
