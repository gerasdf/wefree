from __future__ import division

"""The main window."""

import os
import logging
from bisect import bisect

from PyQt4 import QtCore, Qt, QtGui
from PyQt4.QtGui import (QAction, QMainWindow, QMessageBox, QSystemTrayIcon,
    QIcon, QMenu, QInputDialog, QPushButton, QLineEdit, QDialog)

from wefree.passwords_manager import PM,GEO
from wefree.interfaces import WifiInterfaces

import icons

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
        QMessageBox.about(self, "WeFreed networks Inc.", ABOUT_TEXT)

    def icon_for_signal(self, signal):
        level_index = bisect(SIGNAL_BREAKPOINTS, signal.level)
        if signal.has_db_passwords():
            icons = self.icons['wefree']
        else:
            if signal.encrypted:
                lock = 'lock-'
            else:
                lock = ''
            if not signal.encrypted or signal.has_password():
                icons = self.icons[lock+'signals']
            else:
                icons = self.icons['lock-signals-unknown']
            
        return icons[SIGNALS_IMGS[level_index]]

    def build_menu(self, signals):
        """Build the menu."""
        def action_cmp(a,b):
            aText = a.text().upper()
            bText = b.text().upper()
            if aText == bText: return 0
            if aText < bText: return -1
            return 1
        
        menu = QMenu(self)

        connected = False
        # the signals
        signal_actions = []
        for signal in signals:
            icon = self.icon_for_signal(signal)

            if signal.is_connected():
                connected = True
            
            when_triggered = (lambda sign: lambda:self.please_connect(sign))(signal)
            action = QAction(icon, signal.ssid, self, triggered = when_triggered)
            signal_actions.append(action)
            
        signal_actions.sort(cmp = action_cmp)
        menu.addActions(signal_actions)

        self.update_connected_state(connected)

        # the bottom part
        menu.addSeparator()
        menu.addAction(QAction("Share...",        self, triggered=self.share_keys))
        menu.addAction(QAction("Update Database", self, triggered=self.update_database))
        menu.addAction(QAction("Rescan",          self, triggered=self.rescan_networks))
        menu.addAction(QAction("Quit",            self, triggered=self.app_quit))
        menu.addAction(QAction("WTF?",            self, triggered=self.open_about_dialog))
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

    def share_keys(self):
        to_commit = self.wifi.get_known_networks()
        to_commit = ShareOwnPasswords(self, to_commit).exec_()
        for ap in to_commit:
            PM.add_new_ap(ap)
            PM.report_success_ap(ap, auto_location = False)
    
    def rescan_networks(self):
        self.wifi.force_rescan()

    def refresh_menu_items(self, *args):
        """Refresh."""
        signals = self.wifi.get_signals()
        
        menu = self.build_menu(signals)
        self.sti.setContextMenu(menu)
        
        bssids = [signal.bssid for signal in signals]
        GEO.refresh_seen_bssids(bssids)

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
        self.icons = dict()
        self.icons['wefree'] = dict()
        self.icons['signals'] = dict()
        self.icons['lock-signals'] = dict()
        self.icons['lock-signals-unknown'] = dict()
        
        for strength in SIGNALS_IMGS:
            self.icons['wefree'][strength]                 = QIcon(":/imgs/wefree-192.%d.png" % strength)
            self.icons['signals'][strength]                = QIcon(":/imgs/signals.%d.png" % strength)
            self.icons['lock-signals'][strength]           = QIcon(":/imgs/lock-signals.%d.png" % strength)
            self.icons['lock-signals-unknown'][strength]   = QIcon(":/imgs/lock-signals-unknown.%d.png" % strength)
        
    def iconize(self):
        """Show a system tray icon with a small icon."""

        self.sti = QSystemTrayIcon(self.icons['wefree'][0], self)
        if not self.sti.isSystemTrayAvailable():
            logger.warning("System tray not available.")
            return

        self.refresh_menu_items()
        self.sti.show()

    def update_connected_state(self, connected):
        if connected:
            self.sti.setIcon(self.icons['wefree'][100])
        else:
            self.sti.setIcon(self.icons['wefree'][0])

class ShareOwnPasswords(QDialog):
    def __init__(self, parent, ap_list):
        super(ShareOwnPasswords, self).__init__(parent)
        self.ap_checkbox = []
        self.shared = []
        vbox = QtGui.QVBoxLayout(self)
        self.share_btn = QPushButton("connect and share (Free the world)")
        self.cancel_btn = QPushButton("cancel")
        for ap in ap_list:
            vbox.addLayout(self.new_entry(ap))
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.share_btn)
        hbox.addWidget(self.cancel_btn)
        vbox.addLayout(hbox)
        self.share_btn.clicked.connect(self.share)
        self.cancel_btn.clicked.connect(self.close)

    def exec_(self):
        super(ShareOwnPasswords, self).exec_()
        return self.shared

    def share(self):
        self.shared = [cb.ap for cb in self.ap_checkbox if cb.isChecked()]
        self.close()

    def new_entry(self, ap):
        hbox = QtGui.QHBoxLayout()
        checkbox = QtGui.QCheckBox()
        checkbox.ap = ap
        label = QtGui.QLabel(ap.essid)
        hbox.addWidget(checkbox)
        hbox.addWidget(label)
        self.ap_checkbox.append(checkbox)
        return hbox
