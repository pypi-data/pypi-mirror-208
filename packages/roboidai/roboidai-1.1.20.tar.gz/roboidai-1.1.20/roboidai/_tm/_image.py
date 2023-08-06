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

import numpy as np #line:19
import cv2 #line:20
np .set_printoptions (suppress =True )#line:22
class TmImage :#line:25
    def __init__ (OO0OO0O0000O0OOO0 ,square ='center'):#line:26
        OO0OO0O0000O0OOO0 ._loaded =False #line:27
        OO0OO0O0000O0OOO0 ._model =None #line:28
        OO0OO0O0000O0OOO0 ._data =np .ndarray (shape =(1 ,224 ,224 ,3 ),dtype =np .float32 )#line:29
        OO0OO0O0000O0OOO0 .set_square (square )#line:30
        OO0OO0O0000O0OOO0 ._clear ()#line:31
    def _clear (OOO0OO00O000O0OO0 ):#line:33
        OOO0OO00O000O0OO0 ._best_label =''#line:34
        OOO0OO00O000O0OO0 ._best_confidence =0 #line:35
        OOO0OO00O000O0OO0 ._labels =[]#line:36
        OOO0OO00O000O0OO0 ._confidences =[]#line:37
    def load_model (O0O00000O0OO00O00 ,O0O0OOO0OO0O00OOO ):#line:39
        import os #line:40
        import tensorflow as tf #line:41
        O0O00000O0OO00O00 ._loaded =False #line:42
        try :#line:43
            O0O0OO000OOOOO00O =os .path .join (O0O0OOO0OO0O00OOO ,'keras_model.h5')#line:44
            OOO0OO0OOOOOO000O =os .path .join (O0O0OOO0OO0O00OOO ,'labels.txt')#line:45
            O0O00000O0OO00O00 ._model =tf .keras .models .load_model (O0O0OO000OOOOO00O )#line:46
            OO00000OO00O0OO0O =np .genfromtxt (OOO0OO0OOOOOO000O ,encoding ='utf8',dtype =None )#line:47
            O0O00000O0OO00O00 ._labels =np .array ([OO0OO00O00OOO0O0O for _O0OOOOOOOOOOO00OO ,OO0OO00O00OOO0O0O in OO00000OO00O0OO0O ])#line:48
            O0O00000O0OO00O00 ._loaded =True #line:49
            return True #line:50
        except :#line:51
            return False #line:52
    def _crop_image (OO000OOO00000O000 ,O000OO0O0O0O00O0O ):#line:54
        OOOOO0O0O00000OOO =O000OO0O0O0O00O0O .shape [1 ]#line:55
        OOO0O0OOOO000OO00 =O000OO0O0O0O00O0O .shape [0 ]#line:56
        if OOO0O0OOOO000OO00 >OOOOO0O0O00000OOO :#line:57
            if OO000OOO00000O000 ._square =='left':#line:58
                O00O0O0OOOOO00OO0 =0 #line:59
            elif OO000OOO00000O000 ._square =='right':#line:60
                O00O0O0OOOOO00OO0 =OOO0O0OOOO000OO00 -OOOOO0O0O00000OOO #line:61
            else :#line:62
                O00O0O0OOOOO00OO0 =(OOO0O0OOOO000OO00 -OOOOO0O0O00000OOO )//2 #line:63
            O000OO0O0O0O00O0O =O000OO0O0O0O00O0O [O00O0O0OOOOO00OO0 :O00O0O0OOOOO00OO0 +OOOOO0O0O00000OOO ,:]#line:64
        else :#line:65
            if OO000OOO00000O000 ._square =='left':#line:66
                O00O0O0OOOOO00OO0 =0 #line:67
            elif OO000OOO00000O000 ._square =='right':#line:68
                O00O0O0OOOOO00OO0 =OOOOO0O0O00000OOO -OOO0O0OOOO000OO00 #line:69
            else :#line:70
                O00O0O0OOOOO00OO0 =(OOOOO0O0O00000OOO -OOO0O0OOOO000OO00 )//2 #line:71
            O000OO0O0O0O00O0O =O000OO0O0O0O00O0O [:,O00O0O0OOOOO00OO0 :O00O0O0OOOOO00OO0 +OOO0O0OOOO000OO00 ]#line:72
        return cv2 .resize (O000OO0O0O0O00O0O ,dsize =(224 ,224 ))#line:73
    def predict (OOOOOOO0OO00O0O0O ,O0O00O00OOOO00000 ,threshold =0.5 ):#line:75
        if O0O00O00OOOO00000 is None :#line:76
            OOOOOOO0OO00O0O0O ._clear ()#line:77
        elif OOOOOOO0OO00O0O0O ._loaded :#line:78
            O00OOO000000000O0 =OOOOOOO0OO00O0O0O ._crop_image (O0O00O00OOOO00000 )#line:79
            OOOOOOO0OO00O0O0O ._data [0 ]=(O00OOO000000000O0 .astype (np .float32 )/127.0 )-1 #line:80
            OOOO0O000OOO00000 =OOOOOOO0OO00O0O0O ._confidences =OOOOOOO0OO00O0O0O ._model .predict (OOOOOOO0OO00O0O0O ._data )[0 ]#line:81
            if OOOO0O000OOO00000 .size >0 :#line:82
                OO0OOO0O0OOOO0OO0 =OOOO0O000OOO00000 .argmax ()#line:83
                if OOOO0O000OOO00000 [OO0OOO0O0OOOO0OO0 ]<threshold :#line:84
                    OOOOOOO0OO00O0O0O ._best_label =''#line:85
                    OOOOOOO0OO00O0O0O ._best_confidence =0 #line:86
                else :#line:87
                    OOOOOOO0OO00O0O0O ._best_label =OOOOOOO0OO00O0O0O ._labels [OO0OOO0O0OOOO0OO0 ]#line:88
                    OOOOOOO0OO00O0O0O ._best_confidence =OOOO0O000OOO00000 [OO0OOO0O0OOOO0OO0 ]#line:89
                    return True #line:90
        return False #line:91
    def set_square (O0OOO0O0OOOO0O000 ,O000000OOO00O0OO0 ):#line:93
        if O000000OOO00O0OO0 is None :#line:94
            O0OOO0O0OOOO0O000 ._square ='center'#line:95
        elif isinstance (O000000OOO00O0OO0 ,str ):#line:96
            O0OOO0O0OOOO0O000 ._square =O000000OOO00O0OO0 .lower ()#line:97
    def draw_square (OO0000O00O000OOO0 ,OO0O000O0O00O0OOO ,color =(0 ,255 ,0 ),thickness =2 ,clone =False ):#line:99
        if OO0O000O0O00O0OOO is not None :#line:100
            if clone :#line:101
                OO0O000O0O00O0OOO =OO0O000O0O00O0OOO .copy ()#line:102
            OOOO000000000OOOO =OO0O000O0O00O0OOO .shape [1 ]#line:103
            O000000O0O00OO0O0 =OO0O000O0O00O0OOO .shape [0 ]#line:104
            if O000000O0O00OO0O0 >OOOO000000000OOOO :#line:105
                if OO0000O00O000OOO0 ._square =='left':#line:106
                    O0000O0OO000000OO =0 #line:107
                elif OO0000O00O000OOO0 ._square =='right':#line:108
                    O0000O0OO000000OO =O000000O0O00OO0O0 -OOOO000000000OOOO #line:109
                else :#line:110
                    O0000O0OO000000OO =(O000000O0O00OO0O0 -OOOO000000000OOOO )//2 #line:111
                cv2 .rectangle (OO0O000O0O00O0OOO ,(0 ,O0000O0OO000000OO ),(OOOO000000000OOOO ,O0000O0OO000000OO +OOOO000000000OOOO ),color ,thickness )#line:112
            else :#line:113
                if OO0000O00O000OOO0 ._square =='left':#line:114
                    O0000O0OO000000OO =0 #line:115
                elif OO0000O00O000OOO0 ._square =='right':#line:116
                    O0000O0OO000000OO =OOOO000000000OOOO -O000000O0O00OO0O0 #line:117
                else :#line:118
                    O0000O0OO000000OO =(OOOO000000000OOOO -O000000O0O00OO0O0 )//2 #line:119
                cv2 .rectangle (OO0O000O0O00O0OOO ,(O0000O0OO000000OO ,0 ),(O0000O0OO000000OO +O000000O0O00OO0O0 ,O000000O0O00OO0O0 ),color ,thickness )#line:120
        return OO0O000O0O00O0OOO #line:121
    def get_label (O0OO00O0O0OOO00O0 ):#line:123
        return O0OO00O0O0OOO00O0 ._best_label #line:124
    def get_conf (OOO000O0O00O0O000 ):#line:126
        return OOO000O0O00O0O000 ._best_confidence #line:127
    def get_all_labels (OO000OOOOO000O0O0 ):#line:129
        return OO000OOOOO000O0O0 ._labels #line:130
    def get_all_confs (OOOOO0O00OO000OO0 ):#line:132
        return OOOOO0O00OO000OO0 ._confidences #line:133
