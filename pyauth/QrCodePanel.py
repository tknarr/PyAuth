# -*- coding: utf-8 -*-

# Copyright (C) 2017 Silverglass Technical
# Author: Todd Knarr (tknarr)

import wx

import Configuration
from QrCodeImage import QrCodeImage


class QrCodePanel(wx.Panel):
    MIN_BOX = 2
    MAX_BOX = 16
    BOX_STEPS = MAX_BOX - MIN_BOX

    def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.TAB_TRAVERSAL, name = wx.PanelNameStr, uri = None, border = 0):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)

        self.box_size = Configuration.GetQRBoxSize()
        self.uri = uri
        self.border = border
        self.x_loc = border
        self.y_loc = border

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SHOW, self.OnShow)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Minimum-sized image
        bitmap = QrCodeImage(self.uri, QrCodePanel.MIN_BOX).GetImage().ConvertToBitmap()
        self.min_bitmap_size = bitmap.GetSize()
        min_client_size = self.GetClientSizeForBitmapSize(self.min_bitmap_size)
        min_size = self.ClientToWindowSize(min_client_size)
        self.SetMinSize(min_size)
        self.min_frame_size = self.ClientSizeToFrameSize(min_client_size)
        parent.SetMinSize(self.min_frame_size)
        # Maximum-sized image
        bitmap = QrCodeImage(self.uri, QrCodePanel.MAX_BOX).GetImage().ConvertToBitmap()
        self.max_bitmap_size = bitmap.GetSize()
        max_client_size = self.GetClientSizeForBitmapSize(self.max_bitmap_size)
        max_size = self.ClientToWindowSize(max_client_size)
        self.SetMaxSize(max_size)
        self.max_frame_size = self.ClientSizeToFrameSize(max_client_size)
        parent.SetMaxSize(self.max_frame_size)
        # Calculate bitmap sizing increments
        self.bitmap_width_incr = ((self.max_bitmap_size.GetWidth() - self.min_bitmap_size.GetWidth()) /
                                  QrCodePanel.BOX_STEPS)
        self.bitmap_height_incr = ((self.max_bitmap_size.GetHeight() - self.min_bitmap_size.GetHeight()) /
                                   QrCodePanel.BOX_STEPS)

        self.UpdateBitmap()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, self.x_loc, self.y_loc)

    def OnShow(self, event):
        event.Skip()

    def OnSize(self, event):
        new_bitmap_size = wx.Size(event.GetSize().GetWidth() - self.border * QrCodePanel.MAX_BOX,
                                  event.GetSize().GetHeight() - self.border * QrCodePanel.MIN_BOX)
        # Clamp at min and max sizes
        if new_bitmap_size.GetWidth() < self.min_bitmap_size.GetWidth():
            new_bitmap_size.SetWidth(self.min_bitmap_size.GetWidth())
        elif new_bitmap_size.GetWidth() > self.max_bitmap_size.GetWidth():
            new_bitmap_size.SetWidth(self.max_bitmap_size.GetWidth())
        if new_bitmap_size.GetHeight() < self.min_bitmap_size.GetHeight():
            new_bitmap_size.SetHeight(self.min_bitmap_size.GetHeight())
        elif new_bitmap_size.GetHeight() > self.max_bitmap_size.GetHeight():
            new_bitmap_size.SetHeight(self.max_bitmap_size.GetHeight())

        bitmap_size = self.bitmap.GetSize()
        # Determine the direction of change, smaller or larger, based on the change in the smallest dimension
        # of the new size, ie. if width increases and height decreases, we adjust smaller.
        delta_width = new_bitmap_size.GetWidth() - bitmap_size.GetWidth()
        delta_height = new_bitmap_size.GetHeight() - bitmap_size.GetHeight()
        # In practice that means we can only increase the size of the QR code image if both width and height
        # are increased. If either remains unchanged or decreases, we have to either leave the image unchanged
        # or decrease it's size. Of course if both are unchanged, the image is unchanged.
        if delta_width > 0 and delta_height > 0:
            # Increasing size, we find the box size where the next larger size will exceed the allowable
            # size on either axis.
            new_box = self.box_size
            new_size = wx.Size(bitmap_size.GetWidth(), bitmap_size.GetHeight())
            while new_size.GetWidth() + self.bitmap_width_incr <= new_bitmap_size.GetWidth() \
                    and new_size.GetHeight() + self.bitmap_height_incr <= new_bitmap_size.GetHeight() \
                    and new_box < QrCodePanel.MAX_BOX:
                new_box += 1
                new_size.SetWidth(new_size.GetWidth() + self.bitmap_width_incr)
                new_size.SetHeight(new_size.GetHeight() + self.bitmap_height_incr)
        elif delta_width < 0 or delta_height < 0:
            # Decreasing size, we find the box size where the new image first fits within the allowable size
            # and use that.
            new_box = self.box_size - 1
            new_size = wx.Size(bitmap_size.GetWidth() - self.bitmap_width_incr,
                               bitmap_size.GetHeight() - self.bitmap_height_incr)
            while new_size.GetWidth() > new_bitmap_size.GetWidth() \
                    and new_size.GetHeight() > new_bitmap_size.GetHeight() \
                    and new_box > QrCodePanel.MIN_BOX:
                new_box -= 1
                new_size.SetWidth(new_size.GetWidth() - self.bitmap_width_incr)
                new_size.SetHeight(new_size.GetHeight() - self.bitmap_height_incr)
        else:
            new_box = self.box_size
        if new_box != self.box_size:
            self.box_size = new_box
            self.UpdateBitmap()
            Configuration.SetQRBoxSize(self.box_size)

    def GetClientSizeForBitmapSize(self, bitmap_size):
        bitmap_size.IncBy(self.border * 2, self.border * 2)
        return bitmap_size

    def ClientSizeToFrameSize(self, client_size):
        win_size = self.ClientToWindowSize(client_size)
        p = self.GetParent()
        frame_size = p.ClientToWindowSize(win_size)
        return frame_size

    def UpdateBitmap(self):
        self.bitmap = QrCodeImage(self.uri, self.box_size).GetImage().ConvertToBitmap()
        client_size = self.GetClientSizeForBitmapSize(self.bitmap.GetSize())
        self.SetClientSize(client_size)
        self.SetMinClientSize(client_size)
        frame_size = self.ClientSizeToFrameSize(client_size)
        p = self.GetParent()
        p.SetSize(frame_size)
