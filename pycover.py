#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Exter, BADDCAFE 2014'

import os.path
import cStringIO as StringIO
import shutil
import urllib2
import urlparse

import wx
from wx.lib.newevent import NewCommandEvent
from PIL import Image

from droptarget import FTDropTarget as DropTarget


CoverDropEvent, EVT_COVER_DROP_EVENT = NewCommandEvent()

IMAGE_DOWNLOAD_LIMIT = 1024 * 1024


class CoverImage(object):
    MIN_DIM = (425, 425)  # minimal cover dimensions
    MAX_DIM = (550, 550)  # maximal cover dimensions
    DEF_DIM = (500, 500)  # default cover dimensions
    DEFAULT_NAME = "cover.jpg"

    class ImgInf(object):
        def __init__(self):
            self.path = ''
            self.dim = (0, 0)
            self.size = 0
            self.saved = None
            self.path_in_use = None
            self.format = None

    def __init__(self, path=None, stream=None):
        self.__initialized = False
        self.__image = None
        self.__src = self.ImgInf()
        self.__new = self.ImgInf()

        if path and not stream:
            self.__open_file(path)
        elif stream and not path:
            self.__open_stream(stream)

    def __open_file(self, path):
        try:
            self.__image = Image.open(path)
        except:
            return

        self.__src.size = os.path.getsize(path) / 1024
        self.__src.path = path
        self.__src.path_in_use = True
        self.path = os.path.dirname(path)

        self.__open_finalize()

    def __open_stream(self, stream):
        try:
            self.__image = Image.open(stream)
        except:
            return

        stream.seek(0, os.SEEK_END)
        self.__src.size = stream.tell() / 1024

        self.__open_finalize()

    def __open_finalize(self):
        self.__src.format = self.__image.format
        self.__image = self.__image.convert('RGB')

        self.__src.dim = self.__image.size
        self.__new.dim = self.__calculate_new_dim(self.__src.dim)
        if not self.small:
            self.__image = self.__image.resize(self.dimensions, Image.ANTIALIAS)

        self.__new.size = len(self.__jpg_data) / 1024

        self.__initialized = True

    def __calculate_new_dim(self, old_dim):
        if old_dim > self.MAX_DIM:
            new_dim = range(2)  # create list size of two
            idx = old_dim.index(max(old_dim))  # find bigger dimension index
            new_dim[idx] = self.DEF_DIM[idx]  # new bigger dimension set to fixed value
            # calculate second dimension old_dim_x*default_dim_y/old_dim_y (keep original ration)
            new_dim[idx - 1] = int(float(old_dim[idx - 1]) * self.DEF_DIM[idx] / old_dim[idx])
            new_dim = (new_dim[0], new_dim[1])  # new size as tuple
        else:
            new_dim = old_dim

        return new_dim

    def save(self):
        self.__image.save(self.path, 'jpeg')
        # self.__image.close() #TODO: check if needed?
        self.__new.saved = True

    @property
    def saved(self):
        return self.__new.saved if hasattr(self.__new, 'saved') else False

    @property
    def path(self):
        return self.__new.path

    @path.setter
    def path(self, directory):
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise AttributeError
        self.__new.path = os.path.join(directory, self.DEFAULT_NAME)
        self.__new.path_in_use = os.path.exists(self.__new.path)

    @property
    def path_in_use(self):
        return self.__new.path_in_use if self.__new.path else False

    @property
    def dimensions(self):
        return self.__new.dim

    @property
    def raw_data(self):
        return self.__image.tobytes()

    @property
    def __jpg_data(self):
        return self.__image.tobytes('jpeg', 'RGB')

    @property
    def ok(self):
        return self.__initialized

    @property
    def small(self):
        return self.__src.dim < self.MIN_DIM

    @property
    def heavy(self):
        return self.__new.size > self.__src.size or self.__new.size > 100

    @property
    def compressed(self):
        return self.__new.size < self.__src.size

    @property
    def resized(self):
        return self.__new.dim < self.__src.dim

    @property
    def src_inf(self):
        return self.__src.__dict__

    @property
    def new_inf(self):
        return self.__new.__dict__

    def __evaluate_actions(self):
        actions = ['BACKUP', 'SAVE', 'COPY']
        action_detail = ''
        action = ''
        warning = ''
        error = ''
        is_warning = False
        is_error = False
        pass

    # @property
    # def same_file(self):
    #     return self.__src.path == self.__new.path

    # @property
    # def src_has_path(self):
    #     return self.__src.path_in_use #FIXME: change name?

    # @property
    # def new_has_path(self):
    #     return

    def get_action(self):
        action = None

        if not self.__new.path:
            action = 'WARNING_NO_DESTINATION_PATH'
            return action

        if self.small:
            if self.__new.path_in_use:
                if self.__src.path == self.__new.path and self.compressed:
                    action = 'SAVE  # (COMPRESS) !!!WARNING!!!'
                else:
                    action = 'ERROR_SMALL_INPUT_OUTPUT_IN_USE'
            else:
                if self.__src.path and self.__src.format == 'JPEG' and self.heavy:
                    action = 'COPY  # (COPY SOURCE TO DESTINATION WITH NEW NAME)'
                else:
                    action = 'SAVE  # (CONVERT&SAVE)'

            return action

        if self.heavy:
            if self.__new.path_in_use:
                if self.__src.path == self.__new.path and self.compressed:
                    action = 'SAVE  # (COMPRESS) !!!WARNING!!!'
                else:
                    action = 'ERROR_HEAVY_INPUT_OUTPUT_IN_USE'
            else:
                if self.__src.path and self.__src.format == 'JPEG' and not self.compressed:
                    action = 'COPY  # (COPY SOURCE TO DESTINATION WITH NEW NAME)'
                else:
                    action = 'SAVE  # (CONVERT&SAVE)'
            return action

        if self.resized:
            if self.__new.path_in_use:
                if self.__src.path == self.__new.path:
                    action = 'BACKUP&SAVE  # (BACKUP & RESIZE)or ??SAVE_ONLY?? (RESIZE)'
                else:
                    action = 'BACKUP&SAVE  # (BACKUP & RESIZE)!!!WARNING!!! ASK'
            else:
                action = 'SAVE # (RESIZE)'

            return action

        if self.compressed:
            if self.__new.path_in_use:
                if self.__src.path == self.__new.path:
                    action = 'BACKUP&SAVE  # (BACKUP & COMPRESS) or ??COMPRESS_ONLY??'
                else:
                    action = 'BACKUP&SAVE  # (BACKUP & COMPRESS) !!!WARNING!!! ASK'
            else:
                action = 'SAVE  # (COMPRESS)'

            return action

        if self.__new.path_in_use:
            if self.__src.path != self.__new.path:
                action = 'ASK  # (BACKUP & COPY SOURCE TO DESTINATION WITH NEW NAME) !!!WARNING!!!'
        else:
            action = 'COPY  # (COPY SOURCE TO DESTINATION WITH NEW NAME)'

        return action

    def get_action_2(self):
        action = None
        cover_status = 'OK/WARNING'
        button_enabled = True


        if self.__new.path:
            if self.__new.path_in_use:
                if self.small or self.heavy:
                    if self.__src.path == self.__new.path:
                        if self.compressed:
                            action = 'SAVE  # (COMPRESS) !!!WARNING!!!'
                        else:
                            action = 'DO NOTHING'
                    else:
                        action = 'ERROR_&_INPUT_OUTPUT_IN_USE'
                elif self.resized or self.compressed:
                    if self.__src.path == self.__new.path:
                        action = 'BACKUP&SAVE  # (BACKUP & RESIZE/COMPRESS) or ??COMPRESS_ONLY??'
                    else:
                        action = 'BACKUP&SAVE  # (BACKUP & RESIZE/COMPRESS) !!!WARNING!!! ASK'
                else:
                    if self.__src.path != self.__new.path:
                        action = 'ASK  # (BACKUP & COPY SOURCE TO DESTINATION WITH NEW NAME) !!!WARNING!!!'
                        button_enabled = False
            else:
                if self.small or self.heavy:
                    if self.__src.path and self.__src.format == 'JPEG' and not self.compressed:
                        action = 'COPY  # (COPY SOURCE TO DESTINATION WITH NEW NAME)'
                    else:
                        action = 'SAVE  # (CONVERT&SAVE)'

                elif self.resized or self.compressed:
                    action = 'SAVE  # (RESIZE/COMPRESS)'

                else:
                    action = 'COPY  # (COPY SOURCE TO DESTINATION WITH NEW NAME)'
        else:
            action = 'WARNING_NO_DESTINATION_PATH'
            cover_status = '?'
            button_enabled = False
            warning = True
            error = False

        return action


