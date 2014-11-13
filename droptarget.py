__author__ = 'Exter, 0xBADDCAFE'

import wx


class FTDropTarget(wx.DropTarget):
    """
    Implements drop target functionality to receive files and text

    receiver - any WX class that can bind to events
    evt - class that comes from wx.lib.newevent.NewCommandEvent call

    class variable ID_DROP_FILE
    class variable ID_DROP_TEXT
    """
    ID_DROP_FILE = wx.NewId()
    ID_DROP_TEXT = wx.NewId()

    def __init__(self, receiver, evt):
        """
        receiver - any WX class that can bind to events
        evt - class that comes from wx.lib.newevent.NewCommandEvent call
        """
        wx.DropTarget.__init__(self)
        self.composite = wx.DataObjectComposite()
        self.text_do = wx.TextDataObject()
        self.file_do = wx.FileDataObject()
        self.composite.Add(self.text_do)
        self.composite.Add(self.file_do)
        self.SetDataObject(self.composite)

        self.receiver = receiver
        self.evt = evt


    def OnData(self, x, y, result):
        """Handles dropping files/text """
        if self.GetData():
            drop_type = self.composite.GetReceivedFormat().GetType()
            if drop_type in (wx.DF_TEXT, wx.DF_UNICODETEXT):
                wx.PostEvent(self.receiver, self.evt(id=self.ID_DROP_TEXT, text=self.text_do.GetText()))
            elif drop_type == wx.DF_FILENAME:
                wx.PostEvent(self.receiver, self.evt(id=self.ID_DROP_FILE, files=self.file_do.GetFilenames()))

        assert isinstance(result, object)
        return result

