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
import random #line:21
class QWorld :#line:24
    _LEFT ='left'#line:25
    _RIGHT ='right'#line:26
    _UP ='up'#line:27
    _DOWN ='down'#line:28
    _ACTIONS =(_LEFT ,_RIGHT ,_UP ,_DOWN )#line:29
    def __init__ (OOO0OOO0O0OO00OO0 ,O000OO0O0O0O0O00O ):#line:31
        OOO0OOO0O0OO00OO0 ._robot =O000OO0O0O0O0O00O #line:32
        OOO0OOO0O0OO00OO0 ._q =[[None ,None ,None ,None ],[None ,None ,None ,None ],[None ,None ,None ,None ],[None ,None ,None ,None ]]#line:36
        for O0OOOO0OO000OO00O in range (4 ):#line:37
            for OOO000OOO0OO000OO in range (4 ):#line:38
                OOO0OOO0O0OO00OO0 ._q [O0OOOO0OO000OO00O ][OOO000OOO0OO000OO ]={'left':0 ,'right':0 ,'up':0 ,'down':0 }#line:39
        KeyEvent .start ()#line:40
    def wait_space_key (O0000000O0OO00O0O ):#line:42
        while True :#line:43
            O0OOO00OOOOO0OOOO =KeyEvent .get_released_key ()#line:44
            if O0OOO00OOOOO0OOOO ==KeyEvent .SPACE or O0OOO00OOOOO0OOOO ==KeyEvent .ESC :#line:45
                return O0OOO00OOOOO0OOOO #line:46
            elif O0OOO00OOOOO0OOOO =='r':#line:47
                O0000000O0OO00O0O ._robot .reset ()#line:48
            wait (20 )#line:49
    def wait_key (O0O0000OO0O00O0O0 ):#line:51
        while True :#line:52
            OOO0OO000OOO00OOO =KeyEvent .get_released_key ()#line:53
            if OOO0OO000OOO00OOO ==KeyEvent .SPACE or OOO0OO000OOO00OOO ==KeyEvent .ESC or OOO0OO000OOO00OOO =='o'or OOO0OO000OOO00OOO =='x':#line:54
                return OOO0OO000OOO00OOO #line:55
            elif OOO0OO000OOO00OOO =='r':#line:56
                O0O0000OO0O00O0O0 ._robot .reset ()#line:57
            wait (20 )#line:58
    def _is_valid_action (OO0O0OOO0O00O0O00 ,OO0000O0O0O0O0O00 ,OO00O0O0OO00OOOOO ,O00OOOO0OO00O00O0 ):#line:60
        if O00OOOO0OO00O00O0 ==QWorld ._LEFT :return OO0000O0O0O0O0O00 >0 #line:61
        elif O00OOOO0OO00O00O0 ==QWorld ._RIGHT :return OO0000O0O0O0O0O00 <3 #line:62
        elif O00OOOO0OO00O00O0 ==QWorld ._UP :return OO00O0O0OO00OOOOO <3 #line:63
        else :return OO00O0O0OO00OOOOO >0 #line:64
    def _is_opposite_action (OOOOOOO00OO00O00O ,OO00O00O0OO0OO0OO ):#line:66
        OOOOOO0OOOOO0O0O0 =OOOOOOO00OO00O00O ._robot .get_direction ()#line:67
        if OO00O00O0OO0OO0OO ==QWorld ._LEFT :return OOOOOO0OOOOO0O0O0 ==QWorld ._RIGHT #line:68
        elif OO00O00O0OO0OO0OO ==QWorld ._RIGHT :return OOOOOO0OOOOO0O0O0 ==QWorld ._LEFT #line:69
        elif OO00O00O0OO0OO0OO ==QWorld ._UP :return OOOOOO0OOOOO0O0O0 ==QWorld ._DOWN #line:70
        else :return OOOOOO0OOOOO0O0O0 ==QWorld ._UP #line:71
    def get_max_q_action (O0OO0O00O0OOOOOOO ,OOOOO0O00O0O0O000 ,O0OOOO0O0O0OOO000 ):#line:73
        O00OO000OO0O0000O =[]#line:74
        OOO00OO0OO000OOOO =[]#line:75
        for OO00OOOO0OO0O0O0O in QWorld ._ACTIONS :#line:76
            if O0OO0O00O0OOOOOOO ._is_valid_action (OOOOO0O00O0O0O000 ,O0OOOO0O0O0OOO000 ,OO00OOOO0OO0O0O0O )and O0OO0O00O0OOOOOOO ._is_opposite_action (OO00OOOO0OO0O0O0O )==False :#line:77
                O00OO000OO0O0000O .append (O0OO0O00O0OOOOOOO ._q [O0OOOO0O0O0OOO000 ][OOOOO0O00O0O0O000 ][OO00OOOO0OO0O0O0O ])#line:78
                OOO00OO0OO000OOOO .append (OO00OOOO0OO0O0O0O )#line:79
        OO0000OOO0OOO0OO0 =max (O00OO000OO0O0000O )#line:80
        OO0O0O000O0OO0OOO =[]#line:81
        for OO00OOOO0OO0O0O0O in OOO00OO0OO000OOOO :#line:82
            if O0OO0O00O0OOOOOOO ._q [O0OOOO0O0O0OOO000 ][OOOOO0O00O0O0O000 ][OO00OOOO0OO0O0O0O ]==OO0000OOO0OOO0OO0 :#line:83
                OO0O0O000O0OO0OOO .append (OO00OOOO0OO0O0O0O )#line:84
        return random .choice (OO0O0O000O0OO0OOO )#line:85
    def get_max_q (OOO0OOO00OO00O00O ,O00O00OO00O0OOO0O ,OOOO0OOO00O0OOO00 ):#line:87
        O0OOOO0000O00OOO0 =[]#line:88
        for O00O0OO0OO0OO0O00 in QWorld ._ACTIONS :#line:89
            if OOO0OOO00OO00O00O ._is_valid_action (O00O00OO00O0OOO0O ,OOOO0OOO00O0OOO00 ,O00O0OO0OO0OO0O00 ):#line:90
                O0OOOO0000O00OOO0 .append (OOO0OOO00OO00O00O ._q [OOOO0OOO00O0OOO00 ][O00O00OO00O0OOO0O ][O00O0OO0OO0OO0O00 ])#line:91
        return max (O0OOOO0000O00OOO0 )#line:92
    def get_next_max_q (OOOO0OO000OOO0O0O ,O0OOOOO0O00OO000O ,O00OO0OOOO00OOOO0 ,O00O0O00O0O000O0O ):#line:94
        if OOOO0OO000OOO0O0O ._is_valid_action (O0OOOOO0O00OO000O ,O00OO0OOOO00OOOO0 ,O00O0O00O0O000O0O ):#line:95
            if O00O0O00O0O000O0O ==QWorld ._LEFT :#line:96
                return OOOO0OO000OOO0O0O .get_max_q (O0OOOOO0O00OO000O -1 ,O00OO0OOOO00OOOO0 )#line:97
            elif O00O0O00O0O000O0O ==QWorld ._RIGHT :#line:98
                return OOOO0OO000OOO0O0O .get_max_q (O0OOOOO0O00OO000O +1 ,O00OO0OOOO00OOOO0 )#line:99
            elif O00O0O00O0O000O0O ==QWorld ._UP :#line:100
                return OOOO0OO000OOO0O0O .get_max_q (O0OOOOO0O00OO000O ,O00OO0OOOO00OOOO0 +1 )#line:101
            else :#line:102
                return OOOO0OO000OOO0O0O .get_max_q (O0OOOOO0O00OO000O ,O00OO0OOOO00OOOO0 -1 )#line:103
        return 0 #line:104
    def set_q (OOOOO0O0OOOOO0O0O ,OO00OOO0OO0OO0OO0 ,OOO0OO0O0O00OOOOO ,OOO000OO0O0OO000O ,O0000000O00O000OO ):#line:106
        OOOOO0O0OOOOO0O0O ._q [OOO0OO0O0O00OOOOO ][OO00OOO0OO0OO0OO0 ][OOO000OO0O0OO000O ]=O0000000O00O000OO #line:107
