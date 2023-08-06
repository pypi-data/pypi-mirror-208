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
from ._tool import DownloadTool #line:3
class AgeGenderDetector :#line:6
    _AGE_LABELS =['0-2','4-6','8-12','15-20','25-32','38-43','48-53','60-100']#line:7
    _GENDER_LABELS =['male','female']#line:8
    _MODEL_MEAN_VALUES =(78.4263377603 ,87.7689143744 ,114.895847746 )#line:9
    _DEFAULT_FOLDER ='c:/roboid/model'#line:10
    def __init__ (O00000O00O0O0OOOO ):#line:12
        from ._face_detector import FaceDetector #line:13
        O00000O00O0O0OOOO ._age_net =None #line:14
        O00000O00O0O0OOOO ._gender_net =None #line:15
        O00000O00O0O0OOOO ._face_detector =FaceDetector ()#line:16
        O00000O00O0O0OOOO ._clear ()#line:17
    def _clear (OO00O0O00OOO0OO00 ):#line:19
        OO00O0O00OOO0OO00 ._age_index =-1 #line:20
        OO00O0O00OOO0OO00 ._age_label =''#line:21
        OO00O0O00OOO0OO00 ._age_confidence =0 #line:22
        OO00O0O00OOO0OO00 ._gender_index =-1 #line:23
        OO00O0O00OOO0OO00 ._gender_label =''#line:24
        OO00O0O00OOO0OO00 ._gender_confidence =0 #line:25
    def load_age_model (O0O00000000O0O00O ,folder =None ):#line:27
        try :#line:28
            if folder is None :#line:29
                folder =AgeGenderDetector ._DEFAULT_FOLDER #line:30
            OOOO00O0000OOO00O =os .path .join (folder ,'age.caffemodel')#line:31
            if os .path .exists (OOOO00O0000OOO00O ):#line:32
                O0O00000000O0O00O ._age_net =cv2 .dnn .readNet (OOOO00O0000OOO00O ,os .path .join (folder ,'age.prototxt'))#line:33
            else :#line:34
                O0O00000000O0O00O ._age_net =cv2 .dnn .readNet (folder +'.caffemodel',folder +'.prototxt')#line:35
            return True #line:36
        except :#line:37
            return False #line:38
    def download_age_model (O000OO0OO00O0OOOO ,folder =None ,overwrite =False ):#line:40
        print ('model downloading...')#line:41
        if folder is None :#line:42
            folder =AgeGenderDetector ._DEFAULT_FOLDER #line:43
        if not os .path .isdir (folder ):#line:44
            os .makedirs (folder )#line:45
        DownloadTool .download_model (folder ,'age.caffemodel',overwrite )#line:46
        DownloadTool .download_model (folder ,'age.prototxt',overwrite )#line:47
    def load_gender_model (O0OOOO000OO00O0OO ,folder =None ):#line:49
        try :#line:50
            if folder is None :#line:51
                folder =AgeGenderDetector ._DEFAULT_FOLDER #line:52
            OOO000O00O0OO0OOO =os .path .join (folder ,'gender.caffemodel')#line:53
            if os .path .exists (OOO000O00O0OO0OOO ):#line:54
                O0OOOO000OO00O0OO ._gender_net =cv2 .dnn .readNet (OOO000O00O0OO0OOO ,os .path .join (folder ,'gender.prototxt'))#line:55
            else :#line:56
                O0OOOO000OO00O0OO ._gender_net =cv2 .dnn .readNet (folder +'.caffemodel',folder +'.prototxt')#line:57
            return True #line:58
        except :#line:59
            return False #line:60
    def download_gender_model (O0OOO00OO000OOOOO ,folder =None ,overwrite =False ):#line:62
        print ('model downloading...')#line:63
        if folder is None :#line:64
            folder =AgeGenderDetector ._DEFAULT_FOLDER #line:65
        if not os .path .isdir (folder ):#line:66
            os .makedirs (folder )#line:67
        DownloadTool .download_model (folder ,'gender.caffemodel',overwrite )#line:68
        DownloadTool .download_model (folder ,'gender.prototxt',overwrite )#line:69
    def detect (O0000OO00OOOO00O0 ,OOO0OOO0O00OO000O ,gpu =False ):#line:71
        if OOO0OOO0O00OO000O is None :#line:72
            O0000OO00OOOO00O0 ._clear ()#line:73
        elif O0000OO00OOOO00O0 ._age_net is not None or O0000OO00OOOO00O0 ._gender_net is not None :#line:74
            if O0000OO00OOOO00O0 ._face_detector .detect (OOO0OOO0O00OO000O ,padding =20 ):#line:75
                OOO0O0O00O0O00OOO =O0000OO00OOOO00O0 ._face_detector .crop (OOO0OOO0O00OO000O )#line:76
                if OOO0O0O00O0O00OOO is None :#line:77
                    O0000OO00OOOO00O0 ._clear ()#line:78
                else :#line:79
                    OOOOO00OO0OO00O0O =cv2 .dnn .blobFromImage (OOO0O0O00O0O00OOO ,1.0 ,(227 ,227 ),AgeGenderDetector ._MODEL_MEAN_VALUES ,swapRB =False )#line:80
                    if gpu :#line:81
                        O0000OO00OOOO00O0 ._age_net .setPreferableBackend (cv2 .dnn .DNN_BACKEND_CUDA )#line:82
                        O0000OO00OOOO00O0 ._age_net .setPreferableTarget (cv2 .dnn .DNN_TARGET_CUDA )#line:83
                    if O0000OO00OOOO00O0 ._age_net is not None :#line:84
                        O0000OO00OOOO00O0 ._age_net .setInput (OOOOO00OO0OO00O0O )#line:85
                        OOO0OO000O0O000O0 =O0000OO00OOOO00O0 ._age_net .forward ()[0 ]#line:86
                        OO0000O0OO00O0000 =OOO0OO000O0O000O0 .argmax ()#line:87
                        O0000OO00OOOO00O0 ._age_index =OO0000O0OO00O0000 #line:88
                        O0000OO00OOOO00O0 ._age_label =AgeGenderDetector ._AGE_LABELS [OO0000O0OO00O0000 ]#line:89
                        O0000OO00OOOO00O0 ._age_confidence =OOO0OO000O0O000O0 [OO0000O0OO00O0000 ]#line:90
                    if O0000OO00OOOO00O0 ._gender_net is not None :#line:91
                        O0000OO00OOOO00O0 ._gender_net .setInput (OOOOO00OO0OO00O0O )#line:92
                        OOO0OO000O0O000O0 =O0000OO00OOOO00O0 ._gender_net .forward ()[0 ]#line:93
                        OO0000O0OO00O0000 =OOO0OO000O0O000O0 .argmax ()#line:94
                        O0000OO00OOOO00O0 ._gender_index =OO0000O0OO00O0000 #line:95
                        O0000OO00OOOO00O0 ._gender_label =AgeGenderDetector ._GENDER_LABELS [OO0000O0OO00O0000 ]#line:96
                        O0000OO00OOOO00O0 ._gender_confidence =OOO0OO000O0O000O0 [OO0000O0OO00O0000 ]#line:97
                    return True #line:98
            else :#line:99
                O0000OO00OOOO00O0 ._clear ()#line:100
        return False #line:101
    def draw_result (OO000O0O0000O0000 ,OOOO0OOO0OOO0OOO0 ,color =(0 ,255 ,0 ),thickness =2 ,clone =False ):#line:103
        if OOOO0OOO0OOO0OOO0 is not None :#line:104
            if clone :#line:105
                OOOO0OOO0OOO0OOO0 =OOOO0OOO0OOO0OOO0 .copy ()#line:106
            O0O0OO0O0O000OOOO =OO000O0O0000O0000 ._face_detector .get_box ()#line:107
            if O0O0OO0O0O000OOOO is not None :#line:108
                cv2 .rectangle (OOOO0OOO0OOO0OOO0 ,(O0O0OO0O0O000OOOO [0 ],O0O0OO0O0O000OOOO [1 ]),(O0O0OO0O0O000OOOO [2 ],O0O0OO0O0O000OOOO [3 ]),color ,thickness )#line:109
                if OO000O0O0000O0000 ._age_net is not None and OO000O0O0000O0000 ._gender_net is not None :#line:110
                    OOO0O0OOOOO0000O0 ='{}, {}'.format (OO000O0O0000O0000 ._age_label ,OO000O0O0000O0000 ._gender_label )#line:111
                elif OO000O0O0000O0000 ._age_net is not None :#line:112
                    OOO0O0OOOOO0000O0 =OO000O0O0000O0000 ._age_label #line:113
                elif OO000O0O0000O0000 ._gender_net is not None :#line:114
                    OOO0O0OOOOO0000O0 =OO000O0O0000O0000 ._gender_label #line:115
                else :#line:116
                    OOO0O0OOOOO0000O0 =''#line:117
                cv2 .putText (OOOO0OOO0OOO0OOO0 ,OOO0O0OOOOO0000O0 ,(O0O0OO0O0O000OOOO [0 ],O0O0OO0O0O000OOOO [1 ]-10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,color ,thickness )#line:118
        return OOOO0OOO0OOO0OOO0 #line:119
    def get_age_index (OOO0O0O0O00O0O0O0 ):#line:121
        return OOO0O0O0O00O0O0O0 ._age_index #line:122
    def get_age_label (O0O000O0OO0000O0O ):#line:124
        return O0O000O0OO0000O0O ._age_label #line:125
    def get_age_conf (OO00OO00OO0OOO000 ):#line:127
        return OO00OO00OO0OOO000 ._age_confidence #line:128
    def get_gender_index (OOO0OO0OO0OO00OO0 ):#line:130
        return OOO0OO0OO0OO00OO0 ._gender_index #line:131
    def get_gender_label (OO0OOOO0OOO000OO0 ):#line:133
        return OO0OOOO0OOO000OO0 ._gender_label #line:134
    def get_gender_conf (OO0000OO00000OOOO ):#line:136
        return OO0000OO00000OOOO ._gender_confidence #line:137
