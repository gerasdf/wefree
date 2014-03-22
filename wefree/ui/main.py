
from __future__ import division

"""The main window."""

import logging
from interfaces import WifiInterfaces

from bisect import bisect

from PyQt4.QtGui import (
    QAction,
    QMainWindow,
    QMessageBox,
)
from PyQt4.QtGui import QSystemTrayIcon, QIcon, QMenu


logger = logging.getLogger('wefree.main')

ABOUT_TEXT = u"""
<center>
WeFree<br/>
Let's free the WiFi.<br/>
</center>
"""

# signals and levels to use them
SIGNALS_IMGS = ['25', '50', '75', '100']
SIGNAL_BREAKPOINTS = [.26, .51, .76]

class MainUI(QMainWindow):
    """Main UI."""

    def __init__(self, app_quit):
        super(MainUI, self).__init__()
        self.app_quit = app_quit
        self.wifi = WifiInterfaces()

        logger.debug("Main UI started ok")
        self.sti = None
        self.iconize()

    def open_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(self, "WeFree", ABOUT_TEXT)

    def build_menu(self):
        """Build the menu."""
        menu = QMenu(self)

        # the signals
        for signal in self.wifi.get_signals():
            i = bisect(SIGNAL_BREAKPOINTS, signal.level)
            if signal.encrypted and not signal.has_password():
                fname = "signals-unk-{}.png".format(SIGNALS_IMGS[i])
            else:
                fname = "signals-{}.png".format(SIGNALS_IMGS[i])
            icon = QIcon("wefree/imgs/" + fname)
            action = QAction(
               icon, signal.ssid, self, triggered = (lambda sign: lambda:self.please_connect(sign))(signal))
            menu.addAction(action)

        # the bottom part
        menu.addSeparator()
        menu.addAction(QAction(
            "Refresh", self, triggered=lambda: self.refresh()))
        menu.addAction(QAction(
            "Acerca de", self, triggered=lambda: self.open_about_dialog()))
        menu.addAction(QAction(
            "Salir", self, triggered=self.app_quit))
        return menu

    def please_connect(self, signal):
        print "Requested connection %s" % signal.ssid
        if not signal.has_password():
           self.get_password_for(signal)
           signal.connect()

    def get_password_for(self, signal):
        print "Need password for ", signal.ssid
        signal.add_password("maraca")

    def refresh(self):
        """Refresh."""
        menu = self.build_menu()
        self.sti.setContextMenu(menu)

    def iconize(self):
        """Show a system tray icon with a small icon."""
        icon = QIcon("wefree/imgs/icon-192.png")
        self.sti = QSystemTrayIcon(icon, self)
        if not self.sti.isSystemTrayAvailable():
            logger.warning("System tray not available.")
            return

        menu = self.build_menu()
        self.sti.setContextMenu(menu)
        self.sti.show()
