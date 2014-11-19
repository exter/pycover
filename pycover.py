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


CoverDropEvent, EVT_COVER_DROP_EVENT = NewCommandEvent()


class CoverImage(object):
    MIN_SIZE = (425, 425)
    MAX_SIZE = (550, 550)
    DEF_SIZE = (500, 500)
    DEFAULT_NAME = "cover.jpg"

    class __Data(object):
        def __init__(self):
            self.path = ''
            self.size = (0,0)
            self.weight = ''
            # self.in_use = False
            # self.to_small = False
            # self.heavier = False

    def __init__(self, path=None, stream=None):
        self.__initialized = False
        self.__image = None
        self._jpg_data = None
        self.__src = self.__Data()
        self.__dst = self.__Data()

        if path and not stream:
            self.open_file(path)
        elif stream and not path:
            self.open_stream(stream)

    def open_file(self, path):
        try:
            self.__image = Image.open(path)
        except:
            return

        self.__src.weight = os.path.getsize(path)/1024
        self.__src.path = path
        self.__src.size = self.__image.size

        self.__dst.size = self.__calculate_new_size(self.__src.size)
        if not self.small:
            self.__image = self.__image.resize(self.__src.size, Image.ANTIALIAS)

        self.path = os.path.dirname(path)
        self.__dst.weight = str(len(self.jpg_data) /1024)
        self.__initialized = True

    def open_stream(self, stream):
        try:
            self.__image = Image.open(stream)
        except:
            return
        stream.seek(0, os.SEEK_END)
        self.__src.weight = str(stream.tell()/1024)
        self.__src.path = 'URL'
        # self.__src.in_use = None
        self.__src.size = self.__image.size

        self.__dst.size = self.__calculate_new_size(self.__src.size)
        if not self.small:
            self.__image = self.__image.resize(self.size, Image.ANTIALIAS)

        self.path = None
        # self.__dst.in_use = '?'
        self.__dst.weight = str(len(self.jpg_data) /1024)
        # self.__dst.heavy = self.__dst.weight > self.__src.weight
        self.__initialized = True

    def __calculate_new_size(self, old_size):
        if old_size > self.MAX_SIZE:
            new_size = range(2)  # create list size of two
            idx = old_size.index(max(old_size))  # find bigger dimension index
            new_size[idx] = self.DEF_SIZE[idx]  # new bigger dimension set to fixed value
            # calculate second dimension old_dim_x*default_dim_y/old_dim_y (keep original ration)
            new_size[idx - 1] = int(float(old_size[idx - 1]) * self.DEF_SIZE[idx] / old_size[idx])
            new_size = (new_size[0], new_size[1])  # new size as tuple
        else:
            new_size = old_size

        return new_size
        # self.small_image = False
        # self.__new_size = self.__old_size
        # if self.__old_size < self.MIN_SIZE:
        #     self.small_image = True
        # elif self.__old_size > self.MAX_SIZE:
        #     n = range(2)  # create list size of two
        #     idx = self.__old_size.index(max(self.__old_size))  # find bigger dimension index
        #     n[idx] = self.DEF_SIZE[idx]  # new bigger dimension set to fixed value
        #     # calculate second dimension old_dim_x*default_dim_y/old_dim_y (keep original ration)
        #     n[idx - 1] = int(float(self.__old_size[idx - 1]) * self.DEF_SIZE[idx] / self.__old_size[idx])
        #     self.__new_size = (n[0], n[1])  # new size as tuple

    @property
    def path(self):
        return self.__dst.path

    @path.setter
    def path(self, val):
        if val:
            self.__dst.path = os.path.join(val, self.DEFAULT_NAME)
            self.__dst.in_use = os.path.exists(self.__dst.path)
        else:
            self.__dst.path = None

    @property
    def path_in_use(self):
        return self.__dst.in_use if self.path else False

    @property
    def size(self):
        return self.__dst.size

    # @size.setter
    # def size(self, val):
    #     self.__dst.size = val

    # @property
    # def src_size(self):
    #     return self.__src.size

    # @src_size.setter
    # def src_size(self, val):
    #     self.__src.size = val

    # @property
    # def size(self):
    #     return self.__new_size
    #
    # @property
    # def old_size(self):
    #     return  self.__old_size

    @property
    def raw_data(self):
        return self.__image.tobytes("raw", "RGB") if self.__image else ''

    @property
    def jpg_data(self):
        return self.__image.tobytes("jpeg", "RGB") if self.__image else ''

    @property
    def ok(self):
        return self.__initialized

    @property
    def small(self):
        return self.__src.size < self.MIN_SIZE

    @property
    def src_data(self):
        return self.__src.__dict__

    @property
    def dst_data(self):
        return self.__dst.__dict__



