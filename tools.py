from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys, urllib2

EXIT_CODE_REBOOT = -8

def internet_active():
    try:
        response = urllib2.urlopen('http://www.google.com', timeout=2)
        return True
    except urllib2.URLError as err: pass
    return False



def debug_me(data, kill=True):
    meta = {}
    meta['Type'] = type(data)
    meta['Value'] = data
    print meta
    if kill == True:
        sys.exit(0)



def createAction(parent, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):

    action = QAction(text, parent)
    if icon is not None:
        action.setIcon(QIcon("%s" % icon))
    if shortcut is not None:
        action.setShortcut(QKeySequence(shortcut))
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if slot is not None:
        parent.connect(action, SIGNAL(signal), slot)
    if checkable:
        action.setCheckable(True)

    return action
