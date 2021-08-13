import threading
import databaseManager
import datetime

class MsgProcessingThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.kill_received = False
        self.lastGID = 0
        
    def run(self):
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
                    if self.lastGID != GID:
                        query = f'INSERT INTO {databaseManager.PRICES_TABLE_NAME} (UID, GID, objectType, price1, price10, price100, effects,date) VALUES ({UID},{GID},{objectType},{price1},{price10},{price100},"{effects}","{date}");'
                        self.dbManager.sendQuery(query)
                        self.lastGID = GID
                else:
                    break
        else:
            pass