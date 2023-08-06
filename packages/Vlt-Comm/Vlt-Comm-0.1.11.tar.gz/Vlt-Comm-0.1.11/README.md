## How to install
pip install vlt-comm

## How to use:

from FcBus import *

### Examples:
    ## import all functions from the module
    from FcBus import *

    ## find and open port for vlt communication(auto set baudrate to 115200)
    findb()   #Note: Only support one driver connected at same time

    ## Write 0 to parameter 110
    p[110] = 0

    ## Read parameter 3821 with index = 8
    p[3821.08]

    ## Close serial port
    pclose()

    ## Open serial port
    ope() or p.open()

    ## Let the driver go into testmonitor mode
    tm()

    ## Reset the driver
    reset()


## Get all supported functions:
dir()

## How to use scope like mct-10
def gd():
    return p[3821.01]

def gd1():
    return p[3821.02]

def gd2():
    return p[3821.03]

u = ui(gd, gd1, gd2)

## New commands

### since 0.0.12
laoc(filepath)

llang(filepath)

### since 0.0.13
lmoc(filepath)

lpud(filepath)

u = ui(g1614) #paramter monitor

### since 0.1.3

from FcBus import *  #import everything

p[835] = 0.001 # set parameter must with scaling

getlogs() # function used for dbg log

readee(addr) # functions used for eeprom reading

readee_all(endaddr) # get all data in eeprom

### Release 0.1.4

1. Add return value to findb();  # true -- found
2. Use '\r' for bin loading;
3. Only print one line during parameters' loading;
4. Remove resetctw in getalarm();

### Release 0.1.5
1. Set p[802] to FcBus during findb();
2. import ui by default;

### Release 0.1.7
1. Correct return value for findb() in TM mode;
2. Change commands.json to support larger multi-lang.bin(8 sectore);
3. Export functions tsend, write_version, readee for operation in TM mode.

### Release 0.1.8
1. Add function gsn() to get serial number of IO card;
2. Add function rep() for muti-run process;
3. Don't check virtual com in findb();

### Release 0.1.11
1. Add return value to findb(), (bfound, btm);
2. Don't reload parameters in findb();
3. Use orgin function in command TM;
4. Add function readmoccal to get cal data in MOC;
5. Change moc load waiting time to 2000;
6. Fix some issue during vlt searching;