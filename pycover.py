#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Exter, BADDCAFE 2014'

import wx
from wx.lib.newevent import NewCommandEvent
from PIL import Image
from droptarget import FTDropTarget as DropTarget
import os.path
import urlparse
import urllib2
import cStringIO as StringIO

# TODO: remove img_file global variable and its dependencies
img_file = r'C:\\Users\\Exter\\Downloads\\aaaa.jpg'

CoverDropEvent, EVT_COVER_DROP_EVENT = NewCommandEvent()


class CoverImage(object):
    MIN_SIZE = (425, 425)
    MAX_SIZE = (550, 550)
    DEF_SIZE = (500, 500)
    DEFAULT_NAME = "cover.jpg"

    def __init__(self, path=None, stream=None):

        self.saved = False  # TODO: is should not be here (?)

        self.__path = None
        self.__old_size = ()
        self.__new_size = ()
        self.__image = None
        self.__is_OK = True
        self._old_weight = 0

        self.small_image = False  # FIXME: change variable name

        if path and not stream:
            self.open_file(path)
        elif stream and not path:
            self.open_stream(stream)
        else:
            self.__is_OK = False

    def open_file(self, path):
        try:
            self.__image = Image.open(path)
        except:
            self.__is_OK = False
            print 'ERR: Can\'t open file!'
            return

        self._old_weight = 0  # FIXME: get correct file size

        self.__old_size = self.__image.size
        self.__calculate_new_size()
        self.__image = self.__image.resize(self.__new_size, Image.ANTIALIAS)
        self.path = os.path.dirname(path)

    def open_stream(self, stream):
        try:
            self.__image = Image.open(stream)
        except:
            self.__is_OK = False
            print 'ERR: Can\'t open stream!'
            return
        stream.seek(0, os.SEEK_END)
        self._old_weight = stream.tell()

        self.__old_size = self.__image.size
        self.__calculate_new_size()
        self.__image = self.__image.resize(self.__new_size, Image.ANTIALIAS)

    def __calculate_new_size(self):
        self.small_image = False
        self.__new_size = self.__old_size
        if self.__old_size < self.MIN_SIZE:
            self.small_image = True
        elif self.__old_size > self.MAX_SIZE:
            n = range(2)  # create list size of two
            idx = self.__old_size.index(max(self.__old_size))  # find bigger dimension index
            n[idx] = self.DEF_SIZE[idx]  # new bigger dimension set to fixed value
            # calculate second dimension old_dim_x*default_dim_y/old_dim_y (keep original ration)
            n[idx - 1] = int(float(self.__old_size[idx - 1]) * self.DEF_SIZE[idx] / self.__old_size[idx])
            self.__new_size = (n[0], n[1])  # new size as tuple

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, val):
        self.__path = val

    @property
    def size(self):
        return self.__new_size

    @property
    def data(self):
        return self.__image.convert('RGB').tostring() if self.__image else ''

    @property
    def ok(self):
        return self.__is_OK


#FIXME: JPEG header checker
class ImageHeader(object):
    def __init__(self, header):
        self.header = header
        self.type = ''

    def _is_jpg(self):
        #TODO: write proper jpeg header checker
        """
        currently we are checking only 3 first bytes
        4th byte can be 0xE0, 0xE1, 0xE2 - and this projects to content of 6:11 bytes
        self.header[6:] == 'JFIF\0': # or 'EXIF\0' or 'JFXX\0' - has to be checked
        """
        if self.header[:3] == '\xff\xd8\xff':
            self.type = 'JPEG'
            return True
        else:
            return False

    def _is_png(self):
        if self.header[0:8] == '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
            self.type = 'PNG'
            return True
        else:
            return False

    def _is_gif(self):
        if self.header[0:6] == 'GIF89a':
            self.type = 'GIF'
            return True
        else:
            return False

    def _is_bmp(self):
        if self.header[0:2] == 'BM':
            self.type = 'BMP'
            return True
        else:
            return False

    def is_tiff(self):
        """
        experimental
        """
        if self.header[0:4] == '\x4D\x4D\x00\x2A' or \
                        self.header[0:4] == '\x4D\x4D\x00\x2B' or \
                        self.header[0:4] == '\x49\x49\x2A\x00' or \
                        self.header[0:3] == '\x49\x20\x49':
            self.type = 'TIFF'
            return True
        else:
            return False

    def is_supported(self):
        return self._is_bmp() or \
               self._is_gif() or \
               self._is_jpg() or \
               self._is_png()


