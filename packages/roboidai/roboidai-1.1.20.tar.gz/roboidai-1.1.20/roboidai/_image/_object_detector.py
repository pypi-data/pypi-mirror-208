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

import cv2 #line:2
import os #line:3
import numpy as np #line:4
from PIL import Image ,ImageDraw #line:8
from ._tool import DownloadTool #line:9
from ._util import FontUtil #line:10
initialize =True #line:12
net =None #line:13
classes =None #line:15
COLORS =np .random .uniform (0 ,255 ,size =(80 ,3 ))#line:16
_O000OOO00OO0OOO0O ={'en':['person','bicycle','car','motorcycle','airplane','bus','train','truck','boat','traffic light','fire hydrant','stop sign','parking meter','bench','bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack','umbrella','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket','bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple','sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair','couch','potted plant','bed','dining table','toilet','tv','laptop','mouse','remote','keyboard','cell phone','microwave','oven','toaster','sink','refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush'],'ko':['사람','자전거','자동차','오토바이','비행기','버스','기차','트럭','배','신호등','소화전','정지 신호','주차 미터기','벤치','새','고양이','개','말','양','소','코끼리','곰','얼룩말','기린','배낭','우산','핸드백','넥타이','여행 가방','원반','스키','스노보드','공','연','야구 방망이','야구 글러브','스케이트보드','서프보드','테니스 채','병','포도주 잔','컵','포크','칼','숟가락','그릇','바나나','사과','샌드위치','오렌지','브로콜리','당근','핫도그','피자','도넛','케이크','의자','소파','화분','침대','식탁','변기','텔레비전','노트북','마우스','리모컨','키보드','휴대 전화','전자레인지','오븐','토스터','싱크대','냉장고','책','시계','꽃병','가위','곰 인형','헤어드라이어','칫솔']}#line:38
def populate_class_labels (OOOO00OOOO0O00000 ):#line:40
    if OOOO00OOOO0O00000 in _O000OOO00OO0OOO0O :#line:52
        OO000O000O0O0OOO0 =_O000OOO00OO0OOO0O [OOOO00OOOO0O00000 ]#line:53
    else :#line:54
        OO000O000O0O0OOO0 =_O000OOO00OO0OOO0O ['en']#line:55
    return OO000O000O0O0OOO0 #line:56
def get_output_layers (O0O0000000O000OO0 ):#line:59
    O0000OOOOO0O000O0 =O0O0000000O000OO0 .getLayerNames ()#line:61
    OO00O0OOO0000O0O0 =O0O0000000O000OO0 .getUnconnectedOutLayers ()#line:62
    try :#line:63
        O00O00OO0O0OOOOO0 =[O0000OOOOO0O000O0 [O0OOO0OO0O000OO00 -1 ]for O0OOO0OO0O000OO00 in OO00O0OOO0000O0O0 ]#line:64
    except :#line:65
        O00O00OO0O0OOOOO0 =[O0000OOOOO0O000O0 [O000OO000000OO000 [0 ]-1 ]for O000OO000000OO000 in OO00O0OOO0000O0O0 ]#line:66
    return O00O00OO0O0OOOOO0 #line:68
