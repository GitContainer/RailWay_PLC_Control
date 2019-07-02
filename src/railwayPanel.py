#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        railWayPanel.py
#
# Purpose:     This module is used to provide different function panels for the 
#              rail way hub function.
#              
# Author:      Yuancheng Liu
#
# Created:     2019/07/01
# Copyright:   YC
# License:     YC
#-----------------------------------------------------------------------------
import wx
import wx.grid
import time
import random
import railwayGlobal as gv 

PERIODIC = 500  # how many ms the periodic call back
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelPlaceHolder(wx.Panel):
    """ Place Holder Panel"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        wx.StaticText(self, -1, "Place Holder:", (20, 20))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelInfoGrid(wx.Panel):
    """ Mutli-information panel used to show all sensor's detection situation on the 
        office topview map, sensor connection status and show a Grid to show all the 
        sensor's detection data.
    """
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.nameLbList = []    # PLC name/type list 
        self.gpioLbList = []    # PLC GPIO display list
        self.gridList = []      # PLC data display grid list 
        hsizer = self.buidUISizer()
        self.preSetData()
        self.SetSizer(hsizer)

#-----------------------------------------------------------------------------
    def buidUISizer(self):
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(3):
            vSizer = wx.BoxSizer(wx.VERTICAL)
            nameLb = wx.StaticText(self, label="PLC Name: ".ljust(15))
            self.nameLbList.append(nameLb)
            vSizer.Add(nameLb, flag=flagsR, border=2)
            vSizer.AddSpacer(10)
            gpioLbN = wx.StaticText(self, label="PLC I/O usage: ".ljust(15))
            vSizer.Add(gpioLbN, flag=flagsR, border=2)
            self.gpioLbList.append(gpioLbN)
            vSizer.AddSpacer(10)
            vSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(180, -1), style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
            vSizer.AddSpacer(10)
            grid = wx.grid.Grid(self, -1)
            grid.CreateGrid(8, 4)
            grid.SetRowLabelSize(30)
            grid.SetColLabelSize(22)
            grid.SetColSize(0, 40)
            grid.SetColSize(1, 40)
            grid.SetColSize(2, 40)
            grid.SetColSize(3, 40)
            # Set the label: 
            grid.SetColLabelValue(0, 'IN')
            grid.SetColLabelValue(1, 'Val')
            grid.SetColLabelValue(2, 'OUT')
            grid.SetColLabelValue(3, 'Val')
            vSizer.Add(grid, flag=flagsR, border=2)
            self.gridList.append(grid)
            hsizer.Add(vSizer, flag=flagsR, border=2)
            hsizer.AddSpacer(5)
        return hsizer
#-----------------------------------------------------------------------------
    def preSetData(self):
        """ Pre-set the grid data. """
        for i in range(3):
            dataTuple = gv.PLC_CFG['PLC'+str(i)]
            self.setName(i, 'PLC'+str(i)+ dataTuple[0])
            self.setIOLB(i, dataTuple[3], dataTuple[4])
            for j in range(8):
                self.gridList[i].SetCellValue(j, 0, '%I0.'+str(j))
                self.gridList[i].SetCellValue(j, 1, '0')
                self.gridList[i].SetCellValue(j, 2, '%Q0.'+str(j))
                self.gridList[i].SetCellValue(j, 3, '0')

    def setName(self, idx , name):
        self.nameLbList[idx].SetLabel("PLC Name:".ljust(15)+str(name))

    def setIOLB(self, idx, inputN, outputN):
        lbStr = "PLC I/O usage:  [ " +str(inputN)+'/'+str(outputN)+' ]'
        self.gpioLbList[idx].SetLabel(lbStr)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelPLC(wx.Panel):
    """ PLC panel to show the PLC feedback and contorl the related relay.
    """
    def __init__(self, parent, name, ipAddr):
        """ Init the panel."""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.plcName = name
        self.ipAddr = ipAddr
        self.connected = {'0':'Unconnected', '1':'Connected'}
        self.gpioInList = [0]*8 # PLC GPIO input stuation list. 
        self.gpioLbList = []    # input GPIO data lable display list.
        self.gpioOuList = [False]*8 # PLC GPIO output situation list.
        mainUISizer = self.buidUISizer()
        self.SetSizer(mainUISizer)
        #self.Layout() # must call the layout if the panel size is set to fix.
    
#-----------------------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI sizer"""
        mSizer = wx.BoxSizer(wx.VERTICAL) # main sizer
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        mSizer.AddSpacer(5)
        # Row idx = 0 : set the basic PLC informaiton.
        self.nameLb = wx.StaticText(self, label="PLC Name: ".ljust(15)+self.plcName)
        mSizer.Add(self.nameLb, flag=flagsR, border=2)
        self.ipaddrLb = wx.StaticText(self, label="PLC IPaddr: ".ljust(15)+self.ipAddr)
        mSizer.Add(self.ipaddrLb, flag=flagsR, border=2)
        self.connLb = wx.StaticText(self, label="Connection:".ljust(15)+self.connected['0'])
        mSizer.Add(self.connLb, flag=flagsR, border=2)
        mSizer.AddSpacer(10)
        # Row idx = 1: set the GPIO and feed back of the PLC. 
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(180, -1), style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        mSizer.AddSpacer(10)
        # - row line structure: Input indicator | output label | output button with current status.
        for i in range(8):
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            # M221 doc: IO 0:3 are regular input, IO 4:7 are fast input.
            lbtext = "R_%I0."+str(i) if i < 4 else "F_%I0."+str(i)
            inputLb = wx.StaticText(self, label=lbtext.center(10))
            inputLb.SetBackgroundColour(wx.Colour(120, 120, 120))
            hsizer.Add(inputLb, flag=flagsR, border=2)
            self.gpioLbList.append(inputLb)

            hsizer.AddSpacer(15)
            hsizer.Add(wx.StaticText(self, label=str("%Q0."+str(i)+':').center(10)), flag=flagsR, border=2)
            hsizer.AddSpacer(5)
            outputBt = wx.Button(self, label='OFF', size=(50, 17), name=str(i))
            outputBt.Bind(wx.EVT_BUTTON, self.relayOn)
            hsizer.Add(outputBt, flag=flagsR, border=2)

            mSizer.Add(hsizer, flag=flagsR, border=2)
            mSizer.AddSpacer(3)
        return mSizer

    #-----------------------------------------------------------------------------
    def updateInput(self, idx, status): 
        """ Update the input status for each PLC input indicator."""
        if idx >= 8 or not status in [0,1]: 
            print("PLC panel: the input parameter is not valid") 
            return
        if self.gpioInList[idx] != status:
            self.gpioInList[idx] = status
            # Change the indicator status.
            color = wx.Colour('GREEN') if status else wx.Colour(120, 120, 120)
            self.gpioLbList[idx].SetBackgroundColour(color)
            self.Refresh(False)

    #-----------------------------------------------------------------------------
    def relayOn(self, event): 
        """ Turn on the related ralay based on the user's action and update the 
            button's display situation.
        """
        obj =  event.GetEventObject()
        print("Button idx %s" %str(obj.GetName()))
        idx = int(obj.GetName())
        self.gpioOuList[idx] = not self.gpioOuList[idx]
        [lbtext, color] = ['ON', wx.Colour('Green')] if self.gpioOuList[idx] else ['OFF', wx.Colour(200, 200, 200)]
        obj.SetLabel(lbtext)
        obj.SetBackgroundColour(color)

    #-----------------------------------------------------------------------------
    def OnPaint(self, event):
        """ Draw the whole panel. """
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, 1, 1)
        #dc.SetFont()
        dc.SetTextForeground('Green')
        dc.SetPen(wx.Pen('#CE8349', width=2, style=wx.PENSTYLE_SOLID))
        dc.DrawText(self.plcName, 15, 15 )
        return

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelMap(wx.Panel):
    """RailWay top view map panel to show the rail way contorl situaiton."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(600, 360))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.bitmap = wx.Bitmap(gv.BGPNG_PATH)
        self.wkbitmap = wx.Bitmap(gv.WKPNG_PATH)

        self.bitmapSZ = self.bitmap.GetSize()
        self.toggle = True      # Display toggle flag.     
        self.pplNum = 0         # Number of peopel.
        # Set the tain head and body position.   
        headPos = [550, 160]  # train station start point(train head)
        self.trainPts = [headPos]+[[headPos[0], headPos[1] + 20*(i+1)] for i in range(5)]
        # set the train moving range.
        self.left, self.top, self.right, self.btm = 20, 20, 550, 330
        # set the sensor position.
        self.sensorid = -1
        self.sensorList = [(0, 400, 20), (1, 140, 20), (2, 20, 180),
                           (3, 156, 330), (4, 286, 330), (5, 412, 330)]
        self.toggle = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # gate contorl parameters 
        self.gateCount = 15
        #self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        
    #-----------------------------------------------------------------------------
    def OnPaint(self, event):
        """ Draw the whole panel. """
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, 1, 1)
        # Draw the train on the map.
        dc.SetBrush(wx.Brush('#CE8349'))
        for point in self.trainPts:
            if point[0] == self.right and point[1] != self.top:
                point[1] -= 10
            elif point[1] == self.top and point[0] != self.left:
                point[0] -= 10
            elif point[0] == self.left and point[1] != self.btm:
                point[1] += 10
            elif point[1] == self.btm and point[0] != self.right:
                point[0] += 10
            dc.DrawRectangle(point[0]-7, point[1]-7, 19, 19)
        # High light the sensor which detected the train.
        penColor = 'GREEN' if self.toggle else 'RED'
        dc.SetPen(wx.Pen(penColor, width=4, style=wx.PENSTYLE_LONG_DASH))
        if self.sensorid >= 0:
            sensorPos = self.sensorList[self.sensorid]
            if self.sensorid<2: # top sensors 
                dc.DrawLine(sensorPos[1]+5, sensorPos[2]+10, sensorPos[1]+5, sensorPos[2]+35)
            elif 2 < sensorPos[0]: # left sensors
                dc.DrawLine(sensorPos[1]-5, sensorPos[2]-10, sensorPos[1]-5, sensorPos[2]-35)
            else:   # buttom sensors.
                dc.DrawLine(sensorPos[1]+10, sensorPos[2], sensorPos[1]+35, sensorPos[2])
        self.DrawGate(dc)
        if self.toggle and self.gateCount == 15: 
            dc.DrawBitmap(self.wkbitmap, 250, 7)
        
        #self.DrawStation(dc)
        self.toggle = not self.toggle
    
    #def DrawStation(self, dc):

    #-----------------------------------------------------------------------------
    def DrawGate(self, dc): 
        """ Draw the people passing gate."""

        # Draw the bridge
        if self.gateCount == 15 :
            dc.SetPen(wx.Pen('BLACK', width=1, style=wx.PENSTYLE_DOT))
            dc.SetBrush(wx.Brush(wx.Colour('Black')))
            dc.DrawRectangle(250, 9, 31 ,25)

        penColor = 'GREEN' if self.gateCount == 0 else 'RED'
        dc.SetPen(wx.Pen(penColor, width=1, style=wx.PENSTYLE_DOT))
        dc.DrawLine(250, 0, 250, 45)
        dc.DrawLine(280, 0, 280, 45)

        penColor = 'RED' if self.gateCount == 0 else 'GREEN'

        # Draw the Door 
        doCount = self.gateCount
        dc.SetPen(wx.Pen(penColor, width=2, style=wx.PENSTYLE_SOLID))
        dc.DrawLine(265+doCount, 7, 265+doCount+15, 7)
        dc.DrawLine(265-doCount, 7, 265-doCount-15, 7)
        dc.DrawLine(265+doCount, 37, 265+doCount+15, 37)
        dc.DrawLine(265-doCount, 37, 265-doCount-15, 37)

    #-----------------------------------------------------------------------------
    def checkSensor(self):
        """ Check which sensor has detected the train pass."""
        head, tail = self.trainPts[0], self.trainPts[-1]
        l, r = min(head[0], tail[0]), max(head[0], tail[0])
        t, b = min(head[1], tail[1]), max(head[1], tail[1])
        for sensorPos in self.sensorList:
            if  l <= sensorPos[1] <= r and  t<= sensorPos[2] <=b:
                return sensorPos[0] # return the sensor index
        return -1 # return -1 if there is no sensor detected. 

    #-----------------------------------------------------------------------------
    def periodic(self , now):
        """ periodicly call back to do needed calcualtion/panel update"""
        # Set the detect sensor status related to PLC status
        sensorid = self.checkSensor()
        if self.sensorid != sensorid:
            [idx, state] =[self.sensorid, 0] if self.sensorid >= 0 and sensorid <= 0 else [sensorid, 1]
            if gv.iPlcPanelList[0]:
                gv.iPlcPanelList[0].updateInput(idx, state)
            self.sensorid = sensorid
        # Start to close the gate.
        if self.sensorid == 0: 
            self.gateCount -= 3
        elif self.sensorid == 1: 
            self.gateCount += 3

        if self.gateCount < 0: self.gateCount = 0 
        if  self.gateCount > 15: self.gateCount = 15
        # Update the panel.
        self.updateDisplay()

    #-----------------------------------------------------------------------------
    def OnClick(self, event):
        """ Handle the click event."""
        x, y = event.GetPosition()
        pass

    #-----------------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        self.Refresh(False)
        self.Update()