class CoverFrame(wx.Frame):
    def __init__(self):
        """
        __init__(self, parent, id, title, pos, size, style, name)
        http://www.wxpython.org/docs/api/wx.Frame-class.html
        """

        wx.Frame.__init__(self, None, id=wx.ID_ANY, title='PyCover', pos=wx.DefaultPosition,
                          size=(wx.Size(685, 615)), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        loc = wx.IconLocation(r'C:\Python27\python.exe', 0)
        self.SetIcon(wx.IconFromLocation(loc))
        # ico = wx.Icon(r'C:\Users\Exter\Downloads\download-icon_small.png', wx.BITMAP_TYPE_PNG)
        # self.SetIcon(ico)
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        # bSizer1.SetMinSize( wx.Size( 550,650 ) )
        self.__bitmap1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img_file, wx.BITMAP_TYPE_JPEG), wx.DefaultPosition,
                                         wx.Size(550, 550),
                                         wx.RAISED_BORDER)
        # self.SetSizerAndFit(bSizer1, self)
        self.__bitmap1.SetToolTipString(u"drop image here")
        self.__bitmap1.SetMinSize(wx.Size(550, 550))
        self.__bitmap1.SetMaxSize(wx.Size(550, 550))
        self.__bitmap1.SetDropTarget(DropTarget(wx.GetApp(), CoverDropEvent))

        bSizer1.Add(self.__bitmap1, 0, wx.ALL, 5)

        self.__panel1 = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.__button1 = wx.Button(self.__panel1, wx.ID_ANY, u"&Save", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.__button1, 0, wx.ALL, 5)

        self.__button2 = wx.Button(self.__panel1, wx.ID_ANY, u"???", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.__button2, 0, wx.ALL, 5)

        self.__panel1.SetSizer(bSizer2)
        self.__panel1.Layout()
        bSizer2.Fit(self.__panel1)
        bSizer1.Add(self.__panel1, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bSizer1)

        # statusBar = wx.StatusBar(self, wx.ID_ANY, pos, size, style, name)
        # sb1 = wx.StatusBar(self, id=wx.ID_ANY, size=(0,300), name='path')
        self.__status_bar = self.CreateStatusBar(2)
        """
        http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.StatusBar.html#SetStatusStyles
        """
        self.__status_bar.SetStatusWidths([40, -1])
        # self.__status_bar.SetStatusStyles([wx.SB_NORMAL, wx.SB_RAISED, wx.SB_NORMAL, wx.SB_RAISED])
        self.__status_bar.SetStatusText(' Path:', 0)

        self.Layout()

    def show_new_image(self, image):
        img = wx.EmptyImage(image.size[0], image.size[1])
        img.SetData(image.data)
        bmp = wx.BitmapFromImage(img, wx.BITMAP_TYPE_ANY)
        self.__bitmap1.SetBitmap(bmp)
        self.Refresh()
        self.Layout()

        #def SetNewImage(self, path):
        #    pass

    def set_path_sb(self, path):
        self.__status_bar.SetStatusText(path, 1)


class CoverApp(wx.App):
    """
    __init__(self, redirect, filename, useBestVisual, clearSigInt)
    :url: http://www.wxpython.org/docs/api/wx.App-class.html
    """

    def __init__(self):
        wx.App.__init__(self, False)

        self.image = None
        #bind to drop events
        self.Bind(EVT_COVER_DROP_EVENT, self.__drop_handler)

        self.frame = CoverFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()

    def __drop_handler(self, evt):
        if evt.GetId() == DropTarget.ID_DROP_FILE:
            if len(evt.files) > 1:
                return
            path = evt.files[0]
            if os.path.exists(path):
                wx.CallAfter(self.__on_path, path)

        elif evt.GetId() == DropTarget.ID_DROP_TEXT:
            url = urlparse.urlparse(evt.text)
            if url.scheme:
                wx.CallAfter(self.__on_url, url.geturl())

    def __on_path(self, path):
        if os.path.isdir(path):
            self.__on_dir(path)
        elif os.path.isfile(path):
            self.__on_file(path)

    def __on_file(self, path):
        foo = open(path, 'rb')
        bar = foo.read(11)
        foo.close()

        ih = ImageHeader(bar)
        if not ih.is_supported():
            #print 'ERR: Unsupported content!'
            self.__on_dir(os.path.dirname(path))
            return

        self.image = CoverImage(path=path)
        if not self.image.ok:
            self.image = None
            return

        self.__cleanup_frame()
        assert isinstance(self.image, CoverImage)
        self.frame.show_new_image(self.image)
        self.frame.set_path_sb(self.image.path)

    def __on_dir(self, path):
        if self.image:
            self.image.path = path

            self.frame.set_path_sb(self.image.path)
            #notify status bar about new path

    def __on_url(self, url):
        # open url connection
        try:
            req = urllib2.urlopen(url)
        except (ValueError, urllib2.URLError), e:
            print e.reason()
            return

        # check if we can get length before downloading
        try:
            content_length = int(req.info().getheader('Content-Length').strip())
        except AttributeError:
            content_length = 0
        if content_length > 1024 * 1024:
            req.close()
            print 'ERR: Content is to big (>1MB)'
            return

        bar = req.read(11)  # read first 11 bytes, enough to recognize image
        ih = ImageHeader(bar)
        if not ih.is_supported():
            req.close()
            print 'ERR: Unsupported content!'
            return

        bar = bar + req.read(1024 * 1024 - 11)  # download at most 1MB
        eof = req.read(1)  # check if EOF was reached
        req.close()
        if eof != '':  # if not, then error
            print 'ERR: Content is to big (>1MB)'
            return

        stream = StringIO.StringIO(bar)
        self.image = CoverImage(stream=stream)
        if not self.image.ok:
            self.image = None
            return

        self.__cleanup_frame()
        assert isinstance(self.image, CoverImage)
        self.frame.show_new_image(self.image)

    def __cleanup_frame(self):
        """TODO: cleanup UI, there will be new image"""
        # def save(self):          #
        #     # i = image.tobytes("jpeg", "RGB")
        #     # print 'size: ', len(i)
        #     # import binascii
        #     # print 'image[:12] ', binascii.hexlify( i[:12])
        #     # image.save(path+'tttt.jpg', "JPEG", quality=75)
        #     # f = open(path+'wwww.jpg', 'wb')
        #     # f.write(i)
        #     # f.close()


def main():
    app = CoverApp()
    app.MainLoop()


if __name__ == '__main__':
    main()
