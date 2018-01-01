#!/usr/bin/env python3
# encoding: utf-8
"""
This file is part of OMAD.

OMAD is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

OMAD is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OMAD.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
logger = logging.getLogger(__name__)
import traceback
import os, sys

from .batoto_model import BatotoModel
from .mangafox_model import MangafoxModel

class DownloadController():
    def __init__(self, gui_info_fcn=None):
        self.gui_info_fcn = gui_info_fcn
        self.webpage_model = None
        self.chapters = []
        self.results = []

        self.downloadPath = None
        self.setDownloadPath('.')

    def guiInfoFcn(self, s='Testing printing...', exception=False, downloadProgress=False, trace=[]):
        """
        Used to add ability to use keywords to pyqt signals
        """
        if type(s) != type("") and type(s) != type(b""):
            s = str(s)

        if self.gui_info_fcn is None:
            if downloadProgress:
                s = "Downloading progress: %s " % (s,)
            if exception:
                logger.exception(s)
                for t in trace:
                    logger.exception(str(t))
            else:
                print(s)
        else:
            self.gui_info_fcn(s, exception, downloadProgress, trace)

    def setGuiInfoFcn(self, fcn):
        self.gui_info_fcn = fcn

    def setDownloadPath(self, path):
        if os.path.isdir(path):
            self.downloadPath = os.path.abspath(path)
            return True
        else:
            return False

    def getDownloadPath(self):
        return self.downloadPath

    def setSeriesUrl(self, url, username=None, password=None):
        logger.debug('Set series url: '+url)

        try:
            if ("bato.to" in url) or ("batoto.com" in url):
                self.guiInfoFcn('Detected batoto url')
                self.webpage_model = BatotoModel(url, self.guiInfoFcn)
            elif ("mangafox.me" in url) or ("mangafox.li" in url):
                self.guiInfoFcn('Detected mangafox url')
                self.webpage_model = MangafoxModel(url, self.guiInfoFcn)
            else:
                logger.debug('Unsupported url!')
                self.guiInfoFcn('Unsupported url!')
                self.webpage_model = None
                self.chapters = []
                return False
        except Exception as e:
            logger.exception(e)
            self.guiInfoFcn('Error when setting series url!', exception=True)
            self.webpage_model = None
            self.chapters = []
            return False

        if username is not None and password is not None:
            self.guiInfoFcn("Logging in as '%s'" % username)
            if self.login(username, password):
                self.guiInfoFcn("Sucessfuly logged in!")
            else:
                self.guiInfoFcn("Login failed! Continuing anyway.")

        try:
            self.chapters = self.webpage_model.getChaptersList()
        except Exception as e:
            logger.exception(e)
            self.guiInfoFcn('Error when downloading list of chapters! wrong url?', exception=True)
            self.webpage_model = None
            self.chapters = []
            return False

        return True

    def login(self, username, password):
        """ Returns True if OK, False if failed. """
        if self.webpage_model is None:
            return False
        return self.webpage_model.login(username, password)

    def getLogin(self):
        """ Returns True if user is logged in """
        if self.webpage_model is None:
            return False
        return self.webpage_model.getLogin()

    def getChaptersList(self):
        return self.chapters

    def downloadChapter(self, chapter_list_number):
        # list [name, url]
        chapter = self.chapters[chapter_list_number]
        self.guiInfoFcn('Downloading: '+chapter[0])

        logger.debug('Starting download of chapter:'+str(chapter)+', '+self.downloadPath)
        try:
            r = self.webpage_model.downloadChapter(chapter, self.downloadPath)
        except Exception as e:
            logger.debug('Failed download of chapter:'+str(chapter)+', '+self.downloadPath)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.guiInfoFcn(e, exception=True, trace=trace)
            r = False

        if not r:
            self.guiInfoFcn('Download finished with errors')
        return r

    def downloadChapterRange(self, ch_from, ch_to):
        results = [False] * len(range(ch_from, ch_to+1))
        for i, c_id in enumerate(range(ch_from, ch_to+1)):
            # Downloading progress: x/y
            self.guiInfoFcn(str(c_id+1-ch_from)+'/'+str(ch_to+1-ch_from), downloadProgress=True)

            r = self.downloadChapter(c_id)
            results[i] = r

        self.results = results
        return self.results
