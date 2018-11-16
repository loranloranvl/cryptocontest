import wx
import wx.lib.sized_controls as sc
import wx.lib.mixins.inspection as WIT
import io

from wx.lib.pdfviewer import pdfViewer, pdfButtonPanel

class PDFViewer(sc.SizedFrame):
    def __init__(self, parent, **kwds):
        super(PDFViewer, self).__init__(parent, **kwds)

        paneCont = self.GetContentsPane()
        self.buttonpanel = pdfButtonPanel(paneCont, wx.ID_ANY,
                                wx.DefaultPosition, wx.DefaultSize, 0)
        self.buttonpanel.SetSizerProps(expand=True)
        self.viewer = pdfViewer(paneCont, wx.ID_ANY, wx.DefaultPosition,
                                wx.DefaultSize,
                                wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)

        self.viewer.SetSizerProps(expand=True, proportion=1)

        # introduce buttonpanel and viewer to each other
        self.buttonpanel.viewer = self.viewer
        self.viewer.buttonpanel = self.buttonpanel

def viewPdfBytes(file):
    app = WIT.InspectableApp(redirect=False)
    pdfV = PDFViewer(None, size=(1200, 800))
    file_like_object = io.BytesIO(file)
    pdfV.viewer.LoadFile(file_like_object)
    pdfV.Show()
    app.MainLoop()