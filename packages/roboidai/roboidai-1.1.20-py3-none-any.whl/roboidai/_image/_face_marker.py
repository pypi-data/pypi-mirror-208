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
import os #line:2
import numpy as np #line:3
from ._tool import DownloadTool #line:4
class FaceMarkerDetector :#line:7
    _DEFAULT_FOLDER ='c:/roboid/model'#line:8
    def __init__ (O0OO0O00000O0O00O ):#line:10
        from ._face_detector import FaceDetector #line:11
        O0OO0O00000O0O00O ._loaded =False #line:12
        O0OO0O00000O0O00O ._face_detector =FaceDetector ()#line:13
        O0OO0O00000O0O00O ._facemark =cv2 .face .createFacemarkLBF ()#line:14
        O0OO0O00000O0O00O ._clear ()#line:15
    def _clear (O0O000OO0O00O00OO ):#line:17
        O0O000OO0O00O00OO ._landmarks =np .array ([])#line:18
    def load_model (O0O0O0000O00OOO00 ,folder =None ):#line:20
        try :#line:21
            if folder is None :#line:22
                folder =FaceMarkerDetector ._DEFAULT_FOLDER #line:23
            O000OO0OOO0OOOOO0 =os .path .join (folder ,'face_marker.yaml')#line:24
            if os .path .exists (O000OO0OOO0OOOOO0 ):#line:25
                O0O0O0000O00OOO00 ._facemark .loadModel (O000OO0OOO0OOOOO0 )#line:26
                O0O0O0000O00OOO00 ._loaded =True #line:27
                return True #line:28
            elif isinstance (folder ,str ):#line:29
                if not folder .endswith ('.yaml'):#line:30
                    folder +='.yaml'#line:31
                O0O0O0000O00OOO00 ._facemark .loadModel (folder )#line:32
                O0O0O0000O00OOO00 ._loaded =True #line:33
                return True #line:34
            else :#line:35
                return False #line:36
        except :#line:37
            return False #line:38
    def download_model (O000OOOOOO0O00O00 ,folder =None ,overwrite =False ):#line:40
        print ('model downloading...')#line:41
        if folder is None :#line:42
            folder =FaceMarkerDetector ._DEFAULT_FOLDER #line:43
        if not os .path .isdir (folder ):#line:44
            os .makedirs (folder )#line:45
        DownloadTool .download_model (folder ,'face_marker.yaml',overwrite )#line:46
    def detect (O000OOOOOOOOO0O0O ,OO0000OOO0OOO000O ,gpu =False ):#line:48
        if OO0000OOO0OOO000O is None :#line:49
            O000OOOOOOOOO0O0O ._clear ()#line:50
        elif O000OOOOOOOOO0O0O ._loaded :#line:51
            if O000OOOOOOOOO0O0O ._face_detector .detect (OO0000OOO0OOO000O ,padding =20 ,gpu =gpu ):#line:52
                O0O000O0OO00OOO00 =O000OOOOOOOOO0O0O ._face_detector .get_box ()#line:53
                if O0O000O0OO00OOO00 is None :#line:54
                    O000OOOOOOOOO0O0O ._clear ()#line:55
                else :#line:56
                    _OO0OOO0O000000OO0 =np .array ([[O0O000O0OO00OOO00 [0 ],O0O000O0OO00OOO00 [1 ],O0O000O0OO00OOO00 [2 ]-O0O000O0OO00OOO00 [0 ],O0O000O0OO00OOO00 [3 ]-O0O000O0OO00OOO00 [1 ]]])#line:57
                    OOO000000OO00O000 ,OOO0O0O000OOO0O0O =O000OOOOOOOOO0O0O ._facemark .fit (OO0000OOO0OOO000O ,_OO0OOO0O000000OO0 )#line:58
                    if OOO000000OO00O000 :#line:59
                        O000OOOOOOOOO0O0O ._landmarks =OOO0O0O000OOO0O0O [0 ][0 ]#line:60
                        return True #line:61
                    else :#line:62
                        O000OOOOOOOOO0O0O ._clear ()#line:63
        return False #line:64
    def _draw_dots (O000O0OO0OOOOO0O0 ,O0OO00O00000OOOO0 ,color =(255 ,0 ,0 )):#line:66
        O00OO0O0OO00O0O0O =np .array ([O000O0OO0OOOOO0O0 ._landmarks ])#line:67
        cv2 .face .drawFacemarks (O0OO00O00000OOOO0 ,O00OO0O0OO00O0O0O ,color )#line:68
    def _draw_polylines (OO0O00000OOO000OO ,O00OOOO0O0O0OOO0O ,OOO0OO000000OOO0O ,O0OOO00O0O0O00OO0 ,O00OOO0OO0OO0O00O ,closed =False ,color =(0 ,0 ,255 ),thickness =2 ):#line:70
        O0OOOOO0OOOOOO000 =np .array ([OOO0OO000000OOO0O [OO000OO000OOO0OO0 ]for OO000OO000OOO0OO0 in range (O0OOO00O0O0O00OO0 ,O00OOO0OO0OO0O00O +1 )],np .int32 )#line:71
        cv2 .polylines (O00OOOO0O0O0OOO0O ,[O0OOOOO0OOOOOO000 ],closed ,color ,thickness )#line:73
    def _draw_lines (OO00O0OO0000OO000 ,O0O00000OOOO0O0O0 ,color =(0 ,0 ,255 ),thickness =2 ):#line:75
        OOOOOO0O00000000O =OO00O0OO0000OO000 ._landmarks #line:76
        OO00O0OO0000OO000 ._draw_polylines (O0O00000OOOO0O0O0 ,OOOOOO0O00000000O ,0 ,16 )#line:77
        OO00O0OO0000OO000 ._draw_polylines (O0O00000OOOO0O0O0 ,OOOOOO0O00000000O ,17 ,21 )#line:78
        OO00O0OO0000OO000 ._draw_polylines (O0O00000OOOO0O0O0 ,OOOOOO0O00000000O ,22 ,26 )#line:79
        OO00O0OO0000OO000 ._draw_polylines (O0O00000OOOO0O0O0 ,OOOOOO0O00000000O ,27 ,30 )#line:80
        OO00O0OO0000OO000 ._draw_polylines (O0O00000OOOO0O0O0 ,OOOOOO0O00000000O ,30 ,35 ,True )#line:81
        OO00O0OO0000OO000 ._draw_polylines (O0O00000OOOO0O0O0 ,OOOOOO0O00000000O ,36 ,41 ,True )#line:82
        OO00O0OO0000OO000 ._draw_polylines (O0O00000OOOO0O0O0 ,OOOOOO0O00000000O ,42 ,47 ,True )#line:83
        OO00O0OO0000OO000 ._draw_polylines (O0O00000OOOO0O0O0 ,OOOOOO0O00000000O ,48 ,59 ,True )#line:84
        OO00O0OO0000OO000 ._draw_polylines (O0O00000OOOO0O0O0 ,OOOOOO0O00000000O ,60 ,67 ,True )#line:85
    def draw_result (O0OOOOOOOO00OO00O ,O0OOOOO0OO00000O0 ,type ='dot',clone =False ):#line:87
        if O0OOOOO0OO00000O0 is not None and O0OOOOOOOO00OO00O ._landmarks .size >0 :#line:88
            if clone :#line:89
                O0OOOOO0OO00000O0 =O0OOOOO0OO00000O0 .copy ()#line:90
            if type =='dot':#line:91
                O0OOOOOOOO00OO00O ._draw_dots (O0OOOOO0OO00000O0 )#line:92
            elif type =='line':#line:93
                O0OOOOOOOO00OO00O ._draw_lines (O0OOOOO0OO00000O0 )#line:94
            else :#line:95
                O0OOOOOOOO00OO00O ._draw_lines (O0OOOOO0OO00000O0 )#line:96
                O0OOOOOOOO00OO00O ._draw_dots (O0OOOOO0OO00000O0 )#line:97
        return O0OOOOO0OO00000O0 #line:98
    def get_marker (O0OOO00O00OO000OO ,id ='all'):#line:100
        if isinstance (id ,(int ,float )):#line:101
            id =int (id )#line:102
            if id <1 or id >68 :return None #line:103
            return O0OOO00O00OO000OO ._landmarks [id -1 ]#line:104
        elif isinstance (id ,str ):#line:105
            id =id .lower ()#line:106
            if id =='all':#line:107
                return O0OOO00O00OO000OO ._landmarks #line:108
            elif id =='left eye':#line:109
                return (O0OOO00O00OO000OO ._landmarks [36 ]+O0OOO00O00OO000OO ._landmarks [39 ])/2 #line:110
            elif id =='right eye':#line:111
                return (O0OOO00O00OO000OO ._landmarks [42 ]+O0OOO00O00OO000OO ._landmarks [45 ])/2 #line:112
            elif id =='nose':#line:113
                return O0OOO00O00OO000OO ._landmarks [30 ]#line:114
            elif id =='lip left':#line:115
                return (O0OOO00O00OO000OO ._landmarks [48 ]+O0OOO00O00OO000OO ._landmarks [60 ])/2 #line:116
            elif id =='lip right':#line:117
                return (O0OOO00O00OO000OO ._landmarks [54 ]+O0OOO00O00OO000OO ._landmarks [64 ])/2 #line:118
            elif id =='lip top':#line:119
                return (O0OOO00O00OO000OO ._landmarks [51 ]+O0OOO00O00OO000OO ._landmarks [62 ])/2 #line:120
            elif id =='lip bottom':#line:121
                return (O0OOO00O00OO000OO ._landmarks [57 ]+O0OOO00O00OO000OO ._landmarks [66 ])/2 #line:122
            elif id =='lip':#line:123
                return (O0OOO00O00OO000OO ._landmarks [48 ]+O0OOO00O00OO000OO ._landmarks [51 ]+O0OOO00O00OO000OO ._landmarks [54 ]+O0OOO00O00OO000OO ._landmarks [57 ]+O0OOO00O00OO000OO ._landmarks [60 ]+O0OOO00O00OO000OO ._landmarks [62 ]+O0OOO00O00OO000OO ._landmarks [64 ]+O0OOO00O00OO000OO ._landmarks [66 ])/8 #line:124
        return O0OOO00O00OO000OO ._landmarks #line:125
