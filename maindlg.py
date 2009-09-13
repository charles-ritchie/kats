#!/usr/bin/env python

__version__ = "0.8" #Pretty much feature complete
__author__  = "Charles Ritchie"
__license__ = "GPL"


import platform
import os
import datetime
import re
from PyQt4 import QtCore, QtGui
import shared
from ui import ui_maindlg
import gallerydlg
import qrc_resources


class MainDlg( QtGui.QDialog, ui_maindlg.Ui_MainDlg ):
    def __init__( self, parent= None ):
        super( QtGui.QDialog, self ).__init__( parent )
        self.setupUi( self )
        self.setWindowIcon(QtGui.QIcon(":/4chan.png"))

        self.error = None
        self.urls = None
        self.selected_urls = None
        self.url = None
        self.output_dir = None
        self.scrape_running = False
        self.progress = 0
        self.scraper = shared.ChanScrape( pattern="4chan" )

        #Load settings
        self.settings = shared.Settings("settings")
        if not self.settings.load():
            self.settings.default()
        else:
            self.output_dir = self.settings.settings["previous"]["output_dir"]
        self.urlLineEdit.setText( self.settings.settings["previous"]["url"] )
        self.url = self.settings.settings["previous"]["url"]

        self.refresh()

    #If 'urlLineEdit' text changes reset 'self.url'
    @QtCore.pyqtSignature( "QString" )
    def on_urlLineEdit_textEdited( self ):
        self.urls = None
        self.selected_urls = None
        self.url = unicode( self.urlLineEdit.text() )
        self.refresh()

    @QtCore.pyqtSignature( "" )
    def on_aboutPushButton_clicked( self ):
        QtGui.QMessageBox.about(self, "KATS - About",
            """<b>Kick Ass Thread Scraper</b> v %s
            <p>2009 %s. Released under the %s.
            <p>This is a pretty much feature complete release of KATS, the
            threaded thread scraper for yo interwebs, image board addiction.<p>
            Python %s - Qt %s - PyQt %s on %s""" % (
            __version__, __author__, __license__, platform.python_version(),
            QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, platform.system()))

    @QtCore.pyqtSignature( "" )
    def on_outputLocationPushButton_clicked( self ):
        path = unicode(QtGui.QFileDialog.getExistingDirectory(self,
                "KATS - Choose Output Directory"))
        if path:
            self.output_dir = path
            self.refresh()


    @QtCore.pyqtSignature( "" )
    def on_galleryPushButton_clicked( self ):
        self.message()
        if self.settings.settings["always_scrape"]:
            if not self.urls:
                self.message("Scraping and downloading url list. Please wait...")
                if not self.scrapeUrls( self.url ):
                    self.message( "error - " + self.scraper.error )
                    return
        else:
            self.message("Scraping and downloading url list. Please wait...")
            if not self.scrapeUrls( self.url ):
                self.message( "error - " + self.scraper.error )
                return
        form = gallerydlg.GalleryDlg( self.urls )
        if form.exec_():
            self.selected_urls = form.selected_urls
        self.message()


    @QtCore.pyqtSignature("")
    def on_scrapePushButton_clicked(self):
        self.message()
        self.scrape_running = True
        self.refresh()
        if self.selected_urls:
            urls = self.selected_urls
        else:
            self.message("Scraping and downloading url list. Please wait...")
            if not self.scrapeUrls( self.url ):
                self.message( "error - " + self.scraper.error )
                self.scrape_running = False
                self.refresh()
                return
            urls = self.urls

        self.scrapeProgressBar.setMinimum(0)
        self.scrapeProgressBar.setMaximum(len(urls))
        if self.outputNameLineEdit.text().isEmpty():
            path = "%s%s%s" % (self.output_dir, os.sep,
                               str(datetime.datetime.now()))
        else:
            path = "%s%s%s" % (self.output_dir, os.sep,
                               unicode(self.outputNameLineEdit.text()))
        self.message(u"save to: " + path)


        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except Exception:
                self.error = "error: cannot create directry"
                self.message( self.error )
                self.scrape_running = False
                self.refresh()

        self.message( "start image transfer..." )
        self.thread = GetImages(urls, path)
        self.connect(self.thread, QtCore.SIGNAL("state"), self.stateUpdate)
        self.thread.start()

    @QtCore.pyqtSignature( "" )
    def on_closePushButton_clicked( self ):
        self.reject()

    @QtCore.pyqtSignature( "" )
    def on_cancelPushButton_clicked( self ):
        self.stopThread()

    def reject( self ):
        if self.scrape_running:
            self.thread.stop()
        self.saveSettings()
        QtGui.QDialog.reject( self )

    def closeEvent( self, event ):
        if self.scrape_running:
            self.thread.stop()
        self.saveSettings()

    def saveSettings( self ):
        self.settings.settings["previous"]["url"] = unicode(
            self.urlLineEdit.text())
        if self.output_dir:
            self.settings.settings["previous"]["output_dir"] = self.output_dir
        self.settings.save()

    def stateUpdate( self, state ):
        if state[0] == 0:
            self.scrape_running = False
            self.message( state[1])
            self.scrapeProgressBar.setMaximum(1)
            self.scrapeProgressBar.setValue(1)
            self.refresh()
        if state[0] == 1:
            self.message( state[1] )
            self.progress += 1
            self.scrapeProgressBar.setValue(self.progress)
            if state[1]:
                self.message( "start image transfer..." )
        if state[0] == 2:
            self.message( "error - %s" ) % str(state[1])


    #Lock various parts of the ui, dependent on input
    def refresh( self ):
        #Disable some of the Gui on scrape
        if self.scrape_running:
            self.scrapeProgressBar.reset()
            self.progress = 0
            self.galleryPushButton.setEnabled(False)
            self.scrapePushButton.setEnabled(False)
            self.cancelPushButton.setEnabled(True)
        else:
            self.galleryPushButton.setEnabled(True)
            self.scrapePushButton.setEnabled(True)
            self.cancelPushButton.setEnabled(False)

            #If there's an url unlock gallery, if not lock
            if self.urlLineEdit.text().isEmpty():
                self.galleryPushButton.setEnabled(False)
            else:
                self.galleryPushButton.setEnabled(True)

            #Only allow scrape if there is an url and an output location
            if self.urlLineEdit.text().isEmpty() or not self.output_dir:
                self.scrapePushButton.setEnabled(False)
            else: self.scrapePushButton.setEnabled(True)

    def stopThread( self ):
        self.thread.stop()
        self.thread.wait()
        self.message( "thread execution stopped" )

    #Scraper urls, return status
    def scrapeUrls( self, url ):
        urls = self.scraper.scrape( url )
        if not urls:
            self.error = self.scraper.error
            return None
        self.urls = urls
        return True

    #Display/clear messages in the log area
    def message(self, message=None):
        if not message:
            self.outputTextBrowser.clear()
            QtCore.QCoreApplication.processEvents()
            return
        self.outputTextBrowser.append(message)
        QtCore.QCoreApplication.processEvents()


