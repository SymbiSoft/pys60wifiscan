# Introduction #

WiFiScan is a pys60 (python for s60 symbian devices) application. It scans for wireless networks, shows information about found networks and charts signal strength over time.

# Details #

Keys to use this application:
  * up / down: select next/previous element from list
  * left / right: move through different views
  * select (center of joystick): same as _right_
  * left line (near green _call_ button): toggle filtering by selected SSID ON / OFF
  * right line (near red _hang up_ button): exit application

Views from first(left) to last(right):
  * SSID list
  * BSSID(access point) list
  * details about selected BSSID + dBm chart
  * one line version of details + near full screen dBm chart

Main menu:
<table border='1'><tr><td>
<img src='http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0109.gif' /></td><td>
<b>SSID list</b>
<ol><li>left side:<br>
<ul><li>yellow networks: currently available<br>
</li><li>red networks: currently unavailable<br>
</li><li>joda ( -84 ): currently selected network from list<br>
</li><li>( nuber ): last dBm signal strength indication<br>
</li></ul></li><li>right side:<br>
<ul><li>red line: last dBm<br>
</li><li>grey area: area from worst to best dBm<br>
</td></tr></table>
<table border='1'><tr><td>
<img src='http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0122.gif' /></td><td>
<b>Full details view</b>
</li></ul></li><li>top side:<br>
<ul><li>BSSID: MAC (hardware) address of the access point<br>
</li><li>SSID: ESSID (visual name) of the access point<br>
</li><li>Last seen: LIVE if current, seconds/minutes otherwise<br>
</li><li>Security mode: Open, Wep, 802.1x, Wpa, WpaPsk or Unidentified<br>
</li><li>Connection mode: AdHoc, Infrastructure, SecureInfra, Unknown<br>
</li><li>Channel number: The channel (1-14) on which access point operates. Exclamation marks for multiple usage of the same channel. All used channels are listed in parenthesis.<br>
</li></ul></li><li>bottom side:<br>
<ul><li>red chart: dBm/time for selected BSSID (with gaps when not found)<br>
</li><li>purple charts: dBm/time for all other BSSIDs<br>
</li><li>refresh every 10 seconds<br>
</td></tr></table></li></ul></li></ol>

# Screenshots #

![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0109.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0109.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0110.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0110.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0112.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0112.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0114.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0114.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0115.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0115.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0116.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0116.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0117.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0117.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0121.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0121.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0122.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0122.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Graph1.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Graph1.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Menu.gif](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Menu.gif)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0137.png](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0137.png)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0138.png](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0138.png)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0139.png](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0139.png)
![http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0140.png](http://pys60wifiscan.googlecode.com/svn/trunk/Images/Screenshot0140.png)