class QGame :#line:110
    def __init__ (O0OOOO00OO0O00O0O ):#line:111
        dispose_all ()#line:112
    def start (O0OOO0OO00O0OO0OO ,OOO0O000OO0OO0O0O ):#line:114
        O00000OOOOOOO0O0O =QWorld (OOO0O000OO0OO0O0O )#line:115
        if O00000OOOOOOO0O0O .wait_space_key ()==KeyEvent .ESC :#line:116
            OOO0O000OO0OO0O0O .dispose ()#line:117
            return #line:118
        O00OO00O0OO00OOO0 =[]#line:120
        O00O00OOOO00O000O =0 #line:121
        while True :#line:123
            OO00O000OOO000OO0 =OOO0O000OO0OO0O0O .get_x ()#line:124
            O0O0O0000O000OO00 =OOO0O000OO0OO0O0O .get_y ()#line:125
            O00OOOOO0O0O00O0O =O00000OOOOOOO0O0O .get_max_q_action (OO00O000OOO000OO0 ,O0O0O0000O000OO00 )#line:126
            OO00OOOOOOOO00OOO =O00000OOOOOOO0O0O .get_next_max_q (OO00O000OOO000OO0 ,O0O0O0000O000OO00 ,O00OOOOO0O0O00O0O )#line:127
            print (O00OOOOO0O0O00O0O )#line:129
            OOO0O000OO0OO0O0O .move (O00OOOOO0O0O00O0O )#line:130
            O00O00OOOO00O000O +=1 #line:131
            OOO00O0OO0OO0O000 =O00000OOOOOOO0O0O .wait_key ()#line:132
            if OOO00O0OO0OO0O000 ==KeyEvent .ESC :break #line:133
            O0O000O000OOO0OO0 =0 #line:135
            if OOO00O0OO0OO0O000 =='o':O0O000O000OOO0OO0 =1 #line:136
            elif OOO00O0OO0OO0O000 =='x':O0O000O000OOO0OO0 =-1 #line:137
            O00000OOOOOOO0O0O .set_q (OO00O000OOO000OO0 ,O0O0O0000O000OO00 ,O00OOOOO0O0O00O0O ,O0O000O000OOO0OO0 +0.9 *OO00OOOOOOOO00OOO )#line:139
            if OOO00O0OO0OO0O000 =='o'or OOO00O0OO0OO0O000 =='x':#line:140
                if OOO00O0OO0OO0O000 =='o':#line:141
                    O00OO00O0OO00OOO0 .append (O00O00OOOO00O000O )#line:142
                    O00O00OOOO00O000O =0 #line:143
                    print (O00OO00O0OO00OOO0 )#line:144
                    OOO0O000OO0OO0O0O .express_good ()#line:145
                else :#line:146
                    OOO0O000OO0OO0O0O .express_bad ()#line:147
                OOO0O000OO0OO0O0O .reset ()#line:148
                if O00000OOOOOOO0O0O .wait_space_key ()==KeyEvent .ESC :break #line:149
            wait (20 )#line:151
        OOO0O000OO0OO0O0O .dispose ()#line:153
def play_q_game_hamster ():#line:156
    QGame ().start (GridHamster (y_axis_up =True ))#line:157
def play_q_game_hamster_s (cross =True ):#line:160
    QGame ().start (GridHamsterS (y_axis_up =True ,cross =cross ))#line:161
