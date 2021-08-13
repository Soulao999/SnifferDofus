from pathlib import Path
import pickle

with (Path(__file__).parent / "protocol.pk").open("rb") as f:
    types = pickle.load(f)
    msg_from_id = pickle.load(f)
    types_from_id = pickle.load(f)
    primitives = pickle.load(f)
    # with open("log.txt",'a') as f:
    #     f.write(str(types))
    #     f.write("\n-------------------------------------\n")
    #     f.write(str(msg_from_id))
    #     f.write("\n-------------------------------------\n")
    #     f.write(str(types_from_id))
    #     f.write("\n-------------------------------------\n")
    #     f.write(str(primitives))
