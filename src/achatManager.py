

class AchatManager():
    isOn = False
    count = 0

    @classmethod
    def onMessageEvent(cls,element) -> None:
        if cls.isOn:
            try:
                cls.count += int(element['parameters'][3])
            except Exception as e:
                print(e)
            print(f"Nouveau coût total : {cls.count}")

    @classmethod
    def start(cls) -> None:
        cls.isOn = True
        cls.count = 0

    @classmethod
    def stop(cls) -> None:
        print(f"Coût total : {cls.count}")
        cls.count = 0
        cls.isOn = False
