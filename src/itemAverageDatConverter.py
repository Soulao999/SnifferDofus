from pathlib import Path
import re
import databaseManager
# 060b item 04 prix 060b................
#regex =  re.compile(r'(?<=060b)[0-9a-f]*?04[0-9a-f]+(?=060b)')
regex =  re.compile(r'060b(.*?)(?=060b)')
#regex =  re.compile(r'060b[0-9a-f]*?04[0-9a-f]*?060b')

with open(Path("data/itemAveragePrices.dat"),'rb') as f:
    hexdata = f.read().hex()


print(hexdata[:0])
result = regex.findall(hexdata)
print(f"len : {len(result)}")
i = 0
dbManager = databaseManager.DatabaseManager()
for elt in result[:100]:
    if len((x := elt.split("04"))) == 2:
        byte_array = bytearray.fromhex(x[0])
        GID = byte_array.decode("ASCII")
        print(x[1])
        print(bin(int(x[1],16)))
        price = int(x[1],16)
        print(f"GID : {GID}, Name : {dbManager.getItemNameFromGID(GID)} ,Price = {price}")
    else:
        i +=1
        #print(x)
print(f"i = {i}")
print(bin(int("FFFFFF",16)))
