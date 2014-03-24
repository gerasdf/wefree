from __future__ import division

"""The main window."""

import os
import logging
from bisect import bisect

from PyQt4 import QtCore, Qt, QtGui
from PyQt4.QtGui import (QAction, QMainWindow, QMessageBox, QSystemTrayIcon,
    QIcon, QMenu, QInputDialog, QPushButton, QLineEdit, QDialog)

from wefree.passwords_manager import PM
from wefree.interfaces import WifiInterfaces

#import NetworkManager

logger = logging.getLogger('wefree.main')

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

ABOUT_TEXT = u"""
<center>
WeFree<br/>
Let's free the WiFi.<br/>
</center>
"""

# signals and levels to use them
SIGNALS_IMGS = [0, 25, 50, 75, 100]
SIGNAL_BREAKPOINTS = [.20, .45, .70, .90]

def debug_trace():
    '''Set a tracepoint in the Python debugger that works with Qt'''
    from PyQt4.QtCore import pyqtRemoveInputHook
    from ipdb import set_trace
    pyqtRemoveInputHook()
    set_trace()


class AddPasswordDialog(QDialog):
    def __init__(self, parent, wifi, signal):
        super(AddPasswordDialog, self).__init__(parent)

        self.signal = signal
        self.wifi   = wifi

        self.connect_btn = QPushButton("connect")
        self.connect_and_share_btn = QPushButton("connect and share (Free the world)")
        self.connect_and_share_btn.setDefault(True)
        self.cancel_btn = QPushButton("cancel")
        self.input_password = QLineEdit()
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.input_password)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.connect_btn)
        hbox.addWidget(self.connect_and_share_btn)
        hbox.addWidget(self.cancel_btn)
        vbox.addLayout(hbox)

        self.connect_btn.clicked.connect(self.on_connect)
        self.connect_and_share_btn.clicked.connect(self.on_connect_and_share)
        self.cancel_btn.clicked.connect(self.close)

    def on_connect(self, share=False):
        password = self.input_password.text()
        if password:
            self.signal.add_password(password, report = True)
            if share:
                PM.add_new_password(password, essid=self.signal.ssid, bssid=self.signal.bssid)
        self.close()
        self.signal.report_to_db = share
        self.wifi.connect(self.signal)

    def on_connect_and_share(self):
        self.on_connect(share=True)

class MainUI(QMainWindow):
    """Main UI."""

    def __init__(self, app_quit):
        super(MainUI, self).__init__()
        self.app_quit = app_quit
        self.wifi = WifiInterfaces()
        logger.debug("Main UI started ok")
        self.sti = None
        self.load_icons()
        self.iconize()
        self.wifi.connect_signals(self.refresh_menu_items, self.update_connected_state)
        

    def open_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(self, "WeFree", ABOUT_TEXT)

    def build_menu(self):
        """Build the menu."""
        menu = QMenu(self)

        connected = False
        # the signals
        for signal in self.wifi.get_signals():
            i = bisect(SIGNAL_BREAKPOINTS, signal.level)
            if signal.has_db_passwords():
                icon = self.icon_wefree[SIGNALS_IMGS[i]]
            else:
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
                connected = True
            
            when_triggered = (lambda sign: lambda:self.please_connect(sign))(signal)
            action = QAction(icon, signal.ssid, self, triggered = when_triggered)
            menu.addAction(action)

        self.update_connected_state(connected)

        # the bottom part
        menu.addSeparator()
        menu.addAction(QAction("Update Database", self, triggered=self.update_database))
        menu.addAction(QAction("Acerca de",       self, triggered=self.open_about_dialog))
        menu.addAction(QAction("Rescan",          self, triggered=self.rescan_networks))
        menu.addAction(QAction("Salir",           self, triggered=self.app_quit))
        return menu

    def please_connect(self, signal):
        logger.debug("Requested connection %s" % signal.ssid)
        if not signal.has_password() and signal.encrypted:
            self.get_password_for(signal)
        else:
            self.wifi.connect(signal)

    def get_password_for(self, signal):
        logger.debug("Need password for %s" % signal.ssid)

        d = AddPasswordDialog(self, self.wifi, signal)
        d.show()

    def rescan_networks(self):
        self.wifi.force_rescan()

    def refresh_menu_items(self, *args):
        """Refresh."""
        menu = self.build_menu()
        self.sti.setContextMenu(menu)

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
        self.refresh_menu_items()
        self.update_task = None

    def load_icons(self):
        self.icon_wefree = dict()
        for strength in SIGNALS_IMGS:
            self.icon_wefree[strength]   = QIcon(os.path.join(CURRENT_PATH, "imgs","wefree-192.%d.png" % strength))
        
    def iconize(self):
        """Show a system tray icon with a small icon."""

        self.icon2 = QIcon(os.path.join(CURRENT_PATH, "imgs","icon-192.2.png"))
        self.sti = QSystemTrayIcon(self.icon_wefree[0], self)
        if not self.sti.isSystemTrayAvailable():
            logger.warning("System tray not available.")
            return

        menu = self.build_menu()
        self.sti.setContextMenu(menu)
        self.sti.show()

    def update_connected_state(self, connected):
        if connected:
            self.sti.setIcon(self.icon_wefree[100])
        else:
            self.sti.setIcon(self.icon_wefree[0])
