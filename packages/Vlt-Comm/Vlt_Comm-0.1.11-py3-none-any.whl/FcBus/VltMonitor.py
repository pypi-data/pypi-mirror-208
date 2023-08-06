import sys

import pyqtgraph as pg
from PySide2.QtWidgets import QApplication
from pyqtgraph.Qt import QtGui, QtCore
import time

from serial import SerialException


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        return [time.strftime("%M:%S:", time.localtime(value))+str(int((value - int(value))*1000000)) for value in values]


class ui(object):
    def __init__(self, *funcs):
        if hasattr(sys, 'frozen'):
            self.qt_app = QApplication(sys.argv)
        self.mw = QtGui.QMainWindow()
        self.mw.resize(800, 800)
        self.cw = QtGui.QWidget()
        self.mw.setCentralWidget(self.cw)
        self.l = QtGui.QVBoxLayout()
        self.cw.setLayout(self.l)
        self.pw = pg.PlotWidget(name='Plot1', axisItems={'bottom': TimeAxisItem(orientation='bottom')})  # # giving the plots names allows us to link their axes together
        self.pw = pg.PlotWidget(name='Plot1')  # # giving the plots names allows us to link their axes together
        self.l.addWidget(self.pw)
        self.title = ""
        # self.mw.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.tick = 30
        # self.timer.start(self.tick)
        self.plots = {}
        self.funcs = {}
        self.functypes = {}
        self.datadics = {}
        self.timedics = []
        self.args = {}
        self.bStop = False
        self.max_len = 2000
        self.pens = [(255, 0, 0), (0, 255, 0), (255, 255, 255), (0, 0, 255), (255, 255, 0), (0, 255, 255),
                     (255, 0, 255), (11, 23, 70), (3, 168, 158), (160, 32, 240)]
        self.penindex = 0
        self.pw.plotItem.showGrid(True, True, 0.7)

        if funcs:
            self.add(funcs)
            # self.mw.connect(QtCore.SIGNAL("destroyed"), self.stop)
            # self.mw.destroyed.connet(self.stop)
        if hasattr(sys, 'frozen'):
            self.qt_app.exec_()

    def clearall(self):
        for i in self.funcs.keys():
            self.datadics[i].clear()

    def _add(self, func, functype=0, arg=()):
        # if type(func) is int or type(func) is float:
        #     func = self.func_generate(func)

        if func not in self.funcs.keys():
            self.funcs[func.__name__] = func
            self.functypes[func.__name__] = functype
            self.plots[func.__name__] = self.pw.plot(pen=self.pens[self.penindex])
            self.penindex += 1
            if self.penindex > len(self.pens):
                self.penindex = 0
            self.datadics[func.__name__] = []
            self.args[func.__name__] = arg

    def add(self, funcs):
        self.clearall()
        if isinstance(funcs, list) or isinstance(funcs, tuple):
            for i in funcs:
                self._add(i)
                self.title += (i.__name__ + '   ')
        else:
            self._add(funcs)
            self.title = funcs.__name__
        if len(self.funcs.keys()) >= 1:
            self.timer.start(self.tick * len(self.funcs.keys()))
            self.mw.setWindowTitle(self.title)
            self.mw.show()

    def remove(self, funcname):
        for i in self.funcs():
            pass

    def update(self):
        if self.mw.isHidden():
            self.stop()

        try:
            for i in self.funcs.keys():
                if self.functypes[i] == 0:
                    data = self.funcs[i]()
                    if data is not None:
                        self.datadics[i].append(data)
                        self.timedics.append(time.time())
                elif self.functypes[i] == 1:
                    self.datadics[i] = self.funcs[i](*self.args[i])
                data = self.datadics[i]
                if isinstance(data, list) and len(data) != 0:
                    if len(data) > self.max_len:
                        a = data[-self.max_len:]
                    else:
                        a = data
                    self.timedics = self.timedics[-self.max_len:]
                    self.plots[i].setData(a)
                    # self.plots[i].setData(self.timedics, a)
                    self.datadics[i] = a
        except SerialException:
            self.timer.stop()
            raise
        except Exception:
            pass
#        else:
#            self.stop()

    def stop(self):
        print('Be called')
        self.bStop = True
        self.timer.stop()

    def go(self):
        self.bStop = False
        self.timer.start()

    def hideEvent(self, event):
        self.stop()
        QtGui.QWidget.hide()

    def auto(self):
        self.pw.plotItem.enableAutoRange()
        self.go()
    # def func_generate(self, pnum):
    #     return None
    def viewRangeChanged(self, view, range):
        print('1')
        self.sigRangeChanged.emit(self, range)
        self.pw.plotItem.enableAutoScale()

def plot(*args, **kargs):
    pg.plot(*args, **kargs)