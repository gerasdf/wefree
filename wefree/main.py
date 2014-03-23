"""Main entry point, and initialization of everything we can."""

import sys
import dbus.mainloop.qt
from PyQt4.QtGui import QApplication

dbus.mainloop.qt.DBusQtMainLoop(set_as_default=True)

def start():
    """Rock and roll."""
        
    loop = dbus.mainloop.qt.DBusQtMainLoop(set_as_default=True)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    from wefree.ui.main import MainUI # this must be always after QApplication
                                       # instantiation because dbus and qt mainloop
    MainUI(app.quit)
    
    sys.exit(app.exec_())
