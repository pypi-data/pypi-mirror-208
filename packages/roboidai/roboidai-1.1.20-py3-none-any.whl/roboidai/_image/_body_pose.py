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
from timeit import default_timer as timer #line:23
_O000O0O0O0OO000O0 ={'head':[0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ],'left arm':[12 ,13 ,16 ,17 ,20 ,21 ,24 ,25 ],'right arm':[14 ,15 ,18 ,19 ,22 ,23 ,26 ,27 ],'left leg':[28 ,29 ,32 ,33 ,36 ,37 ,40 ,41 ],'right leg':[30 ,31 ,34 ,35 ,38 ,39 ,42 ,43 ]}#line:32
_O0OOO000OOOOO00O0 =[[11 ,12 ],[11 ,13 ],[13 ,15 ],[12 ,14 ],[14 ,16 ],[11 ,23 ],[12 ,24 ],[23 ,24 ],[23 ,25 ],[24 ,26 ],[25 ,27 ],[26 ,28 ]]#line:33
class BodyPose :#line:36
    def __init__ (OOOO000OOOOO00O00 ):#line:37
        OOOO000OOOOO00O00 ._loaded =False #line:38
        OOOO000OOOOO00O00 ._clear ()#line:39
    def _clear (OO0OO00OO0OOOO0OO ):#line:41
        OO0OO00OO0OOOO0OO ._landmarks =None #line:42
        OO0OO00OO0OOOO0OO ._drawings =None #line:43
    def load_model (O0OOOOO0OOOOO00OO ,threshold =0.5 ):#line:45
        try :#line:46
            O0OOOOO0OOOOO00OO ._pose =mp .solutions .pose .Pose (min_detection_confidence =threshold ,min_tracking_confidence =0.5 )#line:47
            O0OOOOO0OOOOO00OO ._loaded =True #line:48
            return True #line:49
        except :#line:50
            return False #line:51
    def _fill_data (OOO0OOO0OOOOOO0O0 ,OOO0O0O0O0O0OOO00 ):#line:53
        OO00000000OOOO0OO ={}#line:54
        OO00000000OOOO0OO ['left eye']=OOO0O0O0O0O0OOO00 [5 ]#line:55
        OO00000000OOOO0OO ['right eye']=OOO0O0O0O0O0OOO00 [2 ]#line:56
        OO00000000OOOO0OO ['left ear']=OOO0O0O0O0O0OOO00 [8 ]#line:57
        OO00000000OOOO0OO ['right ear']=OOO0O0O0O0O0OOO00 [7 ]#line:58
        OO00000000OOOO0OO ['nose']=OOO0O0O0O0O0OOO00 [0 ]#line:59
        OO00000000OOOO0OO ['mouth']=np .around (OOO0O0O0O0O0OOO00 [9 ]*0.5 +OOO0O0O0O0O0OOO00 [10 ]*0.5 ).astype (np .int32 )#line:60
        O0OOOO0O0O000O0OO =OOO0O0O0O0O0OOO00 [11 ]*0.5 +OOO0O0O0O0O0OOO00 [12 ]*0.5 #line:61
        O0OOOO0O0O000O0OO [0 ]=O0OOOO0O0O000O0OO [0 ]*0.5 +OOO0O0O0O0O0OOO00 [0 ][0 ]*0.5 #line:62
        O0OOOO0O0O000O0OO [1 ]=O0OOOO0O0O000O0OO [1 ]*0.75 +OOO0O0O0O0O0OOO00 [0 ][1 ]*0.25 #line:63
        OO00000000OOOO0OO ['neck']=np .around (O0OOOO0O0O000O0OO ).astype (np .int32 )#line:64
        OO00000000OOOO0OO ['left shoulder']=OOO0O0O0O0O0OOO00 [12 ]#line:65
        OO00000000OOOO0OO ['right shoulder']=OOO0O0O0O0O0OOO00 [11 ]#line:66
        OO00000000OOOO0OO ['left elbow']=OOO0O0O0O0O0OOO00 [14 ]#line:67
        OO00000000OOOO0OO ['right elbow']=OOO0O0O0O0O0OOO00 [13 ]#line:68
        OO00000000OOOO0OO ['left wrist']=OOO0O0O0O0O0OOO00 [16 ]#line:69
        OO00000000OOOO0OO ['right wrist']=OOO0O0O0O0O0OOO00 [15 ]#line:70
        OO00000000OOOO0OO ['left hand']=np .around ((OOO0O0O0O0O0OOO00 [16 ]+OOO0O0O0O0O0OOO00 [18 ]+OOO0O0O0O0O0OOO00 [20 ]+OOO0O0O0O0O0OOO00 [22 ])*0.25 ).astype (np .int32 )#line:71
        OO00000000OOOO0OO ['right hand']=np .around ((OOO0O0O0O0O0OOO00 [15 ]+OOO0O0O0O0O0OOO00 [17 ]+OOO0O0O0O0O0OOO00 [19 ]+OOO0O0O0O0O0OOO00 [21 ])*0.25 ).astype (np .int32 )#line:72
        OO00000000OOOO0OO ['left hip']=OOO0O0O0O0O0OOO00 [24 ]#line:73
        OO00000000OOOO0OO ['right hip']=OOO0O0O0O0O0OOO00 [23 ]#line:74
        OO00000000OOOO0OO ['left knee']=OOO0O0O0O0O0OOO00 [26 ]#line:75
        OO00000000OOOO0OO ['right knee']=OOO0O0O0O0O0OOO00 [25 ]#line:76
        OO00000000OOOO0OO ['left ankle']=OOO0O0O0O0O0OOO00 [28 ]#line:77
        OO00000000OOOO0OO ['right ankle']=OOO0O0O0O0O0OOO00 [27 ]#line:78
        OO00000000OOOO0OO ['left foot']=np .around ((OOO0O0O0O0O0OOO00 [28 ]+OOO0O0O0O0O0OOO00 [30 ]+OOO0O0O0O0O0OOO00 [32 ])/3 ).astype (np .int32 )#line:79
        OO00000000OOOO0OO ['right foot']=np .around ((OOO0O0O0O0O0OOO00 [27 ]+OOO0O0O0O0O0OOO00 [29 ]+OOO0O0O0O0O0OOO00 [31 ])/3 ).astype (np .int32 )#line:80
        return OO00000000OOOO0OO #line:81
    def detect (OO0O0OOOOOO0O0000 ,OO0OOOOOOOO000O0O ):#line:83
        if OO0OOOOOOOO000O0O is not None and OO0O0OOOOOO0O0000 ._loaded :#line:84
            OO0OOOOOOOO000O0O =cv2 .cvtColor (OO0OOOOOOOO000O0O ,cv2 .COLOR_BGR2RGB )#line:85
            OO0OOOOOOOO000O0O .flags .writeable =False #line:86
            OO0O00O00O0OOO00O =OO0O0OOOOOO0O0000 ._pose .process (OO0OOOOOOOO000O0O )#line:87
            if OO0O00O00O0OOO00O and OO0O00O00O0OOO00O .pose_landmarks :#line:88
                OOOO00O00O00OO0OO =OO0O00O00O0OOO00O .pose_landmarks #line:89
                OOO0OO00OO0000OOO =OO0OOOOOOOO000O0O .shape [1 ]#line:90
                O00O0OOOO0000OO00 =OO0OOOOOOOO000O0O .shape [0 ]#line:91
                O0O00O00000O00000 =[OOOO0OO0OOOO0OO0O .x for OOOO0OO0OOOO0OO0O in OOOO00O00O00OO0OO .landmark ]#line:92
                O000OO0O00OO0OOO0 =[O0O000O000OO0O00O .y for O0O000O000OO0O00O in OOOO00O00O00OO0OO .landmark ]#line:93
                O00O00O0000O0OO0O =np .transpose (np .stack ((O0O00O00000O00000 ,O000OO0O00OO0OOO0 )))*(OOO0OO00OO0000OOO ,O00O0OOOO0000OO00 )#line:94
                O00O00O0000O0OO0O =O00O00O0000O0OO0O .astype (np .int32 )#line:95
                OO0O0OOOOOO0O0000 ._landmarks =OO0O0OOOOOO0O0000 ._fill_data (O00O00O0000O0OO0O )#line:96
                OO0O0OOOOOO0O0000 ._drawings =[O00O00O0000O0OO0O ,OO0O0OOOOOO0O0000 ._landmarks ]#line:97
                return True #line:98
        OO0O0OOOOOO0O0000 ._clear ()#line:99
        return False #line:100
    def draw_result (OO0OO00O0OOO0OOO0 ,O000OO00000OOOO00 ,clone =False ):#line:102
        if O000OO00000OOOO00 is not None and OO0OO00O0OOO0OOO0 ._drawings is not None :#line:103
            if clone :#line:104
                O000OO00000OOOO00 =O000OO00000OOOO00 .copy ()#line:105
            O00O0OO0OO0OO0000 =OO0OO00O0OOO0OOO0 ._drawings #line:106
            O00O00000O0OOOO00 =O00O0OO0OO0OO0000 [0 ]#line:107
            for OO000OOOOOO000OO0 in _O0OOO000OOOOO00O0 :#line:108
                OOOO0O0OO0O00OO00 =O00O00000O0OOOO00 [OO000OOOOOO000OO0 [0 ]]#line:109
                O00O000O00000O00O =O00O00000O0OOOO00 [OO000OOOOOO000OO0 [1 ]]#line:110
                cv2 .line (O000OO00000OOOO00 ,(OOOO0O0OO0O00OO00 [0 ],OOOO0O0OO0O00OO00 [1 ]),(O00O000O00000O00O [0 ],O00O000O00000O00O [1 ]),(0 ,255 ,0 ),3 )#line:111
            O000OO0000OO00000 =O00O0OO0OO0OO0000 [1 ]#line:112
            for OOO000O0OOOOOOOO0 in O000OO0000OO00000 :#line:113
                OO0OO0O00OO0O0OO0 =O000OO0000OO00000 [OOO000O0OOOOOOOO0 ]#line:114
                cv2 .circle (O000OO00000OOOO00 ,(OO0OO0O00OO0O0OO0 [0 ],OO0OO0O00OO0O0OO0 [1 ]),3 ,(0 ,0 ,255 ),2 )#line:115
        return O000OO00000OOOO00 #line:116
    def get_xy (O0000O000OOOO00O0 ,id ='all'):#line:118
        if isinstance (id ,str ):#line:119
            O0OOO000000OO0O0O =O0000O000OOOO00O0 ._landmarks #line:120
            id =id .lower ()#line:121
            if id =='all':#line:122
                return O0OOO000000OO0O0O #line:123
            elif O0OOO000000OO0O0O is None :#line:124
                return None #line:125
            elif id in O0OOO000000OO0O0O :#line:126
                return O0OOO000000OO0O0O [id ]#line:127
        return None #line:128
    def get_feature (O00O000OOO0OOOOO0 ,filter ='all'):#line:130
        OOO000OOO0O00OOO0 =O00O000OOO0OOOOO0 ._landmarks #line:131
        if OOO000OOO0O00OOO0 is not None :#line:132
            OO0OOO00O00OO000O =abs (OOO000OOO0O00OOO0 ['right shoulder'][0 ]-OOO000OOO0O00OOO0 ['left shoulder'][0 ])#line:133
            if OO0OOO00O00OO000O >0 :#line:134
                OO0O0OO00O0O0O00O =[]#line:135
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['left eye'])#line:136
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['right eye'])#line:137
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['left ear'])#line:138
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['right ear'])#line:139
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['nose'])#line:140
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['mouth'])#line:141
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['left shoulder'])#line:142
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['right shoulder'])#line:143
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['left elbow'])#line:144
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['right elbow'])#line:145
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['left wrist'])#line:146
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['right wrist'])#line:147
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['left hand'])#line:148
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['right hand'])#line:149
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['left hip'])#line:150
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['right hip'])#line:151
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['left knee'])#line:152
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['right knee'])#line:153
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['left ankle'])#line:154
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['right ankle'])#line:155
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['left foot'])#line:156
                OO0O0OO00O0O0O00O .append (OOO000OOO0O00OOO0 ['right foot'])#line:157
                OOO0O0O0O00O0000O =OOO000OOO0O00OOO0 ['neck']#line:159
                OO0O0OO00O0O0O00O =(OO0O0OO00O0O0O00O -OOO0O0O0O00O0000O )/OO0OOO00O00OO000O #line:160
                OO0O0OO00O0O0O00O =OO0O0OO00O0O0O00O .reshape (-1 )#line:161
                if isinstance (filter ,str ):#line:163
                    filter =filter .lower ()#line:164
                    if filter =='all':#line:165
                        return OO0O0OO00O0O0O00O #line:166
                    elif filter in _O000O0O0O0OO000O0 :#line:167
                        O00O0O0OO0OO0O0O0 =_O000O0O0O0OO000O0 [filter ]#line:168
                        return np .array ([OO0O0OO00O0O0O00O [OO000OO000O00000O ]for OO000OO000O00000O in O00O0O0OO0OO0O0O0 ])#line:169
                elif isinstance (filter ,(list ,tuple )):#line:170
                    O00O0O0OO0OO0O0O0 =[]#line:171
                    for O0O00OO000O000OOO in filter :#line:172
                        if O0O00OO000O000OOO in _O000O0O0O0OO000O0 :#line:173
                            O00O0O0OO0OO0O0O0 .extend (_O000O0O0O0OO000O0 [O0O00OO000O000OOO ])#line:174
                    return np .array ([OO0O0OO00O0O0O00O [OOO000OO00OO000O0 ]for OOO000OO00OO000O0 in O00O0O0OO0OO0O0O0 ])#line:175
        return None #line:176
    def _get_feature_label (O00O0O000O000O000 ,filter ='all'):#line:178
        if isinstance (filter ,str ):#line:179
            filter =filter .lower ()#line:180
            if filter =='all':#line:181
                return ['f'+str (OOO0OOOO0O0OOOOOO )for OOO0OOOO0O0OOOOOO in range (44 )]#line:182
            elif filter in _O000O0O0O0OO000O0 :#line:183
                OOOOO0O00O0000O00 =_O000O0O0O0OO000O0 [filter ]#line:184
                return ['f'+str (O00O0000O00O0O0O0 )for O00O0000O00O0O0O0 in OOOOO0O00O0000O00 ]#line:185
        elif isinstance (filter ,(list ,tuple )):#line:186
            OOOOO0O00O0000O00 =[]#line:187
            for OOO0O0O00OO0O0000 in filter :#line:188
                if OOO0O0O00OO0O0000 in _O000O0O0O0OO000O0 :#line:189
                    OOOOO0O00O0000O00 .extend (_O000O0O0O0OO000O0 [OOO0O0O00OO0O0000 ])#line:190
            return ['f'+str (O000000000OOO00O0 )for O000000000OOO00O0 in OOOOO0O00O0000O00 ]#line:191
    def record_feature (O0OOO0OO000000O00 ,OOO00O0OO0O000000 ,OOOO0OOOOO0O00000 ,filter ='all',interval_msec =100 ,frames =20 ,countdown =3 ):#line:193
        if countdown >0 :#line:194
            OOO00O0OO0O000000 .count_down (countdown )#line:195
        O000O000000O0O00O =0 #line:196
        OOO0OOOOOO0OO0OO0 =timer ()#line:197
        O00O00000O00000OO =','.join (O0OOO0OO000000O00 ._get_feature_label (filter ))#line:198
        OOO00OO0OOO0000OO =[]#line:199
        while True :#line:200
            if O000O000000O0O00O >=frames :break #line:201
            OOO0O0OO0OOOOO00O =OOO00O0OO0O000000 .read ()#line:202
            if O0OOO0OO000000O00 .detect (OOO0O0OO0OOOOO00O ):#line:203
                OOO0O0OO0OOOOO00O =O0OOO0OO000000O00 .draw_result (OOO0O0OO0OOOOO00O )#line:204
                if timer ()>OOO0OOOOOO0OO0OO0 :#line:205
                    OOO00OO0OOO0000OO .append (O0OOO0OO000000O00 .get_feature (filter ))#line:206
                    O000O000000O0O00O +=1 #line:207
                    print ('saved',O000O000000O0O00O )#line:208
                    OOO0OOOOOO0OO0OO0 +=interval_msec /1000.0 #line:209
                if OOO00O0OO0O000000 .check_key ()=='esc':#line:210
                    return #line:211
            OOO00O0OO0O000000 .show (OOO0O0OO0OOOOO00O )#line:212
        if OOOO0OOOOO0O00000 is not None :#line:213
            Util .realize_filepath (OOOO0OOOOO0O00000 )#line:214
            np .savetxt (OOOO0OOOOO0O00000 ,OOO00OO0OOO0000OO ,fmt ='%f',delimiter =',',header =O00O00000O00000OO ,comments ='')#line:215
    @staticmethod #line:217
    def distance (OO0OOOOO00000O0OO ,O0O00000OO000O0O0 ):#line:218
        return Util .distance (OO0OOOOO00000O0OO ,O0O00000OO000O0O0 )#line:219
    @staticmethod #line:221
    def degree (OO0O000OOO000OO00 ,O00OOOO0O00O0OOO0 ):#line:222
        return Util .degree (OO0O000OOO000OO00 ,O00OOOO0O00O0OOO0 )#line:223
    @staticmethod #line:225
    def radian (OOOO0OOOOOO00OO00 ,O00O0O00000OO0OOO ):#line:226
        return Util .radian (OOOO0OOOOOO00OO00 ,O00O0O00000OO0OOO )#line:227