# FIXME: JPEG header checker
class ImageHeader(object):
    def __init__(self, header):
        self.header = header
        self.type = ''

    def __is_jpeg(self):
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

    def __is_png(self):
        if self.header[0:8] == '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
            self.type = 'PNG'
            return True
        else:
            return False

    def __is_gif(self):
        if self.header[0:6] == 'GIF89a':
            self.type = 'GIF'
            return True
        else:
            return False

    def __is_bmp(self):
        if self.header[0:2] == 'BM':
            self.type = 'BMP'
            return True
        else:
            return False

    def __is_tiff(self):
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
        return self.__is_bmp() or \
            self.__is_gif() or \
            self.__is_jpeg() or \
            self.__is_png() or \
            self.__is_tiff()


class CoverWXStaticBoxSizer(wx.StaticBoxSizer):
    def __init__(self, parent, label):
        wx.StaticBoxSizer.__init__(self, wx.StaticBox(parent, wx.ID_ANY, label), wx.VERTICAL)
        self.__sb = self.GetStaticBox()

        self.__dim_label = wx.StaticText(parent, wx.ID_ANY, u'Dimension:')
        self.Add(self.__dim_label, 0, wx.ALL, 5)
        self.__dim_value = wx.TextCtrl(parent, id=wx.ID_ANY, style=wx.TE_CENTER)
        self.__dim_value.Enable(False)
        self.Add(self.__dim_value, 0, wx.EXPAND)

        self.__size_label = wx.StaticText(parent, wx.ID_ANY, u'Size:')
        self.Add(self.__size_label, 0, wx.ALL, 5)
        self.__size_value = wx.TextCtrl(parent, id=wx.ID_ANY, style=wx.TE_CENTER)
        self.__size_value.Enable(False)
        self.Add(self.__size_value, 0, wx.EXPAND)

    def set_label(self, label):
        self.__sb.SetLabel(label)

    def alert_dimension(self, alert=True, colour=wx.RED):
        self.__dim_label.SetForegroundColour(colour if alert else wx.BLACK)

    def alert_size(self, alert=True, colour=wx.RED):
        self.__size_label.SetForegroundColour(colour if alert else wx.BLACK)

    def __clear_values(self):
        self.__dim_value.Clear()
        self.__size_value.Clear()

    def __clear_alerts(self):
        self.__dim_label.SetForegroundColour(wx.BLACK)
        self.__size_label.SetForegroundColour(wx.BLACK)

    def reset(self):
        self.__clear_alerts()
        self.__clear_values()

    def set_dimension(self, dim):
        self.__dim_value.SetValue('%dx%d px' % (dim[0], dim[1]))

    def set_size(self, size):
        self.__size_value.SetValue('%s KB' % size)