class GetImages( QtCore.QThread ):
    def __init__( self, urls, output_dir ):
        QtCore.QThread.__init__(self)
        self.urls = urls
        self.output_dir = output_dir
        self.stopped = False
        self.state = None
        self.error = None

    def run( self ):
        self.connectionHandler = shared.UrlGet()
        self.fileHandler = shared.AccessFile()
        for url in self.urls:
            if self.stopped: break
            self.path = ( "%s%s%s.jpg" ) % ( self.output_dir, os.sep, url[2] )
            if os.path.isfile( self.path ):
                self.state = (1, "already got image: "+self.path)
                self.emit(QtCore.SIGNAL("state"), self.state)
                continue

            response = self.connectionHandler.get( url[0] )
            if not response:
                self.error = self.connectionHandler.error
                self.state = (2, str(self.error))
                self.emit(QtCore.SIGNAL(state), self.state)
                continue

            if self.stopped: break
            if not self.fileHandler.write( response.read(), self.path):
                self.error = self.fileHandler.error
                self.state = (2, str(self.error))
                self.emit(QtCore.SIGNAL("state"), self.state)
                continue

            self.state = (1, "got image: "+self.path)
            self.emit(QtCore.SIGNAL("state"), self.state)

        self.state = (0, "completed")
        self.emit(QtCore.SIGNAL("state"), self.state)

    def stop( self ):
        self.stopped = True

    def isStopped( self ):
        return self.stopped


if __name__ == "__main__":
    settings = shared.Settings("test")
    settings.load()
    print settings.error
    print settings.settings