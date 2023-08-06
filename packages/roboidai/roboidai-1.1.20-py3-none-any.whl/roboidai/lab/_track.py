# Part of the ROBOID project - http://hamster.school
# Copyright (C) 2016 Kwang-Hyun Park (akaii@kw.ac.kr)
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General
# Public License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

import cv2 #line:19
import numpy as np #line:20
def find_track_xy (OO00000OO0OO0O000 ,O0O00OOO0O0000000 ,O000O00000000O0OO ,OO00O00OO0OOO0O0O ,s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:23
    O00O0O0000OOOO000 =OO00000OO0OO0O000 .shape [1 ]#line:24
    OOOOOOO000OO0OOOO =OO00000OO0OO0O000 .shape [0 ]#line:25
    O0OOO0OOOO0O00O0O =0 if window_height <0 else OOOOOOO000OO0OOOO -window_height #line:26
    OO00OO00O0O00OOO0 =OO00000OO0OO0O000 [O0OOO0OOOO0O00O0O :OOOOOOO000OO0OOOO ,:]#line:28
    O0O000OOO000OO0OO =cv2 .cvtColor (OO00OO00O0O00OOO0 ,cv2 .COLOR_BGR2HSV )#line:29
    OOO0O0O000O00O0OO =cv2 .inRange (O0O000OOO000OO0OO ,(OO00O00OO0OOO0O0O [0 ],s_range [0 ],v_range [0 ]),(OO00O00OO0OOO0O0O [1 ],s_range [1 ],v_range [1 ]))#line:31
    if len (OO00O00OO0OOO0O0O )>=4 :#line:32
        OOO0O0O000O00O0OO |=cv2 .inRange (O0O000OOO000OO0OO ,(OO00O00OO0OOO0O0O [2 ],s_range [0 ],v_range [0 ]),(OO00O00OO0OOO0O0O [3 ],s_range [1 ],v_range [1 ]))#line:33
    O0O0OOO0OO0OO0O00 =np .ones ((3 ,3 ),np .uint8 )#line:35
    OOO0O0O000O00O0OO =cv2 .morphologyEx (OOO0O0O000O00O0OO ,cv2 .MORPH_OPEN ,O0O0OOO0OO0OO0O00 )#line:36
    OOO0O0O000O00O0OO =cv2 .morphologyEx (OOO0O0O000O00O0OO ,cv2 .MORPH_CLOSE ,O0O0OOO0OO0OO0O00 )#line:37
    O00O0O0O0000O0O00 ,_O00OOOO0O000O000O =cv2 .findContours (OOO0O0O000O00O0OO ,cv2 .RETR_LIST ,cv2 .CHAIN_APPROX_SIMPLE )#line:39
    OO0O0O00O000OOOO0 =[cv2 .contourArea (O000O0000O00OO0O0 )for O000O0000O00OO0O0 in O00O0O0O0000O0O00 ]#line:40
    if OO0O0O00O000OOOO0 :#line:41
        OOOO00O00O0O00OO0 =np .argmax (OO0O0O00O000OOOO0 )#line:42
        O0O00O0O0OOOOO0O0 =OO0O0O00O000OOOO0 [OOOO00O00O0O00OO0 ]#line:43
        if O0O00O0O0OOOOO0O0 >min_area :#line:44
            OO0OO00OOO0O0OO0O =O00O0O0O0000O0O00 [OOOO00O00O0O00OO0 ]#line:45
            cv2 .drawContours (O0O00OOO0O0000000 ,O00O0O0O0000O0O00 ,OOOO00O00O0O00OO0 ,O000O00000000O0OO ,-1 ,offset =(0 ,O0OOO0OOOO0O00O0O ))#line:46
            O0OOO00OOOO00O000 =cv2 .moments (OO0OO00OOO0O0OO0O )#line:47
            OO00OO0000OO0O0OO =O0OOO00OOOO00O000 ['m00']#line:48
            if OO00OO0000OO0O0OO >0 :#line:49
                return int (O0OOO00OOOO00O000 ['m10']/OO00OO0000OO0O0OO ),int (O0OOO00OOOO00O000 ['m01']/OO00OO0000OO0O0OO )#line:50
    return -1 ,-1 #line:51
def find_green_track_xy (O0O0OOO0O00OO0O00 ,O00OOOOO0OO000000 ,h_range =(40 ,80 ),s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:54
    return find_track_xy (O0O0OOO0O00OO0O00 ,O00OOOOO0OO000000 ,(0 ,255 ,0 ),h_range ,s_range ,v_range ,window_height ,min_area )#line:55
def find_blue_track_xy (O0O0000OOOOO0O000 ,OO0000OO0O0O0OO00 ,h_range =(100 ,140 ),s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:58
    return find_track_xy (O0O0000OOOOO0O000 ,OO0000OO0O0O0OO00 ,(255 ,0 ,0 ),h_range ,s_range ,v_range ,window_height ,min_area )#line:59
def find_red_track_xy (O00OOO0O0O000OO00 ,O0OO000000O0OOO00 ,h_range =(0 ,10 ,170 ,180 ),s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:62
    return find_track_xy (O00OOO0O0O000OO00 ,O0OO000000O0OOO00 ,(0 ,0 ,255 ),h_range ,s_range ,v_range ,window_height ,min_area )#line:63
