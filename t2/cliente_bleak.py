import asyncio
from bleak import BleakClient
import time
import sys
def convert_to_128bit_uuid(short_uuid):
    # Usada para convertir un UUID de 16 bits a 128 bits
    # Los bits fijos son utilizados para BLE ya que todos los UUID de BLE son de 128 bits
    # y tiene este formato: 0000XXXX-0000-1000-8000-00805F9B34FB
    base_uuid = "00000000-0000-1000-8000-00805F9B34FB"
    short_uuid_hex = "{:04X}".format(short_uuid)
    return base_uuid[:4] + short_uuid_hex + base_uuid[8:]


if len(sys.argv) != 2:
    print("USO python3 cliente_bleak.py <1|0>")
    exit(0)

t = sys.argv[1]
t = int(t)
if t:
    ADDRESS = "78:E3:6D:10:CA:3A"
else:
    ADDRESS = "b0:a7:32:d7:85:c6"

print(f"connectando a {ADDRESS}")
CHARACTERISTIC_UUID = convert_to_128bit_uuid(0xFF01) # Busquen este valor en el codigo de ejemplo de esp-idf

async def main(ADDRESS):
    while True:
        try: 
            async with BleakClient(ADDRESS) as client:
                 while True:
                    print(f"Eseperando desde {CHARACTERISTIC_UUID}")
                    print("Characterisic A {0}".format("".join(map(chr, char_value))))
                    await client.write_gatt_char(CHARACTERISTIC_UUID, b"\x01\x00", response=True)
                    #char_value = await client.read_gatt_char(CHARACTERISTIC_UUID)
                    char_value = await client.read_gatt_char(CHARACTERISTIC_UUID)
        except:
            print("Renconectando denuevo!")
asyncio.run(main(ADDRESS))
