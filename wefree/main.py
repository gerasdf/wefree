"""Main entry point, and initialization of everything we can."""

import sys

from wefree.ui.main import MainUI

from PyQt4.QtGui import QApplication

def start():
    """Rock and roll."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    MainUI(app.quit)
    sys.exit(app.exec_())
