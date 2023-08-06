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

from roboid import *#line:19
from roboidai import KeyEvent #line:20
import os #line:21
import pandas as pd #line:22
_O00O000OOOOO0OO00 ={'en':{'usage':'Press space key to move.\nPress s key to save.\nPress ESC key to quit.\n','saved':'Saved to {}'},'ko':{'usage':'스페이스 키를 누르면 이동합니다.\ns키를 누르면 저장합니다.\nESC 키를 누르면 종료합니다.\n','saved':'{}에 저장되었습니다.'}}#line:34
class _O0OO0OO00OOOOOO00 :#line:37
    _STATE_IDLE =0 #line:38
    _STATE_MOVE =1 #line:39
    def _usage (OO0O0O0000O00OO0O ,lang ='en'):#line:41
        print (_O00O000OOOOO0OO00 [lang ]['usage'])#line:42
    def start (O0OO00O0O00O0000O ,OOOOO0OOOOOO0O000 ,lang ='en'):#line:44
        O0OO00O0O00O0000O ._usage (lang )#line:45
        KeyEvent .start ()#line:46
class _OOOO00000O0000OO0 (_O0OO0OO00OOOOOO00 ):#line:49
    def _create_robot (OO00O00OO000OO0OO ):#line:50
        return None #line:51
    def _save (OO0000OO000O00OOO ,O00O0O000O0OO0OOO ,O0000O0OOO0000O00 ):#line:53
        if isinstance (O0000O0OOO0000O00 ,str ):#line:54
            OOO0O000OO0OOOOO0 =os .path .dirname (O0000O0OOO0000O00 )#line:55
            if not os .path .isdir (OOO0O000OO0OOOOO0 ):#line:56
                os .makedirs (OOO0O000OO0OOOOO0 )#line:57
        O00O0O000O0OO0OOO .to_csv (O0000O0OOO0000O00 ,index =False )#line:58
    def start (OO0OOO0O00000000O ,O00O00000OO0O0O0O ,lang ='en'):#line:60
        super (_OOOO00000O0000OO0 ,OO0OOO0O00000000O ).start (O00O00000OO0O0O0O ,lang )#line:61
        OO0O0OO0OO00O0O00 =OO0OOO0O00000000O ._create_robot ()#line:63
        if OO0O0OO0OO00O0O00 is None :#line:64
            KeyEvent .stop ()#line:65
            return #line:66
        O00O00000OO00OO0O =[]#line:68
        O000O0O0O00O0OO0O =[]#line:69
        OOOO00O00O0OOOO00 =[]#line:70
        O000O00OOOO0000O0 =_O0OO0OO00OOOOOO00 ._STATE_IDLE #line:71
        OOO0OOOOO0O00000O =0 #line:72
        OOO0O0O0O000OO0OO =False #line:73
        while True :#line:75
            OOO0OO0O0O0OOO000 =KeyEvent .get_released_key ()#line:76
            if O000O00OOOO0000O0 ==_O0OO0OO00OOOOOO00 ._STATE_IDLE :#line:77
                if OOO0OO0O0O0OOO000 ==KeyEvent .SPACE :#line:78
                    O000O00OOOO0000O0 =_O0OO0OO00OOOOOO00 ._STATE_MOVE #line:79
                    O00OOOOOOO0000000 =[]#line:80
                    OO0OO00OOO0OOOO00 =[]#line:81
                    O0000O00O000OOO00 =[]#line:82
            elif O000O00OOOO0000O0 ==_O0OO0OO00OOOOOO00 ._STATE_MOVE :#line:83
                O0O00O0000OOOO000 =(OO0O0O0OO0OO00O00 -50 )*0.5 #line:84
                OOOO0OOO0O0OO0000 =30 +O0O00O0000OOOO000 #line:85
                O0OOOOO0000OOOO00 =30 -O0O00O0000OOOO000 #line:86
                OO0O0OO0OO00O0O00 .wheels (OOOO0OOO0O0OO0000 ,O0OOOOO0000OOOO00 )#line:87
                if OOO0O0O0O000OO0OO :#line:88
                    O00OOOOOOO0000000 .append (OO0O0OO0OO00O0O00 .left_floor ())#line:89
                    OO0OO00OOO0OOOO00 .append (OOOO0OOO0O0OO0000 )#line:90
                    O0000O00O000OOO00 .append (O0OOOOO0000OOOO00 )#line:91
                if OO0O0O0OO0OO00O00 <30 and OOOO0O00O0000O00O <30 :#line:93
                    OOO0OOOOO0O00000O +=1 #line:94
                    OOO0O0O0O000OO0OO =False #line:95
                    if OOO0OOOOO0O00000O >3 :#line:96
                        OO0O0OO0OO00O0O00 .stop ()#line:97
                        O000O00OOOO0000O0 =_O0OO0OO00OOOOOO00 ._STATE_IDLE #line:98
                        OOO0OOOOO0O00000O =0 #line:99
                        O00O00000OO00OO0O .extend (O00OOOOOOO0000000 [20 :-20 ])#line:100
                        O000O0O0O00O0OO0O .extend (OO0OO00OOO0OOOO00 [20 :-20 ])#line:101
                        OOOO00O00O0OOOO00 .extend (O0000O00O000OOO00 [20 :-20 ])#line:102
                else :#line:103
                    OOO0OOOOO0O00000O =0 #line:104
                    OOO0O0O0O000OO0OO =True #line:105
            OO0O0O0OO0OO00O00 =OO0O0OO0OO00O0O00 .left_floor ()#line:107
            OOOO0O00O0000O00O =OO0O0OO0OO00O0O00 .right_floor ()#line:108
            if OOO0OO0O0O0OOO000 =='s':#line:109
                O00OOO000O0O0OOO0 =pd .DataFrame ({'left_floor':O00O00000OO00OO0O ,'left_wheel':O000O0O0O00O0OO0O ,'right_wheel':OOOO00O00O0OOOO00 })#line:112
                OO0OOO0O00000000O ._save (O00OOO000O0O0OOO0 ,O00O00000OO0O0O0O )#line:113
                print (_O00O000OOOOO0OO00 [lang ]['saved'].format (O00O00000OO0O0O0O ))#line:114
            elif OOO0OO0O0O0OOO000 ==KeyEvent .ESC :#line:115
                break #line:116
            wait (20 )#line:118
        KeyEvent .stop ()#line:120
        OO0O0OO0OO00O0O00 .dispose ()#line:121
