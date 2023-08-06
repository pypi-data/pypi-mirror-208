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

from roboid import Runner #line:19
import ifaddr #line:20
import socket #line:21
import cv2 #line:22
import threading #line:23
import time #line:24
from timeit import default_timer as timer #line:25
_O0000O0O0O0OOOO00 ={8 :'bs',9 :'tab',13 :'enter',27 :'esc'}#line:33
_O0000O0OO0OOOOOOO ={'bs':8 ,'tab':9 ,'enter':13 ,'esc':27 }#line:39
class _OO00OOOO00OO0O0O0 :#line:42
    _AVOIDS =('192.168.0.1','192.168.1.1')#line:43
    @staticmethod #line:45
    def _connect (OO0OOO00O00O0000O ,OO00000O0OOOO0O0O ):#line:46
        OOOO000O000O0000O =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )#line:47
        socket .setdefaulttimeout (1 )#line:48
        O00OOOO00O0O00OO0 =OOOO000O000O0000O .connect_ex ((OO0OOO00O00O0000O ,OO00000O0OOOO0O0O ))#line:49
        OOOO000O000O0000O .close ()#line:50
        return O00OOOO00O0O00OO0 ==0 #line:51
    @staticmethod #line:53
    def scan (max_ip =5 ,multi =False ,wifi_name =None ,user ='admin',passwd ='admin'):#line:54
        O00OO00000OO000O0 =[]#line:55
        OOOOO0O00O000O0OO =[]#line:56
        O0OO0OOO00O0OO000 =ifaddr .get_adapters ()#line:57
        if wifi_name is None :#line:58
            for O00O00OO0O00000O0 in O0OO0OOO00O0OO000 [::-1 ]:#line:59
                for OO0O0OOOO0OOOOOO0 in O00O00OO0O00000O0 .ips :#line:60
                    OOOOOOO0OO0O0OOO0 =OO0O0OOOO0OOOOOO0 .nice_name .lower ()#line:61
                    if 'bluetooth'in OOOOOOO0OO0O0OOO0 :continue #line:62
                    if 'loopback'in OOOOOOO0OO0O0OOO0 :continue #line:63
                    if OO0O0OOOO0OOOOOO0 .ip =='127.0.0.1'or OO0O0OOOO0OOOOOO0 .ip =='0.0.0.0':continue #line:64
                    if isinstance (OO0O0OOOO0OOOOOO0 .ip ,str ):#line:65
                        OO000O0OO00OOO0OO =OO0O0OOOO0OOOOOO0 .ip .split ('.')#line:66
                        if len (OO000O0OO00OOO0OO )>3 and OO000O0OO00OOO0OO [0 ]=='192'and OO000O0OO00OOO0OO [2 ]=='66':#line:67
                            O00OO00000OO000O0 .append (OO0O0OOOO0OOOOOO0 .ip )#line:68
        else :#line:69
            for O00O00OO0O00000O0 in O0OO0OOO00O0OO000 :#line:70
                for OO0O0OOOO0OOOOOO0 in O00O00OO0O00000O0 .ips :#line:71
                    if wifi_name ==OO0O0OOOO0OOOOOO0 .nice_name :#line:72
                        if isinstance (OO0O0OOOO0OOOOOO0 .ip ,str ):#line:73
                            O00OO00000OO000O0 .append (OO0O0OOOO0OOOOOO0 .ip )#line:74
        OO00O0O0000O0O000 =('192.168.66.')#line:75
        OOOO000O000OO0O0O =[]#line:76
        OOOO0O0OOO0O0O00O =[]#line:77
        for OO0O0OOOO0OOOOOO0 in O00OO00000OO000O0 :#line:78
            OO000O0OO00OOO0OO =OO0O0OOOO0OOOOOO0 .split ('.')#line:79
            if len (OO000O0OO00OOO0OO )>3 :#line:80
                OO000OO0000O0OOOO ='{}.{}.{}.'.format (OO000O0OO00OOO0OO [0 ],OO000O0OO00OOO0OO [1 ],OO000O0OO00OOO0OO [2 ])#line:81
                if OO000OO0000O0OOOO in OO00O0O0000O0O000 :#line:82
                    if OO000OO0000O0OOOO not in OOOO000O000OO0O0O :#line:83
                        OOOO000O000OO0O0O .append (OO000OO0000O0OOOO )#line:84
                else :#line:85
                    if OO000OO0000O0OOOO not in OOOO0O0OOO0O0O00O :#line:86
                        OOOO0O0OOO0O0O00O .append (OO000OO0000O0OOOO )#line:87
        OOOO000O000OO0O0O .extend (OOOO0O0OOO0O0O00O )#line:88
        for O0000O0OOO0OOOOOO in range (1 ,max_ip +1 ):#line:90
            O00O00O0O00O0OO0O =[]#line:91
            for OO000OO0000O0OOOO in OOOO000O000OO0O0O :#line:92
                OO0O0O0O000000O00 =OO000OO0000O0OOOO +str (O0000O0OOO0OOOOOO )#line:93
                if OO0O0O0O000000O00 not in _OO00OOOO00OO0O0O0 ._AVOIDS and _OO00OOOO00OO0O0O0 ._connect (OO0O0O0O000000O00 ,9527 ):#line:94
                    O0OO0OO0O00000O0O =cv2 .VideoCapture ('http://'+OO0O0O0O000000O00 +':9527/videostream.cgi?loginuse='+user +'&loginpas='+passwd )#line:95
                    if O0OO0OO0O00000O0O .isOpened ():#line:96
                        OOOOO0O00O000O0OO .append (O0OO0OO0O00000O0O )#line:97
                        if multi :#line:98
                            O00O00O0O00O0OO0O .append (OO000OO0000O0OOOO )#line:99
                        else :#line:100
                            return OOOOO0O00O000O0OO #line:101
            if O00O00O0O00O0OO0O :#line:102
                OOOO000O000OO0O0O =[OOO00OO00OO00OO0O for OOO00OO00OO00OO0O in OOOO000O000OO0O0O if OOO00OO00OO00OO0O not in O00O00O0O00O0OO0O ]#line:103
                O00O00O0O00O0OO0O =[]#line:104
        return OOOOO0O00O000O0OO #line:105
