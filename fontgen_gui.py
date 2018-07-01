#!/usr/bin/env python3

#--------1---------2---------3---------4---------5---------6---------7---------8
PROGRAM_TITLE = 'Embedded Font Generator'
LOREM_IPSUM = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. \
Donec varius lobortis ligula. Suspendisse a accumsan tortor, eget lictus \
metus. Suspendisse mollis consequat sem ultrices porta. Aenean ante massa, \
hendreit maximus gravida a, varius a sapiel.'

import matplotlib.font_manager as fm
import warnings
import wx

from fontgen import *

#--------1---------2---------3---------4---------5---------6---------7---------8
class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)

        # font list
        self.lblFonts = wx.StaticText(self, wx.ID_ANY, "Font Family")
        e = wx.FontEnumerator()
        e.EnumerateFacenames()
        flist = e.GetFacenames()
        self.lbxFonts = wx.ListBox(self, -1, wx.DefaultPosition, (300,100),
                flist, wx.LB_SINGLE)
        # family
        self.lblFamily = wx.StaticText(self, -1, "Family")
        self.choFamily = wx.Choice(self, -1, choices=['Default', 'Decorative',
            'Roman', 'Script', 'Swiss', 'Modern', 'Teletype'])
        self.choFamily.SetSelection(0)
        # FIXME: this has no meaning for now
        self.lblFamily.Show(False)
        self.choFamily.Show(False)
        # style
        self.lblStyle = wx.StaticText(self, -1, "Style")
        self.choStyle = wx.Choice(self, -1, choices=['Normal','Italic','Slant'])
        self.choStyle.SetSelection(0)
        # weight
        self.lblWeight = wx.StaticText(self, -1, "Weight")
        self.choWeight = wx.Choice(self, -1, choices=['Normal','Light','Bold'])
        self.choWeight.SetSelection(0)
        # direction
        self.lblFontDir = wx.StaticText(self, -1, "Direction")
        self.choFontDir = wx.Choice(self, -1, choices=['Horizontal','Vertical'])
        self.choFontDir.SetSelection(0)
        # point size
        self.lblPntSize = wx.StaticText(self, -1, "Point Size")
        self.spnPntSize = wx.SpinCtrl(self, -1, min=8, max=24, initial=10)
        # generate
        self.btnGenFont = wx.Button(self, -1, "Generate LCD Font")
        # sample
        self.txtLorem = wx.TextCtrl(self, -1, LOREM_IPSUM,
                style=wx.TE_READONLY|wx.TE_MULTILINE)

        self.__set_properties()
        self.__do_layout()
        self.__initialize()

    def __set_properties(self):
        self.SetTitle(PROGRAM_TITLE)

    def __do_layout(self):
        sizer_lhs = wx.BoxSizer(wx.VERTICAL)
        sizer_lhs.Add(self.lblFonts, 0,
                wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_CENTRE|wx.ALL, 4)
        sizer_lhs.Add(self.lbxFonts, 1, wx.EXPAND|wx.ALL, 4)

        sizer_g = wx.FlexGridSizer(5, 2, 8, 8)
        sizer_g.Add(self.lblFamily,0,wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT,0)
        sizer_g.Add(self.choFamily,0,wx.EXPAND,0)
        sizer_g.Add(self.lblStyle,0,wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT,0)
        sizer_g.Add(self.choStyle,0,wx.EXPAND,0)
        sizer_g.Add(self.lblWeight,0,wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT,0)
        sizer_g.Add(self.choWeight,0,wx.EXPAND,0)
        sizer_g.Add(self.lblFontDir,0,wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT,0)
        sizer_g.Add(self.choFontDir,0,wx.EXPAND,0)
        sizer_g.Add(self.lblPntSize,0,wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT,0)
        sizer_g.Add(self.spnPntSize,0,wx.EXPAND,0)
        sizer_g.AddGrowableCol(0)

        sizer_rhs = wx.BoxSizer(wx.VERTICAL)
        sizer_rhs.Add(sizer_g, 0, wx.EXPAND, 0)
        sizer_rhs.Add((20,20))
        sizer_rhs.Add(self.btnGenFont, 0, wx.ALL | wx.EXPAND, 4)

        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h.Add(sizer_lhs, 0, wx.ALL | wx.EXPAND, 4)
        sizer_h.Add(sizer_rhs, 1, wx.ALL | wx.EXPAND, 4)

        sizer_v = wx.BoxSizer(wx.VERTICAL)
        sizer_v.Add(sizer_h, 1, wx.ALL|wx.EXPAND, 4)
        sizer_v.Add(self.txtLorem, 1, wx.ALL|wx.EXPAND, 4)

        self.SetSizer(sizer_v)
        sizer_v.Fit(self)
        self.Layout()

    def __initialize(self):

        self.Bind(wx.EVT_LISTBOX, self.OnSelectFont,  self.lbxFonts)
        self.Bind(wx.EVT_CHOICE, self.OnChangeFont, self.choFamily)
        self.Bind(wx.EVT_CHOICE, self.OnChangeFont, self.choStyle)
        self.Bind(wx.EVT_CHOICE, self.OnChangeFont, self.choWeight)
        self.Bind(wx.EVT_SPINCTRL, self.OnChangeFont, self.spnPntSize)
        self.Bind(wx.EVT_BUTTON, self.OnGenerateFont, self.btnGenFont)

        # promote UserWarning as error
        warnings.filterwarnings('error')
        # default font file name
        self.fontfname = None

    def OnSelectFont(self, evt=None):
        self.UpdateSample()

    def OnChangeFont(self, evt=None):
        self.UpdateSample()

    def OnGenerateFont(self, evt=None):
        if self.fontfname is None:
            wx.MessageBox('Select a font first.')
            return
        else:
            generate_font_file(self.fontfname,
                    ftype = self.choFontDir.GetStringSelection().lower(),
                    psize = self.spnPntSize.GetValue())


    def UpdateSample(self):
        # face name
        face = self.lbxFonts.GetStringSelection()
        # family
        if self.choFamily.GetStringSelection() == 'Default':
            wxfamily = wx.FONTFAMILY_DEFAULT
        elif self.choFamily.GetStringSelection() == 'Decorative':
            wxfamily = wx.FONTFAMILY_DECORATIVE
        elif self.choFamily.GetStringSelection() == 'Roman':
            wxfamily = wx.FONTFAMILY_ROMAN
        elif self.choFamily.GetStringSelection() == 'Script':
            wxfamily = wx.FONTFAMILY_SCRIPT
        elif self.choFamily.GetStringSelection() == 'Swiss':
            wxfamily = wx.FONTFAMILY_SWISS
        elif self.choFamily.GetStringSelection() == 'Modern':
            wxfamily = wx.FONTFAMILY_MODERN
        elif self.choFamily.GetStringSelection() == 'Teletype':
            wxfamily = wx.FONTFAMILY_TELETYPE
        else:
            wx.MessageBox("Unknown family type selected.")
        # style
        if self.choStyle.GetStringSelection() == 'Normal':
            wxstyle = wx.FONTSTYLE_NORMAL
            style = 'normal'
        elif self.choStyle.GetStringSelection() == 'Italic':
            wxstyle = wx.FONTSTYLE_ITALIC
            style = 'italic'
        elif self.choStyle.GetStringSelection() == 'Slant':
            wxstyle = wx.FONTSTYLE_SLANT
            style = 'oblique'
        else:
            wx.MessageBox("Unknown font style selected.")
        # weight
        if self.choWeight.GetStringSelection() == 'Normal':
            wxweight = wx.FONTWEIGHT_NORMAL
            weight = 'normal'
        elif self.choWeight.GetStringSelection() == 'Light':
            wxweight = wx.FONTWEIGHT_LIGHT
            weight = 'light'
        elif self.choWeight.GetStringSelection() == 'Bold':
            wxweight = wx.FONTWEIGHT_BOLD
            weight = 'bold'
        # point size
        psize = self.spnPntSize.GetValue()

        # find the font file using matplotlib.font_manager
        mfont = fm.FontProperties(family=face,style=style,weight=weight)
        try:
            self.fontfname = fm.findfont(mfont)
        except UserWarning:
            #wx.MessageBox("TTF/OTF file for \'{}\' are not found.".format(face))
            self.btnGenFont.Disable()
            self.fontfname = None
            return
        else:
            self.btnGenFont.Enable()
            # select font
            font = wx.Font(psize, wxfamily, wxstyle, wxweight, False, face)

            # redraw the sample text
            self.txtLorem.SetLabel(LOREM_IPSUM);
            self.txtLorem.SetFont(font);


#--------1---------2---------3---------4---------5---------6---------7---------8

if __name__ == "__main__":
    app = wx.App()

    frame = MyFrame(None, -1, PROGRAM_TITLE)
    frame.Show()

    app.MainLoop()
