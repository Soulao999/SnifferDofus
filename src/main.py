from multiprocessing import Queue
import threading
from pprint import pprint

import sounds
import logging

from scapy.all import *
import signal
import msgProcessing
from binrw import *
from msg import Msg

buf1 = Buffer()
buf2 = Buffer()

def get_local_ip():
    """from https://stackoverflow.com/a/28950776/5133167
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP
LOCAL_IP = get_local_ip()

def display(pkt):
    print(pkt["TCP"])
    pkt.getlayer(Raw).load

def from_client(pa):
    dst = pa.getlayer(IP).dst
    src = pa.getlayer(IP).src
    if src == LOCAL_IP:
        return True
    elif dst == LOCAL_IP:
        return False
    assert False, "Packet origin unknown"

def on_receive(pa):
    direction = from_client(pa)
    if direction == True: # On utilise seulement les messages en provenance du serveur
        return
    buf = buf1 if direction else buf2
    buf += bytes(pa[TCP].payload)#[40:]
    while (msg:=Msg.fromRaw(buf, direction)):
        addMessageToQueue(msg)
    #print(buf)
        
def addMessageToQueue(msg: Msg):
    logger.info(f"Message received with ID:{msg.id}")
    logger.debug(f"Message content ID: {msg.id} Count: {msg.count} Data: {msg.data}")
    if msg.id == 0:
        return
    # if msg.id != 6000:
    #     return
    try:
        msgJson = msg.json()
        mainQueue.put(msgJson)
    except KeyError as e:
        logger.error(f"Key Error message treatement maybe this key doesn't exits : {e}\nQueue has currently {mainQueue.qsize()} elements\n The buffer contains the following : {buf2}")
        logger.error(f"ID: {msg.id}\nCount: {msg.count}\nData: {msg.data}")
    except IndexError as e:
        logger.error(f"Index Error message treatement maybe this key doesn't exits : {e}\nQueue has currently {mainQueue.qsize()} elements\n MsgID : {msg.id}")

def stop(*args):
    stopSignal.set()
    logger.info("Stop signal form user received")

def init_logger() -> None:
    logging.basicConfig(filename='debug.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')
    logging.info("Logger has been initialized")

if __name__ == "__main__":
    print("Start")
    init_logger()
    logger = logging.getLogger("main")
    stopSignal = threading.Event()
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    mainQueue = Queue(1000)
    logger.info("Initializing msgProcessing Thread")
    msgProcessingWorker = msgProcessing.MsgProcessingThread(mainQueue)
    msgProcessingWorker.setDaemon(True)
    msgProcessingWorker.start()
    logger.info("msgProcessing Thread has started")
    logger.info("Start sniffing")
    capture = sniff(prn=on_receive,filter="tcp port 5555",stop_filter=lambda p: stopSignal.is_set())
    logger.info("Stop sniffing")
    logger.info("Stopping msgProcessing")
    msgProcessingWorker.stop()
    logger.debug(f"Queuesize before program stops: {mainQueue.qsize()}")
    logger.info("End of program")
    print("Stop")