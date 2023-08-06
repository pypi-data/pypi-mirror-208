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

import cv2 #line:1
import numpy as np #line:2
from PIL import Image ,ImageDraw #line:3
from ._util import FontUtil #line:4
_O00OO000OO00000OO ={'en':{'angry':'angry','disgust':'disgust','fear':'fear','happy':'happy','sad':'sad','surprise':'surprise','neutral':'neutral'},'ko':{'angry':'화남','disgust':'혐오','fear':'두려움','happy':'행복','sad':'슬픔','surprise':'놀람','neutral':'무표정'}}#line:26
class FacialExpression :#line:29
    def __init__ (O0O0O0000O0O0OO0O ,lang ='en'):#line:30
        if lang in _O00OO000OO00000OO :#line:31
            O0O0O0000O0O0OO0O ._labels =_O00OO000OO00000OO [lang ]#line:32
        else :#line:33
            O0O0O0000O0O0OO0O ._labels =_O00OO000OO00000OO ['en']#line:34
        O0O0O0000O0O0OO0O ._model =None #line:35
        O0O0O0000O0O0OO0O ._clear ()#line:36
    def _clear (OO0O0OOOO000OO0O0 ):#line:38
        OO0O0OOOO000OO0O0 ._box =None #line:39
        OO0O0OOOO000OO0O0 ._label =''#line:40
        OO0O0OOOO000OO0O0 ._confidence =0 #line:41
    def load_model (OO0OOO0OO0000O00O ):#line:43
        if OO0OOO0OO0000O00O ._model is not None :return True #line:44
        try :#line:45
            from fer import FER #line:46
            OO0OOO0OO0000O00O ._model =FER (mtcnn =True )#line:47
            return True #line:48
        except :#line:49
            return False #line:50
    def detect (OOOO0OOOOO00OOOO0 ,OOO000OOOO0O0OOO0 ):#line:52
        if OOO000OOOO0O0OOO0 is not None and OOOO0OOOOO00OOOO0 ._model is not None :#line:53
            O0OOO0O0O00OOOOOO =OOOO0OOOOO00OOOO0 ._model .detect_emotions (OOO000OOOO0O0OOO0 )#line:54
            if O0OOO0O0O00OOOOOO and len (O0OOO0O0O00OOOOOO )>0 :#line:55
                O00OO00000OO0000O =[max (OOO0OOO0O0O000O0O ["emotions"],key =lambda O00OO0O00OO000OOO :OOO0OOO0O0O000O0O ["emotions"][O00OO0O00OO000OOO ])for OOO0OOO0O0O000O0O in O0OOO0O0O00OOOOOO ]#line:58
                O0O0OO0O00000000O =O00OO00000OO0000O [0 ]#line:59
                OOOO0OOOOO00OOOO0 ._confidence =O0OOO0O0O00OOOOOO [0 ]["emotions"][O0O0OO0O00000000O ]#line:60
                O00O000O00O0000OO =np .array (O0OOO0O0O00OOOOOO [0 ]['box'])#line:61
                O00O000O00O0000OO [2 ]+=O00O000O00O0000OO [0 ]#line:62
                O00O000O00O0000OO [3 ]+=O00O000O00O0000OO [1 ]#line:63
                OOOO0OOOOO00OOOO0 ._box =O00O000O00O0000OO #line:64
                OOOO0OOOOO00OOOO0 ._label =OOOO0OOOOO00OOOO0 ._labels [O0O0OO0O00000000O ]#line:65
                return True #line:66
        OOOO0OOOOO00OOOO0 ._clear ()#line:67
        return False #line:68
    def draw_result (OO00O000OO000O000 ,OOO0O0OOO000O000O ,color =(0 ,255 ,0 ),thickness =2 ,show_conf =False ,clone =False ):#line:70
        if OOO0O0OOO000O000O is not None :#line:71
            if clone :#line:72
                OOO0O0OOO000O000O =OOO0O0OOO000O000O .copy ()#line:73
            O0O0O00000O0OO0O0 =OO00O000OO000O000 ._box #line:74
            if O0O0O00000O0OO0O0 is not None :#line:75
                cv2 .rectangle (OOO0O0OOO000O000O ,(O0O0O00000O0OO0O0 [0 ],O0O0O00000O0OO0O0 [1 ]),(O0O0O00000O0OO0O0 [2 ],O0O0O00000O0OO0O0 [3 ]),color ,thickness )#line:76
                OOO00000OOOOO000O =OO00O000OO000O000 ._label #line:77
                if show_conf :#line:78
                    OOO00000OOOOO000O +=' '+str (format (OO00O000OO000O000 ._confidence *100 ,'.0f'))+'%'#line:79
                O0OO00OOO0OO0OO00 =Image .fromarray (OOO0O0OOO000O000O )#line:80
                OO0O0OO000O0O00OO =ImageDraw .Draw (O0OO00OOO0OO0OO00 )#line:81
                OO0O0OO000O0O00OO .text ((O0O0O00000O0OO0O0 [0 ],O0O0O00000O0OO0O0 [1 ]-20 ),OOO00000OOOOO000O ,font =FontUtil .get_font (),fill =color )#line:82
                return np .asarray (O0OO00OOO0OO0OO00 )#line:83
        return OOO0O0OOO000O000O #line:84
    def get_box (OOO0OO0000OO0OO0O ):#line:86
        return OOO0OO0000OO0OO0O ._box #line:87
    def get_label (O000O0O0OO00OOO00 ):#line:89
        return O000O0O0OO00OOO00 ._label #line:90
    def get_conf (O0OOOOO0000O00OO0 ):#line:92
        return O0OOOOO0000O00OO0 ._confidence #line:93
