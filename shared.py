#!/usr/bin/env python

import urllib2
import re
import os
import cPickle
import BeautifulSoup  #only 3.0.7a is lenient enough with <script> tags
import patterns


class UrlGet():
    """Simple urllib2 based class, to automate error handling.

    Provides basic convenience funtions, to prevent error handling and
    generic urllib2 calls being repeated. Follows standard KATS error convention
    by logging error's to public 'self.error'.

    """
    def __init__(self, url=None):
        self.url = url
        self.error = None

    def get(self, url=None):
        if url:
            self.url = url
        self.error = None
        if not self.url:
            raise self.UrlGetError("No url set.")

        request = urllib2.Request(self.url)
        try:
            try:
                response = urllib2.urlopen(request)
            except ValueError, e:
                self.error = unicode(e)
                return 0
            finally:
                pass #response.close()
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                self.error = unicode(e.reason)
            elif hasattr(e, 'code'):
                self.error = "http error: " + unicode(e.code)
            return 0
        else:
            return response

    class UrlGetError(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)


class ChanScrape():
    """Scrape a thread for image and thumbnail url's.

    Returns a list of image url's, thumbnail url's and the image name, minus the
    extension. Follows standard KATS error convention by logging error's to
    public 'self.error'.

    """
    def __init__(self, url=None, pattern=None):
        self.url = url
        self.pattern = pattern
        self.error = None

    def scrape(self, url=None, pattern=None):
        #Stop continuos instantitation.
        if url: self.url = url
        if pattern: self.pattern = pattern

        if self.pattern not in patterns.PATTERNS:
            self.error = "pattern does not exist: %s" % self.pattern
            return None

        if not self.url:
            self.error = "bad url: %s" % str(self.url)
            return None

        #Define variables.
        pattern = patterns.PATTERNS[self.pattern]
        base_reg = re.compile(pattern["base"])
        file_reg = re.compile(pattern["filename"])
        image_url_list = []

        #Try that connection shiznit.
        connection = UrlGet(self.url)
        response =  connection.get()
        if not response:
            self.error = connection.error
            return None

        #Try to regex teh url.
        try:
            base = base_reg.search(self.url).group()
        except Exception:
            self.error = "regex fail: %s" % self.url
            return None

        #Parse that HTML yo.
        soup = BeautifulSoup.BeautifulSoup(response.read())
        for post in soup.findAll("span", "filesize"):
            url_item = []
            url_string = post.contents[1]["href"]
            try:
                file = file_reg.search(url_string).group()
            except Exception:
                self.error = "regex fail: %s" % url_string
                return None

            #Compile scraped url list.
            complete_url = base + pattern["source"] + file
            file_thumb = file.replace(pattern["thumb_replace"][0],
                                      pattern["thumb_replace"][1])
            complete_thumb_url = base + pattern["thumb"] + file_thumb
            image_url_list.append([complete_url,
                                   complete_thumb_url,
                                   file.split('.')[0]
                                   ])

        return image_url_list


class AccessFile():
    """Read/Write a file stream.

    Convenience class, helping lower repitious exception code written. Follows
    standard KATS error convention by logging error's to public 'self.error'.

    """
    def __init__( self, stream=None, path=None ):
        self.stream = stream
        self.path = path
        self.error = None

    def write( self, stream=None, path=None ):
        if stream: self.stream = stream
        if path: self.path = path
        if self.stream and self.path:
            try:
                stream = stream
                output = file( path, "w" )
                output.write( stream )
                output.close()
            except IOError:
                self.error = "error: and IOError occurred"
                return None
            return True
        self.error = "null stream or path: %S" % self.path
        return None

    def read( self, path ):
        if path: self.path = path
        if self.path:
            try:
                input = file( path, "r" )
                stream = input.read()
                input.close()
            except IOError:
                self.error = "error: and IOError occurred"
                return None
            return stream
        self.error = "null path: %s" % self.path
        return None


class Settings():
    def __init__( self, name ):
        self.name = name
        self.settings = None
        self.error = None
        self.fileHandler = AccessFile()
        file_reg = re.compile( r"[\w_.]*$" )
        base = __file__.replace( file_reg.search( __file__ ).group(), "" )
        self.settings_dir = "%s%s.pickle" % (base, self.name)

    def save( self ):
        if not self.settings:
            self.error = "no settings set"
            return None
        file = cPickle.dumps( self.settings )
        if not self.fileHandler.write( file, self.settings_dir ):
            self.error = self.fileHandler.error
            return None
        return True

    def load( self ):
        if not os.path.isfile( self.settings_dir ):
            self.error = "can't access settings file: %s" % self.settings_dir
            return None
        file = self.fileHandler.read( self.settings_dir )
        if not file:
            self.error = self.fileHandler.error
            return None
        self.settings = cPickle.loads( file )
        return True

    def default( self ):
        previous = {"url": "http://zip.4chan.org/toy/",
                    "output_dir" : os.path.expanduser('~')
                    }
        self.settings = {"always_scrape": False,
                         "previous": previous
                        }