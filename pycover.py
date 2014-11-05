#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Exter'

import wx
import wx.lib.newevent
# from wx import xr
from PIL import Image as PILImage

img_file = r'C:\\Users\\Exter\\Downloads\\aaaa.jpg'


#========================  D R O P ====================================
CoverDragEvent, EVT_COVER_DROP_EVENT = wx.lib.newevent.NewCommandEvent()
ID_COVER_DROP_FILE = wx.NewId()
ID_COVER_DROP_TEXT = wx.NewId()


class CoverDropTarget(wx.DropTarget):

    def __init__(self, *args, **kwargs):
        wx.DropTarget.__init__(self, *args, **kwargs)
        self.composite = wx.DataObjectComposite()
        self.textDropData = wx.TextDataObject()
        self.fileDropData = wx.FileDataObject()
        self.composite.Add(self.textDropData)
        self.composite.Add(self.fileDropData)
        self.SetDataObject(self.composite)

    def OnDrop(self, x, y):
        return True

    def OnData(self, x, y, result):
        self.GetData()
        format_type, format_id = self.GetReceivedFormatAndId()
        if format_type in (wx.DF_TEXT, wx.DF_UNICODETEXT):
            return self.OnTextDrop()
        elif format_type == wx.DF_FILENAME:
            return self.OnFileDrop()
        else:
            return wx.DragError

    def GetReceivedFormatAndId(self):
        format = self.composite.GetReceivedFormat()
        format_type = format.GetType()
        try:
            format_id = format.GetId()  # May throw exception on unknown formats
        except Exception:
            format_id = None
        return format_type, format_id

    def OnTextDrop(self):
        evt = CoverDragEvent(id=ID_COVER_DROP_TEXT, text=self.textDropData.GetText())
        wx.PostEvent(wx.GetApp(), evt)
        return wx.DragCopy

    def OnFileDrop(self):
        evt = CoverDragEvent(id=ID_COVER_DROP_FILE, files=self.fileDropData.GetFilenames())
        wx.PostEvent(wx.GetApp(), evt)
        return wx.DragCopy

#~~~~~~~~~~~~~~~~~~  D R O P ~~~~~~~~~~~~~~~~~~

class CoverFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title='PyCover', pos=wx.DefaultPosition,
                          size=(wx.Size(685, 600)), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        loc = wx.IconLocation(r'C:\Python27\python.exe', 0)
        self.SetIcon(wx.IconFromLocation(loc))
        # ico = wx.Icon(r'C:\Users\Exter\Downloads\download-icon_small.png', wx.BITMAP_TYPE_PNG)
        # self.SetIcon(ico)
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        # bSizer1.SetMinSize( wx.Size( 550,650 ) )
        self.m_bitmap1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img_file, wx.BITMAP_TYPE_JPEG), wx.DefaultPosition,
                                         wx.Size(550, 550),
                                         wx.RAISED_BORDER)
        # self.SetSizerAndFit(bSizer1, self)
        self.m_bitmap1.SetToolTipString(u"drop image here")
        self.m_bitmap1.SetMinSize(wx.Size(550, 550))
        self.m_bitmap1.SetMaxSize(wx.Size(550, 550))
        self.m_bitmap1.SetDropTarget(CoverDropTarget())

        bSizer1.Add(self.m_bitmap1, 0, wx.ALL, 5)

        self.m_panel1 = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.m_button1 = wx.Button(self.m_panel1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.m_button1, 0, wx.ALL, 5)

        self.m_button2 = wx.Button(self.m_panel1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.m_button2, 0, wx.ALL, 5)

        self.m_panel1.SetSizer(bSizer2)
        self.m_panel1.Layout()
        bSizer2.Fit(self.m_panel1)
        bSizer1.Add(self.m_panel1, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        #self.Centre(wx.BOTH)

        # wx.Frame.__init__(self, None, wx.ID_ANY, 'pyCover',
        # style = wx.DEFAULT_FRAME_STYLE | wx.WANTS_CHARS |
        # wx.NO_FULL_REPAINT_ON_RESIZE)
        #
        #
        # self.SetMinSize(500,500)
        # panel = wx.Panel(self, wx.ID_ANY)
        # # p = PILImage.open(img_file)
        # # print p.size
        # # a = wx.Image(img_file, wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        # # bitmap = wx.StaticBitmap(self, wx.ID_ANY, a)
        # png = wx.StaticBitmap(panel, -1, wx.Bitmap(img_file, wx.BITMAP_TYPE_ANY))
        # # bitmap = wx.Bitmap('C:\\Users\\Exte\\rDownloads\\aaaa.jpg')
        # # self.SetIcon(wx.Icon('C:\Users\Exter\Downloads\download-icon_small.png', wx.BITMAP_TYPE_PNG))
        # # mainbox = wx.BoxSizer(wx.HORIZONTAL)
        # # self.SetSizer(mainbox)
        #
        # # leftPanel = wx.Panel(self, wx.ID_ANY, size=(500,500))
        # # leftPanel.MinSize = (500,500)
        # # leftPanel.MaxSize = (500,500)
        # # rightPanel = wx.Panel(self, wx.ID_ANY)
        # # mainbox.Add(leftPanel, 1)
        # # mainbox.Add(rightPanel, 1)
        # # wx.Button(rightPanel, -1, "Button1")
        # # wx.Button(rightPanel, -1, "Button2")
        #
        # # b1 = wx.BoxSizer(wx.HORIZONTAL)
        # # b1.Add(wx.Button())
        # # b1.Add(wx.Button())
        # # self.AddChild(mainPanel)
        #
        # # panel = wx.Panel(self, wx.ID_ANY)
        # # jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # # # bitmap upper left corner is in the position tuple (x, y) = (5, 5)
        # # wx.StaticBitmap(self, -1, jpg1, (10 + jpg1.GetWidth(), 5), (jpg1.GetWidth(), jpg1.GetHeight()))

    def new_image(self, img):
        self.m_bitmap1.SetBitmap(img)
        #dt = self.m_bitmap1.GetDropTarget()
        #self.m_bitmap1.SetMinSize(wx.Size(550, 550))
        #self.m_bitmap1.SetMaxSize(wx.Size(550, 550))
        #self.Center(wx.BOTH)
        self.Refresh()
        self.Layout()
        pass

class ImageHeader(object):

    def __init__(self, header):
        self.header = header
        self.type = ''

    def _is_jpg(self):
        if self.header[:4] == '\xff\xd8\xff\xe0' and \
                        self.header[6:] == 'JFIF\0':
            self.type = 'JPG'
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

    def Check(self):
        return self._is_bmp() or \
               self._is_gif() or \
               self._is_jpg() or \
               self._is_png()


class CoverApp(wx.App):

    def __init__(self):
        wx.App.__init__(self, False)
        #self.frame = None

    def OnInit(self):
        # wx.App.OnInit(self)
        # self.SetAppName('PyCover')

        #bind to drop events
        self.Bind(EVT_COVER_DROP_EVENT, self.handler)

        self.frame = CoverFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

    def handler(self, evt):
        if evt.GetId() == ID_COVER_DROP_TEXT:
            import urlparse
            url = urlparse.urlparse(evt.text)
            if 'http' in url.scheme:
                print 'url: ', url.geturl()
        elif evt.GetId() == ID_COVER_DROP_FILE:
            files = evt.files
            if len(files) > 1:
                return
            file = files[0]
            import os
            import os.path
            if os.path.isfile(file):
                print 'file: ', file
                self.on_file(file)
            elif os.path.isdir(file):
                print 'dir: ', file

    def on_file(self, file):
        img = PILImage.open(file, 'r')
        wximg = wx.EmptyImage(img.size[0], img.size[1])
        wximg.SetData(img.convert('RGB').tostring())
        #wximg.SetAlphaData(img.convert('RGBA').tostring()[3:4])
        bmp = wx.BitmapFromImage(wximg, wx.BITMAP_TYPE_ANY)

        self.frame.new_image(bmp)
        """
        image = wx.EmptyImage(pil.size[0], pil.size[1])
    image.SetData(pil.convert('RGB').tostring())
    return image
        """

def main():
    app = CoverApp()
    app.MainLoop()


if __name__ == '__main__':
    main()
