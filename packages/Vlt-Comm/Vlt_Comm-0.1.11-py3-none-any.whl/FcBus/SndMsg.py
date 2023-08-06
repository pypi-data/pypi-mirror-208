"""
Created on 2011-12-2

@author: U249250
"""
from . import Message


class SndMsg(object):
    """
    classdocs
    """

    # 0 -- Read Parameter Value
    # 1 -- Write Parameter Value in RAM(word)
    # 2 -- Write Parameter Value in RAM(Double Word)
    # 3 -- Write Parameter Value in RAM and EEPROM(Word)
    # 4 -- Write Parameter Value in RAM and EEPROM(double Word)
    # 5 -- Read Parameter Characterisics
    # 6 -- Text
    #-1 -- Read Parameter Characterisics
    TypeEnum = {0: 0x1000, 1: 0x2000, 2: 0x3000, 3: 0xD000, 4: 0xE000, 5: 0x4000, 6: 0xF000, -1: 0x4000}

    data = 0
    stw = 0
    ref = 0
    dataA = [0, 0, 0]

    def __init__(self, type, pnu, index=0, dd=0):
        """
        Constructor
        """
        self.dataA[0] = self.TypeEnum[type] | pnu
        self.dataA[1] = index
        self.dataA[2] = dd
        self.addr = 1

    def pack(self):
        self.data = (self.dataA[0] << 48) + (self.dataA[1] << 32) + (0xffffffff & self.dataA[2])  # Fix send -1 issue
        m = Message.Message(self.data, self.stw, self.ref, addr=self.addr)
        return m.pack()

    def setRef(self, ref):
        self.ref = ref

    def setCtw(self, ctw):
        self.stw = ctw
        
    def setAddr(self, addr):
        self.addr = addr

# def setPnu(self,pnu):
#        self.da

#b = SndMsg(1,1450,0,2)
#
#b.pack()