def draw_bbox (O0O0O0OO0000OO000 ,OO0OO000OO00O0O0O ,OOO0OO00O0O0OO000 ,O0OO0O0OOOO0000OO ,O0O0OOOO0O00000OO ,colors =None ,write_conf =False ):#line:71
    global COLORS #line:73
    global classes #line:74
    if classes is None :#line:76
        classes =populate_class_labels (OO0OO000OO00O0O0O )#line:77
    if colors is None :#line:79
        colors =COLORS #line:80
    _O00O0OO0OO0O000O0 =FontUtil .get_font ()#line:82
    if isinstance (O0OO0O0OOOO0000OO ,str ):#line:83
        O0OO0OO0OOO00O000 =colors [0 ]#line:84
        if write_conf :#line:85
            O0OO0O0OOOO0000OO +=' '+str (format (O0O0OOOO0O00000OO *100 ,'.2f'))+'%'#line:86
        cv2 .rectangle (O0O0O0OO0000OO000 ,(OOO0OO00O0O0OO000 [0 ],OOO0OO00O0O0OO000 [1 ]),(OOO0OO00O0O0OO000 [2 ],OOO0OO00O0O0OO000 [3 ]),O0OO0OO0OOO00O000 ,2 )#line:87
        O00OOOOO000OOO00O =Image .fromarray (O0O0O0OO0000OO000 )#line:88
        O0O000000000O0O00 =ImageDraw .Draw (O00OOOOO000OOO00O )#line:89
        O0OO0OO0OOO00O000 =(int (O0OO0OO0OOO00O000 [0 ]),int (O0OO0OO0OOO00O000 [1 ]),int (O0OO0OO0OOO00O000 [2 ]))#line:90
        O0O000000000O0O00 .text ((OOO0OO00O0O0OO000 [0 ],OOO0OO00O0O0OO000 [1 ]-20 ),O0OO0O0OOOO0000OO ,font =_O00O0OO0OO0O000O0 ,fill =O0OO0OO0OOO00O000 )#line:91
    else :#line:93
        for O0O000O00OOO00000 ,O00O0OO000OO00OO0 in enumerate (O0OO0O0OOOO0000OO ):#line:94
            O0OO0OO0OOO00O000 =colors [classes .index (O00O0OO000OO00OO0 )]#line:95
            cv2 .rectangle (O0O0O0OO0000OO000 ,(OOO0OO00O0O0OO000 [O0O000O00OOO00000 ][0 ],OOO0OO00O0O0OO000 [O0O000O00OOO00000 ][1 ]),(OOO0OO00O0O0OO000 [O0O000O00OOO00000 ][2 ],OOO0OO00O0O0OO000 [O0O000O00OOO00000 ][3 ]),O0OO0OO0OOO00O000 ,2 )#line:96
        O00OOOOO000OOO00O =Image .fromarray (O0O0O0OO0000OO000 )#line:97
        O0O000000000O0O00 =ImageDraw .Draw (O00OOOOO000OOO00O )#line:98
        for O0O000O00OOO00000 ,O00O0OO000OO00OO0 in enumerate (O0OO0O0OOOO0000OO ):#line:99
            O0OO0OO0OOO00O000 =colors [classes .index (O00O0OO000OO00OO0 )]#line:100
            O0OO0OO0OOO00O000 =(int (O0OO0OO0OOO00O000 [0 ]),int (O0OO0OO0OOO00O000 [1 ]),int (O0OO0OO0OOO00O000 [2 ]))#line:101
            if write_conf :#line:102
                O00O0OO000OO00OO0 +=' '+str (format (O0O0OOOO0O00000OO [O0O000O00OOO00000 ]*100 ,'.2f'))+'%'#line:103
            O0O000000000O0O00 .text ((OOO0OO00O0O0OO000 [O0O000O00OOO00000 ][0 ],OOO0OO00O0O0OO000 [O0O000O00OOO00000 ][1 ]-20 ),O00O0OO000OO00OO0 ,font =_O00O0OO0OO0O000O0 ,fill =O0OO0OO0OOO00O000 )#line:104
    return np .asarray (O00OOOOO000OOO00O )#line:107
