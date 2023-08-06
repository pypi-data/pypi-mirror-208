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
import os #line:21
from datetime import datetime #line:22
from timeit import default_timer as timer #line:23
from roboidai ._lang import translate #line:24
_O0O0000O000000OOO ={'en':{'capture_color':'Press SPACE key to collect color data or ESC key to quit.','capture_image':'Press SPACE key to save image or ESC key to quit.','record_image':'Press ESC key to quit.','saved':'saved'},'ko':{'capture_color':'스페이스 키를 누르면 색깔 데이터를 수집하고 ESC 키를 누르면 종료합니다.','capture_image':'스페이스 키를 누르면 영상 한 장을 저장하고 ESC 키를 누르면 종료합니다.','record_image':'ESC 키를 누르면 종료합니다.','saved':'저장됨'}}#line:40
_OO00O0OOOO0O000OO ={'hsv':cv2 .COLOR_BGR2HSV ,'ycrcb':cv2 .COLOR_BGR2YCrCb }#line:44
def collect_image (O0OOOOOOO0OOOO0O0 ,OO0000O0O00OO00OO ,lang ='en'):#line:47
    print (translate ('lab._image.capture_image',lang ))#line:48
    O0O000OOOO0O00000 =0 #line:49
    while True :#line:50
        O000OOOOOOO000000 ,O00O0OO0000OO00OO =O0OOOOOOO0OOOO0O0 .read_until_key ()#line:51
        if O00O0OO0000OO00OO =='esc':#line:52
            break #line:53
        elif O00O0OO0000OO00OO ==' ':#line:54
            if (save_image (O000OOOOOOO000000 ,OO0000O0O00OO00OO )):#line:55
                O0O000OOOO0O00000 +=1 #line:56
                print (translate ('lab._image.saved',lang ),O0O000OOOO0O00000 )#line:57
def record_image (OO000OOOOO0O00O00 ,O000O000000OO0O00 ,interval_msec =100 ,frames =20 ,countdown =3 ,lang ='en'):#line:59
    print (translate ('lab._image.record_image',lang ))#line:60
    if countdown >0 :#line:61
        OO000OOOOO0O00O00 .count_down (countdown )#line:62
    OOO0O0O00OOO0000O =0 #line:63
    O000OOO000O000000 =timer ()#line:64
    while True :#line:65
        if OOO0O0O00OOO0000O >=frames :break #line:66
        O0O00000O0O0O00O0 =OO000OOOOO0O00O00 .read ()#line:67
        OO000OOOOO0O00O00 .show (O0O00000O0O0O00O0 )#line:68
        if timer ()>O000OOO000O000000 :#line:69
            if (save_image (O0O00000O0O0O00O0 ,O000O000000OO0O00 )):#line:70
                OOO0O0O00OOO0000O +=1 #line:71
                print (translate ('lab._image.saved',lang ),OOO0O0O00OOO0000O )#line:72
            O000OOO000O000000 +=interval_msec /1000.0 #line:73
        if OO000OOOOO0O00O00 .check_key ()=='esc':#line:74
            break #line:75
def save_image (OOOOO0000O0O000O0 ,O0O00OOO00O000O00 ,filename =None ):#line:77
    if OOOOO0000O0O000O0 is not None and O0O00OOO00O000O00 is not None :#line:78
        if not os .path .isdir (O0O00OOO00O000O00 ):#line:79
            os .makedirs (O0O00OOO00O000O00 )#line:80
        if filename is None :#line:81
            filename =datetime .now ().strftime ("%Y%m%d_%H%M%S_%f")+'.png'#line:82
        if cv2 .imwrite (os .path .join (O0O00OOO00O000O00 ,filename ),OOOOO0000O0O000O0 ):#line:83
            return True #line:84
        try :#line:85
            OOO000O00O0OO0O00 =os .path .splitext (filename )[1 ]#line:86
            OOOOO0OO00OO0O0OO ,OO0OOOO00OO0OOOOO =cv2 .imencode (OOO000O00O0OO0O00 ,OOOOO0000O0O000O0 )#line:87
            if OOOOO0OO00OO0O0OO :#line:88
                with open (os .path .join (O0O00OOO00O000O00 ,filename ),mode ='w+b')as OO00OOOOO00000000 :#line:89
                    OO0OOOO00OO0OOOOO .tofile (OO00OOOOO00000000 )#line:90
                return True #line:91
            else :#line:92
                return False #line:93
        except :#line:94
            return False #line:95
    return False #line:96
