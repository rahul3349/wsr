import argparse
from collections import defaultdict
from mmap import mmap
import re  
import wx  
 


# Some classes to use for the notebook pages.  Obviously you would
# want to use something more meaningful for your application, these
# are just for illustration.

class Page(wx.Panel):        
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
    def addText(self, text, pos):
        t = wx.StaticText(self, -1, text, pos)
        return t.GetSize()[0]

    def addRed(self, text, pos):
        t = wx.StaticText(self, -1, text, pos)
        t.SetBackgroundColour((255, 0, 0))
        t.SetForegroundColour((255, 0, 0))



class MainFrame(wx.Frame):
    def __init__(self, ws_list):
        wx.Frame.__init__(self, None, title="Simple Notebook Example")

        self.wsList = ws_list

        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        self.pages = []
        line_width = []
        for k, v in self.wsList.items():
            page = Page(nb)
            start_text_pos_x = 5
            start_text_pos_y = 5
            for k1 in sorted(v):
                v1 = v[k1]
                line_width.append(len(v1))
                start = int(v1[0][0])
                text = v1[1]
                line = 'Line No. : {}'.format(k1)
                page.addText(line, (start_text_pos_x, start_text_pos_y))
                start_text_pos_y = start_text_pos_y + 20
                end_pos = page.addText(text.rstrip(), (start_text_pos_x, start_text_pos_y))
                for i in range(1, len(text) - start):
                    page.addRed('#', (end_pos + i*10, start_text_pos_y))
                start_text_pos_y = start_text_pos_y + 20
                        
            self.pages.append(page)
            # add the pages to the notebook with the label to show on the tab
            nb.AddPage(page, k)

        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        correctionMenuItem = fileMenu.Append(wx.NewId(), "Correct WS",
                                       "Removes white space errors in the file")
        self.Bind(wx.EVT_MENU, self.onCorrect, correctionMenuItem)

        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        if len(line_width) > 0:
            maxWidth = max(line_width) * 100
            self.SetMinSize((maxWidth, -1))
        #self.Fit() 

    def onCorrect(self, event):
        def deleteFromMmap(start,end, data, f):
            length = end - start
            size = len(data)
            newsize = size - length

            data.move(start,end,size-end)
            data.flush()
            f.truncate(newsize)
 
        for k, v in self.wsList.items():
            with open(k, "r+") as f:
                for k1, v1 in v.items():
                    print 'Looking for ',k1
                    mm = mmap(f.fileno(), 0)
                    index = 1
                    while True:
                        line_start = mm.tell()
                        line = mm.readline()
                        if line == '': break
                        if index == k1:
                            print index, ' ',mm[line_start], ' :  ', line.rstrip()
                            pos = v1[0]
                            print pos
                            start = line_start + pos[0]
                            end   = line_start + pos[1]
                            print start, '   ', end
                            deleteFromMmap(start, end, mm, f)
                            break
                        index = index + 1    
                    mm.close()

def parseWS(file='wsr.py'):
    ws_list = defaultdict(list)
    f = open(file)
    ws = re.compile('[ \t\r\f\v]+$')
    index = 1
    for line in f:
        m = ws.search(line)
        if m is not None:
            ws_list[index].append(m.span())
            ws_list[index].append(line)
        index = index + 1
    return ws_list


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="record/replay input events")
    arg_parser.add_argument('filenames', nargs="*",help="input files(multiple files can be provided)")
    options = arg_parser.parse_args()


    ws_list = dict()
    for f in options.filenames:
        ws_list[f] = parseWS(f)
    for k, v in ws_list.items():
        print 'file Name : ', k
        for k1, v1 in v.items():
            print 'Line no.', k1, ' WS cols : ',v1
    
    app = wx.App()
    MainFrame(ws_list).Show()
    app.MainLoop()
