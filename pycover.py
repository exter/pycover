#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Exter, BADDCAFE 2014'

import os.path
import cStringIO as StringIO
import urllib2
import urlparse
import shutil

import wx
from wx.lib.newevent import NewCommandEvent
from PIL import Image

from droptarget import FTDropTarget as DropTarget

import EnhancedStatusBar as ESB
# import tools


CoverDropEvent, EVT_COVER_DROP_EVENT = NewCommandEvent()

IMAGE_DOWNLOAD_LIMIT = 1024 * 1024  # 1MB
COVER_MAX_SIZE = 100  # 100 KB

#TODO: issue, when there is no action, source file is fine (size and weight) but resized image is bigger we see WARNING icon, it should be OK and only resized size alerted or something like that

class CoverImage(object):
    MIN_DIM = (425, 425)  # minimal cover dimensions
    MAX_DIM = (550, 550)  # maximal cover dimensions
    DEF_DIM = (500, 500)  # default cover dimensions
    DEFAULT_NAME = "cover.jpg"

    ACTION_BACKUP = 'BACKUP'
    ACTION_COPY = 'COPY'
    ACTION_SAVE = 'SAVE'
    ACTION_RENAME = 'RENAME'

    PATH_STATUS_ERROR = 'ERROR'
    PATH_STATUS_OK = 'OK'
    PATH_STATUS_WARNING = 'WARNING'

    FILE_INFO_OK = 'OK'
    FILE_INFO_SAME = 'SAME FIlE'
    FILE_INFO_USED = 'IN USE'
    FILE_INFO_NEW = 'NEW'
    PATH_UNKNOWN = 'UNKNOWN'

    class ImgInf(object):
        def __init__(self):
            self.path = ''
            self.dim = (0, 0)
            self.size = 0
            self.saved = None
            self.path_in_use = None
            self.format = None

    class CAAD(object):  # Cover Actions and Data
        def __init__(self):
            self.actions = []
            self.info = None
            self.path_status = None
            self.file_info = None
            self.cover_src = None
            self.cover_new = None


    def __init__(self, path=None, stream=None):
        self.__initialized = False
        self.__image = None
        self.__src = self.ImgInf()
        self.__new = self.ImgInf()
        self.__data = self.CAAD()

        if path and not stream:
            self.__open_file(path)
        elif stream and not path:
            self.__open_stream(stream)

    def __open_file(self, path):
        try:
            self.__image = Image.open(path)
        except:
            return

        self.__src.size = os.path.getsize(path) / 1024  # Image size in KB
        self.__src.path = path

        self.__new.path = os.path.join(os.path.dirname(path), self.DEFAULT_NAME)
        self.__new.path_in_use = os.path.exists(self.__new.path)

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

        self.__new.size = len(self.__image.tobytes('jpeg', 'RGB')) / 1024  # Image size in KB

        self.__analyze()
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

    def close(self):
        self.__image.close()  # TODO: check if needed?
        # self.__new.saved = True

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
        self.__analyze()

    @property
    def dimensions(self):
        return self.__new.dim

    @property
    def raw_data(self):
        return self.__image.tobytes()

    @property
    def ok(self):
        return self.__initialized

    @property
    def small(self):
        return self.__src.dim < self.MIN_DIM

    @property
    def heavy(self):
        return self.__new.size > self.__src.size or self.__new.size > COVER_MAX_SIZE

    @property
    def compressed(self):
        return self.__new.size < self.__src.size

    @property
    def resized(self):
        return self.__new.dim < self.__src.dim

    @property
    def src_inf(self):
        return {'dim': self.__src.dim, 'size': self.__src.size}

    @property
    def new_inf(self):
        return {'dim': self.__new.dim, 'size': self.__new.size}

    @property
    def __src_is_dst(self):
        return self.__src.path.lower() == self.__new.path.lower()

    @property
    def __renameable(self):
        return self.__src_is_dst and self.__src.path != self.__new.path


    @property
    def actionable(self):
        return len(self.__data.actions) > 0

    def get_actions(self):
        return self.__data.actions

    def get_data(self):
        return self.__data

    def __analyze(self):
        if self.__new.path:
            if self.__new.path_in_use:
                if self.small or self.heavy:
                    if self.__src_is_dst:
                        if self.compressed:
                            self.__data.actions = [self.ACTION_BACKUP, self.ACTION_SAVE]
                            self.__data.info = 'COVER IS EITHER SMALL OR HEAVY BUT CAN BE COMPRESSED'
                            self.__data.path_status = self.PATH_STATUS_OK
                            self.__data.file_info = self.FILE_INFO_SAME
                        else:
                            self.__data.actions = []
                            self.__data.info = 'NOTHING TO DO SRC==DST, COVER IS EITHER SMALL OR HEAVY'
                            self.__data.path_status = self.PATH_STATUS_OK
                            self.__data.file_info = self.FILE_INFO_SAME
                            # self.__data = {
                            #     'actions': [],
                            #     'info': 'NOTHING TO DO SRC==DST, COVER IS EITHER SMALL OR HEAVY',
                            #     'status': 'OK',
                            #     'path': self.CAAD.P_SAME,
                            # }
                    else:
                        self.__data.actions = []
                        self.__data.info = 'COVER IS EITHER SMALL OR HEAVY AND OUTPUT IS IN USE'
                        self.__data.path_status = self.PATH_STATUS_ERROR
                        self.__data.file_info = self.FILE_INFO_USED
                        # self.__data = {
                        #     'actions': [],
                        #     'info': 'COVER IS EITHER SMALL OR HEAVY AND OUTPUT IS IN USE',
                        #     'status': 'ERROR',
                        #     'path': self.CAAD.P_USE,
                        # }
                elif self.resized or self.compressed:
                    if self.__src_is_dst:
                        self.__data.actions = [self.ACTION_BACKUP, self.ACTION_SAVE]
                        self.__data.info = 'COVER CAN BE RESIZED/COMPRESSED'
                        self.__data.path_status = self.PATH_STATUS_OK
                        self.__data.file_info = self.FILE_INFO_SAME
                        # self.__data = {
                        #     'actions': [self.CAAD.ACT_BACKUP, self.CAAD.ACT_SAVE],
                        #     'info': 'COVER CAN BE RESIZED/COMPRESSED',
                        #     'status': 'OK',
                        #     'path': self.CAAD.P_SAME,
                        # }
                    else:
                        self.__data.actions = []
                        self.__data.info = '?ASK? (BACKUP & RESIZE/COMPRESS) - UNSUPPORTED'
                        self.__data.path_status = self.PATH_STATUS_ERROR
                        self.__data.file_info = self.FILE_INFO_USED
                        # self.__data = {
                        #     'actions': [],
                        #     'info': '?ASK? (BACKUP & RESIZE/COMPRESS) - UNSUPPORTED',
                        #     'status': 'ERROR',
                        #     'path': self.CAAD.P_USE,
                        # }
                else:
                    if self.__src_is_dst:
                        if self.__renameable:
                            self.__data.actions = [self.ACTION_RENAME]
                            self.__data.info = 'COVER OK, RENAME FILE'
                            self.__data.path_status = self.PATH_STATUS_OK
                            self.__data.file_info = self.FILE_INFO_OK
                            # self.__data = {
                            #     'actions': [self.CAAD.ACT_RENAME],  #TODO: check if not to delete and save
                            #     'info': 'COVER OK, RENAME FILE',
                            #     'status': 'OK',
                            #     'path': 'OK',
                            # }
                        else:
                            self.__data.actions = []
                            self.__data.info = 'COVER OK'
                            self.__data.path_status = self.PATH_STATUS_OK
                            self.__data.file_info = self.FILE_INFO_OK
                            # self.__data = {
                            #     'actions': [],  #TODO: check if not to delete and save
                            #     'info': 'COVER OK',
                            #     'status': 'OK',
                            #     'path': 'OK',
                            # }
                    else:
                        self.__data.actions = []
                        self.__data.info = '?ASK? (BACKUP & COPY SOURCE TO DESTINATION WITH NEW NAME) - UNSUPPORTED'
                        self.__data.path_status = self.PATH_STATUS_ERROR
                        self.__data.file_info = self.FILE_INFO_USED
                        # self.__data = {
                        #     'actions': [],
                        #     'info': '?ASK? (BACKUP & COPY SOURCE TO DESTINATION WITH NEW NAME) - UNSUPPORTED',
                        #     'status': 'ERROR',
                        #     'path': self.CAAD.P_USE,
                        # }
            else:
                if self.small or self.heavy:
                    if self.__src.path and self.__src.format == 'JPEG' and not self.compressed:
                        self.__data.actions = [self.ACTION_COPY]
                        self.__data.info = 'COPY SOURCE TO DESTINATION WITH NEW NAME'
                        self.__data.path_status = self.PATH_STATUS_OK
                        self.__data.file_info = self.FILE_INFO_NEW
                        # self.__data = {
                        #     'actions': [self.CAAD.ACT_COPY],
                        #     'info': 'COPY SOURCE TO DESTINATION WITH NEW NAME',
                        #     'status': 'OK',  # 'WARNING',
                        #     'path': self.CAAD.P_NEW,
                        # }
                    else:
                        self.__data.actions = [self.ACTION_SAVE]
                        self.__data.info = 'CONVERT&SAVE'
                        self.__data.path_status = self.PATH_STATUS_OK
                        self.__data.file_info = self.FILE_INFO_NEW
                        # self.__data = {
                        #     'actions': [self.CAAD.ACT_SAVE],
                        #     'info': 'CONVERT&SAVE',
                        #     'status': 'OK',  # 'WARNING',
                        #     'path': self.CAAD.P_NEW,
                        # }
                elif self.resized or self.compressed:
                    self.__data.actions = [self.ACTION_SAVE]
                    self.__data.info = 'RESIZE/COMPRESS'
                    self.__data.path_status = self.PATH_STATUS_OK
                    self.__data.file_info = self.FILE_INFO_NEW
                    # self.__data = {
                    #     'actions': [self.CAAD.ACT_SAVE],
                    #     'info': 'RESIZE/COMPRESS',
                    #     'status': 'OK',
                    #     'path': self.CAAD.P_NEW,
                    # }
                else:
                    if self.__src.path and self.__src.format == 'JPEG':
                        self.__data.actions = [self.ACTION_COPY]
                        self.__data.info = 'COPY SOURCE TO DESTINATION WITH NEW NAME'
                        self.__data.path_status = self.PATH_STATUS_OK
                        self.__data.file_info = self.FILE_INFO_NEW
                        # self.__data = {
                        #     'actions': [self.CAAD.ACT_COPY],
                        #     'info': 'COPY SOURCE TO DESTINATION WITH NEW NAME',
                        #     'status': 'OK',
                        #     'path': self.CAAD.P_NEW,
                        # }
                    else:
                        self.__data.actions = [self.ACTION_SAVE]
                        self.__data.info = 'CONVERT&SAVE'
                        self.__data.path_status = self.PATH_STATUS_OK
                        self.__data.file_info = self.FILE_INFO_NEW
                        # self.__data = {
                        #     'actions': [self.CAAD.ACT_SAVE],
                        #     'info': 'CONVERT&SAVE',
                        #     'status': 'OK',
                        #     'path': self.CAAD.P_NEW,
                        # }
        else:
            self.__data.actions = []
            self.__data.info = 'NO DESTINATION PATH'
            self.__data.path_status = self.PATH_STATUS_WARNING
            self.__data.file_info = self.PATH_UNKNOWN
            # self.__data = {
            #     'actions': [],
            #     'info': 'NO DESTINATION PATH',
            #     'status': 'WARNING',
            #     'path': self.CAAD.P_UKN
            # }

        # self.__data.cover_new= self. if self.small or self.heavy else self.CAAD.ST_OK

        return self.actionable

    def execute_actions(self):
        if not self.actionable:
            return

        for act in self.get_actions():
            if act == self.ACTION_BACKUP:
                directory = os.path.dirname(self.__new.path)
                backup = lambda x: os.path.join(directory, 'cover-PyCoverBackup-%02d.jpg' % x)
                i = 0
                for i in range(10):
                    if not os.path.exists(os.path.join(directory, backup(i))): break
                shutil.move(self.__new.path, backup(i))  # backup original file
                self.__new.saved = True
            elif act == self.ACTION_COPY:
                # copy source file to new destination as cover.jpg
                shutil.copy2(self.__src.path, self.__new.path)
                self.__new.saved = True
            elif act == self.ACTION_SAVE:
                self.__image.save(self.__new.path, 'jpeg')
                self.__new.saved = True
            elif act == self.ACTION_RENAME:  # TODO: check if not to delete and save
                rename = self.__src.path + '.rename'
                shutil.move(self.__src.path, rename)  # Cover.jpg -> Cover.jpg.rename
                shutil.move(rename, self.__new.path)  # Cover.jpg.rename -> cover.jpg
                self.__new.saved = True
            else:
                raise UserWarning

        self.__image.close()
        self.__new.saved = True


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