class Camera :#line:108
    @staticmethod #line:109
    def test (target ='all',max_usb =10 ,max_ip =5 ,wifi_name =None ,user ='admin',passwd ='admin'):#line:110
        OOOOO0OO0OOO000OO ={}#line:111
        O0OOOO00O0000O0OO ={}#line:112
        if isinstance (target ,str ):#line:113
            target =target .lower ()#line:114
        if target =='all'or target =='usb':#line:115
            print ('scanning usb camera...')#line:116
            for OOO0O0000O0OOO0OO in range (max_usb +1 ):#line:117
                O0000OOOO0O000O0O =cv2 .VideoCapture (OOO0O0000O0OOO0OO )#line:118
                if O0000OOOO0O000O0O .isOpened ():#line:119
                    OOOOO0OO0OOO000OO [OOO0O0000O0OOO0OO ]=O0000OOOO0O000O0O #line:120
        if target =='all'or target =='ip':#line:121
            print ('scanning ip camera...')#line:122
            for OOO0O0000O0OOO0OO ,O0000OOOO0O000O0O in enumerate (_OO00OOOO00OO0O0O0 .scan (max_ip ,False ,wifi_name ,user ,passwd )):#line:123
                O0OOOO00O0000O0OO [OOO0O0000O0OOO0OO ]=O0000OOOO0O000O0O #line:124
        print ('scanning completed')#line:125
        while True :#line:126
            for OOO0O0000O0OOO0OO in OOOOO0OO0OOO000OO :#line:127
                O0O0000O0000O0000 ,OOOOO0O0O0O00O0O0 =OOOOO0OO0OOO000OO [OOO0O0000O0OOO0OO ].read ()#line:128
                if O0O0000O0000O0000 :#line:129
                    cv2 .putText (OOOOO0O0O0O00O0O0 ,'press ESC key to quit',(30 ,40 ),cv2 .FONT_HERSHEY_SIMPLEX ,1 ,(255 ,255 ,255 ),2 )#line:130
                    cv2 .imshow ('camera usb{}'.format (OOO0O0000O0OOO0OO ),OOOOO0O0O0O00O0O0 )#line:131
            for OOO0O0000O0OOO0OO in O0OOOO00O0000O0OO :#line:132
                O0O0000O0000O0000 ,OOOOO0O0O0O00O0O0 =O0OOOO00O0000O0OO [OOO0O0000O0OOO0OO ].read ()#line:133
                if O0O0000O0000O0000 :#line:134
                    OOOOO0O0O0O00O0O0 =OOOOO0O0O0O00O0O0 [40 :,:]#line:135
                    cv2 .putText (OOOOO0O0O0O00O0O0 ,'press ESC key to quit',(30 ,40 ),cv2 .FONT_HERSHEY_SIMPLEX ,1 ,(255 ,255 ,255 ),2 )#line:136
                    cv2 .imshow ('camera ip{}'.format (OOO0O0000O0OOO0OO ),OOOOO0O0O0O00O0O0 )#line:137
            if cv2 .waitKey (1 )==27 :#line:138
                break #line:139
        for OOO0O0000O0OOO0OO in OOOOO0OO0OOO000OO :#line:140
            OOOOO0OO0OOO000OO [OOO0O0000O0OOO0OO ].release ()#line:141
        for OOO0O0000O0OOO0OO in O0OOOO00O0000O0OO :#line:142
            O0OOOO00O0000O0OO [OOO0O0000O0OOO0OO ].release ()#line:143
        cv2 .destroyAllWindows ()#line:144
    @staticmethod #line:146
    def check_key (timeout_msec =1 ):#line:147
        O0OO0O000OOOO0O0O =cv2 .waitKey (timeout_msec )#line:148
        if O0OO0O000OOOO0O0O >=32 and O0OO0O000OOOO0O0O <=126 :return chr (O0OO0O000OOOO0O0O )#line:149
        elif O0OO0O000OOOO0O0O in _O0000O0O0O0OOOO00 :return _O0000O0O0O0OOOO00 [O0OO0O000OOOO0O0O ]#line:150
        return None #line:151
    @staticmethod #line:153
    def wait_until_key (key =None ):#line:154
        if isinstance (key ,str ):#line:155
            O0O0OO0O0O0O0O0O0 =key .lower ()#line:156
            if O0O0OO0O0O0O0O0O0 in _O0000O0OO0OOOOOOO :#line:157
                key =_O0000O0OO0OOOOOOO [O0O0OO0O0O0O0O0O0 ]#line:158
            elif len (key )==1 :#line:159
                key =ord (key [0 ])#line:160
        while True :#line:161
            if key is None :#line:162
                if cv2 .waitKey (10 )!=-1 :#line:163
                    break #line:164
            elif cv2 .waitKey (10 )==key :#line:165
                break #line:166
    def __init__ (O0O00O00O000O0O00 ,id =0 ,flip =None ,square =False ,crop =True ,max_ip =5 ,wifi_name =None ,user ='admin',passwd ='admin'):#line:168
        OOO0O0000000O00O0 =None #line:169
        OO0OO00O00O00OO0O =''#line:170
        try :#line:171
            if isinstance (id ,(int ,float )):#line:172
                id =int (id )#line:173
                OO0OO00O00O00OO0O ='usb{}'.format (id )#line:174
                OOO0O0000000O00O0 =O0O00O00O000O0O00 ._create_usb_cam (id ,OO0OO00O00O00OO0O )#line:175
            elif isinstance (id ,str ):#line:176
                id =id .lower ()#line:177
                OO0OO00O00O00OO0O =id #line:178
                if id .startswith ('usb'):#line:179
                    OOO0O0000000O00O0 =O0O00O00O000O0O00 ._create_usb_cam (int (id [3 :]),OO0OO00O00O00OO0O )#line:180
                elif id .startswith ('ip'):#line:181
                    OOO0O0000000O00O0 =O0O00O00O000O0O00 ._create_ip_cam (int (id [2 :]),OO0OO00O00O00OO0O ,max_ip ,wifi_name ,user ,passwd )#line:182
        except :#line:183
            print ('Cannot open camera',OO0OO00O00O00OO0O )#line:184
        O0O00O00O000O0O00 .set_flip (flip )#line:185
        O0O00O00O000O0O00 .set_square (square )#line:186
        O0O00O00O000O0O00 ._crop =crop #line:187
        O0O00O00O000O0O00 ._cap =OOO0O0000000O00O0 #line:188
        O0O00O00O000O0O00 ._title =OO0OO00O00O00OO0O #line:189
        O0O00O00O000O0O00 ._frame =None #line:190
        O0O00O00O000O0O00 ._width =0 #line:191
        O0O00O00O000O0O00 ._height =0 #line:192
        if OOO0O0000000O00O0 is not None :#line:193
            Runner .register_component (O0O00O00O000O0O00 )#line:194
            OO0O0000O0O0O0O00 =threading .Thread (target =O0O00O00O000O0O00 ._run )#line:195
            OO0O0000O0O0O0O00 .daemon =True #line:196
            OO0O0000O0O0O0O00 .start ()#line:197
    def _run (O00OO0OO00OOO0O0O ):#line:199
        while True :#line:200
            if O00OO0OO00OOO0O0O ._cap is not None and O00OO0OO00OOO0O0O ._cap .isOpened ():#line:201
                OO00O0O00O00000OO ,O000O0OOO0O0000OO =O00OO0OO00OOO0O0O ._cap .read ()#line:202
                if OO00O0O00O00000OO :#line:203
                    O00OO0OO00OOO0O0O ._frame =O000O0OOO0O0000OO #line:204
                    O00OO0OO00OOO0O0O ._width =O000O0OOO0O0000OO .shape [1 ]#line:205
                    O00OO0OO00OOO0O0O ._height =O000O0OOO0O0000OO .shape [0 ]#line:206
                else :#line:207
                    O00OO0OO00OOO0O0O ._frame =None #line:208
                    O00OO0OO00OOO0O0O ._width =0 #line:209
                    O00OO0OO00OOO0O0O ._height =0 #line:210
            time .sleep (.01 )#line:211
    def _create_usb_cam (O000OOOO0OO00O0OO ,OO0O0O000O0O00000 ,O0O0O000OOO0O0O0O ):#line:213
        O000OOOO0OO00O0OO ._ip_cam =False #line:214
        OOO0O000O0O0OO0OO =cv2 .VideoCapture (OO0O0O000O0O00000 )#line:215
        if OOO0O000O0O0OO0OO .isOpened ():#line:216
            return OOO0O000O0O0OO0OO #line:217
        print ('Cannot open camera',O0O0O000OOO0O0O0O )#line:218
        return None #line:219
    def _create_ip_cam (O0O0OOO0O00000O0O ,O00OO0O00OO00OOOO ,O00O000OOOOOO0OOO ,max_ip =5 ,wifi_name =None ,user ='admin',passwd ='admin'):#line:221
        O0O0OOO0O00000O0O ._ip_cam =True #line:222
        print ('scanning ip camera...')#line:223
        O00OOO0O0OOO0OOO0 =_OO00OOOO00OO0O0O0 .scan (max_ip ,False ,wifi_name ,user ,passwd )#line:224
        print ('scanning completed')#line:225
        if O00OO0O00OO00OOOO >=0 and O00OO0O00OO00OOOO <len (O00OOO0O0OOO0OOO0 ):#line:226
            return O00OOO0O0OOO0OOO0 [O00OO0O00OO00OOOO ]#line:227
        print ('Cannot open camera',O00O000OOOOOO0OOO )#line:228
        return None #line:229
    def dispose (O00O0OOOO0OO000OO ):#line:231
        if O00O0OOOO0OO000OO ._cap is not None :#line:232
            O00O0OOOO0OO000OO ._cap .release ()#line:233
        cv2 .destroyWindow (O00O0OOOO0OO000OO ._title )#line:234
        Runner .unregister_component (O00O0OOOO0OO000OO )#line:235
    def set_flip (OOOO0OO0O00OO0000 ,flip =None ):#line:237
        if flip is None :#line:238
            OOOO0OO0O00OO0000 ._flip =None #line:239
        elif isinstance (flip ,str ):#line:240
            flip =flip .lower ()#line:241
            if flip .startswith ('h'):OOOO0OO0O00OO0000 ._flip =1 #line:242
            elif flip .startswith ('v'):OOOO0OO0O00OO0000 ._flip =0 #line:243
            elif flip .startswith ('a'):OOOO0OO0O00OO0000 ._flip =-1 #line:244
            elif flip .startswith ('n'):OOOO0OO0O00OO0000 ._flip =None #line:245
    def _to_square (O0O0OO0OO0O0OO0O0 ,OOOOOO0O00O0OO0O0 ):#line:247
        if OOOOOO0O00O0OO0O0 is not None :#line:248
            OOO0OOO000OOO000O =OOOOOO0O00O0OO0O0 .shape [1 ]#line:249
            OO00OOOOO00OO000O =OOOOOO0O00O0OO0O0 .shape [0 ]#line:250
            if OO00OOOOO00OO000O >OOO0OOO000OOO000O :#line:251
                OOO00000OO0OOO0O0 =(OO00OOOOO00OO000O -OOO0OOO000OOO000O )//2 #line:252
                OOOOOO0O00O0OO0O0 =OOOOOO0O00O0OO0O0 [OOO00000OO0OOO0O0 :OOO00000OO0OOO0O0 +OOO0OOO000OOO000O ,:]#line:253
            else :#line:254
                OOO00000OO0OOO0O0 =(OOO0OOO000OOO000O -OO00OOOOO00OO000O )//2 #line:255
                OOOOOO0O00O0OO0O0 =OOOOOO0O00O0OO0O0 [:,OOO00000OO0OOO0O0 :OOO00000OO0OOO0O0 +OO00OOOOO00OO000O ]#line:256
        return OOOOOO0O00O0OO0O0 #line:257
    def get_width (OOO0O0O00000O0OO0 ):#line:259
        return OOO0O0O00000O0OO0 ._width #line:260
    def get_height (O000OOOO0O000O0O0 ):#line:262
        return O000OOOO0O000O0O0 ._height #line:263
    def is_square (O0OOOO000000OOO00 ):#line:265
        return O0OOOO000000OOO00 ._square #line:266
    def set_square (OO0000000OO000000 ,O000000O00O000OO0 ):#line:268
        OO0000000OO000000 ._square =O000000O00O000OO0 #line:269
    def read (O0OO0O0OOO0OOOOOO ):#line:271
        O0OO00OOO0OOOOOO0 =O0OO0O0OOO0OOOOOO ._frame #line:272
        if O0OO00OOO0OOOOOO0 is not None :#line:273
            if O0OO0O0OOO0OOOOOO ._ip_cam and O0OO0O0OOO0OOOOOO ._crop :#line:274
                O0OO00OOO0OOOOOO0 =O0OO00OOO0OOOOOO0 [40 :,:]#line:275
            if O0OO0O0OOO0OOOOOO ._flip is not None :#line:276
                O0OO00OOO0OOOOOO0 =cv2 .flip (O0OO00OOO0OOOOOO0 ,O0OO0O0OOO0OOOOOO ._flip )#line:277
            if O0OO0O0OOO0OOOOOO ._square :#line:278
                O0OO00OOO0OOOOOO0 =O0OO0O0OOO0OOOOOO ._to_square (O0OO00OOO0OOOOOO0 )#line:279
        return O0OO00OOO0OOOOOO0 #line:280
    def read_until_key (OO000OO000O0OO00O ):#line:282
        while True :#line:283
            OO00O0OO0OOO0OOO0 =OO000OO000O0OO00O .read ()#line:284
            OO000OO000O0OO00O .show (OO00O0OO0OOO0OOO0 )#line:285
            O0OOOOOO00O0O0O0O =OO000OO000O0OO00O .check_key ()#line:287
            if O0OOOOOO00O0O0O0O is not None :#line:288
                return OO00O0OO0OOO0OOO0 ,O0OOOOOO00O0O0O0O #line:289
    def show (O000O0OOO000OOO0O ,O00000OO000OOOO0O ):#line:291
        if O00000OO000OOOO0O is not None and O00000OO000OOOO0O .shape [0 ]>0 and O00000OO000OOOO0O .shape [1 ]>0 :#line:292
            cv2 .imshow (O000O0OOO000OOO0O ._title ,O00000OO000OOOO0O )#line:293
    def hide (OOO00OO0OOO000O0O ):#line:295
        cv2 .destroyWindow (OOO00OO0OOO000O0O ._title )#line:296
    def count_down (O00O0O0O00OO00OOO ,count =5 ):#line:298
        O00OOO0000OOO0O0O =O00O0O0O00OO00OOO .read ()#line:299
        if O00OOO0000OOO0O0O is not None :#line:300
            O00O0O0O000000O0O =O00OOO0000OOO0O0O .copy ()#line:301
            cv2 .putText (O00O0O0O000000O0O ,str (count ),(0 ,240 ),cv2 .FONT_HERSHEY_SIMPLEX ,10 ,(255 ,255 ,255 ),20 ,16 )#line:302
            O00O0O0O00OO00OOO .show (O00O0O0O000000O0O )#line:303
        for O0O00OO000O0O0OOO in range (count ,0 ,-1 ):#line:304
            O000OO0000OO00000 =timer ()+1 #line:305
            while timer ()<O000OO0000OO00000 :#line:306
                O00OOO0000OOO0O0O =O00O0O0O00OO00OOO .read ()#line:307
                if O00OOO0000OOO0O0O is not None :#line:308
                    O00O0O0O000000O0O =O00OOO0000OOO0O0O .copy ()#line:309
                    cv2 .putText (O00O0O0O000000O0O ,str (O0O00OO000O0O0OOO ),(0 ,240 ),cv2 .FONT_HERSHEY_SIMPLEX ,10 ,(255 ,255 ,255 ),20 ,16 )#line:310
                    O00O0O0O00OO00OOO .show (O00O0O0O000000O0O )#line:311
                cv2 .waitKey (1 )#line:312
        O00OOO0000OOO0O0O =O00O0O0O00OO00OOO .read ()#line:313
        O00O0O0O00OO00OOO .show (O00OOO0000OOO0O0O )#line:314
        return O00OOO0000OOO0O0O #line:315
