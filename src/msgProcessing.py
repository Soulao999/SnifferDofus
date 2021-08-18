import threading
import databaseManager
import datetime
import objetsElevage
import sounds
import fmManager
import logging
class MsgProcessingThread(threading.Thread):
    def __init__(self, queue):
        self.logger = logging.getLogger("msgProcessing")
        self.logger.info("Initializing message processing")
        threading.Thread.__init__(self)
        self.queue = queue
        self.kill_received = False
        self.lastGID = 0

    def run(self):
        self.FmManager = fmManager.FmManager()
        self.dbManager = databaseManager.DatabaseManager()
        while not self.kill_received:
            element = self.queue.get()
            self.logger.info("New message read in queue")
            self.logger.debug(f"New element in message read : {element}")
            self.messageProcessing(element)
            self.queue.task_done()
            self.logger.debug("End msg processing")
        self.dbManager.stop()

    def stop(self):
        self.kill_received = True

    def messageProcessing(self,element: dict):
        # TODO Transformer en match case dans python 3.10
        if element['__type__'] == 'ExchangeTypesItemsExchangerDescriptionForUserMessage':
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
                    self.logger.info(f"New item prices entered into db")

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
                            self.logger.info(f"New objet elevage price entered into db {databaseManager.OBJETS_ELEVAGE_TABLE_NAME}")
                                        
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
        elif element['__type__'] == 'TextInformationMessagee':
            #TODO Change 65 to Variable
            if element['msgId'] == 65:
                sounds.ding()
                params = element['parameters']
                date = datetime.datetime.now()
                if params[1] != params[2]:
                    self.logger.warning(f"ERREUR LES PARAMS 1 ET 2 SONT DIFFERENTS\n_________________________________________\n____________________________________\n{element}\n_____________________________________________\n_______________________________________\n")
                query = f'INSERT INTO {databaseManager.SOLD_ITEMS_TABLE_NAME} (GID,Price,Quantity,date) VALUES ({params[1]},{params[0]},{params[3]},"{date}");'
                self.dbManager.sendQuery(query)
        elif element['__type__'] == 'ExchangeOfflineSoldItemsMessage':
            self.logger.debug("ExchangeOfflineSoldItemsMessage")
            for item in element['bidHouseItems']:
                GID=item['objectGID']
                qty = item['quantity']
                price = item['price']
                date = datetime.datetime.fromtimestamp(item['date'])
                query = f'INSERT INTO {databaseManager.SOLD_ITEMS_TABLE_NAME} (GID,Price,Quantity,date) VALUES ({GID},{price},{qty},"{date}");'
                self.dbManager.sendQuery(query)
        elif element['__type__'] == 'ObjectAveragePricesMessage':
            self.logger.info("ObjectAveragePrices")
        elif element['__type__'] == 'ObjectAveragePricesErrorMessage':
            self.logger.error("ObjectAveragePrices error")
        else:
            pass