class CoverWXStatusBar(ESB.EnhancedStatusBar):
    def __init__(self, parent):
        ESB.EnhancedStatusBar.__init__(self, parent, style=wx.ST_DOTS_MIDDLE)
        self.SetFieldsCount(3)
        self.SetStatusWidths([50, -1, 125])

        self.__bmp_ok = wx.Bitmap('./res/ok16.png', wx.BITMAP_TYPE_PNG)
        self.__bmp_warning = wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_TOOLBAR, (16, 16))
        self.__bmp_error = wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_TOOLBAR, (16, 16))
        self.__bmp_tick = wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_TOOLBAR, (16, 16))

        self.__status_bmp = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap)
        self.AddWidget(self.__status_bmp)

        panel = wx.Panel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        self.__status_txt = wx.StaticText(panel, wx.ID_ANY, wx.EmptyString)
        bs = wx.BoxSizer(wx.VERTICAL)
        bs.AddStretchSpacer(1)
        bs.Add(self.__status_txt, 0, wx.EXPAND, 0)
        bs.AddStretchSpacer(1)
        panel.SetSizer(bs)
        self.AddWidget(panel, ESB.ESB_EXACT_FIT)

        self.AddWidget(wx.Panel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER), ESB.ESB_EXACT_FIT)  # RESERVED

        self.__bck = [wx.NullBitmap, wx.EmptyString]
        self.__error_status_lc = None

    def path_status(self, img=None, path=''):
        if img and path:
            raise AttributeError

        if img:
            data = img.get_data()

            # bmp = wx.NullBitmap
            if data.path_status == CoverImage.PATH_STATUS_ERROR:
                bmp = self.__bmp_error
            elif data.path_status == CoverImage.PATH_STATUS_WARNING:
                bmp = self.__bmp_warning
            elif data.path_status == CoverImage.PATH_STATUS_OK:
                bmp = self.__bmp_ok
            else:
                raise UserWarning

            self.__status_bmp.SetBitmap(bmp)

            path_info = u' PATH: %s%s'
            file_info = ''
            if data.file_info == CoverImage.FILE_INFO_OK:
                # file_info = ''
                pass
            elif data.file_info == CoverImage.FILE_INFO_SAME:
                if img.actionable:
                    file_info = ' (*)'
                # else:
                #     file_info = ''
            elif data.file_info == CoverImage.FILE_INFO_USED:
                file_info = ' (IN USE)'
            elif data.file_info == CoverImage.FILE_INFO_NEW:
                file_info = ' (NEW)'
            elif data.file_info == CoverImage.PATH_UNKNOWN:
                path_info = u' WARNING: Unknown path!'
            else:
                raise UserWarning

            self.__status_txt.SetLabel(path_info % (img.path, file_info))

        if path:
            self.__status_bmp.SetBitmap(self.__bmp_tick)
            self.__status_txt.SetLabel(u' PATH: %s' % path)

    def error_status(self, msg):
        # TODO: remove if not needed
        # self.__bck = wx.NullBitmap, wx.EmptyString

        if self.__error_status_lc and self.__error_status_lc.IsRunning():
            self.__error_status_lc.Restart()
        else:
            self.__bck = self.__status_bmp.GetBitmap(), self.__status_txt.GetLabelText()
            self.__error_status_lc = wx.CallLater(4399, self.__error_status_cleanup)

        self.__status_bmp.SetBitmap(self.__bmp_error)
        self.__status_txt.SetLabel(u' ERROR: %s' % msg)

    def __error_status_cleanup(self):
        # restore previous status
        self.__status_bmp.SetBitmap(self.__bck[0])
        self.__status_txt.SetLabel(self.__bck[1])

        self.__error_status_lc.Stop()
        self.__error_status_lc = None

    def reset(self):
        if self.__error_status_lc:
            self.__error_status_lc.Stop()
            self.__error_status_lc = None

        self.__status_bmp.SetBitmap(wx.NullBitmap)
        self.__status_txt.SetLabel(wx.EmptyString)


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

        self.__src_sbs = CoverWXStaticBoxSizer(self, u'Source:')
        self.__sizer.Add(self.__src_sbs, 0, wx.EXPAND)

        self.__new_sbs = CoverWXStaticBoxSizer(self, u'Resized:')
        self.__sizer.Add(self.__new_sbs, 0, wx.EXPAND)

        self.__output_sbs = CoverWXStaticBoxSizer(self, u'Output:')
        self.__sizer.Add(self.__output_sbs, 0, wx.EXPAND)
        self.__sizer.Hide(self.__output_sbs)

        self.__sizer.AddStretchSpacer(2)

        box_sizer.Add(self.__sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(box_sizer)

        self.__status_bar = CoverWXStatusBar(self)
        self.SetStatusBar(self.__status_bar)

        self.Layout()
        self.Fit()

    def show_new_image(self, image):
        self.__src_sbs.set_dimension(image.src_inf['dim'])
        self.__src_sbs.set_size(image.src_inf['size'])

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
        self.__src_sbs.alert_dimension(image.small)
        self.__new_sbs.alert_dimension(image.small)
        self.__new_sbs.alert_size(image.heavy)

        if image.small or image.heavy:
            status_icon = wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_TOOLBAR, (32, 32))
        else:
            status_icon = wx.Bitmap('./res/ok32.png', wx.BITMAP_TYPE_PNG)
        self.__bm_status.SetBitmap(status_icon)

        if image.actionable:
            self.__button.SetLabel(u'Save')
            self.__button.SetId(self.ID_BUTTON_SAVE)
            self.__button.Enable(True)
        else:
            self.__button.SetLabel(wx.EmptyString)
            self.__button.SetId(wx.ID_ANY)
            self.__button.Enable(False)

        self.__status_bar.path_status(image)

    def update_path(self, image):
        self.__show_notifications(image)

    def status_error(self, msg):
        self.__status_bar.error_status(msg)

    def show_output_image(self, path):
        img = wx.Image(path)
        bmp = wx.BitmapFromImage(img, wx.BITMAP_TYPE_ANY)
        self.__bm_cover.SetBitmap(bmp)

        dimension = img.GetSize().Get()
        small = dimension < CoverImage.MIN_DIM
        self.__output_sbs.set_dimension(dimension)
        self.__output_sbs.alert_dimension(small)

        size = os.path.getsize(path) / 1024
        heavy = size > COVER_MAX_SIZE
        self.__output_sbs.set_size(size)
        self.__output_sbs.alert_size(heavy)

        if small or heavy:
            status_icon = wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_TOOLBAR, (32, 32))
        else:
            status_icon = wx.Bitmap('./res/ok32.png', wx.BITMAP_TYPE_PNG)
        self.__bm_status.SetBitmap(status_icon)

        self.__button.Enable(True)
        self.__button.SetId(self.ID_BUTTON_CLEAR)
        self.__button.SetLabel(u'Reset')

        self.__sizer.Show(self.__output_sbs)
        self.__sizer.Hide(self.__src_sbs)
        self.__sizer.Hide(self.__new_sbs)

        self.__status_bar.path_status(path=path)

        self.Fit()
        self.Layout()

    def reset(self):
        self.__bm_cover.SetBitmap(wx.NullBitmap)
        self.__bm_status.SetBitmap(wx.NullBitmap)

        self.__button.Enable(False)
        self.__button.SetId(wx.ID_ANY)
        self.__button.SetLabel(wx.EmptyString)

        self.__output_sbs.reset()
        self.__sizer.Hide(self.__output_sbs)

        self.__src_sbs.reset()
        self.__sizer.Show(self.__src_sbs)

        self.__new_sbs.reset()
        self.__sizer.Show(self.__new_sbs)

        self.__status_bar.reset()

        self.Layout()
        self.Fit()


class CoverApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, False)

        self.image = None

        self.frame = CoverFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()

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

        self.frame.reset()
        assert isinstance(self.image, CoverImage)
        self.frame.show_new_image(self.image)

    def __on_dir(self, path):
        if self.image and self.image.actionable:
            self.image.path = path
            self.frame.update_path(self.image)
        else:
            cover_path = os.path.join(path, CoverImage.DEFAULT_NAME)
            if os.path.exists(cover_path) and os.path.isfile(cover_path):
                self.__on_file(cover_path)
            else:
                self.frame.status_error(u'Drop image first!')

    def __on_url(self, url):
        try:  # open url connection
            req = urllib2.urlopen(url)
        except (ValueError, urllib2.URLError), e:
            print e.reason()
            self.frame.status_error(u'urllib2.urlopen exception!')
            return

        try:  # check if we can get length before downloading
            content_length = int(req.info().getheader(u'Content-Length').strip())
        except AttributeError:
            content_length = 0
        if content_length > IMAGE_DOWNLOAD_LIMIT:
            req.close()
            self.frame.status_error(u'Content is to big! (>%dMB)' % (IMAGE_DOWNLOAD_LIMIT / (1024 * 1024)))
            return

        bar = req.read(11)  # read first 11 bytes, enough to recognize image
        ih = ImageHeader(bar)
        if not ih.is_supported():
            req.close()
            self.frame.status_error(u'Unsupported content!')
            return

        bar = bar + req.read(IMAGE_DOWNLOAD_LIMIT - 11)  # download at most 1MB ? (DOWNLOAD_LIMIT)
        eof = req.read(1)  # check if EOF was reached
        req.close()
        if eof != '':  # if not, then error
            self.frame.status_error(u'Content is to big! (>%dMB)' % (IMAGE_DOWNLOAD_LIMIT / (1024 * 1024)))
            return

        stream = StringIO.StringIO(bar)
        self.image = CoverImage(stream=stream)
        if not self.image.ok:
            self.image = None
            self.frame.status_error(u'Cannot open stream!')
            return

        self.frame.reset()
        assert isinstance(self.image, CoverImage)
        self.frame.show_new_image(self.image)

    def __on_button(self, evt):
        if evt.GetId() == CoverFrame.ID_BUTTON_CLEAR:
            # self.image = None
            self.frame.reset()

        elif evt.GetId() == CoverFrame.ID_BUTTON_SAVE:
            self.image.execute_actions()
            if self.image.saved:
                self.frame.show_output_image(self.image.path)
            self.image.close()  # = None
            self.image = None


def main():
    app = CoverApp()
    app.MainLoop()


if __name__ == '__main__':
    main()
