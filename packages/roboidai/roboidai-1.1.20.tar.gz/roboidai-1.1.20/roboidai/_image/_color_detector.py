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
class ColorDetector :#line:23
    def __init__ (OO00O0O0OO00OOO00 ,red_h_range =(0 ,10 ,170 ,180 ),green_h_range =(40 ,80 ),blue_h_range =(100 ,140 ),s_range =(50 ,255 ),v_range =(50 ,255 )):#line:24
        OO00O0O0OO00OOO00 ._h_range ={'red':red_h_range ,'green':green_h_range ,'blue':blue_h_range }#line:29
        OO00O0O0OO00OOO00 ._s_range =s_range #line:30
        OO00O0O0OO00OOO00 ._v_range =v_range #line:31
        OO00O0O0OO00OOO00 ._results ={}#line:32
        OO00O0O0OO00OOO00 ._clear ()#line:33
    def _clear (OO0O0OO0OOOO00000 ):#line:35
        OO0O0OO0OOOO00000 ._results ['red']=None #line:36
        OO0O0OO0OOOO00000 ._results ['green']=None #line:37
        OO0O0OO0OOOO00000 ._results ['blue']=None #line:38
    def _find_blob (OO0O000O0OOOO000O ,O0OO0O0O00O0OOOO0 ,OOOOOOOOO0O0OOO00 ,OO0OOO00O00OOOOO0 ,OO0O00O00OO00OO00 ):#line:40
        O00O00O0OOOO0O0OO =cv2 .cvtColor (O0OO0O0O00O0OOOO0 ,cv2 .COLOR_BGR2HSV )#line:41
        OOO00OOO00O0OOO00 =cv2 .inRange (O00O00O0OOOO0O0OO ,(OOOOOOOOO0O0OOO00 [0 ],OO0OOO00O00OOOOO0 [0 ],OO0O00O00OO00OO00 [0 ]),(OOOOOOOOO0O0OOO00 [1 ],OO0OOO00O00OOOOO0 [1 ],OO0O00O00OO00OO00 [1 ]))#line:43
        if len (OOOOOOOOO0O0OOO00 )>=4 :#line:44
            OOO00OOO00O0OOO00 |=cv2 .inRange (O00O00O0OOOO0O0OO ,(OOOOOOOOO0O0OOO00 [2 ],OO0OOO00O00OOOOO0 [0 ],OO0O00O00OO00OO00 [0 ]),(OOOOOOOOO0O0OOO00 [3 ],OO0OOO00O00OOOOO0 [1 ],OO0O00O00OO00OO00 [1 ]))#line:45
        O0OOOOOOOOOOOOO0O =np .ones ((3 ,3 ),np .uint8 )#line:47
        OOO00OOO00O0OOO00 =cv2 .morphologyEx (OOO00OOO00O0OOO00 ,cv2 .MORPH_OPEN ,O0OOOOOOOOOOOOO0O )#line:48
        OOO00OOO00O0OOO00 =cv2 .morphologyEx (OOO00OOO00O0OOO00 ,cv2 .MORPH_CLOSE ,O0OOOOOOOOOOOOO0O )#line:49
        O00000000OOOO00OO ,_OO0O0O000000O0000 =cv2 .findContours (OOO00OOO00O0OOO00 ,cv2 .RETR_LIST ,cv2 .CHAIN_APPROX_SIMPLE )#line:51
        O00O00OO00O000O0O =[cv2 .contourArea (O0O000000O0O0O0O0 )for O0O000000O0O0O0O0 in O00000000OOOO00OO ]#line:52
        if O00O00OO00O000O0O :#line:53
            OO0000000000OO0O0 =np .argmax (O00O00OO00O000O0O )#line:54
            OOO0O00O0OO00000O =int (O00O00OO00O000O0O [OO0000000000OO0O0 ])#line:55
            if OOO0O00O0OO00000O >5 :#line:56
                OOOOO000O0OO000OO =O00000000OOOO00OO [OO0000000000OO0O0 ]#line:57
                O0OOOO00OOOOO0OOO ,OO000O0000OOOOOOO ,OO0O0O00OO00OO00O ,OOOOOO0O0O00O00OO =cv2 .boundingRect (OOOOO000O0OO000OO )#line:58
                OO0O000OO0000O00O ={'box':(O0OOOO00OOOOO0OOO ,OO000O0000OOOOOOO ,O0OOOO00OOOOO0OOO +OO0O0O00OO00OO00O ,OO000O0000OOOOOOO +OOOOOO0O0O00O00OO ),'width':OO0O0O00OO00OO00O ,'height':OOOOOO0O0O00O00OO ,'area':OO0O0O00OO00OO00O *OOOOOO0O0O00O00OO ,'pixels':OOO0O00O0OO00000O }#line:65
                O0OOO00O00OO00O0O =cv2 .moments (OOOOO000O0OO000OO )#line:66
                O00OO0OO0OOO0000O =O0OOO00O00OO00O0O ['m00']#line:67
                if O00OO0OO0OOO0000O >0 :#line:68
                    OO0O000OO0000O00O ['xy']=(int (O0OOO00O00OO00O0O ['m10']/O00OO0OO0OOO0000O ),int (O0OOO00O00OO00O0O ['m01']/O00OO0OO0OOO0000O ))#line:69
                    return OO0O000OO0000O00O #line:70
        return None #line:71
    def detect (OO0OOOOOO0000O00O ,O0O00O00OOO0OOO0O ):#line:73
        OO0OOOOOO0000O00O ._clear ()#line:74
        if O0O00O00OOO0OOO0O is not None :#line:75
            O00O00OOO0O000O0O =OO0OOOOOO0000O00O ._s_range #line:76
            O000O0O0O00O0O0OO =OO0OOOOOO0000O00O ._v_range #line:77
            OO0OOOOOO0000O00O ._results ['red']=OO0OOOOOO0000O00O ._find_blob (O0O00O00OOO0OOO0O ,OO0OOOOOO0000O00O ._h_range ['red'],O00O00OOO0O000O0O ,O000O0O0O00O0O0OO )#line:78
            OO0OOOOOO0000O00O ._results ['green']=OO0OOOOOO0000O00O ._find_blob (O0O00O00OOO0OOO0O ,OO0OOOOOO0000O00O ._h_range ['green'],O00O00OOO0O000O0O ,O000O0O0O00O0O0OO )#line:79
            OO0OOOOOO0000O00O ._results ['blue']=OO0OOOOOO0000O00O ._find_blob (O0O00O00OOO0OOO0O ,OO0OOOOOO0000O00O ._h_range ['blue'],O00O00OOO0O000O0O ,O000O0O0O00O0O0OO )#line:80
            return True #line:81
        return False #line:82
    def _draw (OO0OO00OO000O00OO ,OO0OOOO000O0000OO ,O0000OO00O0OOO000 ,O00OOOO0OOOO00OO0 ):#line:84
        if O0000OO00O0OOO000 is not None :#line:85
            OOOOO000OO0OOO0OO ,O00OO0OOOOO00OOOO ,O0O000OO00OOO0OO0 ,O0OOO00OO0OOO0000 =O0000OO00O0OOO000 ['box']#line:86
            cv2 .rectangle (OO0OOOO000O0000OO ,(OOOOO000OO0OOO0OO ,O00OO0OOOOO00OOOO ),(O0O000OO00OOO0OO0 ,O0OOO00OO0OOO0000 ),O00OOOO0OOOO00OO0 ,3 )#line:87
            OOO000O00OO000OOO ,O00OOO0OO0O0O0000 =O0000OO00O0OOO000 ['xy']#line:88
            cv2 .putText (OO0OOOO000O0000OO ,'x: {}px'.format (OOO000O00OO000OOO ),(OOOOO000OO0OOO0OO ,O00OO0OOOOO00OOOO -40 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:89
            cv2 .putText (OO0OOOO000O0000OO ,'y: {}px'.format (O00OOO0OO0O0O0000 ),(OOOOO000OO0OOO0OO ,O00OO0OOOOO00OOOO -25 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:90
            cv2 .putText (OO0OOOO000O0000OO ,'pixel: {}'.format (O0000OO00O0OOO000 ['pixels']),(OOOOO000OO0OOO0OO ,O00OO0OOOOO00OOOO -10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:91
    def draw_result (O0OO00OO0OOOOOOO0 ,O0OOOOO00OO0000O0 ,clone =False ):#line:93
        if O0OOOOO00OO0000O0 is not None :#line:94
            if clone :#line:95
                O0OOOOO00OO0000O0 =O0OOOOO00OO0000O0 .copy ()#line:96
            O0OO00OO0OOOOOOO0 ._draw (O0OOOOO00OO0000O0 ,O0OO00OO0OOOOOOO0 ._results ['red'],(0 ,0 ,255 ))#line:97
            O0OO00OO0OOOOOOO0 ._draw (O0OOOOO00OO0000O0 ,O0OO00OO0OOOOOOO0 ._results ['green'],(0 ,255 ,0 ))#line:98
            O0OO00OO0OOOOOOO0 ._draw (O0OOOOO00OO0000O0 ,O0OO00OO0OOOOOOO0 ._results ['blue'],(255 ,0 ,0 ))#line:99
        return O0OOOOO00OO0000O0 #line:100
    def get_xy (O0O00O00000OO0O00 ,OOO0OOO0OOOOO0000 ):#line:102
        if isinstance (OOO0OOO0OOOOO0000 ,str ):#line:103
            OOO0OOO0OOOOO0000 =OOO0OOO0OOOOO0000 .lower ()#line:104
            if OOO0OOO0OOOOO0000 in O0O00O00000OO0O00 ._results :#line:105
                O00OO0OO0OOOOOOOO =O0O00O00000OO0O00 ._results [OOO0OOO0OOOOO0000 ]#line:106
                if O00OO0OO0OOOOOOOO is not None :#line:107
                    return O00OO0OO0OOOOOOOO ['xy']#line:108
        return -1 ,-1 #line:109
    def get_x (O00O0OO0OOO0OO000 ,O000OO0OO00O00000 ):#line:111
        O00O0OO000O0OOO0O ,_OOOOOOO0O0O000O00 =O00O0OO0OOO0OO000 .get_xy (O000OO0OO00O00000 )#line:112
        return O00O0OO000O0OOO0O #line:113
    def get_y (OO0OOO000OO00OOO0 ,O00O0OOOO0OO00OO0 ):#line:115
        _OO0OOO0OOO0O0OO0O ,O000OO0O00OO0O000 =OO0OOO000OO00OOO0 .get_xy (O00O0OOOO0OO00OO0 )#line:116
        return O000OO0O00OO0O000 #line:117
    def get_box (O0O000O0O00O0OO0O ,OOO0OOOO0OO0OOOO0 ):#line:119
        if isinstance (OOO0OOOO0OO0OOOO0 ,str ):#line:120
            OOO0OOOO0OO0OOOO0 =OOO0OOOO0OO0OOOO0 .lower ()#line:121
            if OOO0OOOO0OO0OOOO0 in O0O000O0O00O0OO0O ._results :#line:122
                O00O000000OOOOOOO =O0O000O0O00O0OO0O ._results [OOO0OOOO0OO0OOOO0 ]#line:123
                if O00O000000OOOOOOO is not None :#line:124
                    return O00O000000OOOOOOO ['box']#line:125
        return -1 ,-1 ,-1 ,-1 #line:126
    def get_width (OO000OOO00000O0O0 ,OO0O00OOO0OO0OOOO ):#line:128
        if isinstance (OO0O00OOO0OO0OOOO ,str ):#line:129
            OO0O00OOO0OO0OOOO =OO0O00OOO0OO0OOOO .lower ()#line:130
            if OO0O00OOO0OO0OOOO in OO000OOO00000O0O0 ._results :#line:131
                OOO00OOO000OOO0O0 =OO000OOO00000O0O0 ._results [OO0O00OOO0OO0OOOO ]#line:132
                if OOO00OOO000OOO0O0 is not None :#line:133
                    return OOO00OOO000OOO0O0 ['width']#line:134
        return 0 #line:135
    def get_height (O00000O00OO0OOOO0 ,O000OOOO00O00000O ):#line:137
        if isinstance (O000OOOO00O00000O ,str ):#line:138
            O000OOOO00O00000O =O000OOOO00O00000O .lower ()#line:139
            if O000OOOO00O00000O in O00000O00OO0OOOO0 ._results :#line:140
                O0O0O0OO00OO00OO0 =O00000O00OO0OOOO0 ._results [O000OOOO00O00000O ]#line:141
                if O0O0O0OO00OO00OO0 is not None :#line:142
                    return O0O0O0OO00OO00OO0 ['height']#line:143
        return 0 #line:144
    def get_area (O0000OOO0O0OOO0O0 ,OOOO0O0O0O0OOOOO0 ):#line:146
        if isinstance (OOOO0O0O0O0OOOOO0 ,str ):#line:147
            OOOO0O0O0O0OOOOO0 =OOOO0O0O0O0OOOOO0 .lower ()#line:148
            if OOOO0O0O0O0OOOOO0 in O0000OOO0O0OOO0O0 ._results :#line:149
                OOOO0O0OO000000OO =O0000OOO0O0OOO0O0 ._results [OOOO0O0O0O0OOOOO0 ]#line:150
                if OOOO0O0OO000000OO is not None :#line:151
                    return OOOO0O0OO000000OO ['area']#line:152
        return 0 #line:153
    def get_pixels (O0OOOO00OO00OOO0O ,O00000OOO0000OOO0 ):#line:155
        if isinstance (O00000OOO0000OOO0 ,str ):#line:156
            O00000OOO0000OOO0 =O00000OOO0000OOO0 .lower ()#line:157
            if O00000OOO0000OOO0 in O0OOOO00OO00OOO0O ._results :#line:158
                OOO0OO0O0O0O0OOOO =O0OOOO00OO00OOO0O ._results [O00000OOO0000OOO0 ]#line:159
                if OOO0OO0O0O0O0OOOO is not None :#line:160
                    return OOO0OO0O0O0O0OOOO ['pixels']#line:161
        return 0 #line:162
    def wait_until (OOO0OO0OOOO0O000O ,O0O00OO0000O00000 ,OO0O00OO0O0OO0000 ,interval_msec =1 ,min_pixels =5 ,min_area =5 ):#line:164
        if not isinstance (OO0O00OO0O0OO0000 ,(list ,tuple )):#line:165
            OO0O00OO0O0OO0000 =(OO0O00OO0O0OO0000 ,)#line:166
        OO00OO0O0O0OOO000 =None #line:167
        while OO00OO0O0O0OOO000 is None :#line:168
            O0O0O000OO00OOOOO =O0O00OO0000O00000 .read ()#line:169
            if OOO0OO0OOOO0O000O .detect (O0O0O000OO00OOOOO ):#line:170
                O000OOOO00O0O0OO0 =-1 #line:171
                for O000000O00OOO0O00 in OO0O00OO0O0OO0000 :#line:172
                    OOO0000O00OO00000 =OOO0OO0OOOO0O000O .get_pixels (O000000O00OOO0O00 )#line:173
                    O000O000O0OOOO0OO =OOO0OO0OOOO0O000O .get_area (O000000O00OOO0O00 )#line:174
                    if OOO0000O00OO00000 >min_pixels and O000O000O0OOOO0OO >min_area and OOO0000O00OO00000 >O000OOOO00O0O0OO0 :#line:175
                        O000OOOO00O0O0OO0 =OOO0000O00OO00000 #line:176
                        OO00OO0O0O0OOO000 =O000000O00OOO0O00 #line:177
                O0O0O000OO00OOOOO =OOO0OO0OOOO0O000O .draw_result (O0O0O000OO00OOOOO )#line:178
            O0O00OO0000O00000 .show (O0O0O000OO00OOOOO )#line:179
            if O0O00OO0000O00000 .check_key (interval_msec )=='esc':break #line:180
        return OO00OO0O0O0OOO000 #line:181
