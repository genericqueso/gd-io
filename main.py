import gdio.levelStringImporter as lsi
from gdio.processLevelData import gdObject, gdColor, gdLevel
import gdio.processLevelData as pl
import time


def __main__():
    # The following two lines will extract your level data and transform your topmost level into a gdLevel object (lvl).
    lvldata = lsi.read_leveldata()
    lvl = pl.extract_level(lvldata["k4"])

    # Put your script here!
    
    # The following line will compress the gdLevel object and then write it back to your level data.
    lsi.write_leveldata(pl.compress_level(lvl), False)


start = time.time()
__main__()
end = time.time()
print(str(round(end - start, 6)) + "s")
