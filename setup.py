# setup.py
from distutils.core import setup
import py2exe
setup(
    name = "Dropbox Cache Cleaner",
    description = "Dropbox Cache Cleaner",
    version = "0.1",
    windows = [
        {"script": "DBCacheCleaner.py",
        "icon_resources": [(1, "dbcc.ico")]
        }
    ],
    data_files=[("settings.ini"),
                ("dbcc.png")
    ],
)