def collect_color (O0000O00OOO0000OO ,OOOOOOOOO000O00O0 ,color_space ='hsv',lang ='en'):#line:98
    OOOO00O0O0O0OOO00 =None #line:99
    if isinstance (color_space ,(int ,float )):#line:100
        OOOO00O0O0O0OOO00 =int (color_space )#line:101
    elif isinstance (color_space ,str ):#line:102
        color_space =color_space .lower ()#line:103
        if color_space in _OO00O0OOOO0O000OO :#line:104
            OOOO00O0O0O0OOO00 =_OO00O0OOOO0O000OO [color_space ]#line:105
    O0O0O0O0000O0000O =[]#line:107
    OO0O0OO0O0O00O0O0 =[]#line:108
    OOO0000O0OO00OOOO =[]#line:109
    O0OO00000OO0OOO00 =[]#line:110
    for OO00OOO00O00OO0O0 ,OOO00O0O0O0O0OOO0 in enumerate (OOOOOOOOO000O00O0 ):#line:111
        print ('[{}] {}'.format (OOO00O0O0O0O0OOO0 ,_O0O0000O000000OOO [lang ]['capture_color']))#line:112
        O0O00O0OOOOOO000O ,O0OOOO00OO000OOO0 =O0000O00OOO0000OO .read_until_key ()#line:113
        if O0OOOO00OO000OOO0 =='esc':#line:114
            O0000O00OOO0000OO .hide ()#line:115
            return None ,None #line:116
        elif O0OOOO00OO000OOO0 ==' 'and O0O00O0OOOOOO000O is not None :#line:117
            OOO0OOOO0O000O000 =O0O00O0OOOOOO000O if OOOO00O0O0O0OOO00 is None else cv2 .cvtColor (O0O00O0OOOOOO000O ,OOOO00O0O0O0OOO00 )#line:118
            O0O0O0O0000O0000O .append (OOO0OOOO0O000O000 [:,:,0 ])#line:119
            OO0O0OO0O0O00O0O0 .append (OOO0OOOO0O000O000 [:,:,1 ])#line:120
            OOO0000O0OO00OOOO .append (OOO0OOOO0O000O000 [:,:,2 ])#line:121
            O0OO00000OO0OOO00 .append ([OO00OOO00O00OO0O0 ]*(OOO0OOOO0O000O000 .shape [0 ]*OOO0OOOO0O000O000 .shape [1 ]))#line:122
    O0000O00OOO0000OO .hide ()#line:123
    OOOO000O0OO0OO0OO =np .concatenate (O0O0O0O0000O0000O ,axis =None ).reshape (-1 ,1 )#line:125
    OO0O000OOO000000O =np .concatenate (OO0O0OO0O0O00O0O0 ,axis =None ).reshape (-1 ,1 )#line:126
    OOO0000OO0000OO0O =np .concatenate (OOO0000O0OO00OOOO ,axis =None ).reshape (-1 ,1 )#line:127
    O0OOOOOOOO0O0OOOO =np .concatenate (O0OO00000OO0OOO00 ,axis =None )#line:128
    O0OO0000O00OO0O00 =np .hstack ((OOOO000O0OO0OO0OO ,OO0O000OOO000000O ,OOO0000OO0000OO0O ))#line:129
    return O0OO0000O00OO0O00 ,O0OOOOOOOO0O0OOOO #line:131
def capture_color (O00OO00OO00O00000 ,color_space ='hsv',lang ='en'):#line:133
    OOOO00O000O000O00 =None #line:134
    if isinstance (color_space ,(int ,float )):#line:135
        OOOO00O000O000O00 =int (color_space )#line:136
    elif isinstance (color_space ,str ):#line:137
        color_space =color_space .lower ()#line:138
        if color_space in _OO00O0OOOO0O000OO :#line:139
            OOOO00O000O000O00 =_OO00O0OOOO0O000OO [color_space ]#line:140
    OOOOO000OOO0OO000 =None #line:142
    print (_O0O0000O000000OOO [lang ]['capture_color'])#line:143
    OOO00O0000O00O00O ,O00OOOO000OOOOO0O =O00OO00OO00O00000 .read_until_key ()#line:144
    if O00OOOO000OOOOO0O =='esc':#line:145
        O00OO00OO00O00000 .hide ()#line:146
        return None #line:147
    elif O00OOOO000OOOOO0O ==' 'and OOO00O0000O00O00O is not None :#line:148
        O0O00OO0OOO00O000 =OOO00O0000O00O00O if OOOO00O000O000O00 is None else cv2 .cvtColor (OOO00O0000O00O00O ,OOOO00O000O000O00 )#line:149
        OO000OOO00O0O0O0O =O0O00OO0OOO00O000 [:,:,0 ].reshape (-1 ,1 )#line:150
        OO0OOOOO00O0O0O00 =O0O00OO0OOO00O000 [:,:,1 ].reshape (-1 ,1 )#line:151
        O0O0O0O0OOO000O00 =O0O00OO0OOO00O000 [:,:,2 ].reshape (-1 ,1 )#line:152
        OOOOO000OOO0OO000 =np .hstack ((OO000OOO00O0O0O0O ,OO0OOOOO00O0O0O00 ,O0O0O0O0OOO000O00 ))#line:153
    O00OO00OO00O00000 .hide ()#line:154
    return OOOOO000OOO0OO000 #line:155