class CoverFrame(wx.Frame):
    ID_BUTTON_SAVE = wx.NewId()
    ID_BUTTON_CLEAR = wx.NewId()

    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title='PyCover ver 0.1', pos=wx.DefaultPosition,
                          size=(-1, -1), style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER)

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW))

        box_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.__bm_cover = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size(550, 550),
                                          wx.RAISED_BORDER)
        self.__bm_cover.SetToolTipString(u'...drop image here...')
        self.__bm_cover.SetDropTarget(DropTarget(wx.GetApp(), CoverDropEvent))

        box_sizer.Add(self.__bm_cover, 0, wx.ALL | wx.FIXED_MINSIZE, 5)

        self.__sizer = wx.BoxSizer(wx.VERTICAL)

        self.__button = wx.Button(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(100, -1), wx.NO_BORDER)
        self.__button.Enable(False)
        self.__sizer.Add(self.__button, 0, wx.CENTER, 0)

        self.__sizer.AddStretchSpacer(1)
        self.__bm_status = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size(32, 32))
        self.__sizer.Add(self.__bm_status, 0, wx.CENTER | wx.ALL, 5)

        self.__source_sbs = CoverWXStaticBoxSizer(self, u'Source:')
        self.__sizer.Add(self.__source_sbs, 0, wx.EXPAND)

        self.__new_sbs = CoverWXStaticBoxSizer(self, u'Resized:')
        self.__sizer.Add(self.__new_sbs, 0, wx.EXPAND)

        self.__output_sbs = CoverWXStaticBoxSizer(self, u'Output:')
        self.__sizer.Add(self.__output_sbs, 0, wx.EXPAND)
        self.__sizer.Hide(self.__output_sbs)

        self.__sizer.AddStretchSpacer(2)

        box_sizer.Add(self.__sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(box_sizer)

        # TODO: http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.StatusBar.html#SetStatusStyles
        self.__status_bar = self.CreateStatusBar(2)
        self.__status_bar.SetStatusWidths([40, -1])

        self.Layout()
        self.Fit()

        self.__cl = None

    def show_new_image(self, image):
        if self.__cl:
            self.__cl.Stop()

        self.__source_sbs.set_dimension(image.src_inf['dim'])
        self.__source_sbs.set_size(image.src_inf['size'])

        self.__new_sbs.set_dimension(image.new_inf['dim'])
        self.__new_sbs.set_size(image.new_inf['size'])

        img = wx.EmptyImage(image.dimensions[0], image.dimensions[1])
        img.SetData(image.raw_data)
        bmp = wx.BitmapFromImage(img, wx.BITMAP_TYPE_ANY)
        self.__bm_cover.SetBitmap(bmp)

        self.__show_notifications(image)

        self.Refresh()
        self.Layout()

    def __show_notifications(self, image):
        button_enable = True
        status_icon = wx.Bitmap('./res/ok22.png', wx.BITMAP_TYPE_PNG)

        if image.path:
            msg = ' %s (%s)' % (image.path, 'IN USE' if image.path_in_use else 'NEW')
            self.__update_status(u' Path:', msg)
        else:
            self.__update_status(u'WARN:', u' Unknown path!')
            button_enable = False
            # status_icon = wx.ArtProvider.GetBitmap(wx.ART_WARNING)

        self.__source_sbs.alert_dimension(image.small)
        self.__new_sbs.alert_dimension(image.small)
        self.__new_sbs.alert_size(image.heavy)

        if image.small or image.heavy:
            if image.path_in_use and not image.resized:
                status_icon = wx.ArtProvider.GetBitmap(wx.ART_ERROR)
                button_enable = False
            else:
                status_icon = wx.ArtProvider.GetBitmap(wx.ART_WARNING)

        self.__bm_status.SetBitmap(status_icon)
        if button_enable:
            self.__button.SetLabel(u'Save')
            self.__button.SetId(self.ID_BUTTON_SAVE)
            self.__button.Enable(True)
        else:
            self.__button.SetLabel(wx.EmptyString)
            self.__button.SetId(wx.ID_ANY)
            self.__button.Enable(False)

        print image.get_action()
        print image.get_action_2()

    def update_path(self, image):
        self.__show_notifications(image)
        self.Refresh()
        self.Layout()

    def __update_status(self, status, msg):
        self.__status_bar.SetStatusText(status, 0)
        self.__status_bar.SetStatusText(msg, 1)

    def __update_path(self, path, in_use=False):
        if path:
            msg = ' %s (%s)' % (path, 'IN USE' if in_use else 'NEW')
            self.__update_status(u' Path:', msg)
        else:
            self.__update_status(u'WARN:', u' Unknown path!')

    def status_error(self, msg):
        self.a1 = wx.EmptyString
        self.a2 = wx.EmptyString
        self.a3 = wx.NullBitmap

        if self.__cl and self.__cl.IsRunning():
            self.__cl.Restart()
        else:
            self.a1 = self.__status_bar.GetStatusText(0)
            self.a2 = self.__status_bar.GetStatusText(1)
            self.a3 = self.__bm_status.GetBitmap()
            self.__cl = wx.CallLater(4399, self.__status_error_finished)

        self.__bm_status.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_ERROR))
        self.__update_status(u' ERR:', ' ' + msg)

    def __status_error_finished(self):
        self.__bm_status.SetBitmap(self.a3)
        self.__update_status(self.a1, self.a2)
        self.__cl.Stop()
        self.__cl = None

    def show_output_image(self, path):
        img = wx.Image(path)
        bmp = wx.BitmapFromImage(img, wx.BITMAP_TYPE_ANY)
        self.__bm_cover.SetBitmap(bmp)
        size = img.GetSize()

        self.__button.Enable(True)
        self.__button.SetId(self.ID_BUTTON_CLEAR)
        self.__button.SetLabel(u'Reset')

        self.__output_sbs.set_dimension(size)
        self.__output_sbs.set_size((os.path.getsize(path) / 1024))
        self.__sizer.Show(self.__output_sbs)

        self.__sizer.Hide(self.__source_sbs)
        self.__sizer.Hide(self.__new_sbs)

        self.Fit()
        self.Layout()

    def reset(self):
        self.Layout()
        self.Fit()


class CoverApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, False)

        self.image = None

        self.frame = CoverFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()

        # bind to drop events
        self.Bind(EVT_COVER_DROP_EVENT, self.__drop_handler)
        self.Bind(wx.EVT_BUTTON, self.__on_button)

    def __drop_handler(self, evt):
        self.frame.Raise()

        if evt.GetId() == DropTarget.ID_DROP_FILE:
            if len(evt.files) > 1:
                self.frame.status_error(u'Drop one item only!')
                return
            path = evt.files[0]
            if os.path.exists(path):
                # wx.CallAfter(self.__on_path, path)
                self.__on_path(path)

        elif evt.GetId() == DropTarget.ID_DROP_TEXT:
            url = urlparse.urlparse(evt.text)
            if url.scheme:
                # wx.CallAfter(self.__on_url, url.geturl())
                self.__on_url(url.geturl())
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

    def __on_dir(self, path):
        if self.image:
            self.image.path = path
            self.frame.update_path(self.image)
        else:
            self.frame.status_error(u'Drop image first!')

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
        if content_length > IMAGE_DOWNLOAD_LIMIT:
            req.close()
            self.frame.status_error(u'Content is to big! (>1MB)')
            return

        bar = req.read(11)  # read first 11 bytes, enough to recognize image
        ih = ImageHeader(bar)
        if not ih.is_supported():
            req.close()
            self.frame.status_error(u'Unsupported content!')
            return

        bar = bar + req.read(IMAGE_DOWNLOAD_LIMIT - 11)  # download at most 1MB
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
        print 'do clean up ? here ?'

    def __on_button(self, evt):
        print 'evt.GetId(): ', evt.GetId()

        if evt.GetId() == CoverFrame.ID_BUTTON_CLEAR:
            # self.frame.reset()
            self.image = None
            pass
        elif evt.GetId() == CoverFrame.ID_BUTTON_SAVE:
            # if self.image.small or self.image.heavy:
            #     if not self.image.path_in_use:
            #         # if we have source file and it is JPEG file
            #         if os.path.exists(self.image.src_inf['path']) and self.image.src_inf['format'] == 'JPEG':
            #             # copy source file to new destination as cover.jpg
            #             shutil.copy2(self.image.src_inf['path'], self.image.path)
            #         else:
            #             self.image.save()
            # elif self.image.path_in_use:
            #     directory = os.path.dirname(self.image.path)
            #     backup = lambda x: os.path.join(directory, 'cover-PyCoverBackup-%02d.jpg' % x)
            #     for i in range(10):
            #         if not os.path.exists(os.path.join(directory, backup(i))): break
            #     shutil.move(self.image.path, backup(i))  # backup original file
            #     self.image.save()
            # else:
            #     self.image.save()

            if self.image.saved:
                self.frame.show_output_image(self.image.path)

                # elif evt.GetId() == CoverFrame.ID_BUTTON_CLEAR:
                # print 'CoverFrame.ID_BUTTON_CLEAR'


def main():
    app = CoverApp()
    app.MainLoop()


if __name__ == '__main__':
    main()