class _OOOOOOOOO0O0000O0 (_OOOO00000O0000OO0 ):#line:124
    def _create_robot (OO000OO0O0O0O00O0 ):#line:125
        return Hamster ()#line:126
class _O0O0O0O00OO00O0OO (_OOOO00000O0000OO0 ):#line:129
    def _create_robot (O00O00OOO00O0O000 ):#line:130
        return HamsterS ()#line:131
class _OOOOO0000OO0OOOOO (_OOOO00000O0000OO0 ):#line:134
    def __init__ (OO0O00O000O0OO000 ,O000O000O0O00OO00 ):#line:135
        OO0O00O000O0OO000 ._robot =O000O000O0O00OO00 #line:136
    def _create_robot (O000OOO0000000OOO ):#line:138
        return O000OOO0000000OOO ._robot #line:139
def record_hamster (OOO00O000O000OO0O ,lang ='en'):#line:142
    _OOOOOOOOO0O0000O0 ().start (OOO00O000O000OO0O ,lang )#line:143
def record_hamster_s (O0OO0OOO0O00O00O0 ,lang ='en'):#line:145
    _O0O0O0O00OO00O0OO ().start (O0OO0OOO0O00O00O0 ,lang )#line:146
def record_driving (O0O000OOOOOO0000O ,OOOOO0OOO00000O0O ,lang ='en'):#line:148
    _OOOOO0000OO0OOOOO (O0O000OOOOOO0000O ).start (OOOOO0OOO00000O0O ,lang )#line:149
