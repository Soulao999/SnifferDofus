import threading
import logging

from scapy.fields import ActionField

from achatManager import AchatManager


class CommandManagerThread(threading.Thread):
    def __init__(self) -> None:
        self.logger = logging.getLogger("commandManager")
        self.logger.info("Initializing command Manager")
        self.stop = False
        super().__init__()

    def run(self):
        while not self.stop:
            command = input()
            if command == "achat":
                print("Mode Achat")
                AchatManager.start()
            elif command == "stopAchat":
                print("Sortie Mode Achat")
                AchatManager.stop()
            else:
                pass

    def stop(self) -> None:
        self.stop = True