def detect_common_objects (OO00O0O0O00O000O0 ,O0O000OO0O0000O00 ,confidence =0.5 ,nms_thresh =0.3 ,enable_gpu =False ):#line:110
    O0O00O0O0O0000O0O ,OOO00000O0O0O0OOO =OO00O0O0O00O000O0 .shape [:2 ]#line:112
    OO0OO00O0000OO0OO =0.00392 #line:113
    global classes #line:115
    O00OOOO00O0OOOOOO =cv2 .dnn .blobFromImage (OO00O0O0O00O000O0 ,OO0OO00O0000OO0OO ,(416 ,416 ),(0 ,0 ,0 ),True ,crop =False )#line:131
    global initialize #line:142
    global net #line:143
    if initialize :#line:145
        classes =populate_class_labels (O0O000OO0O0000O00 )#line:146
        initialize =False #line:148
    if enable_gpu :#line:151
        net .setPreferableBackend (cv2 .dnn .DNN_BACKEND_CUDA )#line:152
        net .setPreferableTarget (cv2 .dnn .DNN_TARGET_CUDA )#line:153
    net .setInput (O00OOOO00O0OOOOOO )#line:155
    O0000000OO00OO0O0 =net .forward (get_output_layers (net ))#line:157
    O0OO00OOO00OOO00O =[]#line:159
    OOOO000O00O0O0OOO =[]#line:160
    O000O0OOO000OOO00 =[]#line:161
    for OOOO0000000OO00OO in O0000000OO00OO0O0 :#line:163
        for OO00OO00OOOOOO0O0 in OOOO0000000OO00OO :#line:164
            O0000OO00OO00000O =OO00OO00OOOOOO0O0 [5 :]#line:165
            OOOOOOOO0O00O00O0 =np .argmax (O0000OO00OO00000O )#line:166
            OOO0O0OOOOO0OO00O =O0000OO00OO00000O [OOOOOOOO0O00O00O0 ]#line:167
            if OOO0O0OOOOO0OO00O >confidence :#line:168
                O0OO000OO000O00O0 =int (OO00OO00OOOOOO0O0 [0 ]*OOO00000O0O0O0OOO )#line:169
                OO00000O00OOO0O0O =int (OO00OO00OOOOOO0O0 [1 ]*O0O00O0O0O0000O0O )#line:170
                OO000OO00OO0O0OO0 =int (OO00OO00OOOOOO0O0 [2 ]*OOO00000O0O0O0OOO )#line:171
                O00000O000O0OOOO0 =int (OO00OO00OOOOOO0O0 [3 ]*O0O00O0O0O0000O0O )#line:172
                O0OO00OO00000OO00 =O0OO000OO000O00O0 -(OO000OO00OO0O0OO0 /2 )#line:173
                OO00O00O000O0O00O =OO00000O00OOO0O0O -(O00000O000O0OOOO0 /2 )#line:174
                O0OO00OOO00OOO00O .append (OOOOOOOO0O00O00O0 )#line:175
                OOOO000O00O0O0OOO .append (float (OOO0O0OOOOO0OO00O ))#line:176
                O000O0OOO000OOO00 .append ([O0OO00OO00000OO00 ,OO00O00O000O0O00O ,OO000OO00OO0O0OO0 ,O00000O000O0OOOO0 ])#line:177
    O00OO0O00O0000O00 =cv2 .dnn .NMSBoxes (O000O0OOO000OOO00 ,OOOO000O00O0O0OOO ,confidence ,nms_thresh )#line:180
    OOO0OOO0O0000O00O =[]#line:182
    OOOOOOOOO00O00O00 =[]#line:183
    O000OOOO00000O0OO =[]#line:184
    try :#line:186
        for O00O0O00OOO0OOO0O in O00OO0O00O0000O00 :#line:187
            OO0O000OO00000O00 =O000O0OOO000OOO00 [O00O0O00OOO0OOO0O ]#line:189
            O0OO00OO00000OO00 =OO0O000OO00000O00 [0 ]#line:190
            OO00O00O000O0O00O =OO0O000OO00000O00 [1 ]#line:191
            OO000OO00OO0O0OO0 =OO0O000OO00000O00 [2 ]#line:192
            O00000O000O0OOOO0 =OO0O000OO00000O00 [3 ]#line:193
            OOO0OOO0O0000O00O .append ([int (O0OO00OO00000OO00 ),int (OO00O00O000O0O00O ),int (O0OO00OO00000OO00 +OO000OO00OO0O0OO0 ),int (OO00O00O000O0O00O +O00000O000O0OOOO0 )])#line:194
            OOOOOOOOO00O00O00 .append (str (classes [O0OO00OOO00OOO00O [O00O0O00OOO0OOO0O ]]))#line:195
            O000OOOO00000O0OO .append (OOOO000O00O0O0OOO [O00O0O00OOO0OOO0O ])#line:196
    except :#line:197
        for O00O0O00OOO0OOO0O in O00OO0O00O0000O00 :#line:198
            O00O0O00OOO0OOO0O =O00O0O00OOO0OOO0O [0 ]#line:199
            OO0O000OO00000O00 =O000O0OOO000OOO00 [O00O0O00OOO0OOO0O ]#line:200
            O0OO00OO00000OO00 =OO0O000OO00000O00 [0 ]#line:201
            OO00O00O000O0O00O =OO0O000OO00000O00 [1 ]#line:202
            OO000OO00OO0O0OO0 =OO0O000OO00000O00 [2 ]#line:203
            O00000O000O0OOOO0 =OO0O000OO00000O00 [3 ]#line:204
            OOO0OOO0O0000O00O .append ([int (O0OO00OO00000OO00 ),int (OO00O00O000O0O00O ),int (O0OO00OO00000OO00 +OO000OO00OO0O0OO0 ),int (OO00O00O000O0O00O +O00000O000O0OOOO0 )])#line:205
            OOOOOOOOO00O00O00 .append (str (classes [O0OO00OOO00OOO00O [O00O0O00OOO0OOO0O ]]))#line:206
            O000OOOO00000O0OO .append (OOOO000O00O0O0OOO [O00O0O00OOO0OOO0O ])#line:207
    return OOO0OOO0O0000O00O ,OOOOOOOOO00O00O00 ,O000OOOO00000O0OO #line:209
