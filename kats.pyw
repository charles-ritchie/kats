#!/usr/bin/env python
"""Kick Ass Thread Scraper- Kicks ass and scrapes threads for images.

KATS is a multi-threaded thread scraper, which retrieves images from the likes
of 4chan.org and 888chan.org. Profiles for different image boards are stored in
patterns.py, these consist of a few strings, regex's and tuples. Enter an url in
the url bar, from here you can click 'preview' to preview the images in a
thumbnail gallery and retrieve only those you desire, or press 'scrape' to
scrape images (these buttons will only work if a destination has been chosen and
thedesired url is valid) to a folder.

"""
__version__ = "0.8" #Pretty much feature complete
__author__  = "Charles Ritchie"
__license__ = "GPL"

import sys
import time
import maindlg
try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    print "You need PyQT4 to run this program."
    time.sleep(3)
    sys.exit(0)


def main():
    app = QtGui.QApplication( sys.argv )
    form = maindlg.MainDlg()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()