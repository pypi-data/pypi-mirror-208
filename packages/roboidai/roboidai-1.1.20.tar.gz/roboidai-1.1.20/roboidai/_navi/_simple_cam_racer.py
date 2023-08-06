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
class SimpleCamRacer :#line:23
    _LEFT =1 #line:24
    _RIGHT =2 #line:25
    _RED =3 #line:26
    _GREEN =4 #line:27
    _BLUE =5 #line:28
    _BLOBS ={'left':1 ,'right':2 ,'red':3 ,'green':4 ,'blue':5 }#line:35
    _COLORS ={'red':3 ,'green':4 ,'blue':5 }#line:40
    def __init__ (O0OOO0OO000OOO0OO ,red_h_range =(0 ,10 ,170 ,180 ),green_h_range =(40 ,80 ),blue_h_range =(100 ,140 ),s_range =(50 ,255 ),v_range =(50 ,255 ),lane_window_height =50 ):#line:42
        O0OOO0OO000OOO0OO ._h_range ={SimpleCamRacer ._RED :red_h_range ,SimpleCamRacer ._GREEN :green_h_range ,SimpleCamRacer ._BLUE :blue_h_range }#line:47
        O0OOO0OO000OOO0OO ._s_range =s_range #line:48
        O0OOO0OO000OOO0OO ._v_range =v_range #line:49
        O0OOO0OO000OOO0OO ._lane_window_height =lane_window_height #line:50
        O0OOO0OO000OOO0OO ._direction =1 #line:51
        O0OOO0OO000OOO0OO ._speed =50 #line:52
        O0OOO0OO000OOO0OO ._gain =0.1 #line:53
        O0OOO0OO000OOO0OO ._left_velocity =0 #line:54
        O0OOO0OO000OOO0OO ._right_velocity =0 #line:55
        O0OOO0OO000OOO0OO ._results ={}#line:56
        O0OOO0OO000OOO0OO ._clear ()#line:57
        O0OOO0OO000OOO0OO .set_lane_colors ('green','blue')#line:58
    def _clear (OO0000000OOO00O0O ):#line:60
        OO0000000OOO00O0O ._results [SimpleCamRacer ._LEFT ]=None #line:61
        OO0000000OOO00O0O ._results [SimpleCamRacer ._RIGHT ]=None #line:62
        OO0000000OOO00O0O ._results [SimpleCamRacer ._RED ]=None #line:63
        OO0000000OOO00O0O ._results [SimpleCamRacer ._GREEN ]=None #line:64
        OO0000000OOO00O0O ._results [SimpleCamRacer ._BLUE ]=None #line:65
    def _find_blob (O0OOOO0OO0O0O00O0 ,O0OO0000O00000OO0 ,O00000OO0OO0OO000 ,OO0O00OOOOO00O000 ,OOO00OO000O00OOO0 ,OO00000O00OO0O0O0 ,O0O0OOOOOOO0OOO0O ,OO0OOOO0O0O0OO0O0 ,OO0000O000000O000 ):#line:67
        O0O0OO0O0O00O0O00 =O0OO0000O00000OO0 [OO0OOOO0O0O0OO0O0 :OO0000O000000O000 ,OO00000O00OO0O0O0 :O0O0OOOOOOO0OOO0O ]#line:68
        OOO00OO0OOOOO0OO0 =cv2 .cvtColor (O0O0OO0O0O00O0O00 ,cv2 .COLOR_BGR2HSV )#line:69
        OOO0O000O0OOOO0O0 =cv2 .inRange (OOO00OO0OOOOO0OO0 ,(O00000OO0OO0OO000 [0 ],OO0O00OOOOO00O000 [0 ],OOO00OO000O00OOO0 [0 ]),(O00000OO0OO0OO000 [1 ],OO0O00OOOOO00O000 [1 ],OOO00OO000O00OOO0 [1 ]))#line:71
        if len (O00000OO0OO0OO000 )>=4 :#line:72
            OOO0O000O0OOOO0O0 |=cv2 .inRange (OOO00OO0OOOOO0OO0 ,(O00000OO0OO0OO000 [2 ],OO0O00OOOOO00O000 [0 ],OOO00OO000O00OOO0 [0 ]),(O00000OO0OO0OO000 [3 ],OO0O00OOOOO00O000 [1 ],OOO00OO000O00OOO0 [1 ]))#line:73
        O000O0OOO000OO00O =np .ones ((3 ,3 ),np .uint8 )#line:75
        OOO0O000O0OOOO0O0 =cv2 .morphologyEx (OOO0O000O0OOOO0O0 ,cv2 .MORPH_OPEN ,O000O0OOO000OO00O )#line:76
        OOO0O000O0OOOO0O0 =cv2 .morphologyEx (OOO0O000O0OOOO0O0 ,cv2 .MORPH_CLOSE ,O000O0OOO000OO00O )#line:77
        O0OOOO000O000O00O ,_OOOO00O000O0O0O00 =cv2 .findContours (OOO0O000O0OOOO0O0 ,cv2 .RETR_LIST ,cv2 .CHAIN_APPROX_SIMPLE )#line:79
        O00000OO0O0OOOOOO =[cv2 .contourArea (OO0O0OOO0OO0O00OO )for OO0O0OOO0OO0O00OO in O0OOOO000O000O00O ]#line:80
        if O00000OO0O0OOOOOO :#line:81
            OOOO00OO0OO0O0OOO =np .argmax (O00000OO0O0OOOOOO )#line:82
            OO00OOO0O000000O0 =int (O00000OO0O0OOOOOO [OOOO00OO0OO0O0OOO ])#line:83
            if OO00OOO0O000000O0 >5 :#line:84
                OO000O00O0OOOOO0O =O0OOOO000O000O00O [OOOO00OO0OO0O0OOO ]#line:85
                O00O0OOOOOO000OOO ,OO0OOO0000O0OOOOO ,OO0O0O000000O0O00 ,OO0OO0OOOOOOO0OO0 =cv2 .boundingRect (OO000O00O0OOOOO0O )#line:86
                O00O00OO0000OOO0O ={'box':(O00O0OOOOOO000OOO +OO00000O00OO0O0O0 ,OO0OOO0000O0OOOOO +OO0OOOO0O0O0OO0O0 ,O00O0OOOOOO000OOO +OO0O0O000000O0O00 +OO00000O00OO0O0O0 ,OO0OOO0000O0OOOOO +OO0OO0OOOOOOO0OO0 +OO0OOOO0O0O0OO0O0 ),'width':OO0O0O000000O0O00 ,'height':OO0OO0OOOOOOO0OO0 ,'area':OO0O0O000000O0O00 *OO0OO0OOOOOOO0OO0 ,'pixels':OO00OOO0O000000O0 }#line:93
                O00OOO000OO0OOOOO =cv2 .moments (OO000O00O0OOOOO0O )#line:94
                O00OO00O00OOO0O00 =O00OOO000OO0OOOOO ['m00']#line:95
                if O00OO00O00OOO0O00 >0 :#line:96
                    O00O00OO0000OOO0O ['xy']=(int (O00OOO000OO0OOOOO ['m10']/O00OO00O00OOO0O00 )+OO00000O00OO0O0O0 ,int (O00OOO000OO0OOOOO ['m01']/O00OO00O00OOO0O00 )+OO0OOOO0O0O0OO0O0 )#line:97
                    return O00O00OO0000OOO0O #line:98
        return None #line:99
    def _find_color (O0OO0000OOO0O00O0 ,OOOOOO0OO0OOO00OO ,OO00000O00O0O0O0O ,O000OOO00000O0O00 ,O00OOOOO00OOOO000 ,O00O000OO00000O00 ,OOO0000O00000OO0O ):#line:101
        OO0000OOO000OO000 =O0OO0000OOO0O00O0 ._h_range [OO00000O00O0O0O0O ]#line:102
        OO0OOOO0OO0O0O0O0 =O0OO0000OOO0O00O0 ._s_range #line:103
        OO000OO00OO00O00O =O0OO0000OOO0O00O0 ._v_range #line:104
        if O0OO0000OOO0O00O0 ._left_lane_color ==OO00000O00O0O0O0O and O0OO0000OOO0O00O0 ._right_lane_color ==OO00000O00O0O0O0O :#line:106
            O0OOO0000O0O00O0O =O0OO0000OOO0O00O0 ._find_blob (OOOOOO0OO0OOO00OO ,OO0000OOO000OO000 ,OO0OOOO0OO0O0O0O0 ,OO000OO00OO00O00O ,0 ,O00O000OO00000O00 ,OOO0000O00000OO0O ,O00OOOOO00OOOO000 )#line:107
            O0OO0OO0000OO0OOO =O0OO0000OOO0O00O0 ._find_blob (OOOOOO0OO0OOO00OO ,OO0000OOO000OO000 ,OO0OOOO0OO0O0O0O0 ,OO000OO00OO00O00O ,O00O000OO00000O00 ,O000OOO00000O0O00 ,OOO0000O00000OO0O ,O00OOOOO00OOOO000 )#line:108
            if O0OOO0000O0O00O0O is not None and O0OO0OO0000OO0OOO is not None :#line:109
                O0OO0000OOO0O00O0 ._results [OO00000O00O0O0O0O ]=O0OO0OO0000OO0OOO if O0OO0OO0000OO0OOO ['pixels']>O0OOO0000O0O00O0O ['pixels']else O0OOO0000O0O00O0O #line:110
                O0OO0000OOO0O00O0 ._results [SimpleCamRacer ._LEFT ]=O0OOO0000O0O00O0O #line:111
                O0OO0000OOO0O00O0 ._results [SimpleCamRacer ._RIGHT ]=O0OO0OO0000OO0OOO #line:112
            elif O0OOO0000O0O00O0O is not None :#line:113
                O0OO0000OOO0O00O0 ._results [OO00000O00O0O0O0O ]=O0OOO0000O0O00O0O #line:114
                O0OO0000OOO0O00O0 ._results [SimpleCamRacer ._LEFT ]=O0OOO0000O0O00O0O #line:115
            elif O0OO0OO0000OO0OOO is not None :#line:116
                O0OO0000OOO0O00O0 ._results [OO00000O00O0O0O0O ]=O0OO0OO0000OO0OOO #line:117
                O0OO0000OOO0O00O0 ._results [SimpleCamRacer ._RIGHT ]=O0OO0OO0000OO0OOO #line:118
            else :#line:119
                O0OO0000OOO0O00O0 ._results [OO00000O00O0O0O0O ]=None #line:120
        elif O0OO0000OOO0O00O0 ._left_lane_color ==OO00000O00O0O0O0O :#line:121
            OO00O000O0OO00O0O =O0OO0000OOO0O00O0 ._find_blob (OOOOOO0OO0OOO00OO ,OO0000OOO000OO000 ,OO0OOOO0OO0O0O0O0 ,OO000OO00OO00O00O ,0 ,O000OOO00000O0O00 ,OOO0000O00000OO0O ,O00OOOOO00OOOO000 )#line:122
            O0OO0000OOO0O00O0 ._results [OO00000O00O0O0O0O ]=OO00O000O0OO00O0O #line:123
            if OO00O000O0OO00O0O is not None :#line:124
                O0OO0000OOO0O00O0 ._results [SimpleCamRacer ._LEFT ]=OO00O000O0OO00O0O #line:125
        elif O0OO0000OOO0O00O0 ._right_lane_color ==OO00000O00O0O0O0O :#line:126
            OO00O000O0OO00O0O =O0OO0000OOO0O00O0 ._find_blob (OOOOOO0OO0OOO00OO ,OO0000OOO000OO000 ,OO0OOOO0OO0O0O0O0 ,OO000OO00OO00O00O ,0 ,O000OOO00000O0O00 ,OOO0000O00000OO0O ,O00OOOOO00OOOO000 )#line:127
            O0OO0000OOO0O00O0 ._results [OO00000O00O0O0O0O ]=OO00O000O0OO00O0O #line:128
            if OO00O000O0OO00O0O is not None :#line:129
                O0OO0000OOO0O00O0 ._results [SimpleCamRacer ._RIGHT ]=OO00O000O0OO00O0O #line:130
        else :#line:131
            O0OO0000OOO0O00O0 ._results [OO00000O00O0O0O0O ]=O0OO0000OOO0O00O0 ._find_blob (OOOOOO0OO0OOO00OO ,OO0000OOO000OO000 ,OO0OOOO0OO0O0O0O0 ,OO000OO00OO00O00O ,0 ,O000OOO00000O0O00 ,0 ,O00OOOOO00OOOO000 )#line:132
    def detect (OO0O0OO0O0O0O0O00 ,O0000OOO00000OO0O ):#line:134
        OO0O0OO0O0O0O0O00 ._clear ()#line:135
        if O0000OOO00000OO0O is not None :#line:136
            OOO00O0OO0OOO00O0 =O0000OOO00000OO0O .shape [1 ]#line:137
            O0O000OO0OOOO0OO0 =O0000OOO00000OO0O .shape [0 ]#line:138
            OOO0O00O00OO00OO0 =OOO00O0OO0OOO00O0 //2 #line:139
            O00OO00000O0O0000 =O0O000OO0OOOO0OO0 -OO0O0OO0O0O0O0O00 ._lane_window_height #line:140
            OO0O0OO0O0O0O0O00 ._find_color (O0000OOO00000OO0O ,SimpleCamRacer ._RED ,OOO00O0OO0OOO00O0 ,O0O000OO0OOOO0OO0 ,OOO0O00O00OO00OO0 ,O00OO00000O0O0000 )#line:142
            OO0O0OO0O0O0O0O00 ._find_color (O0000OOO00000OO0O ,SimpleCamRacer ._GREEN ,OOO00O0OO0OOO00O0 ,O0O000OO0OOOO0OO0 ,OOO0O00O00OO00OO0 ,O00OO00000O0O0000 )#line:143
            OO0O0OO0O0O0O0O00 ._find_color (O0000OOO00000OO0O ,SimpleCamRacer ._BLUE ,OOO00O0OO0OOO00O0 ,O0O000OO0OOOO0OO0 ,OOO0O00O00OO00OO0 ,O00OO00000O0O0000 )#line:144
            OOO0O000O00OOO0OO =OO0O0OO0O0O0O0O00 ._results [SimpleCamRacer ._LEFT ]#line:146
            O0OO00OO0000OO000 =OO0O0OO0O0O0O0O00 ._results [SimpleCamRacer ._RIGHT ]#line:147
            O0O00O0OO000O0O00 =abs (OOO0O00O00OO00OO0 -OOO0O000O00OOO0OO ['xy'][0 ])if OOO0O000O00OOO0OO is not None else OOO0O00O00OO00OO0 #line:148
            OOO000000O0O00OOO =abs (O0OO00OO0000OO000 ['xy'][0 ]-OOO0O00O00OO00OO0 )if O0OO00OO0000OO000 is not None else OOO00O0OO0OOO00O0 -OOO0O00O00OO00OO0 #line:149
            OOO00OOOOO00O0O0O =OOO000000O0O00OOO -O0O00O0OO000O0O00 #line:151
            OO0O0OO0O0O0O0O00 ._left_velocity =OO0O0OO0O0O0O0O00 ._direction *OO0O0OO0O0O0O0O00 ._speed +OO0O0OO0O0O0O0O00 ._gain *OOO00OOOOO00O0O0O #line:152
            OO0O0OO0O0O0O0O00 ._right_velocity =OO0O0OO0O0O0O0O00 ._direction *OO0O0OO0O0O0O0O00 ._speed -OO0O0OO0O0O0O0O00 ._gain *OOO00OOOOO00O0O0O #line:153
            return True #line:154
        return False #line:155
    def _draw (OO0OOO0O0OO00O0O0 ,OO0OO00OO00OO0OO0 ,O0O000OOO0OO000O0 ,OOOO00OOOO000OOOO ):#line:157
        if O0O000OOO0OO000O0 is not None :#line:158
            O0O0O000OO0OOOOO0 ,OOO00O00OO0OOO000 ,OO0OO0O0OOO0OO000 ,OOOO0OOOOO0O000OO =O0O000OOO0OO000O0 ['box']#line:159
            cv2 .rectangle (OO0OO00OO00OO0OO0 ,(O0O0O000OO0OOOOO0 ,OOO00O00OO0OOO000 ),(OO0OO0O0OOO0OO000 ,OOOO0OOOOO0O000OO ),OOOO00OOOO000OOOO ,3 )#line:160
            O00O00OO00O0O0O00 ,O0OO0OO00OO0OOOO0 =O0O000OOO0OO000O0 ['xy']#line:161
            cv2 .putText (OO0OO00OO00OO0OO0 ,'x: {}px'.format (O00O00OO00O0O0O00 ),(O0O0O000OO0OOOOO0 ,OOO00O00OO0OOO000 -40 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:162
            cv2 .putText (OO0OO00OO00OO0OO0 ,'y: {}px'.format (O0OO0OO00OO0OOOO0 ),(O0O0O000OO0OOOOO0 ,OOO00O00OO0OOO000 -25 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:163
            cv2 .putText (OO0OO00OO00OO0OO0 ,'pixel: {}'.format (O0O000OOO0OO000O0 ['pixels']),(O0O0O000OO0OOOOO0 ,OOO00O00OO0OOO000 -10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:164
    def _draw_color (O0O00O0OO0000O0OO ,OOOO00000O00OOO00 ,OO0OOOO0OO00O00OO ,OOO0O0OOO0O0000OO ):#line:166
        if O0O00O0OO0000O0OO ._left_lane_color ==OO0OOOO0OO00O00OO or O0O00O0OO0000O0OO ._right_lane_color ==OO0OOOO0OO00O00OO :#line:167
            if O0O00O0OO0000O0OO ._left_lane_color ==OO0OOOO0OO00O00OO :#line:168
                O0O00O0OO0000O0OO ._draw (OOOO00000O00OOO00 ,O0O00O0OO0000O0OO ._results [SimpleCamRacer ._LEFT ],OOO0O0OOO0O0000OO )#line:169
            if O0O00O0OO0000O0OO ._right_lane_color ==OO0OOOO0OO00O00OO :#line:170
                O0O00O0OO0000O0OO ._draw (OOOO00000O00OOO00 ,O0O00O0OO0000O0OO ._results [SimpleCamRacer ._RIGHT ],OOO0O0OOO0O0000OO )#line:171
        else :#line:172
            O0O00O0OO0000O0OO ._draw (OOOO00000O00OOO00 ,O0O00O0OO0000O0OO ._results [OO0OOOO0OO00O00OO ],OOO0O0OOO0O0000OO )#line:173
    def draw_result (O00OOOO00OO0O0O0O ,O000O0OOO000OOOOO ,clone =False ):#line:175
        if O000O0OOO000OOOOO is not None :#line:176
            if clone :#line:177
                O000O0OOO000OOOOO =O000O0OOO000OOOOO .copy ()#line:178
            O00OOOO00OO0O0O0O ._draw_color (O000O0OOO000OOOOO ,SimpleCamRacer ._RED ,(0 ,0 ,255 ))#line:179
            O00OOOO00OO0O0O0O ._draw_color (O000O0OOO000OOOOO ,SimpleCamRacer ._GREEN ,(0 ,255 ,0 ))#line:180
            O00OOOO00OO0O0O0O ._draw_color (O000O0OOO000OOOOO ,SimpleCamRacer ._BLUE ,(255 ,0 ,0 ))#line:181
        return O000O0OOO000OOOOO #line:182
    def set_lane_colors (OOO0OOO000OO000O0 ,OO000OO00O0000O00 ,O0OO00O0O000O0OO0 ):#line:184
        if isinstance (OO000OO00O0000O00 ,str ):#line:185
            OO000OO00O0000O00 =OO000OO00O0000O00 .lower ()#line:186
            if OO000OO00O0000O00 in SimpleCamRacer ._COLORS :#line:187
                OOO0OOO000OO000O0 ._left_lane_color =SimpleCamRacer ._COLORS [OO000OO00O0000O00 ]#line:188
        if isinstance (O0OO00O0O000O0OO0 ,str ):#line:189
            O0OO00O0O000O0OO0 =O0OO00O0O000O0OO0 .lower ()#line:190
            if O0OO00O0O000O0OO0 in SimpleCamRacer ._COLORS :#line:191
                OOO0OOO000OO000O0 ._right_lane_color =SimpleCamRacer ._COLORS [O0OO00O0O000O0OO0 ]#line:192
    def set_backward (O00O0000OO0O0O0OO ,backward =True ):#line:194
        O00O0000OO0O0O0OO ._direction =-1 if backward else 1 #line:195
    def set_speed (O0OO0OO0OO0O000O0 ,O000OOOOOO0000OO0 ):#line:197
        if isinstance (O000OOOOOO0000OO0 ,(int ,float )):#line:198
            O0OO0OO0OO0O000O0 ._speed =O000OOOOOO0000OO0 #line:199
    def set_gain (O00OOOO00OOO00O0O ,O0O0OOO0O000OOOOO ):#line:201
        if isinstance (O0O0OOO0O000OOOOO ,(int ,float )):#line:202
            O00OOOO00OOO00O0O ._gain =O0O0OOO0O000OOOOO #line:203
    def get_velocity (O000O0O000000000O ):#line:205
        return O000O0O000000000O ._left_velocity ,O000O0O000000000O ._right_velocity #line:206
    def get_left_velocity (O000OO000OOOO0O00 ):#line:208
        return O000OO000OOOO0O00 ._left_velocity #line:209
    def get_right_velocity (O00OOO000000OOO00 ):#line:211
        return O00OOO000000OOO00 ._right_velocity #line:212
    def get_xy (OO0000O0O00OOO0OO ,O000O0OOO0O0O00O0 ):#line:214
        if isinstance (O000O0OOO0O0O00O0 ,str ):#line:215
            O000O0OOO0O0O00O0 =O000O0OOO0O0O00O0 .lower ()#line:216
            if O000O0OOO0O0O00O0 in SimpleCamRacer ._BLOBS :#line:217
                O00OO00O000O0O000 =OO0000O0O00OOO0OO ._results [SimpleCamRacer ._BLOBS [O000O0OOO0O0O00O0 ]]#line:218
                if O00OO00O000O0O000 is not None :#line:219
                    return O00OO00O000O0O000 ['xy']#line:220
        return -1 ,-1 #line:221
    def get_x (OOO0OO0O0000OOOOO ,O0OOO00O0000O00O0 ):#line:223
        OOO00OO00O0O000O0 ,_O00O00OOO0O00OOO0 =OOO0OO0O0000OOOOO .get_xy (O0OOO00O0000O00O0 )#line:224
        return OOO00OO00O0O000O0 #line:225
    def get_y (O000O000OOOO0O000 ,OOO0OO000000OOO0O ):#line:227
        _OOOO0OOOO00OOO00O ,OO0000O0OO0O000OO =O000O000OOOO0O000 .get_xy (OOO0OO000000OOO0O )#line:228
        return OO0000O0OO0O000OO #line:229
    def get_box (OO00O000OO0000O0O ,OOOOO00O00O00O000 ):#line:231
        if isinstance (OOOOO00O00O00O000 ,str ):#line:232
            OOOOO00O00O00O000 =OOOOO00O00O00O000 .lower ()#line:233
            if OOOOO00O00O00O000 in SimpleCamRacer ._BLOBS :#line:234
                OOO0OOO00O0OO0O00 =OO00O000OO0000O0O ._results [SimpleCamRacer ._BLOBS [OOOOO00O00O00O000 ]]#line:235
                if OOO0OOO00O0OO0O00 is not None :#line:236
                    return OOO0OOO00O0OO0O00 ['box']#line:237
        return -1 ,-1 ,-1 ,-1 #line:238
    def get_width (O00OOOOO00OOOOOO0 ,O0OOOOOO0O0000OOO ):#line:240
        if isinstance (O0OOOOOO0O0000OOO ,str ):#line:241
            O0OOOOOO0O0000OOO =O0OOOOOO0O0000OOO .lower ()#line:242
            if O0OOOOOO0O0000OOO in SimpleCamRacer ._BLOBS :#line:243
                OO0OO0O0OOO0OOO00 =O00OOOOO00OOOOOO0 ._results [SimpleCamRacer ._BLOBS [O0OOOOOO0O0000OOO ]]#line:244
                if OO0OO0O0OOO0OOO00 is not None :#line:245
                    return OO0OO0O0OOO0OOO00 ['width']#line:246
        return 0 #line:247
    def get_height (OO0000OO0OO0OO000 ,OO0O0OO000O000000 ):#line:249
        if isinstance (OO0O0OO000O000000 ,str ):#line:250
            OO0O0OO000O000000 =OO0O0OO000O000000 .lower ()#line:251
            if OO0O0OO000O000000 in SimpleCamRacer ._BLOBS :#line:252
                OOO00O00O000O0000 =OO0000OO0OO0OO000 ._results [SimpleCamRacer ._BLOBS [OO0O0OO000O000000 ]]#line:253
                if OOO00O00O000O0000 is not None :#line:254
                    return OOO00O00O000O0000 ['height']#line:255
        return 0 #line:256
    def get_area (O0O00000OOOOO00O0 ,OOO0O0O0OO00O00O0 ):#line:258
        if isinstance (OOO0O0O0OO00O00O0 ,str ):#line:259
            OOO0O0O0OO00O00O0 =OOO0O0O0OO00O00O0 .lower ()#line:260
            if OOO0O0O0OO00O00O0 in SimpleCamRacer ._BLOBS :#line:261
                OO00O00OO00O0O0OO =O0O00000OOOOO00O0 ._results [SimpleCamRacer ._BLOBS [OOO0O0O0OO00O00O0 ]]#line:262
                if OO00O00OO00O0O0OO is not None :#line:263
                    return OO00O00OO00O0O0OO ['area']#line:264
        return 0 #line:265
    def get_pixels (OO0OO0OOO00O0O0OO ,OO00O00000OOOOOO0 ):#line:267
        if isinstance (OO00O00000OOOOOO0 ,str ):#line:268
            OO00O00000OOOOOO0 =OO00O00000OOOOOO0 .lower ()#line:269
            if OO00O00000OOOOOO0 in SimpleCamRacer ._BLOBS :#line:270
                OO00OO0OOOOOOOO00 =OO0OO0OOO00O0O0OO ._results [SimpleCamRacer ._BLOBS [OO00O00000OOOOOO0 ]]#line:271
                if OO00OO0OOOOOOOO00 is not None :#line:272
                    return OO00OO0OOOOOOOO00 ['pixels']#line:273
        return 0 #line:274
