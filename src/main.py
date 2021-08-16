from multiprocessing import Queue
import threading
from pprint import pprint

import logging

from scapy.all import *
import signal
import protocol
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
        
def unknownMsgIdProcessing(msg:Msg):
    logging.error(f"ID: {msg.id}\nCount: {msg.count}\nData: {msg.data}")

def addMessageToQueue(msg: Msg):
    if msg.id == 0:
        return
    # if msg.id != 6000:
    #     return
    try:
        msgJson = msg.json()
        mainQueue.put(msgJson)
        # print(msg.json())
        # print(msg.id)
        #pprint(msg.json()["__type__"])
    except KeyError as e:
        print(f"Key Error message treatement maybe this key doesn't exits : {e}\nQueue has currently {mainQueue.qsize()} elements")
        print(f"Key error {buf2}")
        unknownMsgIdProcessing(msg)
    except IndexError as e:
        print(f"Index Error message treatement maybe this key doesn't exits : {e}\nQueue has currently {mainQueue.qsize()} elements")
        print(msg.id)
    #print(msg.data)
    #print(Msg.from_json(msg.json()).data)

def stop(*args):
    print("stop")
    stopSignal.set()

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, filename='SnifferDofus.log', format='%(asctime)s %(levelname)s:%(message)s')
    stopSignal = threading.Event()
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    mainQueue = Queue(10000)
    msgProcessingWorker = msgProcessing.MsgProcessingThread(mainQueue)
    msgProcessingWorker.setDaemon(True)
    msgProcessingWorker.start()
    capture = sniff(prn=on_receive,filter="tcp port 5555",stop_filter=lambda p: stopSignal.is_set())
    print(mainQueue.qsize())
    msgProcessingWorker.stop()
    print("Stop capturing")
    print("Stopping program")