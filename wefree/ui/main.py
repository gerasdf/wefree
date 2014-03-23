from __future__ import division

"""The main window."""

import os
import logging
from bisect import bisect

from PyQt4 import QtCore
from PyQt4.QtGui import (QAction, QMainWindow, QMessageBox, QSystemTrayIcon,
    QIcon, QMenu, QInputDialog)

from wefree.passwords_manager import PM
from wefree.interfaces import WifiInterfaces

import NetworkManager

logger = logging.getLogger('wefree.main')

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

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
        
        for device in NetworkManager.NetworkManager.GetDevices():
            device.connect_to_signal("AccessPointAdded", self.refresh_menu_items)
            device.connect_to_signal("AccessPointRemoved", self.refresh_menu_items)
            device.connect_to_signal("StateChanged", self.device_state_changed, sender_keyword = device)

    def open_about_dialog(self):
        """Show the about dialog."""
        self.sti.setIcon(self.icon2)
        QMessageBox.about(self, "WeFree", ABOUT_TEXT)
        self.sti.setIcon(self.icon1)

    def build_menu(self):
        """Build the menu."""
        menu = QMenu(self)

        # the signals
        for signal in self.wifi.get_signals():
            i = bisect(SIGNAL_BREAKPOINTS, signal.level)
            if signal.encrypted:
                lock = 'lock-'
            else:
                lock = ''
            if not signal.encrypted or signal.has_password():
                fname = lock+"signals-{}.png".format(SIGNALS_IMGS[i])
            else:
                fname = "signals-unk-{}.png".format(SIGNALS_IMGS[i])

            icon = QIcon(os.path.join(CURRENT_PATH, "imgs", fname))
            if signal.is_connected():
                when_triggered = lambda: None
            else:
                when_triggered = (lambda sign: lambda:self.please_connect(sign))(signal)
            action = QAction(
               icon, signal.ssid, self, triggered = when_triggered)
            menu.addAction(action)

        # the bottom part
        menu.addSeparator()
        menu.addAction(QAction(
            "Update Database", self, triggered=lambda: self.update_database()))
        menu.addAction(QAction(
            "Acerca de", self, triggered=lambda: self.open_about_dialog()))
        menu.addAction(QAction(
            "Salir", self, triggered=self.app_quit))
        return menu

    def please_connect(self, signal):
        print "Requested connection %s" % signal.ssid
        if not signal.has_password() and signal.encrypted:
            self.get_password_for(signal)
        signal.connect()

    def get_password_for(self, signal):
        print "Need password for ", signal.ssid
        password, ok = QInputDialog.getText(self, 'Input Password', "Input password for '%s':" % signal.ssid)
        signal.add_password(password)
        PM.add_new_password(password, essid=signal.ssid, bssid=signal.bssid)

    def refresh_menu_items(self, *args):
        """Refresh."""
        menu = self.build_menu()
        self.sti.setContextMenu(menu)

    def device_state_changed(self, new_state, old_state, reason, *args, **kargs):
        if   NetworkManager.NM_DEVICE_STATE_ACTIVATED == new_state:
            print "Connected!"
        elif NetworkManager.NM_DEVICE_STATE_FAILED == new_state:
            print "Failed :-/ (%d)" % reason
        else:
            print '%d -> %d' % (old_state, new_state)
    
    update_done_signal = QtCore.pyqtSignal()

    def update_database(self):
        class UpdateFromServerTask(QtCore.QThread):
            update_done_signal = self.update_done_signal
            def run(self):
                PM.get_passwords_from_server()
                self.update_done_signal.emit()

        self.update_done_signal.connect(self.update_database_done)
        self.update_task = UpdateFromServerTask()
        self.update_task.start()

    def update_database_done(self):
        self.update_task = None

    def iconize(self):
        """Show a system tray icon with a small icon."""
        self.icon1 = QIcon(os.path.join(CURRENT_PATH, "imgs","icon-192.png"))
        self.icon2 = QIcon(os.path.join(CURRENT_PATH, "imgs","icon-192.2.png"))
        self.icon3 = QIcon(os.path.join(CURRENT_PATH, "imgs","icon-192.old.png"))
        self.sti = QSystemTrayIcon(self.icon1, self)
        if not self.sti.isSystemTrayAvailable():
            logger.warning("System tray not available.")
            return

        menu = self.build_menu()
        self.sti.setContextMenu(menu)
        self.sti.show()
