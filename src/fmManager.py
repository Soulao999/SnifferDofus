
import databaseManager
import item
import sounds
import logging

#TODO Il en manque ?
fmSkillIdList = [118, 166, 168, 113, 351, 164]
itemTypeRune = 78

class FmManager():

    def __init__(self) -> None:
        logger = logging.getLogger("FmManager")
        logger.info("Initializing FM Manager")
        self.items = {}
        self.runesUsedForEachUID={} # Un dict UID -> de dict GID -> nbrUsed
        self.currentRuneGID = 0
        self.currentlyFM = False
        self.currentSkillId = 0
        self.currentSkillName = ""
        self.dbManager = databaseManager.DatabaseManager()

        # Pour chaque GID donne le prix mini suivant l'achat par 1,10 ou 100
        self.lastPrices = {}

    def startFM(self,skillId: int) -> None:
        #FIXME Attention appeler même quand d'autres gens sur la map ouvrent l'interface if faut regarder le player ID
        self.currentSkillId = skillId
        self.currentlyFM = True
        self.currentSkillName = self.dbManager.getSkillNameFromGID(skillId)
        
        # Initialisation de lastPrices
        query = f"SELECT * FROM {databaseManager.PRICES_TABLE_NAME} JOIN(SELECT GID,max(date) as maxdate FROM {databaseManager.PRICES_TABLE_NAME} group by GID) as maxTable ON {databaseManager.PRICES_TABLE_NAME}.GID = maxTable.GID WHERE date = maxdate AND objectType = {itemTypeRune}"
        self.dbManager.sendQuery(query)
        for rune in self.dbManager.fetch_all():
            self.lastPrices[rune[1]] = min(rune[3],rune[4]/10,rune[5]/100)
        print(f"startedFM : {self.currentSkillName}")

    def stopFM(self) -> None:
        self.currentRuneGID = 0
        self.currentlyFM = False
        self.currentSkillId = 0
        self.currentMagicPoolStatus = 0
        self.currentSkillName = ""
        print(f"stoppedFM")

    def onExchangeObjectAddedEvent(self,element):
        if self.currentlyFM:
            print(element)
            print(self.dbManager.getItemNameFromGID(element['object']['objectGID']))
            if self.dbManager.getItemTypeFromGID((GID := element['object']['objectGID'])) == itemTypeRune:
                self.currentRuneGID = GID
                self.currentRuneActionid = element['object']['effects'][0]['actionId']
                self.currentRuneValue = element['object']['effects'][0]['value']
            else:
                if (UID := element['object']['objectUID']) in self.items.keys():
                    self.currentItem = self.items[UID]
                else:
                    self.currentItem = item.Item(GID=element['object']['objectGID'],UID=UID,name=self.dbManager.getItemNameFromGID(element['object']['objectGID']))
                    self.runesUsedForEachUID[UID] = {}
                    for effect in element['object']['effects']:
                        self.currentItem.effects[effect['actionId']] = effect['value']
                    self.items[UID] = self.currentItem

        
    
    def onFMEvent(self,element):
        if self.currentlyFM:
            print(element)
            if (result := element['craftResult']) == 2:
                #Neutre ou succès
                pass
            elif result == 1:
                # Echec critique
                pass
            runesUsed = self.runesUsedForEachUID[element['objectInfo']['objectUID']]
            if self.currentRuneGID in runesUsed.keys():
                runesUsed[self.currentRuneGID] += 1
            else:
                runesUsed[self.currentRuneGID] = 1
            
            oldEffects = self.currentItem.effects.copy()
            self.currentItem.effects = {}
            for effect in element['objectInfo']['effects']:
                self.currentItem.effects[effect['actionId']] = effect['value']

            if (status := element['magicPoolStatus']) == 1:
                # Aucune variation du puit
                pass
            else:
                # + reliquat status 2
                # - reliquat status 3
                # Calcul du puit
                puitInit = self.currentItem.puit
                poidsRuneUsed = self.dbManager.getPoidsFromGID(self.currentRuneActionid)*self.currentRuneValue
                newPuit = puitInit - poidsRuneUsed # Dans tous les cas le poids de la rune utilisée est soustrait
                for actionId,value in oldEffects.items():
                    try:
                        delta = value - self.currentItem.effects[actionId]
                    except KeyError as e:
                        delta = value
                    if actionId == self.currentRuneActionid and delta < 0:
                        delta = 0
                    poids = self.dbManager.getPoidsFromGID(actionId)
                    #print(f"delta : {delta}; poids: {poids}; name: {self.dbManager.getEffectNameFromID(actionId)}")
                    if delta > 0:
                        # Caract moins bien
                        newPuit += poids*delta
                    elif delta < 0:
                        # Caract mieux
                        newPuit += poids*delta
                if newPuit < 0:
                    sounds.ding()
                self.currentItem.puit = newPuit


            total = 0
            # Affiche à l'utilisateur les statistiques sur la forgemagie de cet objet
            for rune,nbr in self.runesUsedForEachUID[element['objectInfo']['objectUID']].items():    
                try:
                    price = nbr*self.lastPrices[rune]
                    total += price
                    print(f"Qty: {nbr} Name: {self.dbManager.getItemNameFromGID(rune)} Estimated Price: {total}")
                except KeyError as e:
                    print(f"{nbr} {self.dbManager.getItemNameFromGID(rune)}")
            print(f"Total: {total} k\nCurrent pool: {self.currentItem.puit}")