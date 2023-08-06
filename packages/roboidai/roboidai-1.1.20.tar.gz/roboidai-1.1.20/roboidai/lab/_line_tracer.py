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
from roboidai ._lang import translate #line:23
class _OO00O00O0OO000OO0 :#line:26
    _STATE_IDLE =0 #line:27
    _STATE_MOVE =1 #line:28
    def _usage (OOOO0000OO00O0OOO ,lang ='en'):#line:30
        print (translate ('lab._line_tracer.usage',lang ))#line:31
    def start (O000000OO00O0O0OO ,OO0O0O0OO0O0O00OO ,lang ='en'):#line:33
        O000000OO00O0O0OO ._usage (lang )#line:34
        KeyEvent .start ()#line:35
class _O0O0000000O0OOOOO (_OO00O00O0OO000OO0 ):#line:38
    def _save (O0OO00O00OOO00OO0 ,OO000OOOO0O000OOO ,O00O0OOOOOO0O0O0O ):#line:39
        if isinstance (O00O0OOOOOO0O0O0O ,str ):#line:40
            O0000000O000OO0O0 =os .path .dirname (O00O0OOOOOO0O0O0O )#line:41
            if not os .path .isdir (O0000000O000OO0O0 ):#line:42
                os .makedirs (O0000000O000OO0O0 )#line:43
        OO000OOOO0O000OOO .to_csv (O00O0OOOOOO0O0O0O ,index =False )#line:44
    def start (OO0OO0O0OOO0000O0 ,O000OO0O0OOOO0OO0 ,O0O0O0OO00O000OO0 ,sensor ='left',lang ='en'):#line:46
        super (_O0O0000000O0OOOOO ,OO0OO0O0OOO0000O0 ).start (O0O0O0OO00O000OO0 ,lang )#line:47
        if O000OO0O0OOOO0OO0 is None :#line:49
            KeyEvent .stop ()#line:50
            return #line:51
        O00OOO00O0OOO0OOO =[]#line:53
        OO0000000OOO0000O =[]#line:54
        O00O0O0OO0OOOO0O0 =[]#line:55
        OOO00O00OOOOOOO0O =[]#line:56
        O0O0OOOO0OOO0OO0O =_OO00O00O0OO000OO0 ._STATE_IDLE #line:57
        OO0000OO000O0OO00 =0 #line:58
        O00000O000OOO0O00 =False #line:59
        while True :#line:61
            O0O00OOOO0O0O0OOO =KeyEvent .get_released_key ()#line:62
            if O0O0OOOO0OOO0OO0O ==_OO00O00O0OO000OO0 ._STATE_IDLE :#line:63
                if O0O00OOOO0O0O0OOO ==KeyEvent .SPACE :#line:64
                    O0O0OOOO0OOO0OO0O =_OO00O00O0OO000OO0 ._STATE_MOVE #line:65
                    OO0O0OOOO0OO0OO00 =[]#line:66
                    OOO0OOOO0OOOOO0O0 =[]#line:67
                    OO000OOO000O000OO =[]#line:68
                    OO00OO0O00OOO00OO =[]#line:69
            elif O0O0OOOO0OOO0OO0O ==_OO00O00O0OO000OO0 ._STATE_MOVE :#line:70
                if sensor =='left':#line:71
                    O00000OO000OOO00O =(O00000O00OOO0O00O -50 )*0.5 #line:72
                elif sensor =='right':#line:73
                    O00000OO000OOO00O =(50 -O0O00000O00O000OO )*0.5 #line:74
                else :#line:75
                    O00000OO000OOO00O =(O00000O00OOO0O00O -O0O00000O00O000OO )*0.5 #line:76
                OO0O0OOOO0OOOOO00 =30 +O00000OO000OOO00O #line:77
                OOOO00O0O00O000O0 =30 -O00000OO000OOO00O #line:78
                O000OO0O0OOOO0OO0 .wheels (OO0O0OOOO0OOOOO00 ,OOOO00O0O00O000O0 )#line:79
                if O00000O000OOO0O00 :#line:80
                    OO0O0OOOO0OO0OO00 .append (O000OO0O0OOOO0OO0 .left_floor ())#line:81
                    OOO0OOOO0OOOOO0O0 .append (O000OO0O0OOOO0OO0 .right_floor ())#line:82
                    OO000OOO000O000OO .append (OO0O0OOOO0OOOOO00 )#line:83
                    OO00OO0O00OOO00OO .append (OOOO00O0O00O000O0 )#line:84
                if O00000O00OOO0O00O <30 and O0O00000O00O000OO <30 :#line:86
                    OO0000OO000O0OO00 +=1 #line:87
                    O00000O000OOO0O00 =False #line:88
                    if OO0000OO000O0OO00 >3 :#line:89
                        O000OO0O0OOOO0OO0 .stop ()#line:90
                        O0O0OOOO0OOO0OO0O =_OO00O00O0OO000OO0 ._STATE_IDLE #line:91
                        OO0000OO000O0OO00 =0 #line:92
                        O00OOO00O0OOO0OOO .extend (OO0O0OOOO0OO0OO00 [20 :-20 ])#line:93
                        OO0000000OOO0000O .extend (OOO0OOOO0OOOOO0O0 [20 :-20 ])#line:94
                        O00O0O0OO0OOOO0O0 .extend (OO000OOO000O000OO [20 :-20 ])#line:95
                        OOO00O00OOOOOOO0O .extend (OO00OO0O00OOO00OO [20 :-20 ])#line:96
                else :#line:97
                    OO0000OO000O0OO00 =0 #line:98
                    O00000O000OOO0O00 =True #line:99
            O00000O00OOO0O00O =O000OO0O0OOOO0OO0 .left_floor ()#line:101
            O0O00000O00O000OO =O000OO0O0OOOO0OO0 .right_floor ()#line:102
            if O0O00OOOO0O0O0OOO ==KeyEvent .ESC :#line:103
                if sensor =='left':#line:104
                    O00O0O0O00OOOO000 =pd .DataFrame ({'left_floor':O00OOO00O0OOO0OOO ,'left_wheel':O00O0O0OO0OOOO0O0 ,'right_wheel':OOO00O00OOOOOOO0O })#line:107
                elif sensor =='right':#line:108
                    O00O0O0O00OOOO000 =pd .DataFrame ({'right_floor':OO0000000OOO0000O ,'left_wheel':O00O0O0OO0OOOO0O0 ,'right_wheel':OOO00O00OOOOOOO0O })#line:111
                else :#line:112
                    O00O0O0O00OOOO000 =pd .DataFrame ({'left_floor':O00OOO00O0OOO0OOO ,'right_floor':OO0000000OOO0000O ,'left_wheel':O00O0O0OO0OOOO0O0 ,'right_wheel':OOO00O00OOOOOOO0O })#line:116
                OO0OO0O0OOO0000O0 ._save (O00O0O0O00OOOO000 ,O0O0O0OO00O000OO0 )#line:117
                print (translate ('lab._line_tracer.saved',lang ).format (O0O0O0OO00O000OO0 ))#line:118
                wait (1000 )#line:119
                break #line:120
            wait (20 )#line:122
        KeyEvent .stop ()#line:124
        O000OO0O0OOOO0OO0 .dispose ()#line:125
def collect_driving_data (OO00O00OOOO0O00OO ,OO000OO0O000OOO00 ,sensor ='all',lang ='en'):#line:128
    if isinstance (OO00O00OOOO0O00OO ,Hamster )or isinstance (OO00O00OOOO0O00OO ,HamsterS ):#line:129
        _O0O0000000O0OOOOO ().start (OO00O00OOOO0O00OO ,OO000OO0O000OOO00 ,sensor ,lang )#line:130