# FIXME: JPEG header checker
class ImageHeader(object):
    def __init__(self, header):
        self.header = header
        self.type = ''

    def _is_jpg(self):
        # TODO: write proper jpeg header checker
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

    ID_BUTTON_SAVE = wx.NewId()
    ID_BUTTON_CLEAR = wx.NewId()

    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title='PyCover ver 0.1', pos=wx.DefaultPosition,
                          size=(-1, -1), style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER)

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW))

        self.bs_main = wx.BoxSizer(wx.HORIZONTAL)

        self.__bm_cover = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size(550, 550),
                                           wx.RAISED_BORDER)
        self.__bm_cover.SetToolTipString(u'Drop image here')
        self.__bm_cover.SetDropTarget(DropTarget(wx.GetApp(), CoverDropEvent))

        self.bs_main.Add(self.__bm_cover, 0, wx.ALL | wx.FIXED_MINSIZE, 5)

        self.bs_right = wx.BoxSizer(wx.VERTICAL)

        self.__button = wx.Button(self, wx.ID_ANY, u'Save', wx.DefaultPosition, wx.Size(100, -1), wx.NO_BORDER)
        self.__button.Enable(False)
        self.bs_right.Add(self.__button, 0, wx.CENTER, 0)

        self.bs_right.AddStretchSpacer(1)

        self.__sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u'Original:'), wx.VERTICAL)
        self.__sbs1_st1 = wx.StaticText(self, wx.ID_ANY, u'Size:')
        self.__sbs1.Add(self.__sbs1_st1, 0, wx.ALL, 5)
        self.__sbs1_tc1 = wx.TextCtrl(self, id=wx.ID_ANY, style=wx.TE_CENTER)
        self.__sbs1_tc1.Enable(False)
        self.__sbs1.Add(self.__sbs1_tc1, 0, wx.EXPAND)
        self.__sbs1_st2 = wx.StaticText(self, wx.ID_ANY, u'Weight:')
        self.__sbs1.Add(self.__sbs1_st2, 0, wx.ALL, 5)
        self.__sbs1_tc2 = wx.TextCtrl(self, id=wx.ID_ANY, style=wx.TE_CENTER)
        self.__sbs1_tc2.Enable(False)
        self.__sbs1.Add(self.__sbs1_tc2, 0, wx.EXPAND)
        self.bs_right.Add(self.__sbs1, 0, wx.EXPAND)

        self.__sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u'New:'), wx.VERTICAL)
        self.__sbs2_st1 = wx.StaticText(self, wx.ID_ANY, u'Size:')
        self.__sbs2.Add(self.__sbs2_st1, 0, wx.ALL, 5)
        self.__sbs2_tc1 = wx.TextCtrl(self, id=wx.ID_ANY, style=wx.TE_CENTER)
        self.__sbs2_tc1.Enable(False)
        self.__sbs2.Add(self.__sbs2_tc1, 0, wx.EXPAND)
        self.__sbs2_st2 = wx.StaticText(self, wx.ID_ANY, u'Weight:')
        self.__sbs2.Add(self.__sbs2_st2, 0, wx.ALL, 5)
        self.__sbs2_tc2 = wx.TextCtrl(self, id=wx.ID_ANY, style=wx.TE_CENTER)
        self.__sbs2_tc2.Enable(False)
        self.__sbs2.Add(self.__sbs2_tc2, 0, wx.EXPAND)
        self.bs_right.Add(self.__sbs2, 0, wx.EXPAND)

        self.bs_right.AddStretchSpacer(1)

        self.__bm_status = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(u'./res/status_idle.png', wx.BITMAP_TYPE_PNG),
                                           wx.DefaultPosition, wx.Size(32, 32))
        self.bs_right.Add(self.__bm_status, 0, wx.CENTER | wx.ALL, 5)

        self.bs_main.Add(self.bs_right,0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.bs_main)

        #TODO: http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.StatusBar.html#SetStatusStyles
        self.__status_bar = self.CreateStatusBar(2)
        self.__status_bar.SetStatusWidths([40, -1])

        self.Fit()
        self.Layout()

    def show_new_image(self, image):
        img = wx.EmptyImage(image.size[0], image.size[1])
        img.SetData(image.raw_data)
        bmp = wx.BitmapFromImage(img, wx.BITMAP_TYPE_ANY)
        self.__bm_cover.SetBitmap(bmp)
        self.__fill_sbs1(image.src_data)
        self.__fill_sbs2(image.dst_data)
        self.Refresh()
        self.Layout()

    def set_path_sb(self, path):
        self.__status_bar.SetStatusText(path, 1)

    def __fill_sbs1(self, data):
        self.__sbs1_tc1.SetValue('%dx%d px' % data['size'])
        self.__sbs1_tc2.SetValue('%s KB' % data['weight'])

    def __fill_sbs2(self, data):
        self.__sbs2_tc1.SetValue('%dx%d px' % data['size'])
        self.__sbs2_tc2.SetValue('%s KB' % data['weight'])

    def __update_status(self, status, msg):
        self.__status_bar.SetStatusText(status, 0)
        self.__status_bar.SetStatusText(msg, 1)

    def update_path(self, path, in_use=True):
        if path:
            path = path + ' (in use)' if in_use else ' (new)'
            self.__update_status(u' Path:', ' ' + path)
        else:
            self.status_error(u'Unknown path!')

    def status_error(self, msg):
        # self.__update_status(u' ERR:', ' ' + msg)
        print u' ERR: ', u' ' + msg

    @property
    def button(self):
        return self.__button


class CoverApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, False)

        self.image = None

        self.frame = CoverFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()

        # bind to drop events
        self.Bind(EVT_COVER_DROP_EVENT, self.__drop_handler)
        self.Bind(wx.EVT_BUTTON, self.__on_button, self.frame.button)

    def __drop_handler(self, evt):
        if evt.GetId() == DropTarget.ID_DROP_FILE:
            if len(evt.files) > 1:
                self.frame.status_error(u'Drop one item only!')
                return
            path = evt.files[0]
            if os.path.exists(path):
                wx.CallAfter(self.__on_path, path)

        elif evt.GetId() == DropTarget.ID_DROP_TEXT:
            url = urlparse.urlparse(evt.text)
            if url.scheme:
                wx.CallAfter(self.__on_url, url.geturl())
            else:
                self.frame.status_error(u'This is not URL!')

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
            self.__on_dir(os.path.dirname(path))
            return

        self.image = CoverImage(path=path)
        if not self.image.ok:
            self.image = None
            self.frame.status_error(u'Cannot open image file!')
            return

        self.__cleanup_frame()
        assert isinstance(self.image, CoverImage)
        self.frame.show_new_image(self.image)
        self.frame.set_path_sb(self.image.path)

    def __on_dir(self, path):
        if self.image:
            self.image.path = path
            self.frame.set_path_sb(self.image.path)
        else:
            self.frame.status_error(u'Drop image first!')
            # notify status bar about new path

    def __on_url(self, url):
        # open url connection
        try:
            req = urllib2.urlopen(url)
        except (ValueError, urllib2.URLError), e:
            print e.reason()
            self.frame.status_error(u'urllib2.urlopen exception!')
            return

        # check if we can get length before downloading
        try:
            content_length = int(req.info().getheader(u'Content-Length').strip())
        except AttributeError:
            content_length = 0
        if content_length > 1024 * 1024:
            req.close()
            self.frame.status_error(u'Content is to big! (>1MB)')
            return

        bar = req.read(11)  # read first 11 bytes, enough to recognize image
        ih = ImageHeader(bar)
        if not ih.is_supported():
            req.close()
            self.frame.status_error(u'Unsupported content!')
            return

        bar = bar + req.read(1024 * 1024 - 11)  # download at most 1MB
        eof = req.read(1)  # check if EOF was reached
        req.close()
        if eof != '':  # if not, then error
            self.frame.status_error(u'Content is to big! (>1MB)')
            return

        stream = StringIO.StringIO(bar)
        self.image = CoverImage(stream=stream)
        if not self.image.ok:
            self.image = None
            self.frame.status_error(u'Cannot open stream!')
            return

        self.__cleanup_frame()
        assert isinstance(self.image, CoverImage)
        self.frame.show_new_image(self.image)

    def __cleanup_frame(self):
        """TODO: cleanup UI, there will be new image"""

    def __on_button(self, evt):
        print 'clicked: ', evt.GetId()
        if evt.GetId() == CoverFrame.ID_BUTTON_SAVE:
            # self.image
            # def save(self):          #
            # # i = image.tobytes("jpeg", "RGB")
            #     # print 'size: ', len(i)
            #     # import binascii
            #     # print 'image[:12] ', binascii.hexlify( i[:12])
            #     # image.save(path+'tttt.jpg', "JPEG", quality=75)
            #     # f = open(path+'wwww.jpg', 'wb')
            #     # f.write(i)
            #     # f.close()
            print 'save'

    def reset_after_error(self):
        pass


def main():
    app = CoverApp()
    app.MainLoop()


if __name__ == '__main__':
    main()
