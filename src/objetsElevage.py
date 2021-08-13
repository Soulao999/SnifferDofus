import databaseManager
import json
import xlsxwriter
import datetime

class ObjetElevage():
    def __init__(self,name,GID,price1,price10,price100,efficiency,durability) -> None:
        self.name = name
        self.GID = GID
        self.price1 = price1
        self.price10 = price10
        self.price100 = price100
        self.efficiency = efficiency
        self.durability = durability

    def __repr__(self) -> str:
        return f"{self.name}"

    def calculateRatio(self) -> float:
        prices = []
        if self.price1 != 0:
            prices.append(self.price1)
        if self.price10 != 0:
            prices.append(self.price10/10)
        if self.price100 != 0:
            prices.append(self.price100/100)
        if len(prices) == 0:
            return 0
        price = min(prices)
        return self.efficiency*self.durability/price

def initXlsxSheet(sheet: xlsxwriter.worksheet.Worksheet) -> None:
    sheet.write(0,0,"Name")
    sheet.write(0,1,"GID")
    sheet.write(0,2,"Eff")
    sheet.write(0,3,"Dur")
    sheet.write(0,4,"Price1")
    sheet.write(0,5,"Price10")
    sheet.write(0,6,"Price100")
    sheet.write(0,7,"Ratio")

def addObjInXlsxSheet(sheet : xlsxwriter.worksheet.Worksheet,row: int,obj: ObjetElevage) -> None:
    sheet.write(row,0,obj.name)
    sheet.write(row,1,obj.GID)
    sheet.write(row,2,obj.efficiency)
    sheet.write(row,3,obj.durability)
    sheet.write(row,4,obj.price1)
    sheet.write(row,5,obj.price10)
    sheet.write(row,6,obj.price100)
    sheet.write(row,7,obj.calculateRatio())

if __name__ == "__main__":
    objetsElevageId = 93
    usageActionId = 812
    efficiencyActionId = 1007
    dbManager = databaseManager.DatabaseManager()
    a = "SELECT GID,max(date) as date FROM Prices group by GID"
    query = f"SELECT maxPrices.GID,name,objectType,price1,price10,price100,maxPrices.date,effects FROM (SELECT maxDate.GID,objectType,price1,price10,price100,maxDate.date,effects FROM {databaseManager.PRICES_TABLE_NAME},({a}) maxDate WHERE {databaseManager.PRICES_TABLE_NAME}.date=maxDate.date AND {databaseManager.PRICES_TABLE_NAME}.GID=maxDate.GID AND objectType={objetsElevageId}) as maxPrices JOIN  {databaseManager.ITEMS_TABLE_NAME} ON maxPrices.GID={databaseManager.ITEMS_TABLE_NAME}.GID"
    # La query recupère les données les plus récente de tous les items déjà enregistrés
    dbManager.sendQuery(query)
    result = dbManager.fetch_all()
    dbManager.stop()
    # Création des objets contenant les infos
    Objects = []
    for object in result:
        effects = object[-1].replace("'",'"')
        effects = json.loads(effects)
        for elt in effects:
            if elt["actionId"] == usageActionId:
                dur = elt["diceConst"]
            elif elt["actionId"] == efficiencyActionId:
                eff = elt["value"]
        Objects.append(ObjetElevage(object[1],object[0],object[3],object[4],object[5],eff,dur))


    # Création de l'excel
    workbook = xlsxwriter.Workbook(f'Elevage_{str(datetime.datetime.now())[:-16]}_{datetime.datetime.now().timestamp()}.xlsx')
    rowDict = {"Mangeoire":1,"Foudroyeur":1,"Dragofesse":1,"Caresseur":1,"Abreuvoir":1,"Baffeur":1}
    sheetDict = {}
    for typ in rowDict.keys():
        sheetDict[typ] = workbook.add_worksheet(typ)
        initXlsxSheet(sheetDict[typ])
    count = len(Objects)
    for obj in Objects:
        for typ,row in rowDict.items():
            if typ in obj.name:
                addObjInXlsxSheet(sheetDict[typ],row,obj)
                rowDict[typ] += 1
                count -= 1
                break
    if count > 0:
        print(f"Non processed objects : {count}")
    workbook.close()