import json
import random
from importlib.resources import files
from .VltOp import p
from .tools import asciitostr

af = json.loads(files('FcBus').joinpath('tmcmds.json').read_text())

def tsend(cmdstr, timeout = 100):
    #print(cmdstr)
    p._Product__write(cmdstr)
    ret = p.wait_redboot(timeout)
    try:
        ret = ret.decode()
        #print(ret)
        ret = ret.replace('\n', '').replace('\r', '').replace('RedBoot>', '')
    except UnicodeDecodeError:
        print(ret)
    #print("=======================================================================")
    return ret

def tmaoc(af):
    for i in af["dtmaoc"]:
        cc = "dtm " + i["cmd"]
        if "go" not in cc:
            tsend(cc)

def gsn():
    a = tsend("dtm read_ee -a 0x140 -l 18")
    return asciitostr(a)


def tmmoc(af):
    for i in af["dtmmoc"]:
        cc = "dtm moc " + i["cmd"]
        if "go" in cc:
            continue
        if "normal" in cc:
            continue
        if "reset" in cc:
            continue
        if "erase" in cc:
            continue
        tsend(cc)

def tmbuildin(af):
    for i in af["buildin"]:
        cc = i["cmd"]
        if "go" not in cc:
            tsend(cc)

def ramcheck(addr = 0, val = 0x12345678):
    tsend("dtm writemem -a {} -v {}".format(addr, val))
    ret = tsend("dtm readmem -a {}".format(addr))
    assert(int(ret, 16) == val)
    ret = tsend("dtm logicmem -a {} -v 0xffffffff".format(addr))
    assert(int(ret, 16) == val)
    ret = tsend("dtm logicmem -a {} -o 0".format(addr))
    assert(int(ret, 16) == val)


def readee(addr = 0, length = 4):
    ret = tsend("dtm read_ee -a {} -l {}".format(addr, length))

def write_version(version = 2):
    tsend("dtm write_ee -a 0x364 -d {}00".format(version))

class cmds():
    def __init__(self, jsonfile):
        with open(jsonfile, encoding="utf-8") as ff:
            af = json.load(ff)


if __name__ == "__main__":
    tmaoc(af)
    tmmoc(af)
