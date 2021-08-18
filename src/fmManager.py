
import databaseManager
import item
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
        self.currentMagicPoolStatus = 0
        self.dbManager = databaseManager.DatabaseManager()

    def startFM(self,skillId: int) -> None:
        #FIXME Attention appeler même quand d'autres gens sur la map ouvrent l'interface if faut regarder le player ID
        self.currentSkillId = skillId
        self.currentlyFM = True
        self.currentSkillName = self.dbManager.getSkillNameFromGID(skillId)
        print(f"startedFM : {self.currentSkillName}")

    def stopFM(self) -> None:
        self.currentRuneGID = 0
        self.currentlyFM = False
        self.currentSkillId = 0
        self.currentMagicPoolStatus = 0
        self.currentSkillName = ""
        print(f"stoppedFM")

    def onExchangeObjectAddedEvent(self,element):
        print(element)
        if self.currentlyFM:
            print(self.dbManager.getItemNameFromGID(element['object']['objectGID']))
            if self.dbManager.getItemTypeFromGID((GID := element['object']['objectGID'])) == itemTypeRune:
                self.currentRuneGID = GID
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
                pass
            elif result == 1:
                pass
            runesUsed = self.runesUsedForEachUID[element['objectInfo']['objectUID']]
            if self.currentRuneGID in runesUsed.keys():
                runesUsed[self.currentRuneGID] += 1
            else:
                runesUsed[self.currentRuneGID] = 1
            self.currentMagicPoolStatus = element['magicPoolStatus']
            for effect in element['objectInfo']['effects']:
                self.currentItem.effects[effect['actionId']] = effect['value']
            print(self.runesUsedForEachUID)