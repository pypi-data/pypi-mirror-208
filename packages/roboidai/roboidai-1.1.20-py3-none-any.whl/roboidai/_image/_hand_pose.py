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
_O0O0O0O0000O0OOO0 =(0 ,1 ,2 ,5 ,9 ,13 ,17 )#line:26
_OOO0OO00OOO0O0000 =[[0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,40 ,41 ,42 ,43 ,44 ,45 ,46 ,47 ],[8 ,9 ,10 ,11 ,12 ,13 ,14 ,15 ,48 ,49 ,50 ,51 ,52 ,53 ,54 ,55 ],[16 ,17 ,18 ,19 ,20 ,21 ,22 ,23 ,56 ,57 ,58 ,59 ,60 ,61 ,62 ,63 ],[24 ,25 ,26 ,27 ,28 ,29 ,30 ,31 ,64 ,65 ,66 ,67 ,68 ,69 ,70 ,71 ],[32 ,33 ,34 ,35 ,36 ,37 ,38 ,39 ,72 ,73 ,74 ,75 ,76 ,77 ,78 ,79 ]]#line:33
class HandPose :#line:36
    def __init__ (OO00OOOO0O00O00O0 ):#line:37
        OO00OOOO0O00O00O0 ._loaded =False #line:38
        OO00OOOO0O00O00O0 ._both_hands =False #line:39
        OO00OOOO0O00O00O0 ._left_hand_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(0 ,255 ,0 ),thickness =3 )#line:40
        OO00OOOO0O00O00O0 ._right_hand_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(255 ,0 ,0 ),thickness =3 )#line:41
        OO00OOOO0O00O00O0 ._both_hands_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(255 ,255 ,0 ),thickness =3 )#line:42
        OO00OOOO0O00O00O0 ._landmark_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(0 ,0 ,255 ),circle_radius =3 )#line:43
        OO00OOOO0O00O00O0 ._clear ()#line:44
    def _clear (OO00OOOO0OO00OO0O ):#line:46
        OO00OOOO0OO00OO0O ._points ={'left':{},'right':{}}#line:50
        OO00OOOO0OO00OO0O ._boxes ={'left':{},'right':{}}#line:54
        OO00OOOO0OO00OO0O ._widths ={'left':{},'right':{}}#line:58
        OO00OOOO0OO00OO0O ._heights ={'left':{},'right':{}}#line:62
        OO00OOOO0OO00OO0O ._areas ={'left':{},'right':{}}#line:66
        OO00OOOO0OO00OO0O ._landmarks ={'left':None ,'right':None }#line:70
        OO00OOOO0OO00OO0O ._is_right =[False ,False ]#line:71
        OO00OOOO0OO00OO0O ._drawings =None #line:72
    def load_model (OO0OO000OO0O0O0OO ,both_hands =False ,threshold =0.5 ):#line:74
        OO0OO000OO0O0O0OO ._both_hands =both_hands #line:75
        try :#line:76
            O0OOOO00O000000O0 =2 if both_hands else 1 #line:77
            OO0OO000OO0O0O0OO ._hands =mp .solutions .hands .Hands (max_num_hands =O0OOOO00O000000O0 ,min_detection_confidence =threshold ,min_tracking_confidence =0.5 )#line:78
            OO0OO000OO0O0O0OO ._loaded =True #line:79
            return True #line:80
        except :#line:81
            return False #line:82
    def _calc_xyz (OOOOO000O0OO00O0O ,O0OOO0OO00000O00O ,O000OOO00OO0000OO ,O00OOO00000OOOO0O ,indices =None ):#line:84
        if indices is None :#line:85
            OOOOO000O0OO00O0O ._points [O0OOO0OO00000O00O ][O000OOO00OO0000OO ]=np .around (np .mean (O00OOO00000OOOO0O ,axis =0 )).astype (np .int32 )#line:86
        else :#line:87
            OOOOO000O0OO00O0O ._points [O0OOO0OO00000O00O ][O000OOO00OO0000OO ]=np .around (np .mean ([O00OOO00000OOOO0O [OO0OOOO00O000O0O0 ]for OO0OOOO00O000O0O0 in indices ],axis =0 )).astype (np .int32 )#line:88
    def _calc_box (OOOOOO0O0OOOO0O0O ,OO000OOO0O0OOOOO0 ,O000O0OOOOO00O0O0 ,OOO0O000OO00OOO0O ,indices =None ):#line:90
        if indices is None :#line:91
            OO000O00O0OOOO0OO =np .min (OOO0O000OO00OOO0O ,axis =0 )#line:92
            OO0O00O0OOOOO0000 =np .max (OOO0O000OO00OOO0O ,axis =0 )#line:93
        else :#line:94
            O0O0O0O00O00OO00O =[OOO0O000OO00OOO0O [O0000OO00O0O0O00O ]for O0000OO00O0O0O00O in indices ]#line:95
            OO000O00O0OOOO0OO =np .min (O0O0O0O00O00OO00O ,axis =0 )#line:96
            OO0O00O0OOOOO0000 =np .max (O0O0O0O00O00OO00O ,axis =0 )#line:97
        OOOOOO0O0OOOO0O0O ._boxes [OO000OOO0O0OOOOO0 ][O000O0OOOOO00O0O0 ]=[OO000O00O0OOOO0OO [0 ],OO000O00O0OOOO0OO [1 ],OO0O00O0OOOOO0000 [0 ],OO0O00O0OOOOO0000 [1 ]]#line:98
        O00O00O00OO00OOOO =abs (OO0O00O0OOOOO0000 [0 ]-OO000O00O0OOOO0OO [0 ])#line:99
        O0O00OO000O0OO000 =abs (OO0O00O0OOOOO0000 [1 ]-OO000O00O0OOOO0OO [1 ])#line:100
        OOOOOO0O0OOOO0O0O ._widths [OO000OOO0O0OOOOO0 ][O000O0OOOOO00O0O0 ]=O00O00O00OO00OOOO #line:101
        OOOOOO0O0OOOO0O0O ._heights [OO000OOO0O0OOOOO0 ][O000O0OOOOO00O0O0 ]=O0O00OO000O0OO000 #line:102
        OOOOOO0O0OOOO0O0O ._areas [OO000OOO0O0OOOOO0 ][O000O0OOOOO00O0O0 ]=O00O00O00OO00OOOO *O0O00OO000O0OO000 #line:103
    def _calc_landmark (O0O0OOOO00OOO0OO0 ,OO0OOOOO00O000OOO ,O000O0OOOOO0OO0O0 ,OOO0OO00OO00OO0OO ):#line:105
        O00O00O00000O00O0 =[OOO0000O0O00O00O0 .x for OOO0000O0O00O00O0 in OO0OOOOO00O000OOO .landmark ]#line:106
        O0000O0000OOO00OO =[O0OOO00OOOO0000O0 .y for O0OOO00OOOO0000O0 in OO0OOOOO00O000OOO .landmark ]#line:107
        OO000OOOOO0O00O0O =[O0000O000O0O00OOO .z for O0000O000O0O00OOO in OO0OOOOO00O000OOO .landmark ]#line:108
        OO00O0000OOOOO00O =np .transpose (np .stack ((O00O00O00000O00O0 ,O0000O0000OOO00OO ,OO000OOOOO0O00O0O )))*(O000O0OOOOO0OO0O0 ,OOO0OO00OO00OO0OO ,O000O0OOOOO0OO0O0 )#line:109
        return OO00O0000OOOOO00O .astype (np .int32 )#line:110
    def _fill_data (O00000O000OO00O00 ,OO00OOO0O0OOOOO00 ,O0O0000O0O00OOO00 ):#line:112
        O00000O000OO00O00 ._landmarks [OO00OOO0O0OOOOO00 ]=O0O0000O0O00OOO00 #line:113
        O00000O000OO00O00 ._calc_box (OO00OOO0O0OOOOO00 ,'hand',O0O0000O0O00OOO00 )#line:114
        O00000O000OO00O00 ._calc_box (OO00OOO0O0OOOOO00 ,'palm',O0O0000O0O00OOO00 ,_O0O0O0O0000O0OOO0 )#line:115
        O00000O000OO00O00 ._calc_xyz (OO00OOO0O0OOOOO00 ,'hand',O0O0000O0O00OOO00 )#line:116
        O00000O000OO00O00 ._calc_xyz (OO00OOO0O0OOOOO00 ,'palm',O0O0000O0O00OOO00 ,_O0O0O0O0000O0OOO0 )#line:117
    def detect (O0O0OOO0O00OO00OO ,OOOOOOO0O000O000O ):#line:119
        if OOOOOOO0O000O000O is not None and O0O0OOO0O00OO00OO ._loaded :#line:120
            OOOOOOO0O000O000O =cv2 .cvtColor (OOOOOOO0O000O000O ,cv2 .COLOR_BGR2RGB )#line:121
            OOOOOOO0O000O000O .flags .writeable =False #line:122
            O00O00OOO0OO0OOOO =O0O0OOO0O00OO00OO ._hands .process (OOOOOOO0O000O000O )#line:123
            if O00O00OOO0OO0OOOO and O00O00OOO0OO0OOOO .multi_hand_landmarks and len (O00O00OOO0OO0OOOO .multi_hand_landmarks )>0 and O00O00OOO0OO0OOOO .multi_handedness and len (O00O00OOO0OO0OOOO .multi_handedness )>0 :#line:124
                OO00OO0O0O0O0O0OO =OOOOOOO0O000O000O .shape [1 ]#line:125
                O0O000O00OO0000O0 =OOOOOOO0O000O000O .shape [0 ]#line:126
                if O0O0OOO0O00OO00OO ._both_hands :#line:127
                    OO0O0O0O0OOOOO0OO =True #line:128
                    OO0OO0OO000OO0O0O =True #line:129
                    OOOOOOOOO000O0O00 =O00O00OOO0OO0OOOO .multi_hand_landmarks [0 ]#line:130
                    if len (OOOOOOOOO000O0O00 .landmark )==21 :#line:131
                        O000OO0OO0O0O0O00 =O0O0OOO0O00OO00OO ._calc_landmark (OOOOOOOOO000O0O00 ,OO00OO0O0O0O0O0OO ,O0O000O00OO0000O0 )#line:132
                        O000O00OO0OO0OO00 =O00O00OOO0OO0OOOO .multi_handedness [0 ].classification .pop ()#line:133
                        if O000O00OO0OO0OO00 and O000O00OO0OO0OO00 .label =='Left':#line:134
                            O0O0OOO0O00OO00OO ._is_right [0 ]=False #line:135
                            O0O0OOO0O00OO00OO ._fill_data ('left',O000OO0OO0O0O0O00 )#line:136
                        else :#line:137
                            O0O0OOO0O00OO00OO ._is_right [0 ]=True #line:138
                            O0O0OOO0O00OO00OO ._fill_data ('right',O000OO0OO0O0O0O00 )#line:139
                    else :#line:140
                        OO0O0O0O0OOOOO0OO =False #line:141
                    if len (O00O00OOO0OO0OOOO .multi_hand_landmarks )>1 and len (O00O00OOO0OO0OOOO .multi_handedness )>1 :#line:142
                        O0O0OO00OO00O00OO =O00O00OOO0OO0OOOO .multi_hand_landmarks [1 ]#line:143
                        if len (O0O0OO00OO00O00OO .landmark )==21 :#line:144
                            O000OO0OO0O0O0O00 =O0O0OOO0O00OO00OO ._calc_landmark (O0O0OO00OO00O00OO ,OO00OO0O0O0O0O0OO ,O0O000O00OO0000O0 )#line:145
                            O000O00OO0OO0OO00 =O00O00OOO0OO0OOOO .multi_handedness [1 ].classification .pop ()#line:146
                            if O000O00OO0OO0OO00 and O000O00OO0OO0OO00 .label =='Left':#line:147
                                O0O0OOO0O00OO00OO ._is_right [1 ]=False #line:148
                                O0O0OOO0O00OO00OO ._fill_data ('left',O000OO0OO0O0O0O00 )#line:149
                            else :#line:150
                                O0O0OOO0O00OO00OO ._is_right [1 ]=True #line:151
                                O0O0OOO0O00OO00OO ._fill_data ('right',O000OO0OO0O0O0O00 )#line:152
                        else :#line:153
                            OO0OO0OO000OO0O0O =False #line:154
                    if OO0O0O0O0OOOOO0OO and OO0OO0OO000OO0O0O :#line:155
                        O0O0OOO0O00OO00OO ._drawings =O00O00OOO0OO0OOOO #line:156
                        return True #line:157
                else :#line:158
                    OO0000OO0O00O0O00 =O00O00OOO0OO0OOOO .multi_hand_landmarks [0 ]#line:159
                    if len (OO0000OO0O00O0O00 .landmark )==21 :#line:160
                        O000OO0OO0O0O0O00 =O0O0OOO0O00OO00OO ._calc_landmark (OO0000OO0O00O0O00 ,OO00OO0O0O0O0O0OO ,O0O000O00OO0000O0 )#line:161
                        O0O0OOO0O00OO00OO ._fill_data ('left',O000OO0OO0O0O0O00 )#line:162
                        O0O0OOO0O00OO00OO ._fill_data ('right',O000OO0OO0O0O0O00 )#line:163
                        O0O0OOO0O00OO00OO ._drawings =O00O00OOO0OO0OOOO #line:164
                        return True #line:165
        O0O0OOO0O00OO00OO ._clear ()#line:166
        return False #line:167
    def draw_result (O000O00OOO000O00O ,OOOO000OO0OO00O00 ,clone =False ):#line:169
        O00000O0O0O00OOO0 =O000O00OOO000O00O ._drawings #line:170
        if OOOO000OO0OO00O00 is not None and O00000O0O0O00OOO0 is not None and O00000O0O0O00OOO0 .multi_hand_landmarks and len (O00000O0O0O00OOO0 .multi_hand_landmarks )>0 :#line:171
            if clone :#line:172
                OOOO000OO0OO00O00 =OOOO000OO0OO00O00 .copy ()#line:173
            if O000O00OOO000O00O ._both_hands :#line:174
                O0O000000OO0O00O0 =O00000O0O0O00OOO0 .multi_hand_landmarks [0 ]#line:175
                O000OOO00OOOOO000 =O000O00OOO000O00O ._right_hand_drawing_spec if O000O00OOO000O00O ._is_right [0 ]else O000O00OOO000O00O ._left_hand_drawing_spec #line:176
                mp .solutions .drawing_utils .draw_landmarks (OOOO000OO0OO00O00 ,O0O000000OO0O00O0 ,mp .solutions .hands .HAND_CONNECTIONS ,O000O00OOO000O00O ._landmark_drawing_spec ,O000OOO00OOOOO000 )#line:177
                if len (O00000O0O0O00OOO0 .multi_hand_landmarks )>1 :#line:178
                    O0O000000OO0O00O0 =O00000O0O0O00OOO0 .multi_hand_landmarks [1 ]#line:179
                    O000OOO00OOOOO000 =O000O00OOO000O00O ._right_hand_drawing_spec if O000O00OOO000O00O ._is_right [1 ]else O000O00OOO000O00O ._left_hand_drawing_spec #line:180
                    mp .solutions .drawing_utils .draw_landmarks (OOOO000OO0OO00O00 ,O0O000000OO0O00O0 ,mp .solutions .hands .HAND_CONNECTIONS ,O000O00OOO000O00O ._landmark_drawing_spec ,O000OOO00OOOOO000 )#line:181
            else :#line:182
                mp .solutions .drawing_utils .draw_landmarks (OOOO000OO0OO00O00 ,O00000O0O0O00OOO0 .multi_hand_landmarks [0 ],mp .solutions .hands .HAND_CONNECTIONS ,O000O00OOO000O00O ._landmark_drawing_spec ,O000O00OOO000O00O ._both_hands_drawing_spec )#line:183
        return OOOO000OO0OO00O00 #line:184
    def get_xy (O0O00O0O0O0O0O000 ,OO00000OO0OO0OOO0 ,id ='all',index =0 ):#line:186
        O0OOO0000000O0000 =O0O00O0O0O0O0O000 .get_xyz (OO00000OO0OO0OOO0 ,id ,index )#line:187
        if O0OOO0000000O0000 is None :return None #line:188
        if O0OOO0000000O0000 .ndim ==1 :#line:189
            return O0OOO0000000O0000 [:2 ]#line:190
        elif O0OOO0000000O0000 .ndim ==2 :#line:191
            return O0OOO0000000O0000 [:,:2 ]#line:192
        return None #line:193
    def get_xyz (OOOO00O0O0OOOO000 ,OO0O000O00000OOOO ,id ='all',index =0 ):#line:195
        if isinstance (id ,(int ,float )):#line:196
            if OOOO00O0O0OOOO000 ._landmarks [OO0O000O00000OOOO ]is None :return None #line:197
            id =int (id )#line:198
            if id ==0 :return OOOO00O0O0OOOO000 ._landmarks [OO0O000O00000OOOO ][0 ]#line:199
            id =(id -1 )*4 +(3 -index )+1 #line:200
            if id <0 or id >20 :return None #line:201
            return OOOO00O0O0OOOO000 ._landmarks [OO0O000O00000OOOO ][id ]#line:202
        elif isinstance (id ,str ):#line:203
            id =id .lower ()#line:204
            if id =='all':#line:205
                return OOOO00O0O0OOOO000 ._landmarks [OO0O000O00000OOOO ]#line:206
            elif id in OOOO00O0O0OOOO000 ._points [OO0O000O00000OOOO ]:#line:207
                return OOOO00O0O0OOOO000 ._points [OO0O000O00000OOOO ][id ]#line:208
        return None #line:209
    def get_box (OO00OO0O0OO0000OO ,O0OOOOO0OOO0OOO00 ,id ='all'):#line:211
        if isinstance (id ,str ):#line:212
            id =id .lower ()#line:213
            if id =='all':#line:214
                return OO00OO0O0OO0000OO ._boxes [O0OOOOO0OOO0OOO00 ]#line:215
            elif id in OO00OO0O0OO0000OO ._boxes [O0OOOOO0OOO0OOO00 ]:#line:216
                return OO00OO0O0OO0000OO ._boxes [O0OOOOO0OOO0OOO00 ][id ]#line:217
        return None #line:218
    def get_width (O000O000O00OOO00O ,O0O0O00O00O0OO00O ,id ='all'):#line:220
        if isinstance (id ,str ):#line:221
            id =id .lower ()#line:222
            if id =='all':#line:223
                return O000O000O00OOO00O ._widths [O0O0O00O00O0OO00O ]#line:224
            elif id in O000O000O00OOO00O ._widths [O0O0O00O00O0OO00O ]:#line:225
                return O000O000O00OOO00O ._widths [O0O0O00O00O0OO00O ][id ]#line:226
        return 0 #line:227
    def get_height (OO000OOOO000O0O00 ,O0OO00OO0OOOOO0O0 ,id ='all'):#line:229
        if isinstance (id ,str ):#line:230
            id =id .lower ()#line:231
            if id =='all':#line:232
                return OO000OOOO000O0O00 ._heights [O0OO00OO0OOOOO0O0 ]#line:233
            elif id in OO000OOOO000O0O00 ._heights [O0OO00OO0OOOOO0O0 ]:#line:234
                return OO000OOOO000O0O00 ._heights [O0OO00OO0OOOOO0O0 ][id ]#line:235
        return 0 #line:236
    def get_area (OOO0O0OOOOOOOOOO0 ,O0OO00O000O00O0O0 ,id ='all'):#line:238
        if isinstance (id ,str ):#line:239
            id =id .lower ()#line:240
            if id =='all':#line:241
                return OOO0O0OOOOOOOOOO0 ._areas [O0OO00O000O00O0O0 ]#line:242
            elif id in OOO0O0OOOOOOOOOO0 ._areas [O0OO00O000O00O0O0 ]:#line:243
                return OOO0O0OOOOOOOOOO0 ._areas [O0OO00O000O00O0O0 ][id ]#line:244
        return 0 #line:245
    def get_feature (OOOOOOOO0O0O000OO ,filter ='all'):#line:247
        OO00O00OOOOO0O000 =OOOOOOOO0O0O000OO .get_width ('left','palm')#line:248
        O0O0O0O0O0O0O0OOO =OOOOOOOO0O0O000OO .get_height ('left','palm')#line:249
        O0OO0000O0000O000 =[OO00O00OOOOO0O000 ,O0O0O0O0O0O0O0OOO ]#line:250
        if OO00O00OOOOO0O000 >0 and O0O0O0O0O0O0O0OOO >0 :#line:251
            OO0O0O0OO0O000O00 =OOOOOOOO0O0O000OO ._landmarks ['left']#line:252
            OOOO0OOOO0OOOO0OO =OOOOOOOO0O0O000OO ._landmarks ['right']#line:253
            if OO0O0O0OO0O000O00 is not None and OOOO0OOOO0OOOO0OO is not None :#line:254
                O000O0OOOO0OO00O0 =OO0O0O0OO0O000O00 [0 ,:2 ]#line:255
                OO0O0O0OO0O000O00 =(OO0O0O0OO0O000O00 [1 :,:2 ]-O000O0OOOO0OO00O0 )/O0OO0000O0000O000 #line:256
                O000O0OOOO0OO00O0 =OOOO0OOOO0OOOO0OO [0 ,:2 ]#line:257
                OOOO0OOOO0OOOO0OO =(OOOO0OOOO0OOOO0OO [1 :,:2 ]-O000O0OOOO0OO00O0 )/O0OO0000O0000O000 #line:258
                OO00OOOO000OOO00O =np .concatenate ((OO0O0O0OO0O000O00 .reshape (-1 ),OOOO0OOOO0OOOO0OO .reshape (-1 )),axis =None )#line:259
                if isinstance (filter ,str ):#line:260
                    filter =filter .lower ()#line:261
                    if filter =='all':#line:262
                        return OO00OOOO000OOO00O #line:263
                elif isinstance (filter ,(int ,float )):#line:264
                    filter =int (filter )#line:265
                    if filter >0 and filter <6 :#line:266
                        OO0OO00OOO0O00O00 =_OOO0OO00OOO0O0000 [filter -1 ]#line:267
                        return np .array ([OO00OOOO000OOO00O [OOOO00OOOO0OO0OO0 ]for OOOO00OOOO0OO0OO0 in OO0OO00OOO0O00O00 ])#line:268
                elif isinstance (filter ,(list ,tuple )):#line:269
                    OO0OO00OOO0O00O00 =[]#line:270
                    for OOO0O000OOOO00OO0 in filter :#line:271
                        if isinstance (OOO0O000OOOO00OO0 ,(int ,float )):#line:272
                            OOO0O000OOOO00OO0 =int (OOO0O000OOOO00OO0 )#line:273
                            if OOO0O000OOOO00OO0 >0 and OOO0O000OOOO00OO0 <6 :#line:274
                                OO0OO00OOO0O00O00 .extend (_OOO0OO00OOO0O0000 [OOO0O000OOOO00OO0 -1 ])#line:275
                    return np .array ([OO00OOOO000OOO00O [O000OOO00OO0O0O0O ]for O000OOO00OO0O0O0O in OO0OO00OOO0O00O00 ])#line:276
        return None #line:277
    def _get_feature_label (O00OO0000O0O0O000 ,filter ='all'):#line:279
        if isinstance (filter ,str ):#line:280
            filter =filter .lower ()#line:281
            if filter =='all':#line:282
                return ['f'+str (O0O00O0OOO0000O0O )for O0O00O0OOO0000O0O in range (80 )]#line:283
        elif isinstance (filter ,(int ,float )):#line:284
            filter =int (filter )#line:285
            if filter >0 and filter <6 :#line:286
                O0O0OO00OOOO0OO0O =_OOO0OO00OOO0O0000 [filter -1 ]#line:287
                return ['f'+str (OO0OOO0O000OO0000 )for OO0OOO0O000OO0000 in O0O0OO00OOOO0OO0O ]#line:288
        elif isinstance (filter ,(list ,tuple )):#line:289
            O0O0OO00OOOO0OO0O =[]#line:290
            for O0O00000OO0OOOO0O in filter :#line:291
                if isinstance (O0O00000OO0OOOO0O ,(int ,float )):#line:292
                    O0O00000OO0OOOO0O =int (O0O00000OO0OOOO0O )#line:293
                    if O0O00000OO0OOOO0O >0 and O0O00000OO0OOOO0O <6 :#line:294
                        O0O0OO00OOOO0OO0O .extend (_OOO0OO00OOO0O0000 [O0O00000OO0OOOO0O -1 ])#line:295
            return ['f'+str (OOO0OO0000O00OOO0 )for OOO0OO0000O00OOO0 in O0O0OO00OOOO0OO0O ]#line:296
    def record_feature (OO00O0O0000OO00O0 ,OO0O0OO0OO00O00OO ,OOOO0O00OO0OO0O0O ,filter ='all',interval_msec =100 ,frames =20 ,countdown =3 ):#line:298
        if countdown >0 :#line:299
            OO0O0OO0OO00O00OO .count_down (countdown )#line:300
        OOO00000000OO0000 =0 #line:301
        OO00OOOO0OO00000O =timer ()#line:302
        OO00OO00O0O0OOOO0 =','.join (OO00O0O0000OO00O0 ._get_feature_label (filter ))#line:303
        O000OO00000O00OO0 =[]#line:304
        while True :#line:305
            if OOO00000000OO0000 >=frames :break #line:306
            O0OO0OOOO00O0OO00 =OO0O0OO0OO00O00OO .read ()#line:307
            if OO00O0O0000OO00O0 .detect (O0OO0OOOO00O0OO00 ):#line:308
                O0OO0OOOO00O0OO00 =OO00O0O0000OO00O0 .draw_result (O0OO0OOOO00O0OO00 )#line:309
                if timer ()>OO00OOOO0OO00000O :#line:310
                    O000OO00000O00OO0 .append (OO00O0O0000OO00O0 .get_feature (filter ))#line:311
                    OOO00000000OO0000 +=1 #line:312
                    print ('saved',OOO00000000OO0000 )#line:313
                    OO00OOOO0OO00000O +=interval_msec /1000.0 #line:314
                if OO0O0OO0OO00O00OO .check_key ()=='esc':#line:315
                    return #line:316
            OO0O0OO0OO00O00OO .show (O0OO0OOOO00O0OO00 )#line:317
        if OOOO0O00OO0OO0O0O is not None :#line:318
            Util .realize_filepath (OOOO0O00OO0OO0O0O )#line:319
            np .savetxt (OOOO0O00OO0OO0O0O ,O000OO00000O00OO0 ,fmt ='%f',delimiter =',',header =OO00OO00O0O0OOOO0 ,comments ='')#line:320
    @staticmethod #line:322
    def distance (OOOOO0000O00OO000 ,OOO0O0O000O000OOO ):#line:323
        return Util .distance (OOOOO0000O00OO000 ,OOO0O0O000O000OOO )#line:324
    @staticmethod #line:326
    def degree (OO0OOOOO00O000000 ,O00O00OO0OO0O0OO0 ):#line:327
        return Util .degree (OO0OOOOO00O000000 ,O00O00OO0OO0O0OO0 )#line:328
    @staticmethod #line:330
    def radian (OOO00OO0O0OOOO0OO ,O00O00OOOOOOOOOOO ):#line:331
        return Util .radian (OOO00OO0O0OOOO0OO ,O00O00OOOOOOOOOOO )#line:332
