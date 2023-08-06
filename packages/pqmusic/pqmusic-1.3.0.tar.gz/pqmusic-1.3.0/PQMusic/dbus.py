#!/usr/bin/python3
from PyQt5.QtCore import QCoreApplication, Q_CLASSINFO, pyqtSlot
from PyQt5.QtDBus import QDBusConnection, QDBusAbstractAdaptor

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


class Service(QDBusAbstractAdaptor):
    Q_CLASSINFO('D-Bus Interface', 'io.sonlink.pqmusic')
    Q_CLASSINFO('D-Bus Introspection', ''
                '  <interface name="io.sonlink.pqmusic">\n'
                '    <method name="AddFiles">\n'
                '      <arg direction="in" type="s" name="text"/>\n'
                '    </method>\n'
                '  </interface>\n'
                '')

    def __init__(self, parent):
        super().__init__(parent)
        QDBusConnection.sessionBus().registerObject("/", parent)

        if not QDBusConnection.sessionBus().registerService("io.sonlink.pqmusic"):
            print(QDBusConnection.sessionBus().lastError().message())

    @pyqtSlot(result=str)
    def AddFiles(self):
        return 'hello'


if __name__ == '__main__':
    app = QCoreApplication([])

    if not QDBusConnection.sessionBus().isConnected():
        print("Cannot connect to the D-Bus session bus.\n",
              "Please check your system settings and try again.\n")

    service = Service(app)
    print('Now we are running')
    app.exec_()