def load_common_objects_model (OO0O0O0OO0O00OO0O ,OO00OO0OO0OOO00O0 ):#line:211
    global net #line:212
    try :#line:213
        net =cv2 .dnn .readNet (OO0O0O0OO0O00OO0O ,OO00OO0OO0OOO00O0 )#line:214
        return True #line:215
    except :#line:216
        return False #line:217
class YOLO :#line:220
    def __init__ (O0OO0O0OO0O0O0O00 ,OOO000000O0O0O0OO ,OOOOOOOOOOOO00000 ,O00OOOO000O0OOOO0 ,version ='yolov3'):#line:222
        print ('[INFO] Initializing YOLO ..')#line:224
        O0OO0O0OO0O0O0O00 .config =OOOOOOOOOOOO00000 #line:226
        O0OO0O0OO0O0O0O00 .weights =OOO000000O0O0O0OO #line:227
        O0OO0O0OO0O0O0O00 .version =version #line:228
        with open (O00OOOO000O0OOOO0 ,'r')as OO0OO000O0OOOO0OO :#line:230
            O0OO0O0OO0O0O0O00 .labels =[O0O00O0O0O000OOO0 .strip ()for O0O00O0O0O000OOO0 in OO0OO000O0OOOO0OO .readlines ()]#line:231
        O0OO0O0OO0O0O0O00 .colors =np .random .uniform (0 ,255 ,size =(len (O0OO0O0OO0O0O0O00 .labels ),3 ))#line:233
        O0OO0O0OO0O0O0O00 .net =cv2 .dnn .readNet (O0OO0O0OO0O0O0O00 .weights ,O0OO0O0OO0O0O0O00 .config )#line:235
        O0O0000O0OOO0O00O =O0OO0O0OO0O0O0O00 .net .getLayerNames ()#line:237
        O0OO0O0OO0O0O0O00 .output_layers =[O0O0000O0OOO0O00O [O0OO0OOO0000O0O0O [0 ]-1 ]for O0OO0OOO0000O0O0O in O0OO0O0OO0O0O0O00 .net .getUnconnectedOutLayers ()]#line:239
    def detect_objects (O0O0000OOOO0O0O0O ,O0O00O0OOOOO0OOOO ,confidence =0.5 ,nms_thresh =0.3 ,enable_gpu =False ):#line:243
        if enable_gpu :#line:245
            net .setPreferableBackend (cv2 .dnn .DNN_BACKEND_CUDA )#line:246
            net .setPreferableTarget (cv2 .dnn .DNN_TARGET_CUDA )#line:247
        O0OOOO0000O0O00O0 ,OOO00000O0OOO00O0 =O0O00O0OOOOO0OOOO .shape [:2 ]#line:249
        OO00O0OOOO000OO00 =0.00392 #line:250
        OO00O00O000OOOOOO =cv2 .dnn .blobFromImage (O0O00O0OOOOO0OOOO ,OO00O0OOOO000OO00 ,(416 ,416 ),(0 ,0 ,0 ),True ,crop =False )#line:253
        O0O0000OOOO0O0O0O .net .setInput (OO00O00O000OOOOOO )#line:255
        O0000O0OO00O00OOO =O0O0000OOOO0O0O0O .net .forward (O0O0000OOOO0O0O0O .output_layers )#line:257
        O0OO00O0OO00O0OO0 =[]#line:259
        O00O00OOOO0O0O0OO =[]#line:260
        OOO0OOO00O0O0OO00 =[]#line:261
        for OO00O0OOOOOO000O0 in O0000O0OO00O00OOO :#line:263
            for OOOO00OOOO0OO000O in OO00O0OOOOOO000O0 :#line:264
                O00OOO000O0O000OO =OOOO00OOOO0OO000O [5 :]#line:265
                OOOO0O0000O00O0O0 =np .argmax (O00OOO000O0O000OO )#line:266
                OO0O0O00O000O00OO =O00OOO000O0O000OO [OOOO0O0000O00O0O0 ]#line:267
                if OO0O0O00O000O00OO >confidence :#line:268
                    O00000OO0O00000O0 =int (OOOO00OOOO0OO000O [0 ]*OOO00000O0OOO00O0 )#line:269
                    OOO0O00O0OOO0OO00 =int (OOOO00OOOO0OO000O [1 ]*O0OOOO0000O0O00O0 )#line:270
                    O000OOO00O00O00O0 =int (OOOO00OOOO0OO000O [2 ]*OOO00000O0OOO00O0 )#line:271
                    O00OOOOO00O00O0OO =int (OOOO00OOOO0OO000O [3 ]*O0OOOO0000O0O00O0 )#line:272
                    OO0000OO0O00OOO00 =O00000OO0O00000O0 -(O000OOO00O00O00O0 /2 )#line:273
                    O0OO00000OOO00000 =OOO0O00O0OOO0OO00 -(O00OOOOO00O00O0OO /2 )#line:274
                    O0OO00O0OO00O0OO0 .append (OOOO0O0000O00O0O0 )#line:275
                    O00O00OOOO0O0O0OO .append (float (OO0O0O00O000O00OO ))#line:276
                    OOO0OOO00O0O0OO00 .append ([OO0000OO0O00OOO00 ,O0OO00000OOO00000 ,O000OOO00O00O00O0 ,O00OOOOO00O00O0OO ])#line:277
        OOOO0O0OO0O0OOOO0 =cv2 .dnn .NMSBoxes (OOO0OOO00O0O0OO00 ,O00O00OOOO0O0O0OO ,confidence ,nms_thresh )#line:280
        OO00O0OOOO000OO0O =[]#line:282
        O0OO0O0000O0OO0OO =[]#line:283
        O0O0OO000OO00OO00 =[]#line:284
        for OOO00OOOOO0OO000O in OOOO0O0OO0O0OOOO0 :#line:286
            OOO00OOOOO0OO000O =OOO00OOOOO0OO000O [0 ]#line:287
            OO0O0OO0OO0OO00OO =OOO0OOO00O0O0OO00 [OOO00OOOOO0OO000O ]#line:288
            OO0000OO0O00OOO00 =OO0O0OO0OO0OO00OO [0 ]#line:289
            O0OO00000OOO00000 =OO0O0OO0OO0OO00OO [1 ]#line:290
            O000OOO00O00O00O0 =OO0O0OO0OO0OO00OO [2 ]#line:291
            O00OOOOO00O00O0OO =OO0O0OO0OO0OO00OO [3 ]#line:292
            OO00O0OOOO000OO0O .append ([int (OO0000OO0O00OOO00 ),int (O0OO00000OOO00000 ),int (OO0000OO0O00OOO00 +O000OOO00O00O00O0 ),int (O0OO00000OOO00000 +O00OOOOO00O00O0OO )])#line:293
            O0OO0O0000O0OO0OO .append (str (O0O0000OOOO0O0O0O .labels [O0OO00O0OO00O0OO0 [OOO00OOOOO0OO000O ]]))#line:294
            O0O0OO000OO00OO00 .append (O00O00OOOO0O0O0OO [OOO00OOOOO0OO000O ])#line:295
        return OO00O0OOOO000OO0O ,O0OO0O0000O0OO0OO ,O0O0OO000OO00OO00 #line:297
    def draw_bbox (OO0OOO00OO0000O00 ,O00000O0O0OOO0OO0 ,OO0O000OOOOOOOOO0 ,OO0OOO00OO0000000 ,O0OO000O00OO0OOOO ,colors =None ,write_conf =False ):#line:300
        if colors is None :#line:302
            colors =OO0OOO00OO0000O00 .colors #line:303
        if isinstance (OO0OOO00OO0000000 ,list ):#line:305
            for O0OO0O0OO00000O0O ,O000OOO0OO0OOO000 in enumerate (OO0OOO00OO0000000 ):#line:306
                O000000O00O0OO000 =colors [OO0OOO00OO0000O00 .labels .index (O000OOO0OO0OOO000 )]#line:308
                if write_conf :#line:310
                    O000OOO0OO0OOO000 +=' '+str (format (O0OO000O00OO0OOOO [O0OO0O0OO00000O0O ]*100 ,'.2f'))+'%'#line:311
                cv2 .rectangle (O00000O0O0OOO0OO0 ,(OO0O000OOOOOOOOO0 [O0OO0O0OO00000O0O ][0 ],OO0O000OOOOOOOOO0 [O0OO0O0OO00000O0O ][1 ]),(OO0O000OOOOOOOOO0 [O0OO0O0OO00000O0O ][2 ],OO0O000OOOOOOOOO0 [O0OO0O0OO00000O0O ][3 ]),O000000O00O0OO000 ,2 )#line:313
                cv2 .putText (O00000O0O0OOO0OO0 ,O000OOO0OO0OOO000 ,(OO0O000OOOOOOOOO0 [O0OO0O0OO00000O0O ][0 ],OO0O000OOOOOOOOO0 [O0OO0O0OO00000O0O ][1 ]-10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,O000000O00O0OO000 ,2 )#line:315
        else :#line:316
            O000000O00O0OO000 =colors [0 ]#line:317
            if write_conf :#line:318
                OO0OOO00OO0000000 +=' '+str (format (O0OO000O00OO0OOOO *100 ,'.2f'))+'%'#line:319
            cv2 .rectangle (O00000O0O0OOO0OO0 ,(OO0O000OOOOOOOOO0 [0 ],OO0O000OOOOOOOOO0 [1 ]),(OO0O000OOOOOOOOO0 [2 ],OO0O000OOOOOOOOO0 [3 ]),O000000O00O0OO000 ,2 )#line:320
            cv2 .putText (O00000O0O0OOO0OO0 ,O000OOO0OO0OOO000 ,(OO0O000OOOOOOOOO0 [0 ],OO0O000OOOOOOOOO0 [1 ]-10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,O000000O00O0OO000 ,2 )#line:321
class ObjectDetector :#line:324
    _DEFAULT_FOLDER ='c:/roboid/model'#line:325
    def __init__ (OO0000O0OOOO0O000 ,multi =False ,lang ='en'):#line:327
        OO0000O0OOOO0O000 ._multi =multi #line:328
        OO0000O0OOOO0O000 ._lang =lang #line:329
        OO0000O0OOOO0O000 ._loaded =False #line:330
        OO0000O0OOOO0O000 ._clear ()#line:331
    def _clear (OOOO0000OO0OOO0O0 ):#line:333
        if OOOO0000OO0OOO0O0 ._multi :#line:334
            OOOO0000OO0OOO0O0 ._boxes =[]#line:335
            OOOO0000OO0OOO0O0 ._labels =[]#line:336
            OOOO0000OO0OOO0O0 ._confidences =[]#line:337
        else :#line:338
            OOOO0000OO0OOO0O0 ._boxes =None #line:339
            OOOO0000OO0OOO0O0 ._labels =''#line:340
            OOOO0000OO0OOO0O0 ._confidences =0 #line:341
    def load_model (O00O0OO000OO0OOO0 ,folder =None ):#line:343
        try :#line:344
            if folder is None :#line:345
                folder =ObjectDetector ._DEFAULT_FOLDER #line:346
            O0O0OO0OO0O0000O0 =os .path .join (folder ,'object.weights')#line:347
            if os .path .exists (O0O0OO0OO0O0000O0 ):#line:348
                OOOOOO00O000000O0 =os .path .join (folder ,'object.cfg')#line:349
            else :#line:350
                O0O0OO0OO0O0000O0 =folder +'.weights'#line:351
                OOOOOO00O000000O0 =folder +'.cfg'#line:352
            if load_common_objects_model (O0O0OO0OO0O0000O0 ,OOOOOO00O000000O0 ):#line:353
                O00O0OO000OO0OOO0 ._loaded =True #line:354
                return True #line:355
            return False #line:356
        except :#line:357
            return False #line:358
    def download_model (OO0OOO0OOO0O00OO0 ,folder =None ,overwrite =False ):#line:360
        print ('model downloading...')#line:361
        if folder is None :#line:362
            folder =ObjectDetector ._DEFAULT_FOLDER #line:363
        if not os .path .isdir (folder ):#line:364
            os .makedirs (folder )#line:365
        DownloadTool .download_model (folder ,'object.weights',overwrite )#line:366
        DownloadTool .download_model (folder ,'object.cfg',overwrite )#line:367
    def detect (O0000OO0O0000OO00 ,OOOO0O0OO00OOOOO0 ,conf_threshold =0.5 ,nms_threshold =0.4 ,gpu =False ):#line:369
        if OOOO0O0OO00OOOOO0 is None :#line:370
            O0000OO0O0000OO00 ._clear ()#line:371
        elif O0000OO0O0000OO00 ._loaded :#line:372
            OOOO0OO0000O0OO0O ,O0OOOOOOO00OOOOO0 ,O000O0O0O00OO00OO =detect_common_objects (OOOO0O0OO00OOOOO0 ,O0000OO0O0000OO00 ._lang ,conf_threshold ,nms_threshold ,gpu )#line:373
            if O0000OO0O0000OO00 ._multi :#line:374
                O0000OO0O0000OO00 ._boxes =OOOO0OO0000O0OO0O #line:375
                O0000OO0O0000OO00 ._labels =O0OOOOOOO00OOOOO0 #line:376
                O0000OO0O0000OO00 ._confidences =O000O0O0O00OO00OO #line:377
                return len (O0OOOOOOO00OOOOO0 )>0 #line:378
            else :#line:379
                O00000O0O000O00OO =-1 #line:380
                O0O00000O0OO0OO0O =-1 #line:381
                for OO00O0000OOOO0O0O ,O000O0OO0OO00OOOO in enumerate (OOOO0OO0000O0OO0O ):#line:382
                    OOOO000OO0O0OOO00 =abs (O000O0OO0OO00OOOO [2 ]-O000O0OO0OO00OOOO [0 ])*abs (O000O0OO0OO00OOOO [3 ]-O000O0OO0OO00OOOO [1 ])#line:383
                    if OOOO000OO0O0OOO00 >O00000O0O000O00OO :#line:384
                        O00000O0O000O00OO =OOOO000OO0O0OOO00 #line:385
                        O0O00000O0OO0OO0O =OO00O0000OOOO0O0O #line:386
                if O0O00000O0OO0OO0O <0 :#line:387
                    O0000OO0O0000OO00 ._boxes =None #line:388
                    O0000OO0O0000OO00 ._labels =''#line:389
                    O0000OO0O0000OO00 ._confidences =0 #line:390
                else :#line:391
                    O0000OO0O0000OO00 ._boxes =OOOO0OO0000O0OO0O [O0O00000O0OO0OO0O ]#line:392
                    O0000OO0O0000OO00 ._labels =O0OOOOOOO00OOOOO0 [O0O00000O0OO0OO0O ]#line:393
                    O0000OO0O0000OO00 ._confidences =O000O0O0O00OO00OO [O0O00000O0OO0OO0O ]#line:394
                    return True #line:395
        return False #line:396
    def draw_result (O0OO000O00O0OO0OO ,O00OOOOOO0O00O0O0 ,colors =None ,show_conf =False ):#line:398
        if O00OOOOOO0O00O0O0 is not None :#line:399
            if O0OO000O00O0OO0OO ._multi or O0OO000O00O0OO0OO ._boxes is not None :#line:400
                O00OOOOOO0O00O0O0 =draw_bbox (O00OOOOOO0O00O0O0 ,O0OO000O00O0OO0OO ._lang ,O0OO000O00O0OO0OO ._boxes ,O0OO000O00O0OO0OO ._labels ,O0OO000O00O0OO0OO ._confidences ,colors ,show_conf )#line:401
        return O00OOOOOO0O00O0O0 #line:402
    def get_box (OO0OO0000O0OOO0OO ):#line:404
        return OO0OO0000O0OOO0OO ._boxes #line:405
    def get_label (OOOOOOOOO0O0OO0O0 ):#line:407
        return OOOOOOOOO0O0OO0O0 ._labels #line:408
    def get_conf (O000O0000OOO000OO ):#line:410
        return O000O0000OOO000OO ._confidences #line:411
