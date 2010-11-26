#    WiFiScan - Scan wireless networks and show reception level through time
#    Copyright (C) 2010  Simon Murgelj
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    wlantools module needed, get it from Christophe Berger's page: http://chris.berger.cx/PyS60/PyS60
#

import appuifw,e32,sysinfo,graphics,time,key_codes,math,sys
SIS_VERSION = "0.11.23"

class WiFiScan:
  def closeCanvas(self):
    appuifw.app.body=self.oldBody
    appuifw.app.title=self.oldTitle
    appuifw.app.screen=self.oldScreenSize
    self.canvas=None
    self.workImg=None
    appuifw.app.exit_key_handler=None
  
  def exitKeyHandler(self):
    self.exitFlag += 1
  
  def __init__(self):
    # user settings
    
    # colors; (0,0,0)=black; (255,255,255)=white; (r,g,b)
    self.colorBackground=(0,0,0) # background color
    self.colorBorder=(40,40,100) # border color
    self.colorMinMax=(80,80,80) # min - max area color
    self.colorLast=(255,40,40) # last dBm line color
    self.colorText=(255,255,40) # color of text displayed
    self.colorTextInvalid=(255,40,40) # color of invalid text displayed
    self.colorTimer=(0,150,0) # color of timer on top
    self.colorGraphPoint=(255,0,0) # color or graph points in DETAILS view
    self.colorGraphPointOthers=(60,20,100) # color or graph points of unselected networks in DETAILS view
    self.colorGraphMarkers=(80,80,80) # color of graph lines (-70, -80, ...) in DETAILS view
    
    # numbers
    self.numberFont=0 # number of font (don't overdo it!) (-1 is usualy digital)
    self.numberFontSize=10 # font size
    self.numberScreenPercentDBM=0.30 # right side screen width percentage for dBm min-max scale
    self.numberMinDBM=-100 # lowest dBm on scale (-60 to -80 typical for 802.11)
    self.numberMaxDBM=-40 # highest dBm on scale
    self.numberRefreshSecs=11.0 # refresh interval, in seconds
    self.numberGraphSeparation=3 # x separation from 2 seperate points on graph in DETAILS view
    self.numberGraphLineWidth=2 # line width on graph in DETAILS view
    
    # global settings
    self.screenSize=sysinfo.display_pixels()
    self.exitFlag=0 # time to exit?
    self.lastRefresh=0 # last time of data refresh
    self.BSSIDs={} # data of all Access Points
    self.SSIDs={} # summary of APs by SSID
    self.lastTimeID=0 # ID by last time ob data refresh
    self.selectedMenu='SSID' # SSID, BSSID, DETAILS
    self.selectedSSID='' # SSID selected in menu
    self.selectedBSSID='' # BSSID selected in menu
    self.showDetailsData=1 # toggle- show data in DETAILS view, or just graph(s)
    self.showAllNetworks=1 # toggle- filter by SSID
    self.keyDown='' # current(last) key pressed
    
    # save old screen
    self.oldScreenSize=appuifw.app.screen
    self.oldTitle=appuifw.app.title
    self.oldBody=appuifw.app.body
    
    # new screen
    appuifw.app.screen='full'
    appuifw.app.title=u"Gizmo_X's WiFiScan"
    
    print "*******************************"
    print "*** Gizmo_X's PyS60 WiFiScan ***"
    print "*******************************"
    print "WifiScan  Copyright (C) 2010  Simon Murgelj"
    print "This program comes with ABSOLUTELY NO WARRANTY;"
    print "This is free software, and you are welcome to"
    print "redistribute it under certain conditions;"
    print "(GNU/GPLv3 license)"
    print ""
    print "up/down: move through networks"
    print "right, center: go to next menu"
    print "left: go to previous menu"
    print "right_soft: toggle - show all networks"
    print "left_soft: exit (with prompt)"
    print ""
    
    self.lastRefresh=time.clock()
    self.refreshData()
    while self.exitFlag == 1:
      e32.ao_sleep(0.1)
      if abs(time.clock() - self.lastRefresh) > 1.0:
        self.exitFlag = 0
    
    self.canvas=appuifw.Canvas(redraw_callback=self.redraw, event_callback=self.keyEvent)
    self.workImg=graphics.Image.new(self.screenSize)
    appuifw.app.body=self.canvas
  
  
  def keyEvent(self, event):
    if event['type'] == appuifw.EEventKeyDown:
      if event['scancode'] == key_codes.EScancodeUpArrow:
        self.keyDown = 'up'
      elif event['scancode'] == key_codes.EScancodeDownArrow:
        self.keyDown = 'down'
      elif event['scancode'] == key_codes.EScancodeLeftArrow:
        self.keyDown = 'left'
      elif event['scancode'] == key_codes.EScancodeRightArrow:
        self.keyDown = 'right'
      elif event['scancode'] == key_codes.EScancodeSelect:
        self.keyDown = 'select'
      elif event['scancode'] == key_codes.EScancodeRightSoftkey:
        self.keyDown = 'rightsoft'
      elif event['scancode'] == key_codes.EScancodeLeftSoftkey:
        self.keyDown = 'leftsoft'
      else:
        self.keyDown = 'other'
  
  
  def refreshData(self):
    self.lastTimeID=time.clock()
    wlans=wlantools.scan(False)
    # for each WiFi network found:
    for wlanx in wlans:
      # prepare AP data for saving 
      saveData={}
      saveData['TimeID']=self.lastTimeID
      saveData['SSID']=wlanx['SSID']
      saveData['SecurityMode']=wlanx['SecurityMode']
      saveData['ConnectionMode']=wlanx['ConnectionMode']
      saveData['Channel']=wlanx['Channel']
      saveData['LastRxDBM']=wlanx['RxLevel']
      saveData['BestRxDBM']=wlanx['RxLevel']
      saveData['WorstRxDBM']=wlanx['RxLevel']
      saveData['RxDBMs']=[wlanx['RxLevel']]
      
      if wlanx['BSSID'] in self.BSSIDs:
        oldSD=self.BSSIDs[wlanx['BSSID']]
        # check min and max values
        if oldSD['BestRxDBM'] > saveData['BestRxDBM']:
          saveData['BestRxDBM']=oldSD['BestRxDBM']
        if oldSD['WorstRxDBM'] < saveData['WorstRxDBM']:
          saveData['WorstRxDBM']=oldSD['WorstRxDBM']
        # add previous dBms
        saveData['RxDBMs'].extend(oldSD['RxDBMs'])
        # delete too old/too many
        if len(saveData['RxDBMs'])*self.numberGraphSeparation > self.screenSize[0]:
          saveData['RxDBMs']=saveData['RxDBMs'][0:self.screenSize[0]]
      
      # finally save data
      self.BSSIDs[wlanx['BSSID']]=saveData
      
      # prepare SSID summary data for saving
      saveData2 = {}
      saveData2['TimeID']=self.lastTimeID
      saveData2['LastRxDBMs']=[saveData['LastRxDBM']]
      saveData2['BestRxDBM']=saveData['BestRxDBM']
      saveData2['WorstRxDBM']=saveData['WorstRxDBM']
      saveData2['BSSIDs']=[wlanx['BSSID']]

      # check with old data
      if wlanx['SSID'] in self.SSIDs:
        oldSD2=self.SSIDs[wlanx['SSID']]
        if oldSD2['BestRxDBM'] > saveData2['BestRxDBM']:
          saveData2['BestRxDBM']=oldSD2['BestRxDBM']
        if oldSD2['WorstRxDBM'] < saveData2['WorstRxDBM']:
          saveData2['WorstRxDBM']=oldSD2['WorstRxDBM']
        if wlanx['BSSID'] in oldSD2['BSSIDs']:
          saveData2['BSSIDs']=oldSD2['BSSIDs']
        else:
          saveData2['BSSIDs'].extend(oldSD2['BSSIDs'])
        if oldSD2['TimeID'] == saveData2['TimeID']:
          saveData2['LastRxDBMs'].extend(oldSD2['LastRxDBMs'])
      
      # finally save data
      self.SSIDs[wlanx['SSID']]=saveData2
    
    # add RxDBMs one element to missing networks
    for bssidx in self.BSSIDs.keys():
      if self.BSSIDs[bssidx]['TimeID'] != self.lastTimeID:
        self.BSSIDs[bssidx]['RxDBMs'].insert(0, -1000)
    
    # remove old networks without data
    for bssidx in self.BSSIDs.keys():
      if self.BSSIDs[bssidx]['TimeID'] != self.lastTimeID:
        if (time.clock() - self.BSSIDs[bssidx]['TimeID'])/self.numberRefreshSecs*self.numberGraphSeparation > self.screenSize[0]:
          self.SSIDs[self.BSSIDs[bssidx]['SSID']]['BSSIDs'].remove(bssidx)
          if len(self.SSIDs[self.BSSIDs[bssidx]['SSID']]['BSSIDs']) == 0:
            del self.BSSIDs[bssidx]
  
  
  def redraw(self,rect):
    if rect == (0,0,self.screenSize[0],1) and (self.exitFlag < 1):
      linePoints=((0,0),(self.screenSize[0] * min(1,max(0,(time.clock() - self.lastRefresh) / self.numberRefreshSecs)),0))
      self.workImg.line(linePoints, outline=self.colorTimer, width=2)
    else:
      # background fill
      self.workImg.clear(self.colorBackground)
      
      # prepare fonts
      numFont=(appuifw.available_fonts()[self.numberFont],self.numberFontSize)
      numFontBig=(appuifw.available_fonts()[self.numberFont],int(self.numberFontSize*2))
      
      # precalculate font heights (in pixels)
      ((x1, y1, x2, y2), dummy, dummy) = self.workImg.measure_text(u'pqjPQJ', font=numFontBig)
      numFontBigHeight=y2-y1
      ((x1, y1, x2, y2), dummy, dummy) = self.workImg.measure_text(u'pqjPQJ', font=numFont)
      numFontHeight=y2-y1
      numFontCenterY=self.screenSize[1]/2 + numFontBigHeight/2
      
      # precalculate min-max area limits
      numDiffDBMMinMax=self.numberMaxDBM-self.numberMinDBM
      numDiffDBMMinMax=max(numDiffDBMMinMax,1)
      numMinYMinMax=int(self.screenSize[0] * (1 - self.numberScreenPercentDBM)) + 3
      numMaxYMinMax=self.screenSize[0] - 3
      numDiffYMinMax=numMaxYMinMax-numMinYMinMax
      
      # exit flag clear?
      if self.exitFlag > 0:
        if (len(self.keyDown) > 0) and (self.keyDown != 'rightsoft'):
          self.exitFlag -= 1
          self.keyDown=''
      
      # show all toggle
      if self.keyDown == 'leftsoft':
        self.showAllNetworks = not self.showAllNetworks
      
      # next/prev menu selection
      if self.selectedMenu=='SSID':
        if (self.keyDown == 'right') or (self.keyDown == 'select'):
          self.selectedMenu='BSSID'
          self.selectedBSSID=''
          self.keyDown=''
      
      elif self.selectedMenu=='BSSID':
        if self.keyDown == 'left':
          self.selectedMenu='SSID'
          self.keyDown=''
        elif (self.keyDown == 'right') or (self.keyDown == 'select'):
          self.selectedMenu='DETAILS'
          self.showDetailsData=1
          self.keyDown=''
      
      elif self.selectedMenu=='DETAILS':
        if self.keyDown == 'left':
          self.selectedMenu='BSSID'
          self.keyDown=''
        elif self.keyDown == 'right':
          self.showDetailsData = not self.showDetailsData
          self.keyDown=''
      
      if self.selectedMenu=='SSID':
        # sort SSIDs by descending LastRxDBMs, last seen first
        sorSSIDs=[]
        arrWork=[]
        for ssidx, valx in self.SSIDs.iteritems():
          if valx['TimeID'] == self.lastTimeID:
            valx['SSID']=ssidx
            arrWork.append([max(valx['LastRxDBMs']),valx])
        arrWork.sort()
        arrWork.reverse()
        sorSSIDs.extend(arrWork)
        arrWork=[]
        for ssidx, valx in self.SSIDs.iteritems():
          if valx['TimeID'] != self.lastTimeID:
            valx['SSID']=ssidx
            arrWork.append([max(valx['LastRxDBMs']),valx])
        arrWork.sort()
        arrWork.reverse()
        sorSSIDs.extend(arrWork)
        
        # find index of selected SSID
        numIndexSelSSID=0
        if len(self.selectedSSID) != 0:
          for i in range(0, len(sorSSIDs)):
            if sorSSIDs[i][1]['SSID'] == self.selectedSSID:
              numIndexSelSSID=i
              break
        if len(sorSSIDs) > 0:
          self.selectedSSID = sorSSIDs[numIndexSelSSID][1]['SSID']
      
      elif (self.selectedMenu=='BSSID') or (self.selectedMenu=='DETAILS'):
        # sort BSSIDs descending LastRxDBMs, last seen first
        sorBSSIDs=[]
        arrWork=[]
        for bssidx, valx in self.BSSIDs.iteritems():
          if valx['TimeID'] == self.lastTimeID:
            if (self.showAllNetworks) or (valx['SSID']==self.selectedSSID):
              valx['BSSID']=bssidx
              arrWork.append([valx['LastRxDBM'],valx])
        arrWork.sort()
        arrWork.reverse()
        sorBSSIDs.extend(arrWork)
        arrWork=[]
        for bssidx, valx in self.BSSIDs.iteritems():
          if valx['TimeID'] != self.lastTimeID:
            if (self.showAllNetworks) or (valx['SSID']==self.selectedSSID):
              valx['BSSID']=bssidx
              arrWork.append([valx['LastRxDBM'],valx])
        arrWork.sort()
        arrWork.reverse()
        sorBSSIDs.extend(arrWork)
      
        # find index of selected BSSID
        numIndexSelBSSID=0
        if (len(self.selectedBSSID) == 0) and (self.showAllNetworks):
          self.selectedBSSID = self.SSIDs[self.selectedSSID]['BSSIDs'][0]
        if len(self.selectedBSSID) != 0:
          for i in range(0, len(sorBSSIDs)):
            if sorBSSIDs[i][1]['BSSID'] == self.selectedBSSID:
              numIndexSelBSSID=i
              break
        if len(sorBSSIDs) > 0:
          self.selectedBSSID = sorBSSIDs[numIndexSelBSSID][1]['BSSID']
      
      # up/down change selection
      if self.selectedMenu=='SSID':
        if (self.keyDown == 'up') and (len(sorSSIDs) > 0):
          numIndexSelSSID=(numIndexSelSSID-1)%len(sorSSIDs)
          self.keyDown = ''
          self.selectedSSID = sorSSIDs[numIndexSelSSID][1]['SSID']
        elif (self.keyDown == 'down') and (len(sorSSIDs) > 0):
          numIndexSelSSID=(numIndexSelSSID+1)%len(sorSSIDs)
          self.keyDown = ''
          self.selectedSSID = sorSSIDs[numIndexSelSSID][1]['SSID']
      elif (self.selectedMenu=='BSSID') or (self.selectedMenu=='DETAILS'):
        if (self.keyDown == 'up') and (len(sorBSSIDs) > 0):
          numIndexSelBSSID=(numIndexSelBSSID-1)%len(sorBSSIDs)
          self.keyDown = ''
          self.selectedBSSID = sorBSSIDs[numIndexSelBSSID][1]['BSSID']
          self.selectedSSID = sorBSSIDs[numIndexSelBSSID][1]['SSID']
        elif (self.keyDown == 'down') and (len(sorBSSIDs) > 0):
          numIndexSelBSSID=(numIndexSelBSSID+1)%len(sorBSSIDs)
          self.keyDown = ''
          self.selectedBSSID = sorBSSIDs[numIndexSelBSSID][1]['BSSID']
          self.selectedSSID = sorBSSIDs[numIndexSelBSSID][1]['SSID']
      
      # clear keyDown, not needed
      self.keyDown=''
      
      # draw selected (center) element
      numCurrY = numFontCenterY
      # check for empty list
      if len(self.SSIDs) == 0:
        uText=u'!!! NO WIRELESS NETWORKS FOUND!'
        self.workImg.text((3,numCurrY),uText,self.colorTextInvalid,numFontBig)
      elif self.exitFlag > 0:
        uText=u'!!!  PRESS AGAIN TO EXIT'
        self.workImg.text((3,numCurrY),uText,self.colorTextInvalid,numFontBig)
        numCurrY += numFontBigHeight + 3
        uText=u'!!!  OR ANY OTHER KEY TO RETURN'
        self.workImg.text((3,numCurrY),uText,self.colorTextInvalid,numFontBig)
      else:
        if (self.selectedMenu=='SSID') or (self.selectedMenu=='BSSID'):
          # selected element first, on center
          if self.selectedMenu=='SSID':
            currEle=sorSSIDs[numIndexSelSSID%len(sorSSIDs)][1]
          else:
            currEle=sorBSSIDs[numIndexSelBSSID%len(sorBSSIDs)][1]
          # SSID text
          if currEle['TimeID'] == self.lastTimeID:
            if self.selectedMenu=='SSID':
              uText=currEle['SSID'] + unicode(' ( ' + str(max(currEle['LastRxDBMs'])) + ' )')
            else:
              uText=currEle['BSSID'] + unicode(' ( ' + str(currEle['LastRxDBM']) + ' )')
            self.workImg.text((3,numCurrY),uText,self.colorText,numFontBig)
          else:
            if self.selectedMenu=='SSID':
              uText=currEle['SSID']
            else:
              uText=currEle['BSSID']
            self.workImg.text((3,numCurrY),uText,self.colorTextInvalid,numFontBig)
          # clear too long text
          rectPoints=((int(self.screenSize[0] * (1 - self.numberScreenPercentDBM) + 1), numCurrY - numFontBigHeight - 3), (self.screenSize[0], numCurrY + 6))
          self.workImg.rectangle(rectPoints, fill=self.colorBackground)
          # border
          rectPoints=((0, numCurrY - numFontBigHeight - 3), (self.screenSize[0]-1, numCurrY + 5))
          self.workImg.rectangle(rectPoints, outline=self.colorBorder, width=2)
          # delimiter line
          linePoints=((int(self.screenSize[0] * (1 - self.numberScreenPercentDBM)), numCurrY - numFontBigHeight - 3), (int(self.screenSize[0] * (1 - self.numberScreenPercentDBM)), numCurrY + 4))
          self.workImg.line(linePoints, outline=self.colorBorder, width=2)
          # min - max area - painted
          numMin = min(numMaxYMinMax,max(numMinYMinMax,int(numMinYMinMax + numDiffYMinMax * (currEle['WorstRxDBM'] - self.numberMinDBM) / numDiffDBMMinMax)))
          numMax = min(numMaxYMinMax,max(numMinYMinMax,int(numMinYMinMax + numDiffYMinMax * (currEle['BestRxDBM'] - self.numberMinDBM) / numDiffDBMMinMax)))
          if numMin == numMax:
            numMax += 1      
          rectPoints=((numMin, numCurrY - numFontBigHeight), (numMax, numCurrY + 3))
          self.workImg.rectangle(rectPoints, fill=self.colorMinMax)
          # lines for last dBm
          if (self.selectedMenu=='SSID') and (currEle['TimeID'] == self.lastTimeID):
            for dbmx in currEle['LastRxDBMs']:
              numY = min(numMaxYMinMax,max(numMinYMinMax,int(numMinYMinMax + numDiffYMinMax * (dbmx - self.numberMinDBM) / numDiffDBMMinMax)))
              linePoints=((numY, numCurrY - numFontBigHeight), (numY, numCurrY + 1))
              self.workImg.line(linePoints, outline=self.colorLast, width=2)
          elif self.selectedMenu=='BSSID':
            numY = min(numMaxYMinMax,max(numMinYMinMax,int(numMinYMinMax + numDiffYMinMax * (currEle['LastRxDBM'] - self.numberMinDBM) / numDiffDBMMinMax)))
            linePoints=((numY, numCurrY - numFontBigHeight), (numY, numCurrY + 1))
            self.workImg.line(linePoints, outline=self.colorLast, width=2)
          # min - max area - levels dots
          for numDBM in range(math.ceil(self.numberMinDBM/10.0)*10.0,math.floor(self.numberMaxDBM/10.0)*10.0+0.1,10.0):
            numDot = min(numMaxYMinMax,max(numMinYMinMax,int(numMinYMinMax + numDiffYMinMax * (numDBM - self.numberMinDBM) / numDiffDBMMinMax)))
            self.workImg.point((numDot, numCurrY - numFontBigHeight - 1), outline=self.colorBorder, width=2)
            self.workImg.point((numDot, numCurrY + 2), outline=self.colorBorder, width=2)
          
          # find first position
          numOffset=0
          while numCurrY >= -2:
            numOffset -= 1
            if numOffset == -1:
              numCurrY -= numFontBigHeight + 8
            else:
              numCurrY -= numFontHeight + 5
            if (self.selectedMenu=='SSID' and (numIndexSelSSID+numOffset+1)%len(sorSSIDs) == 0) or (self.selectedMenu=='BSSID' and (numIndexSelBSSID+numOffset+1)%len(sorBSSIDs) == 0):
              numCurrY -= numFontHeight + 5
          
          # loop from beginning to the end
          while numCurrY <= self.screenSize[1] + numFontHeight:
            numOffset += 1
            
            # skip blank (under/overflow) element
            if ((self.selectedMenu=='SSID') and (numIndexSelSSID+numOffset)%len(sorSSIDs) == 0) or ((self.selectedMenu=='BSSID') and (numIndexSelBSSID+numOffset)%len(sorBSSIDs) == 0):
              numCurrY += numFontHeight + 5
            
            # set correct position for offset
            if numOffset == 0:
              numCurrY += numFontBigHeight + 8 + numFontHeight + 9
              numOffset += 1
              # skip blank (under/overflow) element
              if ((self.selectedMenu=='SSID') and (numIndexSelSSID+numOffset)%len(sorSSIDs) == 0) or ((self.selectedMenu=='BSSID') and (numIndexSelBSSID+numOffset)%len(sorBSSIDs) == 0):
                numCurrY += numFontHeight + 5
            else:
              numCurrY += numFontHeight + 5
            
            # draw current element
            if self.selectedMenu=='SSID':
              currEle=sorSSIDs[(numIndexSelSSID+numOffset)%len(sorSSIDs)][1]
            else:
              currEle=sorBSSIDs[(numIndexSelBSSID+numOffset)%len(sorBSSIDs)][1]
            # SSID text
            if currEle['TimeID'] == self.lastTimeID:
              if self.selectedMenu=='SSID':
                uText=currEle['SSID'] + unicode(' ( ' + str(max(currEle['LastRxDBMs'])) + ' )')
              else:
                uText=currEle['BSSID'] + unicode(' ( ' + str(currEle['LastRxDBM']) + ' )')
              self.workImg.text((3,numCurrY),uText,self.colorText,numFont)
            else:
              if self.selectedMenu=='SSID':
                uText=currEle['SSID']
              else:
                uText=currEle['BSSID'] + unicode(' ( ' + str(currEle['LastRxDBM']) + ' )')
              self.workImg.text((3,numCurrY),uText,self.colorTextInvalid,numFont)
            # clear too long text
            rectPoints=((int(self.screenSize[0] * (1 - self.numberScreenPercentDBM) + 1), numCurrY - numFontHeight), (self.screenSize[0], numCurrY + 2))
            self.workImg.rectangle(rectPoints, fill=self.colorBackground)
            # border
            rectPoints=((0, numCurrY - numFontHeight - 1), (self.screenSize[0]-1, numCurrY + 3))
            self.workImg.rectangle(rectPoints, outline=self.colorBorder, width=1)
            # delimiter line
            linePoints=((int(self.screenSize[0] * (1 - self.numberScreenPercentDBM)), numCurrY - numFontHeight - 1), (int(self.screenSize[0] * (1 - self.numberScreenPercentDBM)), numCurrY + 3))
            self.workImg.line(linePoints, outline=self.colorBorder, width=1)
            # min - max area
            numMin = min(numMaxYMinMax,max(numMinYMinMax,int(numMinYMinMax + numDiffYMinMax * (currEle['WorstRxDBM'] - self.numberMinDBM) / numDiffDBMMinMax)))
            numMax = min(numMaxYMinMax,max(numMinYMinMax,int(numMinYMinMax + numDiffYMinMax * (currEle['BestRxDBM'] - self.numberMinDBM) / numDiffDBMMinMax)))
            if numMin == numMax:
              numMax += 1
            rectPoints=((numMin, numCurrY - numFontHeight), (numMax, numCurrY + 2))
            self.workImg.rectangle(rectPoints, fill=self.colorMinMax)
            # lines for last dBm
            if (self.selectedMenu=='SSID') and (currEle['TimeID'] == self.lastTimeID):
              for dbmx in currEle['LastRxDBMs']:
                numY = min(numMaxYMinMax,max(numMinYMinMax,int(numMinYMinMax + numDiffYMinMax * (dbmx - self.numberMinDBM) / numDiffDBMMinMax)))
                linePoints=((numY, numCurrY - numFontHeight), (numY, numCurrY))
                self.workImg.line(linePoints, outline=self.colorLast, width=2)
            elif self.selectedMenu=='BSSID':
              numY = min(numMaxYMinMax,max(numMinYMinMax,int(numMinYMinMax + numDiffYMinMax * (currEle['LastRxDBM'] - self.numberMinDBM) / numDiffDBMMinMax)))
              linePoints=((numY, numCurrY - numFontHeight), (numY, numCurrY))
              self.workImg.line(linePoints, outline=self.colorLast, width=2)
            # min - max area - levels dots
            for numDBM in range(math.ceil(self.numberMinDBM/10.0)*10.0,math.floor(self.numberMaxDBM/10.0)*10.0+0.1,10.0):
              numDot = min(numMaxYMinMax,max(numMinYMinMax,int(numMinYMinMax + numDiffYMinMax * (numDBM - self.numberMinDBM) / numDiffDBMMinMax)))
              self.workImg.point((numDot, numCurrY - numFontHeight), outline=self.colorBorder, width=1)
              self.workImg.point((numDot, numCurrY + 1), outline=self.colorBorder, width=1)
        
        elif self.selectedMenu=='DETAILS':
          # check for a valid BSSID ID
          if len(self.selectedBSSID) == 0:
            self.selectedMenu='BSSID'
            if len(sorBSSIDs) == 0:
              self.selectedMenu='SSID'
          else:
            # at the top, texts
            # prepare properties to show
            currEle=self.BSSIDs[self.selectedBSSID]
            showData=[]
            showData.append(['BSSID',self.selectedBSSID])
            showData.append(['SSID',currEle['SSID']])
            if abs(time.clock()-currEle['TimeID']) < (self.numberRefreshSecs*1.9):
              showData.append(['Last seen','LIVE'])           
            elif abs(time.clock()-currEle['TimeID']) < 60:
              showData.append(['Last seen',str(int(abs(time.clock()-currEle['TimeID']))) + ' seconds ago'])
            else:
              showData.append(['Last seen',str(int(abs(time.clock()-currEle['TimeID'])/6.0)/10.0) + ' minutes ago'])
            showData.append(['Security mode',currEle['SecurityMode']])
            showData.append(['Connection mode',currEle['ConnectionMode']])            
            showData.append(['Channel number',str(currEle['Channel'])])

            # find and append channel numbers
            channelNums=[]
            for bssidx in sorBSSIDs:
              channelNums.append(bssidx[1]['Channel'])
            channelNums.sort()
            if len(channelNums) > 1:
              if channelNums.count(currEle['Channel'])>1:
                showData[-1][1] += ' ' + ('!' * channelNums.count(currEle['Channel'])) + ' '
              showData[-1][1] += '   ('
              for chno in channelNums:
                showData[-1][1] += ' ' + str(chno)
              showData[-1][1] += ' )'
              showData[-1][1] = unicode(showData[-1][1])
            
            numCurrY = 0
            if self.showDetailsData:
              for val1, val2 in showData:
                # set correct position
                numCurrY += numFontHeight + 5
                # text 1
                uText=unicode(val1 + ': ')
                self.workImg.text((3,numCurrY),uText,self.colorText,numFont)
                # clear too long text
                rectPoints=((int(self.screenSize[0] * 0.5 + 1), numCurrY - numFontHeight), (self.screenSize[0], numCurrY + 2))
                self.workImg.rectangle(rectPoints, fill=self.colorBackground)
                # text 2
                uText=unicode(val2)
                self.workImg.text((int(self.screenSize[0] * 0.5 + 3),numCurrY),uText,self.colorText,numFont)
                # border
                rectPoints=((0, numCurrY - numFontHeight - 1), (self.screenSize[0]-1, numCurrY + 3))
                self.workImg.rectangle(rectPoints, outline=self.colorBorder, width=1)
                # delimiter line
                linePoints=((int(self.screenSize[0] * 0.5), numCurrY - numFontHeight - 1), (int(self.screenSize[0] * 0.5), numCurrY + 3))
                self.workImg.line(linePoints, outline=self.colorBorder, width=1)
            else:
              strOneLine='| '
              for val1, val2 in showData:
                # text 2 concatenate
                strOneLine += val2 + ' | '
              # set correct position
              numCurrY += numFontHeight + 5
              # one line text
              self.workImg.text((3,numCurrY),unicode(strOneLine),self.colorText,numFont)
              # border
              rectPoints=((0, numCurrY - numFontHeight - 1), (self.screenSize[0]-1, numCurrY + 3))
              self.workImg.rectangle(rectPoints, outline=self.colorBorder, width=1)
            
            # on the bottom, graph
            # set correct position
            numCurrY += 4
            
            # selected network last, on top of others
            sorBSSIDs.append(sorBSSIDs.pop(numIndexSelBSSID))
            # draw graph(s), from right to left
            for bssidx in sorBSSIDs:
              # if key input then draw next time with fresh data
              if len(self.keyDown) > 0:
                break
              # show the work done up until now
              self.canvas.blit(self.workImg)
              # set defaults - nonselected networks
              currEle = bssidx[1]
              currColorPoint=self.colorGraphPointOthers
              currColorLine=currColorPoint
              if currEle['BSSID'] == self.selectedBSSID:
                # draw horizontal marker lines
                for numDBM in range(math.ceil(self.numberMinDBM/10.0)*10.0,math.floor(self.numberMaxDBM/10.0)*10.0+0.1,10.0):
                  numDot = min(self.screenSize[1],max(numCurrY,int(self.screenSize[1] - (self.screenSize[1]-numCurrY) * (numDBM - self.numberMinDBM) / numDiffDBMMinMax)))
                  self.workImg.line(((0,numDot),(self.screenSize[0],numDot)), outline=self.colorGraphMarkers, width=self.numberGraphLineWidth)
                # set "active" color
                currColorPoint=self.colorGraphPoint
                (cR,cG,cB)=currColorPoint
                currColorLine=(cR*0.4,cG*0.4,cB*0.4)
              numCurrX = self.screenSize[0]
              numLastPos=(-1,-1)
              for dbmx in currEle['RxDBMs']:
                numCurrX -= self.numberGraphSeparation
                if dbmx == -1000:
                  numPos = (-1, -1)
                else:
                  numPos = (numCurrX,min(self.screenSize[1],max(numCurrY,int(self.screenSize[1] - (self.screenSize[1]-numCurrY) * (dbmx - self.numberMinDBM) / numDiffDBMMinMax))))
                if (numLastPos != (-1, -1)) and (numPos != (-1, -1)):
                  self.workImg.line((numPos, numLastPos), outline=currColorLine, width=self.numberGraphLineWidth)              
                if numLastPos != (-1, -1):
                  self.workImg.point(numLastPos, outline=currColorPoint, width=self.numberGraphLineWidth)
                numLastPos=numPos
              if numPos != (-1, -1):
                self.workImg.point(numPos, outline=currColorPoint, width=self.numberGraphLineWidth)
            
            # draw horizontal marker line numbers
            for numDBM in range(math.ceil(self.numberMinDBM/10.0)*10.0,math.floor(self.numberMaxDBM/10.0)*10.0+0.1,10.0):
              numDot = min(self.screenSize[1],max(numCurrY,int(self.screenSize[1] - (self.screenSize[1]-numCurrY) * (numDBM - self.numberMinDBM) / numDiffDBMMinMax)))
              self.workImg.text((3,numDot+numFontHeight+2),unicode(str(numDBM)),self.colorGraphMarkers,numFont)
        
      
    # if key input then draw next time with fresh data
    if len(self.keyDown) == 0:
      # show the final work done, on canvas
      self.canvas.blit(self.workImg)
  
  
  def run(self):
    appuifw.app.exit_key_handler=self.exitKeyHandler
    self.redraw(())
    lastTimerDraw=time.clock()
    
    while self.exitFlag < 2:
      if abs(time.clock() - self.lastRefresh) > self.numberRefreshSecs:
        self.lastRefresh=time.clock()
        self.exitFlag = 0
        self.redraw((0,0,self.screenSize[0],1))
        self.refreshData()
        self.redraw(())
      if len(self.keyDown) > 0:
        self.redraw(())
      if abs(time.clock() - lastTimerDraw) > 0.2:
        self.redraw((0,0,self.screenSize[0],1))
        lastTimerDraw = time.clock()
        e32.reset_inactivity()
      e32.ao_sleep(0.05)
    
    self.closeCanvas()
    print ""
    print "*** Gizmo_X's PyS60 WiFiScan exited!"
    print ""

try:
  import wlantools
  WiFiScanApp=WiFiScan()
  WiFiScanApp.run()
  sys.exit()
except ImportError:
  print "ERROR: module 'wlantools' failed to import!"
  print "You can get it from http://chris.berger.cx/PyS60/PyS60"
  print ""
  e32.ao_sleep(5.0)
  sys.exit()
