__author__ = 'Exter'

# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun  5 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 725,615 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )

		self.SetSizeHintsSz( wx.Size( 725,615 ), wx.Size( 725,615 ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )

		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer1.SetMinSize( wx.Size( 700,550 ) )
		self.m_bitmap1 = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 550,550 ), wx.RAISED_BORDER )
		self.m_bitmap1.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )
		self.m_bitmap1.SetToolTipString( u"drop image here" )
		self.m_bitmap1.SetMinSize( wx.Size( 550,550 ) )
		self.m_bitmap1.SetMaxSize( wx.Size( 550,550 ) )

		bSizer1.Add( self.m_bitmap1, 0, wx.ALL|wx.FIXED_MINSIZE, 5 )

		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel1.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )
		self.m_panel1.SetMinSize( wx.Size( 100,550 ) )
		self.m_panel1.SetMaxSize( wx.Size( 150,550 ) )

		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		bSizer2.SetMinSize( wx.Size( -1,550 ) )
		self.m_button1 = wx.Button( self.m_panel1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.Size( 150,-1 ), wx.NO_BORDER )
		self.m_button1.SetMinSize( wx.Size( 150,-1 ) )
		self.m_button1.SetMaxSize( wx.Size( 150,-1 ) )

		bSizer2.Add( self.m_button1, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 5 )


		bSizer2.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel1, wx.ID_ANY, u"original:" ), wx.VERTICAL )

		self.m_staticText1 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"size:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )
		sbSizer1.Add( self.m_staticText1, 0, wx.ALL, 5 )

		self.m_textCtrl1 = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl1.Enable( False )

		sbSizer1.Add( self.m_textCtrl1, 0, wx.EXPAND, 5 )

		self.m_staticText2 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"weigth:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		sbSizer1.Add( self.m_staticText2, 0, wx.ALL, 5 )

		self.m_textCtrl2 = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl2.Enable( False )

		sbSizer1.Add( self.m_textCtrl2, 0, wx.EXPAND|wx.FIXED_MINSIZE, 5 )


		bSizer2.Add( sbSizer1, 1, wx.EXPAND, 5 )

		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel1, wx.ID_ANY, u"new:" ), wx.VERTICAL )

		self.m_staticText3 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"size:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		sbSizer2.Add( self.m_staticText3, 0, wx.ALL, 5 )

		self.m_textCtrl3 = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl3.Enable( False )

		sbSizer2.Add( self.m_textCtrl3, 0, wx.EXPAND, 5 )

		self.m_staticText4 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"estimated weight:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		sbSizer2.Add( self.m_staticText4, 0, wx.ALL, 5 )

		self.m_textCtrl4 = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl4.Enable( False )

		sbSizer2.Add( self.m_textCtrl4, 0, wx.EXPAND, 5 )


		bSizer2.Add( sbSizer2, 1, wx.EXPAND, 5 )


		bSizer2.AddSpacer( ( 0, 0), 1, 0, 5 )

		self.m_bitmap2 = wx.StaticBitmap( self.m_panel1, wx.ID_ANY, wx.Bitmap( u"./resources/favicon.ico", wx.BITMAP_TYPE_ICO ), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_bitmap2.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNHIGHLIGHT ) )
		self.m_bitmap2.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )

		bSizer2.Add( self.m_bitmap2, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		self.m_panel1.SetSizer( bSizer2 )
		self.m_panel1.Layout()
		bSizer2.Fit( self.m_panel1 )
		bSizer1.Add( self.m_panel1, 1, wx.ALL|wx.FIXED_MINSIZE, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()
		self.m_statusBar1 = self.CreateStatusBar( 2, wx.ST_SIZEGRIP, wx.ID_ANY )

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


if __name__ == '__main__':
    # wx.App.__init__(self, False)
    #
    #     self.image = None
    #     #bind to drop events
    #     self.Bind(EVT_COVER_DROP_EVENT, self.__drop_handler)
    #
    #     self.frame = CoverFrame()
    #     self.SetTopWindow(self.frame)
    #     self.GetTopWindow().SetMinSize(wx.Size(725,615))
    #     self.frame.Show()

    app = wx.App(False)
    frame = MyFrame1(None)
    app.SetTopWindow(frame)

    frame.Show()
    # app.GetTopWindow().Show()
    # app.mainframe = frame
    app.MainLoop()