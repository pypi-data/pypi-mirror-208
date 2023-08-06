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
class BodySegmentation :#line:24
    def __init__ (O0OOO0OO00000OO00 ):#line:25
        O0OOO0OO00000OO00 ._loaded =False #line:26
        O0OOO0OO00000OO00 ._condition =None #line:27
        O0OOO0OO00000OO00 ._bg_image =None #line:28
        O0OOO0OO00000OO00 ._bg_color =None #line:29
        O0OOO0OO00000OO00 ._bg_temp =None #line:30
    def load_model (OOO0O0O00O000O000 ,model =0 ):#line:32
        try :#line:33
            OOO0O0O00O000O000 ._segmentation =mp .solutions .selfie_segmentation .SelfieSegmentation (model_selection =model )#line:34
            OOO0O0O00O000O000 ._loaded =True #line:35
            return True #line:36
        except :#line:37
            return False #line:38
    def _fit_to (OOOO0OOOO0OO0OO00 ,O00000O00O0O00OO0 ,OO0OO000O0O0OO000 ,O0000000OO0OOOOOO ):#line:40
        if O00000O00O0O00OO0 is not None :#line:41
            OOO0OO00000OOO0O0 =O00000O00O0O00OO0 .shape [1 ]#line:42
            OO00O000O00000OOO =O00000O00O0O00OO0 .shape [0 ]#line:43
            if OOO0OO00000OOO0O0 ==OO0OO000O0O0OO000 and OO00O000O00000OOO ==O0000000OO0OOOOOO :#line:44
                return O00000O00O0O00OO0 #line:45
            OO000OOO00000OO00 =OOO0OO00000OOO0O0 /OO00O000O00000OOO #line:46
            OOO00000O0OOO0O0O =OO0OO000O0O0OO000 /O0000000OO0OOOOOO #line:47
            if OOO00000O0OOO0O0O >OO000OOO00000OO00 :#line:48
                OO00O000O00000OOO =int (OO0OO000O0O0OO000 *OO00O000O00000OOO /OOO0OO00000OOO0O0 )#line:49
                O00000O00O0O00OO0 =cv2 .resize (O00000O00O0O00OO0 ,(OO0OO000O0O0OO000 ,OO00O000O00000OOO ))#line:50
                O0OOOO0OO0O0O0OO0 =(OO00O000O00000OOO -O0000000OO0OOOOOO )//2 #line:51
                O00000O00O0O00OO0 =O00000O00O0O00OO0 [O0OOOO0OO0O0O0OO0 :O0OOOO0OO0O0O0OO0 +O0000000OO0OOOOOO ,:]#line:52
            else :#line:53
                OOO0OO00000OOO0O0 =int (O0000000OO0OOOOOO *OOO0OO00000OOO0O0 /OO00O000O00000OOO )#line:54
                O00000O00O0O00OO0 =cv2 .resize (O00000O00O0O00OO0 ,(OOO0OO00000OOO0O0 ,O0000000OO0OOOOOO ))#line:55
                O0OOOO0OO0O0O0OO0 =(OOO0OO00000OOO0O0 -OO0OO000O0O0OO000 )//2 #line:56
                O00000O00O0O00OO0 =O00000O00O0O00OO0 [:,O0OOOO0OO0O0O0OO0 :O0OOOO0OO0O0O0OO0 +OO0OO000O0O0OO000 ]#line:57
        return O00000O00O0O00OO0 #line:58
    def set_background (O00O0O00OO00O0OOO ,O0O0O0O00OOOO000O ,arg2 =None ,arg3 =None ):#line:60
        if isinstance (O0O0O0O00OOOO000O ,str ):#line:61
            O00O0000000OO0OO0 =cv2 .imread (O0O0O0O00OOOO000O )#line:62
            if O00O0000000OO0OO0 is None :#line:63
                try :#line:64
                    O00O0000000OO0OO0 =np .fromfile (O0O0O0O00OOOO000O ,np .uint8 )#line:65
                    O00O0O00OO00O0OOO ._bg_image =cv2 .imdecode (O00O0000000OO0OO0 ,cv2 .IMREAD_COLOR )#line:66
                except :#line:67
                    O00O0O00OO00O0OOO ._bg_image =None #line:68
            else :#line:69
                O00O0O00OO00O0OOO ._bg_image =O00O0000000OO0OO0 #line:70
            O00O0O00OO00O0OOO ._bg_color =None #line:71
        elif isinstance (O0O0O0O00OOOO000O ,(int ,float )):#line:72
            if isinstance (arg2 ,(int ,float ))and isinstance (arg3 ,(int ,float )):#line:73
                O00O0O00OO00O0OOO ._bg_image =None #line:74
                O00O0O00OO00O0OOO ._bg_color =(int (arg3 ),int (arg2 ),int (O0O0O0O00OOOO000O ))#line:75
        else :#line:76
            O00O0O00OO00O0OOO ._bg_image =O0O0O0O00OOOO000O #line:77
            O00O0O00OO00O0OOO ._bg_color =None #line:78
    def process (OOOO00OOOO0OOO0O0 ,O000OO0OOO0O0O000 ):#line:80
        if O000OO0OOO0O0O000 is not None and OOOO00OOOO0OOO0O0 ._loaded :#line:81
            O000OO0OOO0O0O000 =cv2 .cvtColor (O000OO0OOO0O0O000 ,cv2 .COLOR_BGR2RGB )#line:82
            O000OO0OOO0O0O000 .flags .writeable =False #line:83
            O0000OO0O00OO0OOO =OOOO00OOOO0OOO0O0 ._segmentation .process (O000OO0OOO0O0O000 )#line:84
            if O0000OO0O00OO0OOO and O0000OO0O00OO0OOO .segmentation_mask is not None :#line:85
                OOOO00OOOO0OOO0O0 ._condition =np .stack ((O0000OO0O00OO0OOO .segmentation_mask ,)*3 ,axis =-1 )>0.1 #line:86
                return True #line:87
        OOOO00OOOO0OOO0O0 ._condition =None #line:88
        return False #line:89
    def _get_background (OOO0O00O000OOO0O0 ,OOOOOOOO00OO0O0OO ,O0O00OO000OO0O0O0 ):#line:91
        if OOO0O00O000OOO0O0 ._bg_temp is None :#line:92
            OOO0O00O000OOO0O0 ._bg_temp =np .zeros (OOOOOOOO00OO0O0OO ,dtype =np .uint8 )#line:93
        elif OOO0O00O000OOO0O0 ._bg_temp .shape [0 ]!=OOOOOOOO00OO0O0OO [0 ]or OOO0O00O000OOO0O0 ._bg_temp .shape [1 ]!=OOOOOOOO00OO0O0OO [1 ]:#line:94
            OOO0O00O000OOO0O0 ._bg_temp =np .zeros (OOOOOOOO00OO0O0OO ,dtype =np .uint8 )#line:95
        if O0O00OO000OO0O0O0 is None :#line:96
            O0O00OO000OO0O0O0 =(0 ,0 ,0 )#line:97
        OOO0O00O000OOO0O0 ._bg_temp [:]=O0O00OO000OO0O0O0 #line:98
        return OOO0O00O000OOO0O0 ._bg_temp #line:99
    def draw_result (O0O00OO0O00OO0OOO ,O0O0OOO00O0O00000 ):#line:101
        if O0O0OOO00O0O00000 is not None and O0O00OO0O00OO0OOO ._condition is not None :#line:102
            if O0O00OO0O00OO0OOO ._bg_image is not None :#line:103
                O00OO00O00000OOO0 =O0O00OO0O00OO0OOO ._fit_to (O0O00OO0O00OO0OOO ._bg_image ,O0O0OOO00O0O00000 .shape [1 ],O0O0OOO00O0O00000 .shape [0 ])#line:104
            else :#line:105
                O00OO00O00000OOO0 =O0O00OO0O00OO0OOO ._get_background (O0O0OOO00O0O00000 .shape ,O0O00OO0O00OO0OOO ._bg_color )#line:106
            O0O0OOO00O0O00000 =np .where (O0O00OO0O00OO0OOO ._condition ,O0O0OOO00O0O00000 ,O00OO00O00000OOO0 )#line:107
        return O0O0OOO00O0O00000 #line:108
