import threading
import databaseManager
import datetime
import objetsElevage
import sounds
import fmManager
class MsgProcessingThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.kill_received = False
        self.lastGID = 0

    def run(self):
        self.FmManager = fmManager.FmManager()
        self.dbManager = databaseManager.DatabaseManager()
        while not self.kill_received:
            element = self.queue.get()
            self.messageProcessing(element)
            #print("-------------------------------------")
            #print(element)
            self.queue.task_done()
        self.dbManager.stop()

    def stop(self):
        self.kill_received = True

    def messageProcessing(self,element: dict):
        #sounds.ding()
        #print(f"{datetime.datetime.now()} : {element}")
        # TODO Transformer en match case dans python 3.10
        if element['__type__'] == 'ExchangeTypesItemsExchangerDescriptionForUserMessage':
            #print(f"{datetime.datetime.now()} : {element}")
            print(f"{datetime.datetime.now()} : {self.queue.qsize()}")
            objectType = element['objectType']
            itemTypeDescriptions = element['itemTypeDescriptions']
            for itemTypeDescription in itemTypeDescriptions:
                if itemTypeDescription['__type__'] == 'BidExchangerObjectInfo':
                    UID = itemTypeDescription['objectUID']
                    GID = itemTypeDescription['objectGID']
                    effects = str(itemTypeDescription['effects'])
                    prices = itemTypeDescription['prices']
                    price1 = prices[0]
                    price10 = prices[1]
                    price100 = prices[2]
                    date = datetime.datetime.now()
                    #Evite plusiseurs fois le même object à la suite mais pose problème quand plusieurs caractéristiques d'objet en dehors du for peut être ce système le self.lastGID=GID
                    # if self.lastGID != GID:
                    query = f'INSERT INTO {databaseManager.PRICES_TABLE_NAME} (UID, GID, objectType, price1, price10, price100, effects,date) VALUES ({UID},{GID},{objectType},{price1},{price10},{price100},"{effects}","{date}");'
                    self.dbManager.sendQuery(query)
                    #self.lastGID = GID

                    if objectType == objetsElevage.objetsElevageId:
                                # Dans le cas d'un object d'élevage on sauvegarde en plus dans une table spéciale si celui-ci est au max en durabilité
                                # TODO dans une fonction séparée
                        for effect in itemTypeDescription['effects']:
                            if effect['actionId'] == objetsElevage.usageActionId:
                                toSave = ((effect['diceNum'] == effect['diceConst']) and (effect['diceSide'] == effect['diceConst']))
                                dur = effect['diceConst']
                            elif effect['actionId'] == objetsElevage.efficiencyActionId:
                                eff = effect['value']
                        if toSave:
                            name = self.dbManager.getItemNameFromGID(GID)
                            query = f'INSERT INTO {databaseManager.OBJETS_ELEVAGE_TABLE_NAME} (name, GID, price1, price10, price100, efficiency,durability,date) VALUES ("{name}",{GID},{price1},{price10},{price100},{eff},{dur},"{date}");'
                            self.dbManager.sendQuery(query)
                                        
                else:
                    break
        elif element['__type__'] == 'InteractiveUsedMessage':
            if (skillId := element['skillId']) in fmManager.fmSkillIdList: # SI le skill Id est de la FM on passe en mode FM
                self.FmManager.startFM(skillId)
        elif element['__type__'] == 'ExchangeLeaveMessage':
            if self.FmManager.currentlyFM: # Si on est en mode FM et qu'on reçoi un message de fermeture on est plus dans ce mode
                self.FmManager.stopFM()
        elif element['__type__'] == 'ExchangeCraftResultMagicWithObjectDescMessage':
            self.FmManager.onFMEvent(element)
        elif element['__type__'] == 'ExchangeObjectAddedMessage':
            self.FmManager.onExchangeObjectAddedEvent(element)
        else:
            pass