#!/usr/bin/env python

import time
import os
import threading
import re
from PyQt4 import QtCore, QtGui
from ui import ui_gallerydlg
import shared
import qrc_resources


class GalleryDlg(QtGui.QDialog, ui_gallerydlg.Ui_GalleryDlg):
    """Basic dialog to select required images from thumbnails.

    Takes a ChanScrape url list, downloads then displays thumbnails. Downloading
    images is a long running process, so it is run in a child process.
    If items are selected from the gallery self. 'selected_items' will be set to
    url list with respective items included. If nothing is selected, 'None' will
    be returned.

    """
    def __init__( self, urls, parent=None ):
        #Set important variables and check 'urls' arg, tpye
        super(QtGui.QDialog, self).__init__( parent )
        self.setupUi( self )
        self.setWindowIcon(QtGui.QIcon(":/4chan.png"))

        self.urls = []
        self.selected_urls = None

        if not urls: return

        #Use a regex on '__file__' to set temp directory
        file_reg = re.compile( r"[\w_.]*$" )
        base = __file__.replace( file_reg.search(__file__).group(), "" )
        self.temp_image_location = "%scache%s" % ( base, os.sep )

        #Construct image holder layout.
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(6)
        for item in urls:
            item_layout = QtGui.QHBoxLayout()
            filename_label = QtGui.QLabel( item[2] )
            check_box = QtGui.QCheckBox()
            item_layout.addWidget( check_box )
            item_layout.addWidget( filename_label )
            item_layout.addStretch()

            picture_layout = QtGui.QHBoxLayout()
            label = QtGui.QLabel( "loading..." )
            label.setFrameStyle( QtGui.QFrame.StyledPanel|
                                QtGui.QFrame.Sunken )
            picture_layout.addWidget( label )
            picture_layout.addStretch()

            layout.addLayout( item_layout )
            layout.addLayout( picture_layout )
            self.urls.append( [check_box, label, item] )

        #Render layout to 'scrollArea'
        frame = QtGui.QFrame()
        frame.setLayout( layout )
        self.scrollArea.setWidget( frame )

        #Start thread loading images, setup slot for 'imageDone' signal
        self.thread = downloadThumbs(self.urls, self.temp_image_location)
        self.connect(self.thread, QtCore.SIGNAL( "imageDone" ), self.setPicture)
        QtCore.QTimer.singleShot(0, self.thread.start)

    #Event handlers
    @QtCore.pyqtSignature( "" )
    def on_selectAllPushButton_clicked( self ):
        for item in self.urls:
            item[0].setChecked(1)

    @QtCore.pyqtSignature( "" )
    def on_selectNonePushButton_clicked( self ):
        for item in self.urls:
            item[0].setChecked( 0 )

    @QtCore.pyqtSignature( "" )
    def on_buttonBox_accepted( self ):
        self.selected_urls = []
        for item in self.urls:
            if item[0].isChecked():
                self.selected_urls.append( item[2] )
        if not len( self.selected_urls ):
            self.selected_urls = None

    #Reimplement window termination methods, to ensure a clean thread stop
    def closeEvent( self, event ):
        self.stopThread()

    def accept( self ):
        self.stopThread()
        QtGui.QDialog.accept(self)

    def reject( self ):
        self.stopThread()
        QtGui.QDialog.reject(self)

    #Ensure thread is cleanly stopped
    def stopThread(self):
        try:
            self.thread.stop()
            self.thread.wait()
        except AttributeError:
            pass


    #Update gui with picture recieved from child thread
    def setPicture( self, target ):
        target[1].setPixmap( QtGui.QPixmap.fromImage( QtGui.QImage(target[0] )))
        QtCore.QCoreApplication.processEvents()


#Class run as a child thread, grabs pictures from a list of urls
class downloadThumbs( QtCore.QThread ):
    def __init__( self, items, temp_image_location ):
        QtCore.QThread.__init__( self )
        self.stopped = False
        self.items = items
        self.temp_image_location = temp_image_location

    def run( self ):
        #Setup connection and file handlers
        connectionHandler = shared.UrlGet()
        fileHandler = shared.AccessFile()
        for item in self.items:
            if self.isStopped(): return
            filename = self.temp_image_location + item[2][2] + ".tmp"
            label = item[1]
            thumb_url = item[2][1]

            #Try to load from cache
            if not os.path.isfile( filename ):
                #Three attempts to download thumbnail
                for attempt in ( 1, 2, 3 ):
                    label.setText( "attempt - " + str( attempt ) )
                    QtCore.QCoreApplication.processEvents()
                    response = connectionHandler.get( thumb_url )
                    if self.isStopped(): return
                    if response: break
                    time.sleep( 0.1 )

                #No response? inform the user
                if not response:
                    label.setText( "load failed - "
                                  + str( connectionHandler.error ) )
                    QtCore.QCoreApplication.processEvents()
                    continue

                #Output file to cache
                if not fileHandler.write( response.read(), filename ):
                    label.setText( "load failed - " + str( outputFile.error ) )
                    QtCore.QCoreApplication.processEvents()
                    continue

            #Send a signal and tuple with thumbnail filename to the gui
            self.emit( QtCore.SIGNAL( "imageDone" ), ( filename, label ) )

    #Trigger exit flag
    def stop( self ):
        self.stopped = True

    #Check exit flag, used internally
    def isStopped( self ):
        return self.stopped


#Standalone test
def main():
    import sys

    #When running test as main set 'url' to a thread url
    url = "http://zip.4chan.org/toy/imgboard.html"
    urls = shared.ChanScrape( url, "4chan" ).scrape()

    app = QtGui.QApplication( sys.argv )
    form = GalleryDlg( urls )
    form.show()
    app.exec_()

    #Print selected items.
    print form.selected_urls

if __name__ == "__main__":
    main()