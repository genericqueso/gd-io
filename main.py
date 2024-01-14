import levelStringImporter as lsi
from processLevelData import gdObject, gdColor, gdLevel
import processLevelData as pl
import time

def __main__():
    lvldata = lsi.read_leveldata()
    lvl = pl.extract_level(lvldata["k4"])

    # put your script here!

    print(len(lvl.objs))
    lsi.write_leveldata(pl.compress_level(lvl))


start = time.time()
__main__()
end = time.time()
print(str(round(end - start, 6)) + "s")
