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
import mediapipe as mp #line:21
from ._util import Util #line:22
class FaceDetector :#line:25
    def __init__ (OO0OOOO00000O00O0 ,threshold =0.5 ):#line:26
        OO0OOOO00000O00O0 ._clear ()#line:27
        try :#line:28
            OO0OOOO00000O00O0 ._model =mp .solutions .face_detection .FaceDetection (min_detection_confidence =threshold )#line:29
        except :#line:30
            OO0OOOO00000O00O0 ._model =None #line:31
    def _clear (O0OO0O000000OO0O0 ):#line:33
        O0OO0O000000OO0O0 ._points ={'left eye':None ,'right eye':None ,'left ear':None ,'right ear':None ,'nose':None ,'mouth':None }#line:41
        O0OO0O000000OO0O0 ._box =None #line:42
        O0OO0O000000OO0O0 ._width =0 #line:43
        O0OO0O000000OO0O0 ._height =0 #line:44
        O0OO0O000000OO0O0 ._area =0 #line:45
        O0OO0O000000OO0O0 ._confidence =0 #line:46
        O0OO0O000000OO0O0 ._drawings =None #line:47
    def detect (O0OO00000O0000O0O ,O0OO000O00O0O0OOO ,padding =0 ):#line:49
        if O0OO000O00O0O0OOO is not None and O0OO00000O0000O0O ._model is not None :#line:50
            O0OO000O00O0O0OOO =cv2 .cvtColor (O0OO000O00O0O0OOO ,cv2 .COLOR_BGR2RGB )#line:51
            O0OO000O00O0O0OOO .flags .writeable =False #line:52
            O0OOO0O0OOO0OO00O =O0OO00000O0000O0O ._model .process (O0OO000O00O0O0OOO )#line:53
            if O0OOO0O0OOO0OO00O and O0OOO0O0OOO0OO00O .detections and len (O0OOO0O0OOO0OO00O .detections )>0 :#line:54
                OOO0OO0OO00OO000O =O0OOO0O0OOO0OO00O .detections [0 ]#line:55
                O0OO000OOO0O0O0OO =OOO0OO0OO00OO000O .location_data #line:56
                if O0OO000OOO0O0O0OO :#line:57
                    OO00OO00OO00OOO00 =O0OO000OOO0O0O0OO .relative_bounding_box #line:58
                    if OO00OO00OO00OOO00 :#line:59
                        O00O00000O0O0O00O =O0OO000O00O0O0OOO .shape [1 ]#line:60
                        OO0000OOO0OOO0000 =O0OO000O00O0O0OOO .shape [0 ]#line:61
                        OO0O00O0000O00OOO =O0OO00000O0000O0O ._box #line:62
                        if OO0O00O0000O00OOO is None :OO0O00O0000O00OOO =np .zeros (4 )#line:63
                        OO0O00O0000O00OOO [0 ]=max (0 ,OO00OO00OO00OOO00 .xmin *O00O00000O0O0O00O -padding )#line:64
                        OO0O00O0000O00OOO [1 ]=max (0 ,OO00OO00OO00OOO00 .ymin *OO0000OOO0OOO0000 -padding )#line:65
                        OO0O00O0000O00OOO [2 ]=min ((OO00OO00OO00OOO00 .xmin +OO00OO00OO00OOO00 .width )*O00O00000O0O0O00O +padding ,O00O00000O0O0O00O -1 )#line:66
                        OO0O00O0000O00OOO [3 ]=min ((OO00OO00OO00OOO00 .ymin +OO00OO00OO00OOO00 .height )*OO0000OOO0OOO0000 +padding ,OO0000OOO0OOO0000 -1 )#line:67
                        OO0O00O0000O00OOO =OO0O00O0000O00OOO .astype (np .int32 )#line:68
                        O0OO00000O0000O0O ._box =OO0O00O0000O00OOO #line:69
                        O0OO00000O0000O0O ._width =abs (OO0O00O0000O00OOO [2 ]-OO0O00O0000O00OOO [0 ])#line:70
                        O0OO00000O0000O0O ._height =abs (OO0O00O0000O00OOO [3 ]-OO0O00O0000O00OOO [1 ])#line:71
                        O0OO00000O0000O0O ._area =O0OO00000O0000O0O ._width *O0OO00000O0000O0O ._height #line:72
                        OO0OOO0O0O00O00O0 =[O00OOO0O000000000 .x for O00OOO0O000000000 in O0OO000OOO0O0O0OO .relative_keypoints ]#line:73
                        OOOOOO0O0OOOOOOOO =[O0OOOOO00OO00OO0O .y for O0OOOOO00OO00OO0O in O0OO000OOO0O0O0OO .relative_keypoints ]#line:74
                        O00O0OOOO0000OOO0 =np .transpose (np .stack ((OO0OOO0O0O00O00O0 ,OOOOOO0O0OOOOOOOO )))*(O00O00000O0O0O00O ,OO0000OOO0OOO0000 )#line:75
                        O00O0OOOO0000OOO0 =O00O0OOOO0000OOO0 .astype (np .int32 )#line:76
                        OO0O00000O0OO000O =O0OO00000O0000O0O ._points #line:77
                        OO0O00000O0OO000O ['left eye']=O00O0OOOO0000OOO0 [0 ]#line:78
                        OO0O00000O0OO000O ['right eye']=O00O0OOOO0000OOO0 [1 ]#line:79
                        OO0O00000O0OO000O ['left ear']=O00O0OOOO0000OOO0 [4 ]#line:80
                        OO0O00000O0OO000O ['right ear']=O00O0OOOO0000OOO0 [5 ]#line:81
                        OO0O00000O0OO000O ['nose']=O00O0OOOO0000OOO0 [2 ]#line:82
                        OO0O00000O0OO000O ['mouth']=O00O0OOOO0000OOO0 [3 ]#line:83
                        O0OO00000O0000O0O ._confidence =OOO0OO0OO00OO000O .score [0 ]#line:84
                        O0OO00000O0000O0O ._drawings =np .concatenate ((OO0O00O0000O00OOO ,O00O0OOOO0000OOO0 .reshape (-1 )),axis =None )#line:85
                        return True #line:86
        O0OO00000O0000O0O ._clear ()#line:87
        return False #line:88
    def _draw (OOO0O0O0O0000OO00 ,OO000OO000O000O0O ,O00000O000OO0O00O ,OOO0OOO0OOO0O0000 ,OO00O0OO000000O00 ):#line:90
        cv2 .rectangle (OO000OO000O000O0O ,(O00000O000OO0O00O [0 ],O00000O000OO0O00O [1 ]),(O00000O000OO0O00O [2 ],O00000O000OO0O00O [3 ]),OOO0OOO0OOO0O0000 ,OO00O0OO000000O00 )#line:91
        cv2 .circle (OO000OO000O000O0O ,(O00000O000OO0O00O [4 ],O00000O000OO0O00O [5 ]),OO00O0OO000000O00 ,OOO0OOO0OOO0O0000 ,-1 )#line:92
        cv2 .circle (OO000OO000O000O0O ,(O00000O000OO0O00O [6 ],O00000O000OO0O00O [7 ]),OO00O0OO000000O00 ,OOO0OOO0OOO0O0000 ,-1 )#line:93
        cv2 .circle (OO000OO000O000O0O ,(O00000O000OO0O00O [8 ],O00000O000OO0O00O [9 ]),OO00O0OO000000O00 ,OOO0OOO0OOO0O0000 ,-1 )#line:94
        cv2 .circle (OO000OO000O000O0O ,(O00000O000OO0O00O [10 ],O00000O000OO0O00O [11 ]),OO00O0OO000000O00 ,OOO0OOO0OOO0O0000 ,-1 )#line:95
        cv2 .circle (OO000OO000O000O0O ,(O00000O000OO0O00O [12 ],O00000O000OO0O00O [13 ]),OO00O0OO000000O00 ,OOO0OOO0OOO0O0000 ,-1 )#line:96
        cv2 .circle (OO000OO000O000O0O ,(O00000O000OO0O00O [14 ],O00000O000OO0O00O [15 ]),OO00O0OO000000O00 ,OOO0OOO0OOO0O0000 ,-1 )#line:97
    def draw_result (OO0O00000OO00O0OO ,OOO0000O00OOOO0OO ,color =(0 ,255 ,0 ),thickness =2 ,clone =False ):#line:99
        if OOO0000O00OOOO0OO is not None :#line:100
            if clone :#line:101
                OOO0000O00OOOO0OO =OOO0000O00OOOO0OO .copy ()#line:102
            if OO0O00000OO00O0OO ._drawings is not None :#line:103
                OO0O00000OO00O0OO ._draw (OOO0000O00OOOO0OO ,OO0O00000OO00O0OO ._drawings ,color ,thickness )#line:104
        return OOO0000O00OOOO0OO #line:105
    def get_xy (OO00OO0O000000OOO ,id ='all'):#line:107
        if isinstance (id ,str ):#line:108
            id =id .lower ()#line:109
            if id =='all':#line:110
                return OO00OO0O000000OOO ._points #line:111
            elif id in OO00OO0O000000OOO ._points :#line:112
                return OO00OO0O000000OOO ._points [id ]#line:113
        return None #line:114
    def get_box (OOO0O0OOOO000O000 ):#line:116
        return OOO0O0OOOO000O000 ._box #line:117
    def get_width (O000000OOO0000OOO ):#line:119
        return O000000OOO0000OOO ._width #line:120
    def get_height (O0OO0000OOOO00O00 ):#line:122
        return O0OO0000OOOO00O00 ._height #line:123
    def get_area (O00000OOOOOO0O0O0 ):#line:125
        return O00000OOOOOO0O0O0 ._area #line:126
    def get_conf (O0000OOO0O0OO00O0 ):#line:128
        return O0000OOO0O0OO00O0 ._confidence #line:129
    def get_orientation (OOOO00O000OO00000 ,degree =False ):#line:131
        O0O00O0O000OOOOO0 =OOOO00O000OO00000 .get_xy ('left eye')#line:132
        O0OO00O0OO00OO000 =OOOO00O000OO00000 .get_xy ('right eye')#line:133
        if degree :#line:134
            return Util .degree (O0O00O0O000OOOOO0 ,O0OO00O0OO00OO000 )#line:135
        else :#line:136
            return Util .radian (O0O00O0O000OOOOO0 ,O0OO00O0OO00OO000 )#line:137
    def crop (O00OOO000OOO0O0OO ,OOO00O0O0O0000000 ,clone =False ):#line:139
        if OOO00O0O0O0000000 is None or O00OOO000OOO0O0OO ._box is None :return None #line:140
        if clone :OOO00O0O0O0000000 =OOO00O0O0O0000000 .copy ()#line:141
        OO0O0OO00000O0O0O =O00OOO000OOO0O0OO ._box #line:142
        return OOO00O0O0O0000000 [OO0O0OO00000O0O0O [1 ]:OO0O0OO00000O0O0O [3 ],OO0O0OO00000O0O0O [0 ]:OO0O0OO00000O0O0O [2 ]]#line:143
    @staticmethod #line:145
    def distance (O0O00OO000OOO0OO0 ,O0O0O0OOOO00O00O0 ):#line:146
        return Util .distance (O0O00OO000OOO0OO0 ,O0O0O0OOOO00O00O0 )#line:147
    @staticmethod #line:149
    def degree (OOOO00OOO0OOO00OO ,O000O00000O00000O ):#line:150
        return Util .degree (OOOO00OOO0OOO00OO ,O000O00000O00000O )#line:151
    @staticmethod #line:153
    def radian (O0O000O0O00OO0O0O ,OO0OOOOO0O00OOO0O ):#line:154
        return Util .radian (O0O000O0O00OO0O0O ,OO0OOOOO0O00OOO0O )#line:155
