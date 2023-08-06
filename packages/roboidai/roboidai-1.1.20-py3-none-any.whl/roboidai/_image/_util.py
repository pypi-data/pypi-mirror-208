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

import math #line:19
import os #line:20
class Util :#line:23
    @staticmethod #line:24
    def distance (OO00OO0OOOOO0O0O0 ,O0O0000O0O00OOO0O ):#line:25
        if OO00OO0OOOOO0O0O0 is not None and O0O0000O0O00OOO0O is not None :#line:26
            OOO00000OOO00OOO0 =min (len (OO00OO0OOOOO0O0O0 ),len (O0O0000O0O00OOO0O ))#line:27
            OO0OO0000OO0O0O0O =0 #line:28
            for OO000OOOOOOO00O00 in range (OOO00000OOO00OOO0 ):#line:29
                OO0OO0000OO0O0O0O +=(OO00OO0OOOOO0O0O0 [OO000OOOOOOO00O00 ]-O0O0000O0O00OOO0O [OO000OOOOOOO00O00 ])**2 #line:30
            return math .sqrt (OO0OO0000OO0O0O0O )#line:31
        return None #line:32
    @staticmethod #line:34
    def degree (O0O0OO0O0O0000O00 ,OO000000OO000OOOO ):#line:35
        if O0O0OO0O0O0000O00 is not None and OO000000OO000OOOO is not None :#line:36
            O0OO0OO0O0O0O0O00 =OO000000OO000OOOO [0 ]-O0O0OO0O0O0000O00 [0 ]#line:37
            OOO000O000OO000O0 =O0O0OO0O0O0000O00 [1 ]-OO000000OO000OOOO [1 ]#line:38
            return math .degrees (math .atan2 (OOO000O000OO000O0 ,O0OO0OO0O0O0O0O00 ))#line:39
        return None #line:40
    @staticmethod #line:42
    def radian (O0O00OO0OO00O0000 ,OO0O0O00000O0OO0O ):#line:43
        if O0O00OO0OO00O0000 is not None and OO0O0O00000O0OO0O is not None :#line:44
            OO0OOO00OO00O0O00 =OO0O0O00000O0OO0O [0 ]-O0O00OO0OO00O0000 [0 ]#line:45
            O000O0O0OOO0OOOOO =O0O00OO0OO00O0000 [1 ]-OO0O0O00000O0OO0O [1 ]#line:46
            return math .atan2 (O000O0O0OOO0OOOOO ,OO0OOO00OO00O0O00 )#line:47
        return None #line:48
    @staticmethod #line:50
    def realize_filepath (O00OO00O00000000O ):#line:51
        if isinstance (O00OO00O00000000O ,str ):#line:52
            OOOOO00O00O00OO00 =os .path .dirname (O00OO00O00000000O )#line:53
            if not os .path .isdir (OOOOO00O00O00OO00 ):#line:54
                os .makedirs (OOOOO00O00O00OO00 )#line:55
class FontUtil :#line:58
    _FONT =None #line:59
    @staticmethod #line:61
    def get_font ():#line:62
        if FontUtil ._FONT is None :#line:63
            from PIL import ImageFont #line:64
            FontUtil ._FONT =ImageFont .truetype (os .sep .join ([os .path .dirname (os .path .realpath (__file__ )),'malgun.ttf']),12 )#line:65
        return FontUtil ._FONT #line:66
