class Item():
    def __init__(self, GID=0, UID=0, name="",effects={}) -> None:
        
        self.GID = GID
        self.UID = UID
        self.name = name
        # Dico avec clé l'actionId et valeur la value
        self.effects = effects
        self.puit = 0