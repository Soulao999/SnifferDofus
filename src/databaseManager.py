import sqlite3
from pathlib import Path

DB_NAME = Path("data/prices.db")
PRICES_TABLE_NAME = "Prices"
ITEMS_TABLE_NAME = "GIDToName"
ITEMS_TYPES_TABLE_NAME = "TypeToName"
EFFECTS_TABLE_NAME = "EffectToName"

class DatabaseManager():

    def __init__(self):
        self.con = sqlite3.connect(DB_NAME)
        self.cur = self.con.cursor()

    def sendQuery(self,query: str):
        self.cur.execute(query)
        self.con.commit()

    def fetch_all(self):
        return self.cur.fetchall()

    def stop(self):
        self.con.close()

    def getItemNameFromGID(self,GID: int) -> str:
        query = f"SELECT name FROM {ITEMS_TABLE_NAME} WHERE GID={GID}"
        self.sendQuery(query)
        return self.fetch_all()[0][0]
    
    def getItemTypeNameFromID(self,ID: int) -> str:
        query = f"SELECT name FROM {ITEMS_TYPES_TABLE_NAME} WHERE ID={ID}"
        self.sendQuery(query)
        return self.fetch_all()[0][0]

    def getEffectNameFromID(self,ID: int) -> str:
        query = f"SELECT name FROM {EFFECTS_TABLE_NAME} WHERE ID={ID}"
        self.sendQuery(query)
        return self.fetch_all()[0][0]

    def getAllRecordsFromGID(self, GID: int) -> "list[tuple]":
        query = f"SELECT * FROM {PRICES_TABLE_NAME} WHERE GID={GID}"
        self.sendQuery(query)
        return self.fetch_all()

if __name__ == "__main__":
    db = DatabaseManager()
    result = db.getAllRecordsFromGID(15452)