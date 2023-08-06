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

_OOO0000OOOO00OO00 ={'en':['bird','dog','elephant','zebra'],'ko':['새','개','코끼리','얼룩말']}#line:23
_OOOOO0O0O0OOOO00O ={'en':{'init':'Place your robot on the starting position and align the direction.','show_animal':'Show the animal on the camera.','guess':'It looks like a(n) {0}. Let\'s move to the {0}\'s house.','replay':'Replay? [y/n]','wing':'Does it have wings?','nose':'Does it have a very long nose?','stripe':'Does it have stripes on the body?','bird':'bird','dog':'dog','elephant':'elephant','zebra':'zebra'},'ko':{'init':'로봇을 출발지에 방향을 맞추어 올려 놓아 주세요.','show_animal':'카메라에 동물을 보여 주세요.','guess':'{0}인 것 같네요. {0} 집으로 이동합니다.','replay':'다시 시작할까요? [y/n]','wing':'날개가 있습니까?','nose':'코가 아주 깁니까?','stripe':'몸에 줄무늬가 있습니까?','bird':'새','dog':'개','elephant':'코끼리','zebra':'얼룩말'}}#line:51
def move_zoo (OOOO0OOO00O00O000 ,OO0O0O0OO00OOOO0O ,lang ='en'):#line:54
    if OO0O0O0OO00OOOO0O ==_OOO0000OOOO00OO00 [lang ][0 ]:#line:55
        OOOO0OOO00O00O000 .board_forward ()#line:56
        OOOO0OOO00O00O000 .board_left ()#line:57
        OOOO0OOO00O00O000 .board_forward ()#line:58
    elif OO0O0O0OO00OOOO0O ==_OOO0000OOOO00OO00 [lang ][1 ]:#line:59
        OOOO0OOO00O00O000 .board_forward ()#line:60
        OOOO0OOO00O00O000 .board_right ()#line:61
        OOOO0OOO00O00O000 .board_forward ()#line:62
    elif OO0O0O0OO00OOOO0O ==_OOO0000OOOO00OO00 [lang ][2 ]:#line:63
        OOOO0OOO00O00O000 .board_forward ()#line:64
        OOOO0OOO00O00O000 .board_forward ()#line:65
        OOOO0OOO00O00O000 .board_left ()#line:66
        OOOO0OOO00O00O000 .board_forward ()#line:67
    elif OO0O0O0OO00OOOO0O ==_OOO0000OOOO00OO00 [lang ][3 ]:#line:68
        OOOO0OOO00O00O000 .board_forward ()#line:69
        OOOO0OOO00O00O000 .board_forward ()#line:70
        OOOO0OOO00O00O000 .board_right ()#line:71
        OOOO0OOO00O00O000 .board_forward ()#line:72
def play_zoo_cam (O0OOO0O000000OOO0 ,O0O0OO0OO000O00O0 ,model_folder =None ,lang ='en'):#line:74
    import roboid #line:75
    import roboidai as ai #line:76
    O00OO00OOO000O000 =ai .ObjectDetector (lang =lang )#line:78
    O00OO00OOO000O000 .download_model (model_folder )#line:79
    O00OO00OOO000O000 .load_model (model_folder )#line:80
    while True :#line:82
        print ()#line:83
        print (_OOOOO0O0O0OOOO00O [lang ]['init'])#line:84
        print (_OOOOO0O0O0OOOO00O [lang ]['show_animal'])#line:85
        while True :#line:86
            O0OO0O00000OOOOO0 =O0O0OO0OO000O00O0 .read ()#line:87
            if O00OO00OOO000O000 .detect (O0OO0O00000OOOOO0 ):#line:88
                O0OOO0O0O0000000O =O00OO00OOO000O000 .get_label ()#line:89
                if O0OOO0O0O0000000O in _OOO0000OOOO00OO00 [lang ]:#line:90
                    O0O0OO0OO000O00O0 .hide ()#line:91
                    print (_OOOOO0O0O0OOOO00O [lang ]['guess'].format (O0OOO0O0O0000000O ))#line:92
                    move_zoo (O0OOO0O000000OOO0 ,O0OOO0O0O0000000O ,lang )#line:93
                    roboid .wait (200 )#line:94
                    break #line:95
            O0O0OO0OO000O00O0 .show (O0OO0O00000OOOOO0 )#line:96
            if O0O0OO0OO000O00O0 .check_key ()=='esc':#line:97
                break #line:98
        print (_OOOOO0O0O0OOOO00O [lang ]['replay'])#line:99
        if input ()!='y':#line:100
            break #line:101
    O0OOO0O000000OOO0 .stop ()#line:102
    roboid .wait (100 )#line:103
def play_zoo_tree (O000O0OOO0OO0OOOO ,lang ='en'):#line:105
    import roboid #line:106
    from ._tree import Node #line:107
    OOOO00OOO000OO000 =Node (_OOOOO0O0O0OOOO00O [lang ]['wing'])#line:109
    OOOO00OOO000OO000 .add_left (_OOOOO0O0O0OOOO00O [lang ]['bird'])#line:110
    O0OOO00O0O00OO000 =OOOO00OOO000OO000 .add_right (_OOOOO0O0O0OOOO00O [lang ]['nose'])#line:111
    O0OOO00O0O00OO000 .add_left (_OOOOO0O0O0OOOO00O [lang ]['elephant'])#line:112
    O0OOO00O0O00OO000 =O0OOO00O0O00OO000 .add_right (_OOOOO0O0O0OOOO00O [lang ]['stripe'])#line:113
    O0OOO00O0O00OO000 .add_left (_OOOOO0O0O0OOOO00O [lang ]['zebra'])#line:114
    O0OOO00O0O00OO000 .add_right (_OOOOO0O0O0OOOO00O [lang ]['dog'])#line:115
    while True :#line:117
        print ()#line:118
        print (_OOOOO0O0O0OOOO00O [lang ]['init'])#line:119
        O0OOO00O0O00OO000 =OOOO00OOO000OO000 #line:120
        while True :#line:121
            if O0OOO00O0O00OO000 .is_terminal ():#line:122
                O000O0000000O00OO =O0OOO00O0O00OO000 .get_key ()#line:123
                print (_OOOOO0O0O0OOOO00O [lang ]['guess'].format (O000O0000000O00OO ))#line:124
                break #line:125
            else :#line:126
                print (O0OOO00O0O00OO000 .get_key ()+'[y/n]')#line:127
                if input ()=='y':#line:128
                    O0OOO00O0O00OO000 =O0OOO00O0O00OO000 .get_left ()#line:129
                else :#line:130
                    O0OOO00O0O00OO000 =O0OOO00O0O00OO000 .get_right ()#line:131
        move_zoo (O000O0OOO0OO0OOOO ,O000O0000000O00OO ,lang )#line:132
        print (_OOOOO0O0O0OOOO00O [lang ]['replay'])#line:133
        if input ()=='y':#line:134
            O0OOO00O0O00OO000 =OOOO00OOO000OO000 #line:135
        else :#line:136
            break #line:137
    O000O0OOO0OO0OOOO .stop ()#line:138
    roboid .wait (100 )#line:139
