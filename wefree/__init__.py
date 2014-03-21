"""The package."""

# special import before any other imports to configure GUI to use API 2
import sip
for name in "QDate QDateTime QString QTextStream QTime QUrl QVariant".split():
    sip.setapi(name, 2)   # API v2 FTW!
