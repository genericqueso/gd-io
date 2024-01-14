import base64
import gzip
import os
import zlib
import struct
import xml.etree.ElementTree as ET
import subprocess

gamedir = os.getenv("localappdata") + "\\GeometryDash\\"
locallevels = "CCLocalLevels.dat"

# most of the methods in this file are condensed, simplified versions of the code present with sputnix's version
# this was done for clarity because the way it was before was an absolute mess

def decryptreplace(string: str) -> str:
    return string.replace("-", "+").replace("_", "/").replace("\0", "")


def encryptreplace(string: str) -> str:
    return string.replace("+", "-").replace("/", "_")


def xor(data, key):
    return bytearray([i ^ key for i in data]).decode()


def decrypt(ls):
    data = decryptreplace(ls)
    while len(data) % 4 != 0:
        data += "="
    data = base64.b64decode(data)
    return gzip.decompress(data)


def encrypt(dls):
    data = gzip.compress(dls)
    data = base64.b64encode(data)
    return "H4sIAAAAAAAAC" + encryptreplace(data.decode("utf-8"))[13:]


def decrypt_gamesave():
    with open(gamedir + locallevels, "rb") as f:
        data = f.read()
    res = xor(data, 11)
    return zlib.decompress(base64.b64decode(decryptreplace(res).encode())[10:], -zlib.MAX_WBITS)


def encrypt_gamesave(data):
    encrypted = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x0b"
    encrypted += zlib.compress(data)[2:-4] + struct.pack("I", zlib.crc32(data)) + struct.pack("I", len(data))
    encoded = encryptreplace(base64.b64encode(encrypted).decode()).encode()
    fin = xor(encoded, 11).encode()

    try:
        with open(gamedir + locallevels, "wb") as f:
            f.write(fin)
        update_runs()
    except:
        print("Failed to write:", locallevels)


def read_leveldata(decrypt_lvlstring=True) -> dict[str, str]:
    root = ET.ElementTree(ET.fromstring(decrypt_gamesave())).getroot()
    lvlnode = [node.text for node in root[0][1][3]]
    lvldata = dict(zip(lvlnode[::2], lvlnode[1::2]))
    if decrypt_lvlstring:
        lvldata["k4"] = str(decrypt(lvldata["k4"]))
    print("Accessing level", lvldata["k2"])
    return lvldata


def write_leveldata(lvlstring: str, start_game=False) -> None:
    root = ET.ElementTree(ET.fromstring(decrypt_gamesave())).getroot()
    lvldata_index = [node.text for node in root[0][1][3]].index("k4") + 1
    root[0][1][3][lvldata_index].text = encrypt(bytes(lvlstring, "utf-8"))
    encrypt_gamesave(ET.tostring(root, encoding="utf8", method="xml"))
    if start_game: subprocess.call(r"cmd /c start steam://run/322170")  # open gd


def write_levelstring_to_file(lvldata: dict[str, str]) -> None:
    with open("data/lvldata/" + lvldata["k2"] + ".txt", "w") as f:
        f.write(lvldata["k4"])


def update_runs():
    if not os.path.exists("runs.txt"):
        f = open("runs.txt", "w+")
        f.write(str(0))
        f.close()
    f = open("runs.txt", "r")
    runs = int(f.read())
    runs = runs + 1
    f.close()
    f = open("runs.txt", "w")
    f.write(str(runs))
    f.close()
    print("Done!", runs)
